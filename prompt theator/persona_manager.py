import json
import os

class PersonaManager:
    """
    Manages characters and personas for the Prompt Studio.
    Supports inheritance from a baseline.
    """
    def __init__(self, characters_dir="characters"):
        self.characters_dir = characters_dir
        self.personas = {}
        self.load_personas()

    def load_personas(self):
        """Scans the characters directory and loads all JSON personas."""
        if not os.path.exists(self.characters_dir):
            os.makedirs(self.characters_dir)
            
        self.personas = {}
        
        # Ensure baseline is loaded first if it exists
        baseline_path = os.path.join(self.characters_dir, "baseline.json")
        baseline_data = {}
        if os.path.exists(baseline_path):
            with open(baseline_path, "r") as f:
                baseline_data = json.load(f)
                self.personas["Baseline"] = baseline_data

        for filename in os.listdir(self.characters_dir):
            if filename.endswith(".json") and filename != "baseline.json":
                path = os.path.join(self.characters_dir, filename)
                with open(path, "r") as f:
                    data = json.load(f)
                    name = data.get("name", filename[:-5])
                    
                    # Inheritance Logic
                    if data.get("inherits") == "baseline":
                        merged = baseline_data.copy()
                        merged.update(data)
                        # Merge arrays like traits
                        if "traits" in data and "traits" in baseline_data:
                            merged["traits"] = list(set(baseline_data["traits"] + data["traits"]))
                        self.personas[name] = merged
                    else:
                        self.personas[name] = data

    def get_persona_names(self):
        return sorted(list(self.personas.keys()))

    def wrap_prompt(self, persona_name, user_intent, context=""):
        """
        Wraps the user intent and context with the selected persona's constraints.
        """
        persona = self.personas.get(persona_name)
        if not persona:
            return f"CONTEXT:\n{context}\n\nUSER: {user_intent}"

        system_msg = persona.get("system_background", "")
        signature = persona.get("signature", "")
        
        wrapped = (
            f"SYSTEM PERSONA: {persona_name}\n"
            f"BACKGROUND: {system_msg}\n"
            f"{'---' if context else ''}\n"
            f"{context}\n"
            f"{'---' if context else ''}\n"
            f"USER INTENT: {user_intent}\n\n"
            f"RESPONSE {signature}:"
        )
        return wrapped

if __name__ == "__main__":
    # Test
    pm = PersonaManager(characters_dir="d:/whitepaper/prompt theator/characters")
    print(f"Loaded: {pm.get_persona_names()}")
    print("\n--- Wrapped Prompt (Baseline) ---")
    print(pm.wrap_prompt("Baseline", "What is the meaning of life?"))
