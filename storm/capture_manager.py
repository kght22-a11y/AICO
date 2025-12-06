#!/usr/bin/env python3
# capture_manager.py — handles reading/writing the persistent prompt+answer history

import json
import os
from typing import List, Dict

CAPTURE_FILE = "captured.ndjson"

def append_entry(prompt: str, output: str):
    """
    Append a new prompt + output entry to the capture file.
    """
    import datetime
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "prompt": prompt,
        "output": output
    }
    with open(CAPTURE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def load_history() -> str:
    """
    Returns all captured prompts+outputs concatenated as text.
    Each entry is separated by a newline for readability.
    """
    if not os.path.exists(CAPTURE_FILE):
        return ""
    lines = []
    with open(CAPTURE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                prompt = entry.get("prompt","")
                output = entry.get("output","")
                lines.append(f"PROMPT: {prompt}\nRESPONSE: {output}")
            except Exception:
                continue
    return "\n".join(lines)
