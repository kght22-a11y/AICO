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

def slugify(text):
    return re.sub(r'[^a-zA-Z0-9]', '_', text).strip('_')

def run_ollama_storm(model_name, prompts, num_trajectories, seed, log_callback=None, progress_callback=None, stop_event=None, num_thread=14):
    def log(msg):
        if log_callback: log_callback(msg)
        else: print(msg)

    total_expected = len(prompts) * num_trajectories
    log(f"--- Running Ollama Storm (Seed: {seed}, Total: {total_expected}, Threads: {num_thread}) ---")
    all_texts = []
    labels = []
    
    current_count = 0
    for prompt_idx, prompt in enumerate(prompts):
        if stop_event and stop_event.is_set():
            log("!! Run interrupted by stop event.")
            break
            
        for i in range(num_trajectories):
            if stop_event and stop_event.is_set():
                break
                
            traj_seed = seed + i + (prompt_idx * 1000)
            
            try:
                response = ollama.generate(
                    model=model_name, 
                    prompt=prompt,
                    options={
                        "seed": traj_seed,
                        "temperature": 0.8,
                        "top_k": 50,
                        "top_p": 0.95,
                        "num_predict": 50,
                        "num_thread": num_thread
                    }
                )
                
                gen_text = response.get('response', '')
                
                # Strip DeepSeek <think> tags so tracking models without answers cluster correctly
                gen_text = re.sub(r'<think>.*?</think>', '', gen_text, flags=re.DOTALL).strip()
                
                if not gen_text:
                    gen_text = "<EMPTY_RESPONSE>"
                    
                all_texts.append(gen_text)
                labels.append(prompt_idx)
                
                current_count += 1
                if progress_callback:
                    progress_callback(current_count, total_expected)
                else:
                    # Clearer progress for standalone terminal users
                    log(f" +++ Progress: {current_count}/{total_expected} Total | {(current_count-1)//num_trajectories}/{len(prompts)} Prompts +++")
            except Exception as e:
                log(f"Ollama generation failed: {e}")
                
    return all_texts, np.array(labels)

def get_next_filename(base_path, prefix="deep_map_", ext=".png"):
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    files = glob.glob(os.path.join(base_path, f"{prefix}*{ext}"))
    max_num = 0
    for f in files:
        match = re.search(rf"{prefix}(\d+){ext}", os.path.basename(f))
        if match:
            max_num = max(max_num, int(match.group(1)))
    return os.path.join(base_path, f"{prefix}{max_num + 1}{ext}")

def map_and_plot(model_name, texts, labels, embedder, save_dir, show_plot=True):
    unique_texts = list(set(texts))
    if len(unique_texts) < 2:
        print(f"\n[ERROR] Invalid map. All generated trajectories for {model_name} are identical or entirely blank. UMAP cannot mathematically project entirely overlapping zero-distance points without hallucinating meaningless jitter.")
        return None

    print("\n--- Embedding Unique Trajectories ---")
    unique_embeddings = embedder.encode(unique_texts, convert_to_numpy=True)
    
    print("--- Projecting mathematically perfectly without jitter ---")
    n_neigh = min(15, len(unique_texts) - 1) if len(unique_texts) > 2 else 2
    reducer = umap.UMAP(n_neighbors=n_neigh, min_dist=0.1, random_state=42)
    unique_proj = reducer.fit_transform(unique_embeddings)
    
    # Reconstruct original size with identical points perfectly overlapped
    proj_map = dict(zip(unique_texts, unique_proj))
    proj = np.array([proj_map[t] for t in texts])

    
    print("--- Plotting ---")
    fig, ax = plt.subplots(figsize=(15, 10))
    
    s_val = 15 if len(texts) < 1000 else 8
    alpha_val = 0.6 if len(texts) < 1000 else 0.4
    
    scatter = ax.scatter(proj[:, 0], proj[:, 1], c=labels, cmap='tab20', alpha=alpha_val, s=s_val)
    ax.set_title(f"CDLSS Deep Topography (Model: {model_name}, Trajectories: {len(texts)})")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("UMAP Dimension 1")
    ax.set_ylabel("UMAP Dimension 2")
    
    handles, _ = scatter.legend_elements()
    labels_str = [f"P{i}: {PROMPTS[i][:20]}..." for i in range(len(PROMPTS))]
    fig.legend(handles, labels_str, loc="lower center", ncol=min(7, len(PROMPTS)), fontsize='x-small')
    plt.tight_layout(rect=[0, 0.1, 1, 0.95])
    
    prefix = f"deep_map_{slugify(model_name)}_"
    out_file = get_next_filename(save_dir, prefix=prefix)
    plt.savefig(out_file, dpi=150)
    print(f"Plot saved to {out_file}.")
    
    if show_plot:
        plt.show()
    else:
        plt.close(fig)
        
    return out_file

def run_deep_map(model_name, num_trajectories, log_callback=None, progress_callback=None, stop_event=None, num_thread=14):
    def log(msg):
        if log_callback: log_callback(msg)
        else: print(msg)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    maps_dir = os.path.join(base_dir, "maps")
    if not os.path.exists(maps_dir):
        os.makedirs(maps_dir)

    dataset_path = os.path.join(maps_dir, f"deep_map_{slugify(model_name)}.json")
    
    # Load cumulative dataset
    cumulative_texts = []
    cumulative_labels = []
    if os.path.exists(dataset_path):
        log(f"Loading existing trajectories from {os.path.basename(dataset_path)}...")
        with open(dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Flatten stored data: { "P0": ["T1", "T2"], "P1": ["T1"] } -> texts, labels
            for p_idx, prompt in enumerate(PROMPTS):
                responses = data.get("responses", {}).get(prompt, [])
                cumulative_texts.extend(responses)
                cumulative_labels.extend([p_idx] * len(responses))
        log(f"Found {len(cumulative_texts)} existing trajectories.")

    # Generate new trajectories
    # Determine start iteration based on current count to keep seeds unique
    start_iter = (len(cumulative_texts) // len(PROMPTS)) + 1
    new_texts, new_labels = run_ollama_storm(
        model_name, PROMPTS, num_trajectories, 
        SEED_BASE + start_iter * 100, log, 
        progress_callback, stop_event, num_thread=num_thread
    )
    
    cumulative_texts.extend(new_texts)
    cumulative_labels.extend(new_labels)
    
    if len(cumulative_texts) == 0:
        log("No data to plot.")
        return None

    # Save cumulative dataset
    save_data = {
        "model": model_name,
        "total_trajectories": len(cumulative_texts),
        "responses": {p: [] for p in PROMPTS}
    }
    # Group by prompt
    for t, l_idx in zip(cumulative_texts, cumulative_labels):
        save_data["responses"][PROMPTS[l_idx]].append(t)
        
    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, indent=4)
    log(f"Cumulative dataset updated: {dataset_path}")

    # Plot
    log("Loading embedding model and generating topography...")
    embedder = SentenceTransformer(EMBED_MODEL)
    img_path = map_and_plot(model_name, cumulative_texts, np.array(cumulative_labels), embedder, maps_dir, show_plot=False)
    
    return img_path

if __name__ == "__main__":
    import threading
    
    # Standalone execution settings
    MODEL = "qwen3-coder:30b"
    N_PER_PROMPT = 10  # How many to add in this run
    
    print(f"--- Standalone Deep Map Storm: {MODEL} ---")
    
    stop_ev = threading.Event()
    try:
        img = run_deep_map(MODEL, N_PER_PROMPT, stop_event=stop_ev)
        if img and os.path.exists(img):
            print(f"\nSuccess! Opening map: {img}")
            os.startfile(img)
    except KeyboardInterrupt:
        print("\nInterrupt received. Closing current batch and plotting...")
        stop_ev.set()
        # The run_deep_map call should finish its current step and return the path
