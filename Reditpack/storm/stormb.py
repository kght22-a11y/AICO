#!/usr/bin/env python3
"""
stormb.py — hallucination storm with batch embedding
Sequential sampling, embeddings computed in batch
"""
import sys, json, time, uuid
from datetime import datetime
from typing import List
import numpy as np
from tqdm import tqdm

import capture_manager

try:
    import ollama; OLLAMA_AVAILABLE=True
except: OLLAMA_AVAILABLE=False
try:
    from sentence_transformers import SentenceTransformer; S_TRANS_AVAILABLE=True
except: S_TRANS_AVAILABLE=False

CONFIG_FILE="storm_config.json"
with open(CONFIG_FILE) as f: CONFIG=json.load(f)

MODEL=CONFIG.get("model","llama3:8b")
N_PATHS=int(CONFIG.get("n_paths",200))
TEMPERATURE=float(CONFIG.get("temperature",0.9))
MAX_TOKENS=int(CONFIG.get("max_tokens",128))
LAMBDA=float(CONFIG.get("temporal",{}).get("lambda",0.015))
FREEZE_THRESHOLD=float(CONFIG.get("thresholds",{}).get("freeze_threshold",0.75))
DCX_THRESHOLD=float(CONFIG.get("thresholds",{}).get("dcx_threshold",0.35))
SHADOW_LOG_FILE=CONFIG.get("logging",{}).get("shadow_log_file","storm_shadow_log.ndjson")

EMBEDDER=None
def init_embedder():
    global EMBEDDER
    if EMBEDDER is not None: return
    if OLLAMA_AVAILABLE:
        try: ollama.embed("nomic-embed-text","test"); EMBEDDER=("ollama","nomic-embed-text"); return
        except: pass
    if S_TRANS_AVAILABLE:
        try: EMBEDDER=("sentence", SentenceTransformer("all-MiniLM-L6-v2")); return
        except: pass
    EMBEDDER=("fallback",None)

def embed_texts(texts: List[str]) -> np.ndarray:
    init_embedder()
    p=EMBEDDER[0]
    if p=="ollama":
        model=EMBEDDER[1]; vecs=[]
        for t in texts:
            r=ollama.embed(model,t)
            vecs.append(np.array(r["embeddings"][0],dtype=np.float32))
        return np.vstack(vecs)
    if p=="sentence":
        model=EMBEDDER[1]; return model.encode(texts,convert_to_numpy=True,normalize_embeddings=True,batch_size=32).astype(np.float32)
    def tiny(s): import numpy as _np; rng=_np.random.default_rng(abs(hash(s))%(2**32)); return rng.normal(size=(64,)).astype(_np.float32)
    return np.vstack([tiny(t) for t in texts])

def call_ollama_generate(prompt: str) -> str:
    if OLLAMA_AVAILABLE:
        try:
            res=ollama.generate(model=MODEL,prompt=prompt,options={"temperature":TEMPERATURE,"max_tokens":MAX_TOKENS})
            if isinstance(res,dict): return res.get("response","")
            return str(res)
        except: pass
    import subprocess
    p=subprocess.Popen(["ollama","run",MODEL],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    stdout,stderr=p.communicate(prompt)
    return stdout.strip() if p.returncode==0 else f"<OLLAMA_ERROR: {stderr.strip()}>"

def generate_trajectories(prompt:str,n_paths:int):
    traj=[]
    for _ in tqdm(range(n_paths),desc="Generating trajectories"):
        traj.append(call_ollama_generate(prompt))
    return traj

def vectorized_dcx(embs: np.ndarray, lambda_val: float) -> np.ndarray:
    norms=np.linalg.norm(embs,axis=1,keepdims=True); norms[norms==0]=1.0
    embs_n=embs/norms
    sim=np.abs(embs_n@embs_n.T)
    n=embs.shape[0]; dt=np.abs(np.arange(n)[:,None]-np.arange(n)[None,:])
    decay=np.exp(-lambda_val*dt)
    return (sim*decay).astype(np.float32)

def run_storm(prompt:str):
    start_ns=int(time.time()*1e9); run_id=str(uuid.uuid4()); timestamp=datetime.utcnow().isoformat()+"Z"
    traj=generate_trajectories(prompt,N_PATHS)
    emb=embed_texts(traj)  # batch embedding
    dcx=vectorized_dcx(emb,LAMBDA)
    frozen = np.min(dcx.mean(axis=1))>=FREEZE_THRESHOLD
    if frozen:
        final_output="FROZEN_HIGH_DIVERGENCE"
    else:
        final_output=traj[int(np.argmin(dcx.mean(axis=1)))]
    capture_manager.append_result(prompt,final_output,MODEL,meta={"frozen":frozen})
    print("\n=== STORM RESULT ===\n",final_output,"\nAppended to capture file.\n")
    return final_output

if __name__=="__main__":
    if len(sys.argv)<2: print("Usage: python stormb.py \"prompt\""); exit(1)
    run_storm(sys.argv[1])
