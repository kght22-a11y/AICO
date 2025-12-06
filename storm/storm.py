#!/usr/bin/env python3
# storm.py — Baseline Logic
import sys, json, time, uuid, math
from datetime import datetime, timezone
import numpy as np
import subprocess

# Config
try:
    with open("storm_config.json") as f: CONFIG = json.load(f)
except: CONFIG = {}

MODEL = CONFIG.get("model", "qwen2.5:0.5b")
N_PATHS = int(CONFIG.get("n_paths", 10))
# Default fallback to 1 if not in config to save your GPU
WORKERS = int(CONFIG.get("runtime", {}).get("workers", 1))

def call_ollama(prompt):
    # Direct CLI call is safer for stability
    try:
        p = subprocess.Popen(["ollama", "run", MODEL], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        out, err = p.communicate(prompt)
        return out.strip() if p.returncode == 0 else f"[Error: {err.strip()}]"
    except Exception as e:
        return f"[Exception: {e}]"

def tiny_embed(texts):
    # Fallback embedding if Ollama fails (Random projection)
    vecs = []
    for t in texts:
        rng = np.random.default_rng(abs(hash(t)) % (2**32))
        vecs.append(rng.normal(size=(64,)).astype(np.float32))
    return np.vstack(vecs)

def run_storm(prompt):
    start = time.time()
    print(f"Generating {N_PATHS} trajectories...")
    
    # 1. Generate
    traj = []
    for i in range(N_PATHS):
        print(f"Path {i+1}/{N_PATHS}...")
        traj.append(call_ollama(prompt))

    # 2. Embed (Using fallback for speed/safety on base model)
    embs = tiny_embed(traj)
    
    # 3. DCX Logic
    # Calculate divergence from mean
    centroid = np.mean(embs, axis=0)
    sims = np.dot(embs, centroid)
    # Simple selection: closest to centroid
    best_idx = int(np.argmax(sims))
    
    final = traj[best_idx]
    
    # Metadata
    meta = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "selected_index": best_idx,
        "duration": time.time() - start
    }
    
    # Output for the Backend to capture
    print(json.dumps(meta))
    print("---FINAL_OUTPUT---")
    print(final)

if __name__ == "__main__":
    if len(sys.argv) > 1: run_storm(sys.argv[1])