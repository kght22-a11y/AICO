# storm_backend.py — Execution logic for Stormfront
import json
import os
import sys
import subprocess
import capture_manager
import storm_memory  # Required for Context & Amnesia

CONFIG_FILE = "storm_config.json"

STORM_OPTIONS = {
    "No Enhancements": "storm.py",
    "All Enhancements": "storma.py",
    "Vector Enhancement": "stormv.py",
    "Batch Enhancement": "stormb.py",
    "Parallel Enhancement": "stormp.py"
}

def load_config():
    if not os.path.exists(CONFIG_FILE): return {}
    # Use utf-8-sig to handle Windows Notepad BOMs automatically
    with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def clear_context():
    """Wipes the rolling memory via the memory module."""
    storm_memory.clear_memory()

def run_storm_process(config, new_prompt):
    # 1. Load Context via Memory Module (The Hippocampus)
    context_text = storm_memory.get_full_context()
    
    # 2. Construct the full prompt (Context + New Input)
    full_prompt = f"{context_text}\nUSER: {new_prompt}" if context_text else new_prompt

    # 3. Identify Script
    variant_name = config["frontend"].get("storm_variant", "No Enhancements")
    script_name = STORM_OPTIONS.get(variant_name, "storm.py")

    # 4. Execute
    print(f"\n>> Launching {script_name}...")
    try:
        # Run the python script in a subprocess
        result = subprocess.run(
            [sys.executable, script_name, full_prompt],
            capture_output=True, text=True, check=True, encoding="utf-8"
        )
        output_text = result.stdout.strip()
        return output_text, None
    except subprocess.CalledProcessError as e:
        return None, f"<STORM_ERROR: {e}>\nStderr: {e.stderr}"

def commit_result(prompt, output):
    """
    Decides whether to remember the interaction or forget it.
    """
    # --- SELECTIVE AMNESIA ---
    # If the system froze, DO NOT commit this to the Rolling Memory.
    if "SYSTEM FREEZE" in output or "FROZEN_HIGH_DIVERGENCE" in output:
        print(f"\n[NEURAL FLUSH] Hallucination detected. Wiping short-term memory of this event.")
        # We purposely do NOT call update_context here.
        # The AI will wake up next time as if this conversation never happened.
    else:
        # Only commit successful, coherent thoughts to the rolling context
        storm_memory.update_context(prompt, output) 
    
    # Always keep raw logs for the Black Box Recorder (Audit)
    capture_manager.append_entry(prompt, output)