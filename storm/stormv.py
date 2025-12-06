#!/usr/bin/env python3
# storm_vectorized_dcx.py — Vectorized DCX only (sequential sampling + non-batched embedding)

import sys, json, time, math, os, uuid
from datetime import datetime
from typing import List
import numpy as np
from tqdm import tqdm

try:
    import ollama; OLLAMA_AVAILABLE=True
except: OLLAMA_AVAILABLE=False
try:
    from sentence_transformers import SentenceTransformer; S_TRANS_AVAILABLE=True
except: S_TRANS_AVAILABLE=False

CONFIG_FILE="storm_config.json"
if not os.path.exists(CONFIG_FILE): raise SystemExit("Missing config")
with open(CONFIG_FILE) as f: CONFIG=json.load(f)
MODEL=CONFIG.get("model","llama3:8b"); N_PATHS=int(CONFIG.get("n_paths",200))
TEMPERATURE=float(CONFIG.get("temperature",0.9)); MAX_TOKENS=int(CONFIG.get("max_tokens",128))
LAMBDA=float(CONFIG.get("temporal",{}).get("lambda",0.015)); DCX_THRESHOLD=float(CONFIG.get("thresholds",{}).get("dcx_threshold",0.35))
FREEZE_THRESHOLD=float(CONFIG.get("thresholds",{}).get("freeze_threshold",0.75))
SHADOW_LOG_FILE=CONFIG.get("logging",{}).get("shadow_log_file","storm_shadow_log.ndjson")
RESULT_DIR=CONFIG.get("logging",{}).get("result_dir",".")

EMBEDDER=None
def init_embedder():
    global EMBEDDER
    if EMBEDDER is not None: return
    if S_TRANS_AVAILABLE:
        EMBEDDER=("sentence", SentenceTransformer("all-MiniLM-L6-v2")); print("[embed] MiniLM"); return
    EMBEDDER=("fallback",None); print("[embed] fallback")
def embed_texts_seq(texts):
    init_embedder()
    if EMBEDDER[0]=="sentence":
        model=EMBEDDER[1]; arr=model.encode(texts,convert_to_numpy=True,normalize_embeddings=True,batch_size=32); return arr.astype(np.float32)
    def tiny(s): import numpy as _np; rng=_np.random.default_rng(abs(hash(s))%(2**32)); return rng.normal(size=(64,)).astype(_np.float32)
    return np.vstack([tiny(t) for t in texts])

def call_ollama_generate(prompt):
    if OLLAMA_AVAILABLE:
        try:
            res=ollama.generate(model=MODEL,prompt=prompt,options={"temperature":float(TEMPERATURE),"max_tokens":int(MAX_TOKENS)})
            if isinstance(res,dict): return res.get("response","")
            return str(res)
        except: pass
    import subprocess
    p = subprocess.Popen(["ollama","run",MODEL], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = p.communicate(prompt)
    if p.returncode==0: return stdout.strip()
    return f"<OLLAMA_ERROR_CLI: {stderr.strip()}>"

def vectorized_dcx(embs, lambda_val):
    norms=np.linalg.norm(embs,axis=1,keepdims=True); norms[norms==0]=1.0
    embs_n=embs/norms
    sim = np.abs(embs_n @ embs_n.T)
    n=embs.shape[0]; idx=np.arange(n); dt=np.abs(idx[:,None]-idx[None,:])
    decay = np.exp(-lambda_val*dt)
    return (sim * decay).astype(np.float32)

def run_storm(prompt):
    start=time.time(); run_id=str(uuid.uuid4()); timestamp=datetime.utcnow().isoformat()+"Z"
    traj=[]
    print(f"Generating {N_PATHS} trajectories (sequential)...")
    for _ in tqdm(range(N_PATHS)): traj.append(call_ollama_generate(prompt))
    emb = embed_texts_seq(traj)
    dcx = vectorized_dcx(emb,LAMBDA)
    mean = dcx.mean(axis=1); dcx_min=float(np.min(mean)); frozen = dcx_min>=FREEZE_THRESHOLD
    if frozen:
        final="FROZEN_HIGH_DIVERGENCE"; sel=None; conf=0.0
    else:
        sel=int(np.argmin(mean)); final=traj[sel]; conf=float(1.0-mean[sel])
    meta={"run_id":run_id,"timestamp":timestamp,"model":MODEL,"n_requested":N_PATHS,"n_generated":len(traj),"n_pruned":0,"dcx_min":dcx_min,"frozen":bool(frozen),"selected_index":sel,"collapse_time_ns":int((time.time()-start)*1e9),"confidence_score":conf}
    with open(SHADOW_LOG_FILE,"a",encoding="utf-8") as fh: fh.write(json.dumps({"run_id":run_id,"timestamp":timestamp,"prompt":prompt,"meta":meta})+"\n")
    rf=os.path.join(RESULT_DIR,f"storm_result_{run_id}.json")
    with open(rf,"w",encoding="utf-8") as fh: json.dump({"meta":meta,"final_output":final},fh,indent=2)
    print("final_output:"); print(final); print(json.dumps(meta,indent=2))
    return meta, final
#!/usr/bin/env python3
"""
stormv.py — hallucination storm with vectorized DCX
Sequential sampling, vectorized DCX computation.
"""
import sys, json, time, math, uuid
from datetime import datetime
from typing import List
import numpy as np
from tqdm import tqdm
import subprocess

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
        model=EMBEDDER[1]; return model.encode(texts,convert_to_numpy=True,normalize_embeddings=True).astype(np.float32)
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
    norms = np.linalg.norm(embs,axis=1,keepdims=True); norms[norms==0]=1.0
    embs_n = embs / norms
    sim = np.abs(embs_n @ embs_n.T)
    n = embs.shape[0]; dt = np.abs(np.arange(n)[:,None] - np.arange(n)[None,:])
    decay = np.exp(-lambda_val*dt)
    return (sim*decay).astype(np.float32)

def run_storm(prompt:str):
    start_ns=int(time.time()*1e9); run_id=str(uuid.uuid4()); timestamp=datetime.utcnow().isoformat()+"Z"
    traj=generate_trajectories(prompt,N_PATHS)
    emb=embed_texts(traj)
    dcx=vectorized_dcx(emb,LAMBDA)
    frozen = np.min(dcx.mean(axis=1))>=FREEZE_THRESHOLD
    if frozen:
        final_output="FROZEN_HIGH_DIVERGENCE"
    else:
        final_output=traj[int(np.argmin(dcx.mean(axis=1)))]
    # shadow log
    with open(SHADOW_LOG_FILE,"a",encoding="utf-8") as fh:
        fh.write(json.dumps({"run_id":run_id,"timestamp":timestamp,"prompt":prompt,"meta":{"frozen":frozen},"trajectories_sample":traj[:10]})+"\n")
    # append to centralized capture
    capture_manager.append_result(prompt,final_output,MODEL,meta={"frozen":frozen})
    print("\n=== STORM RESULT ===\n",final_output,"\nAppended to capture file.\n")
    return final_output

if __name__=="__main__":
    if len(sys.argv)<2: print("Usage: python stormv.py \"prompt\""); exit(1)
    run_storm(sys.argv[1])

if __name__=="__main__":
    if len(sys.argv)<2: print("Usage: python storm_vectorized_dcx.py \"prompt\""); sys.exit(1)
    run_storm(sys.argv[1])
