import os
import sys
import glob
import re
import json
import numpy as np
import matplotlib.pyplot as plt
import umap
from sentence_transformers import SentenceTransformer
import ollama

MODEL_NAME = "qwen3-coder:480b-cloud"
EMBED_MODEL = "all-MiniLM-L6-v2"
SEED_1 = 42
SEED_2 = 1337

PROMPTS = [
    "The capital of France is",
    "In a futuristic city where data is currency, a rogue hacker",
    "The most important protocol for AICO unikernel is",
    "Why did the chicken cross the Moebius strip?",
    "The quantum entanglement of two particles implies",
    "A recipe for a cake that tastes like a rainy afternoon",
    "The legal implications of a self-aware toaster",
    "Describe a sunset on a planet with three suns",
    "The recursive nature of a mirror reflecting another mirror",
    "How to build a functional time machine using only duct tape",
    "The emotional landscape of a lonely satellite",
    "A mathematical proof that love is a universal constant",
    "The first words spoken by a plant that just gained speech",
    "An architectural plan for a city built inside a giant tree",
]

def run_ollama_storm(prompts, num_trajectories, seed):
    print(f"\n--- Running Ollama Storm (Base Seed: {seed}, Model: {MODEL_NAME}) ---")
    all_texts = []
    labels = []
    
    for prompt_idx, prompt in enumerate(prompts):
        for i in range(num_trajectories):
            # We vary the seed slightly per trajectory to ensure different paths
            traj_seed = seed + i + (prompt_idx * 100)
            
            try:
                response = ollama.generate(
                    model=MODEL_NAME, 
                    prompt=prompt,
                    options={
                        "seed": traj_seed,
                        "temperature": 0.8,
                        "top_k": 50,
                        "top_p": 0.95,
                        "num_predict": 50
                    }
                )
                
                gen_text = response.get('response', '')
                
                # Strip DeepSeek <think> tags so tracking models without answers cluster correctly
                gen_text = re.sub(r'<think>.*?</think>', '', gen_text, flags=re.DOTALL).strip()
                
                if not gen_text:
                    gen_text = "<EMPTY_RESPONSE>"
                    
                all_texts.append(gen_text)
                labels.append(prompt_idx)
            except Exception as e:
                print(f"Ollama generation failed: {e}")
                
    return all_texts, np.array(labels)

def get_next_filename(base_path, prefix="qwen_invariance_", ext=".png"):
    files = glob.glob(os.path.join(base_path, f"{prefix}*{ext}"))
    max_num = 0
    for f in files:
        match = re.search(rf"{prefix}(\d+){ext}", os.path.basename(f))
        if match:
            max_num = max(max_num, int(match.group(1)))
    return os.path.join(base_path, f"{prefix}{max_num + 1}{ext}")

def map_and_plot_side_by_side(texts1, labels1, texts2, labels2, embedder):
    if len(set(texts1)) < 2 or len(set(texts2)) < 2:
        print("\n[ERROR] Invalid map. One or both runs consist entirely of identically blank or repeated responses. UMAP cannot mathematically project entirely overlapping zero-distance points without hallucinating meaningless jitter.")
        return

    unique1 = list(set(texts1))
    unique2 = list(set(texts2))
    
    print("\n--- Embedding Unique Trajectories (SentenceTransformers) ---")
    emb1_unique = embedder.encode(unique1, convert_to_numpy=True)
    emb2_unique = embedder.encode(unique2, convert_to_numpy=True)
    
    print("--- Projecting mathematically perfectly without jitter ---")
    n_neigh1 = min(15, len(unique1) - 1) if len(unique1) > 2 else 2
    n_neigh2 = min(15, len(unique2) - 1) if len(unique2) > 2 else 2
    
    reducer1 = umap.UMAP(n_neighbors=n_neigh1, min_dist=0.1, random_state=42)
    reducer2 = umap.UMAP(n_neighbors=n_neigh2, min_dist=0.1, random_state=42)
    
    proj1_unique = reducer1.fit_transform(emb1_unique)
    proj2_unique = reducer2.fit_transform(emb2_unique)
    
    # Reconstruct original size arrays with points flawlessly aligned
    proj_map1 = dict(zip(unique1, proj1_unique))
    proj_map2 = dict(zip(unique2, proj2_unique))
    
    proj1 = np.array([proj_map1[t] for t in texts1])
    proj2 = np.array([proj_map2[t] for t in texts2])

    print("--- Plotting Side-by-Side ---")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9))
    
    sc1 = ax1.scatter(proj1[:, 0], proj1[:, 1], c=labels1, cmap='tab20', alpha=0.6, s=30)
    ax1.set_title(f"Run 1 (Seed: {SEED_1})")
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_xlabel("UMAP Dimension 1")
    ax1.set_ylabel("UMAP Dimension 2")
    
    sc2 = ax2.scatter(proj2[:, 0], proj2[:, 1], c=labels2, cmap='tab20', alpha=0.6, s=30)
    ax2.set_title(f"Run 2 (Seed: {SEED_2})")
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_xlabel("UMAP Dimension 1")
    ax2.set_ylabel("UMAP Dimension 2")
    
    plt.suptitle(f"CDLSS Topography Invariance Check (Ollama Model: {MODEL_NAME})", fontsize=16)
    
    handles, _ = sc1.legend_elements()
    labels_str = [f"P{i}: {PROMPTS[i][:20]}..." for i in range(len(PROMPTS))]
    fig.legend(handles, labels_str, loc="lower center", ncol=min(7, len(PROMPTS)), fontsize='small')
    
    plt.tight_layout(rect=[0, 0.1, 1, 0.95])
    
    out_file = get_next_filename(os.path.dirname(__file__))
    plt.savefig(out_file)
    print(f"Plot saved to {out_file}.")
    plt.show()

if __name__ == "__main__":
    print("CDLSS Invariance Check: Qwen-30b (Ollama)")
    print("-" * 40)
    
    try:
        print(f"Loading Embedding Model: {EMBED_MODEL}...")
        embedder = SentenceTransformer(EMBED_MODEL)
        
        num_traj = 5 # 5 trajectories per prompt per run for a clear but reasonably fast test
        
        print(f"\nPhase 1: Running Storm with Seed {SEED_1}")
        texts1, lbls1 = run_ollama_storm(PROMPTS, num_traj, SEED_1)
        
        print(f"\nPhase 2: Running Storm with Seed {SEED_2}")
        texts2, lbls2 = run_ollama_storm(PROMPTS, num_traj, SEED_2)
        
        if len(texts1) > 0 and len(texts2) > 0:
            map_and_plot_side_by_side(texts1, lbls1, texts2, lbls2, embedder)
        else:
            print("\nError: Failed to generate trajectories.")
            
    except ImportError as ie:
        print(f"\nMissing essential package: {ie}")
    except Exception as e:
        print(f"\nError running tests: {e}")
        import traceback
        traceback.print_exc()
