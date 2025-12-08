#!/usr/bin/env python3
# stormfront.py — Menu-based front end for Decision Storm (capture-manager integrated)

import json
import os
import subprocess
import sys
from stormc import compress  # semantic compression (optional)
import capture_manager  # unified result capture

CONFIG_FILE = "storm_config.json"

STORM_OPTIONS = {
    "No Enhancements": "storm.py",
    "All Enhancements": "storma.py",
    "Vector Enhancement": "stormv.py",
    "Batch Enhancement": "stormb.py",
    "Parallel Enhancement": "stormp.py"
}

# QBasic style color codes
class Colors:
    RESET = '\033[0m'
    BLUE_BG = '\033[44m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    WHITE = '\033[97m'
    BLACK = '\033[30m'
    LIGHT_BLUE = '\033[94m'
    HIGHLIGHT = '\033[30;47m'

# --- Load / Save config ---
def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

# --- Screen / Menu ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_menu(title, options):
    clear_screen()
    print(f"{Colors.BLUE_BG}{Colors.YELLOW}")
    print("="*80)
    print(f"{title.center(80)}")
    print("="*80)
    print(f"{Colors.CYAN}")
    for i, option in enumerate(options, 1):
        print(f"  {i:2}. {option}")
    print(f"{Colors.YELLOW}{'='*80}")
    print(f"{Colors.WHITE}", end='')
    choice = input("Select option: ")
    print(Colors.RESET, end='')
    return choice

def edit_value(label, current, type_cast=str):
    print(f"{Colors.BLUE_BG}{Colors.CYAN}", end='')
    value = input(f"{label} [{Colors.YELLOW}{current}{Colors.CYAN}]: ")
    print(Colors.RESET, end='')
    if value.strip() == "":
        return current
    try:
        return type_cast(value)
    except Exception:
        print(f"{Colors.BLUE_BG}{Colors.YELLOW}Invalid input, keeping current value.{Colors.RESET}")
        return current

# --- Main front end ---
def main():
    config = load_config()
    config.setdefault("runtime", {})["workers"] = config.get("runtime", {}).get("workers", 1)
    config.setdefault("enhancements", True)
    config.setdefault("frontend", {})
    config.setdefault("model", "llama3:8b")
    config["frontend"].setdefault("storm_variant", "No Enhancements")
    config["frontend"].setdefault("num_trajectories", 40)

    while True:
        choice = draw_menu("DECISION STORM CONFIGURATION", [
            f"Model: {config.get('model','llama3:8b')}",
            f"Storm Variant: {config['frontend'].get('storm_variant','No Enhancements')}",
            f"Worker Threads: {config['runtime']['workers']}",
            f"Enhancements ON/OFF: {config['enhancements']}",
            f"Number of Trajectories: {config['frontend'].get('num_trajectories',40)}",
            "Edit Next Prompt",
            "Save Config",
            "Run Storm",
            "Exit"
        ])

        # --- Menu logic ---
        if choice == "1":
            config["model"] = edit_value("Model", config.get("model","llama3:8b"))
        elif choice == "2":
            print("Available Storm Variants:")
            for i, name in enumerate(STORM_OPTIONS.keys(), 1):
                print(f"  {i}. {name}")
            sel = input("Select variant: ")
            try:
                sel_idx = int(sel)-1
                variant = list(STORM_OPTIONS.keys())[sel_idx]
                config["frontend"]["storm_variant"] = variant
            except:
                print("Invalid selection.")
                input()
        elif choice == "3":
            config["runtime"]["workers"] = edit_value("Worker Threads", config["runtime"]["workers"], int)
        elif choice == "4":
            config["enhancements"] = edit_value("Enhancements ON/OFF", config["enhancements"], lambda x: x.lower() in ["true","on","1"])
        elif choice == "5":
            config["frontend"]["num_trajectories"] = edit_value("Number of Trajectories", config["frontend"].get("num_trajectories",40), int)
            if config["frontend"]["num_trajectories"] % 40 != 0 or config["frontend"]["num_trajectories"] > 200:
                print("Number of trajectories must be a multiple of 40 up to 200.")
                config["frontend"]["num_trajectories"] = 40
        elif choice == "6":
            # Edit next prompt
            new_prompt = input("Enter your next prompt: ").strip()
            if not new_prompt:
                print("Prompt cannot be empty.")
                input()
                continue

            # Load full context
            context_text = capture_manager.load_history()
            full_prompt = f"{context_text}\n{new_prompt}" if context_text else new_prompt

            # Call storm variant
            storm_script = STORM_OPTIONS.get(config["frontend"]["storm_variant"], "storm.py")
            try:
                result = subprocess.run([sys.executable, storm_script, full_prompt],
                                        capture_output=True, text=True, check=True)
                output_text = result.stdout.strip()
            except subprocess.CalledProcessError as e:
                output_text = f"<STORM_ERROR: {e}>"

            # Save prompt+response
            capture_manager.append_entry(new_prompt, output_text)
            print("\nStorm output captured. Press Enter to continue...")
            input()
        elif choice == "7":
            save_config(config)
            print("Configuration saved. Press Enter to continue...")
            input()
        elif choice == "8":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Press Enter to continue...")
            input()


if __name__ == "__main__":
    main()
