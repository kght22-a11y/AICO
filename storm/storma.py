#!/usr/bin/env python3
# storma.py — All Enhancements (Vectorized DCX + Safe Embedding)

import sys, json, time, math, uuid, os
from datetime import datetime, timezone
import numpy as np
from tqdm import tqdm
import subprocess

# Config
with open("storm_config.json") as f: CONFIG = json.load(f)
MODEL = CONFIG.get("model", "qwen2.5:0.5b")
N_PATHS = int(CONFIG.get("n_paths", 10))
LAMBDA = float(CONFIG.get("temporal", {}).get("lambda", 0.015))
DCX_THRESH = float(CONFIG.get("thresholds", {}).get("dcx_threshold", 0.35))

# Try imports
try: 
    from sentence_transformers import SentenceTransformer
    S_TRANS = True
except: 
    S_TRANS = False

try:
    import ollama
    OLLAMA_LIB = True
except:
    OLLAMA_LIB = False

def get_embeddings(texts):
    # Priority 1: Sentence Transformers (CPU - Safe for 1660 Ti)
    if S_TRANS:
        try:
            model = SentenceTransformer("all-MiniLM-L6-v2")
            return model.encode(texts, convert_to_numpy=True)
        except: pass
    
    # Priority 2: Ollama (Might crash if VRAM is full)
    if OLLAMA_LIB:
        try:
            vecs = []
            for t in texts:
                r = ollama.embed(model='nomic-embed-text', input=t)
                vecs.append(r['embeddings'][0])
            return np.array(vecs)
        except: pass

    # Priority 3: Fallback (Randomized Hashing - Never crashes)
    print("!! WARNING: Using Fallback Embeddings (Low Accuracy) !!")
    vecs = []
    for t in texts:
        rng = np.random.default_rng(abs(hash(t)) % (2**32))
        vecs.append(rng.normal(size=(64,)))
    return np.array(vecs)

def call_gen(prompt):
    try:
        # Force UTF-8 environment for subprocess
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        p = subprocess.Popen(["ollama", "run", MODEL], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', env=env)
        out, err = p.communicate(prompt)
        return out.strip() if p.returncode == 0 else "Error"
    except: return "Error"

def run():
    prompt = sys.argv[1]
    start = time.time()
    
    # 1. Generate Trajectories
    print(f"Storming {N_PATHS} paths via {MODEL}...")
    traj = []
    for i in tqdm(range(N_PATHS)):
        traj.append(call_gen(prompt))
        
    # 2. Embed
    print("Collapsing Wave Function (Embedding)...")
    embs = get_embeddings(traj)
    
    # 3. Vectorized DCX Calculation
    # Normalize
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    norms[norms==0] = 1.0
    embs_n = embs / norms
    
    # Similarity Matrix
    sim = np.abs(embs_n @ embs_n.T)
    
    # Temporal Decay
    n = len(traj)
    idx = np.arange(n)
    dt = np.abs(idx[:,None] - idx[None,:])
    decay = np.exp(-LAMBDA * dt)
    
    # DCX Matrix
    dcx = sim * decay
    
    # 4. Selection
    means = dcx.mean(axis=1)
    dcx_min = np.min(means)
    
    if dcx_min > DCX_THRESH:
        final = ">> SYSTEM FREEZE: Hallucination Storm Variance exceeded safety limits."
    else:
        best_idx = np.argmax(means) # Max connectivity = most central/stable thought
        final = traj[best_idx]

    print(final)

if __name__ == "__main__":
    if len(sys.argv) > 1: run()