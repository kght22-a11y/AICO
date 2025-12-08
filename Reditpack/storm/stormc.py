# stormc.py — Semantic Compression Module + Frontend Helpers
# ----------------------------------------------------------
# Provides semantic compression and convenient functions for stormfront.py

import re
import json
import os
from typing import Dict, Any, Tuple

CONFIG_FILE = "storm_config.json"

# -----------------------------
# Load config if available
# -----------------------------
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
else:
    CONFIG = {
        "frontend": {
            "context_window_max": 4096,
            "continuous_context_file": "continuous.ndjson"
        }
    }

# -----------------------------
# Semantic Compressor Class
# -----------------------------

class StormSemanticCompressor:
    """
    Semantic context compressor:
      - normalizes phrasing
      - deduplicates repeated ideas
      - extracts structured meaning
      - preserves causal relationships
      - generates persistent summary-state
    """

    def __init__(self):
        self.summary_state = {
            "facts": [],
            "goals": [],
            "constraints": [],
            "notes": [],
            "history": []
        }

    # ---------------------
    #  Public API
    # ---------------------
    def compress(self, text: str, aggressive: bool = False) -> Tuple[str, Dict]:
        normalized = self._normalize(text)
        extracted = self._extract_semantics(normalized)
        deduped = self._dedupe(extracted)
        self._merge_state(deduped)
        compressed = self._render_summary(aggressive)
        return compressed, self.summary_state

    # ---------------------
    #  Core Steps
    # ---------------------
    def _normalize(self, text: str) -> str:
        t = text.strip()
        t = re.sub(r"[!?]{2,}", "!", t)
        t = re.sub(r"\.{2,}", ".", t)
        t = re.sub(r"\s+", " ", t)
        t = re.sub(r"\b(\w+)\s+\1\b", r"\1", t, flags=re.I)
        return t

    def _extract_semantics(self, text: str) -> Dict[str, Any]:
        info = {"facts": [], "goals": [], "constraints": [], "notes": [], "history": []}
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for s in sentences:
            ls = s.lower()
            if not s:
                continue
            if any(k in ls for k in ["is", "are", "will be", "means"]):
                info["facts"].append(s)
            elif any(k in ls for k in ["goal", "aim", "intend", "want to"]):
                info["goals"].append(s)
            elif any(k in ls for k in ["must", "cannot", "should not", "required"]):
                info["constraints"].append(s)
            elif any(k in ls for k in ["because", "therefore", "so that"]):
                info["history"].append(s)
            else:
                info["notes"].append(s)
        return info

    def _dedupe(self, info: Dict[str, Any]) -> Dict[str, Any]:
        return {key: list(dict.fromkeys(values)) for key, values in info.items()}

    def _merge_state(self, new_info: Dict[str, Any]):
        for key, values in new_info.items():
            existing = self.summary_state[key]
            for v in values:
                if v not in existing:
                    existing.append(v)

    def _render_summary(self, aggressive: bool = False) -> str:
        parts = []

        def add(label, items):
            if not items:
                return
            if aggressive:
                parts.append(f"{label}:{' | '.join(items)}")
            else:
                parts.append(f"{label}:\n  - " + "\n  - ".join(items))

        add("facts", self.summary_state["facts"])
        add("goals", self.summary_state["goals"])
        add("constraints", self.summary_state["constraints"])
        add("notes", self.summary_state["notes"])
        add("history", self.summary_state["history"])
        return "\n".join(parts)

# -----------------------------
# Singleton instance + functional interface
# -----------------------------
_instance = StormSemanticCompressor()

def compress(text: str, aggressive: bool = False):
    """Shortcut: compress(text) -> (compressed_text, state)"""
    return _instance.compress(text, aggressive)

# -----------------------------
# Frontend helper functions
# -----------------------------

def compress_context(context_file=None, aggressive=False) -> str:
    """
    Reads the context file, compresses semantically, returns the compressed text.
    """
    if context_file is None:
        context_file = CONFIG["frontend"].get("continuous_context_file", "continuous.ndjson")
    if not os.path.exists(context_file):
        return ""

    with open(context_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    text = " ".join(lines)
    compressed, _state = compress(text, aggressive=aggressive)
    max_len = CONFIG["frontend"].get("context_window_max", 4096)
    return compressed[-max_len:]  # trim to max context size

def run_context_storm(prompt=None) -> str:
    """
    Uses compressed context + optional prompt, returns final string
    ready for the backend.
    """
    context_file = CONFIG["frontend"].get("continuous_context_file", "continuous.ndjson")
    context_compressed = compress_context(context_file)

    if prompt:
        context_compressed += "\n" + prompt

    # Normally you would call run_storm(context_compressed) here
    return context_compressed
