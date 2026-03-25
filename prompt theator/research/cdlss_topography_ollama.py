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

MODEL_NAME = "qwen3-coder:30b"
EMBED_MODEL = "all-MiniLM-L6-v2"
SEED_BASE = 42

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
    print(f"\n--- Running Ollama Storm (Seed: {seed}, Model: {MODEL_NAME}) ---")
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
                all_texts.append(gen_text)
                labels.append(prompt_idx)
            except Exception as e:
                print(f"Ollama generation failed: {e}")
                
    return all_texts, np.array(labels)

def get_next_filename(base_path, prefix="ollama_topography_", ext=".png"):
    files = glob.glob(os.path.join(base_path, f"{prefix}*{ext}"))
    max_num = 0
    for f in files:
        match = re.search(rf"{prefix}(\d+){ext}", os.path.basename(f))
        if match:
            max_num = max(max_num, int(match.group(1)))
    return os.path.join(base_path, f"{prefix}{max_num + 1}{ext}")

def map_and_plot(texts, labels, embedder):
    print("\n--- Embedding Trajectories (SentenceTransformers) ---")
    embeddings = embedder.encode(texts, convert_to_numpy=True)
    
    print("--- Projecting with UMAP ---")
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42)
    proj = reducer.fit_transform(embeddings)
    
    print("--- Plotting ---")
    fig, ax = plt.subplots(figsize=(12, 8))
    
    scatter = ax.scatter(proj[:, 0], proj[:, 1], c=labels, cmap='tab20', alpha=0.6, s=25)
    ax.set_title(f"CDLSS Semantic Topography (Ollama Model: {MODEL_NAME})")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("UMAP Dimension 1")
    ax.set_ylabel("UMAP Dimension 2")
    
    handles, _ = scatter.legend_elements()
    labels_str = [f"P{i}: {PROMPTS[i][:20]}..." for i in range(len(PROMPTS))]
    fig.legend(handles, labels_str, loc="lower center", ncol=min(4, len(PROMPTS)), fontsize='small')
    plt.tight_layout(rect=[0, 0.1, 1, 0.95])
    
    out_file = get_next_filename(os.path.dirname(__file__))
    plt.savefig(out_file)
    print(f"Plot saved to {out_file}.")
    
    json_out = out_file.replace(".png", ".json")
    log_data = {p: [] for p in PROMPTS}
    for t, l_idx in zip(texts, labels):
        log_data[PROMPTS[l_idx]].append(t)
        
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=4)
    print(f"Prompt responses saved to {json_out}.")
    plt.show()

if __name__ == "__main__":
    print("CDLSS Topography: Ollama Integration")
    print("-" * 40)
    
    try:
        print(f"Loading Embedding Model: {EMBED_MODEL}...")
        embedder = SentenceTransformer(EMBED_MODEL)
        
        text_list = []
        lbl_list = []
        
        print("\n" + "="*50)
        print("Starting continuous Hallucination Storm via Ollama.")
        print("Press Ctrl+C at any time to stop and plot the results!")
        print("="*50 + "\n")
        
        batch_size = 3
        iteration = 0
        try:
            while True:
                iteration += 1
                texts, l = run_ollama_storm(PROMPTS, batch_size, SEED_BASE + iteration)
                
                text_list.extend(texts)
                lbl_list.extend(l)
                
                total = len(text_list) // len(PROMPTS)
                print(f"+++ Total trajectories per prompt so far: {total} +++")
                
        except KeyboardInterrupt:
            print("\n" + "="*50)
            print("Storm interrupted by user. Proceeding to semantic mapping...")
            print("="*50)
            
        if len(text_list) > 0:
            map_and_plot(text_list, np.array(lbl_list), embedder)
        else:
            print("\nNo trajectories generated. Exiting.")
            
    except ImportError as ie:
        print(f"\nMissing essential package: {ie}")
        print("pip install ollama sentence-transformers matplotlib umap-learn numpy")
    except Exception as e:
        print(f"\nError running tests: {e}")
        import traceback
        traceback.print_exc()
