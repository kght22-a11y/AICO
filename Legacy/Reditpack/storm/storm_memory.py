#!/usr/bin/env python3
# storm_memory.py — Rolling Context Compressor

import json
import os
import sys
import subprocess
import time

# --- CONFIG ---
MEMORY_FILE = "aico_memory.json"
MAX_ACTIVE_CHARS = 4000  # Trigger compression if history > this
# Use a tiny model for compression to save GPU/Time
COMPRESSION_MODEL = "qwen2.5:0.5b" 

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"summary": "", "recent_history": []}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(mem_data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem_data, f, indent=2)

def call_compressor(text_chunk):
    """Asks the tiny model to compress text into dense facts."""
    prompt = (
        f"SYSTEM: Compress the following log into a concise, dense summary. "
        f"Keep facts, discard fluff. Output ONLY the summary.\n\n"
        f"LOG:\n{text_chunk}"
    )
    try:
        # Windows encoding fix
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        # Use 'ollama run' via subprocess to avoid library issues
        result = subprocess.run(
            ["ollama", "run", COMPRESSION_MODEL, prompt],
            capture_output=True, text=True, encoding="utf-8", env=env
        )
        return result.stdout.strip()
    except Exception as e:
        return f"[Compression Failed: {e}]"

def update_context(new_prompt, new_output):
    """Adds interaction, checks size, compresses if needed."""
    mem = load_memory()
    
    # 1. Append new interaction
    entry = f"USER: {new_prompt}\nAICO: {new_output}"
    mem["recent_history"].append(entry)
    
    # 2. Check Size
    full_text = "\n".join(mem["recent_history"])
    
    if len(full_text) > MAX_ACTIVE_CHARS:
        print(f"\n[MEMORY] Context buffer full ({len(full_text)} chars). Compressing...")
        
        # Keep last 2, compress rest
        keep_count = 2
        to_compress_list = mem["recent_history"][:-keep_count]
        to_keep_list = mem["recent_history"][-keep_count:]
        
        text_to_compress = "\n".join(to_compress_list)
        
        # 3. Compress
        new_summary_chunk = call_compressor(text_to_compress)
        
        # 4. Merge into Summary
        timestamp = int(time.time())
        block_header = f"\n[MEM_BLOCK_{timestamp}] "
        mem["summary"] += block_header + new_summary_chunk
        
        # 5. Prune
        mem["recent_history"] = to_keep_list
        print(f"[MEMORY] Compression Complete.")
        
    save_memory(mem)

def get_full_context():
    """Returns the string to feed into the Storm."""
    mem = load_memory()
    context = ""
    
    if mem["summary"]:
        context += f"--- SYSTEM MEMORY STREAM ---\n{mem['summary']}\n----------------------------\n"
        
    if mem["recent_history"]:
        context += "\n".join(mem['recent_history'])
        
    return context
    def clear_memory():
        """Wipes the hippocampus."""
        blank = {"summary": "", "recent_history": []}
        save_memory(blank)
        print("[MEMORY] History cleared.")