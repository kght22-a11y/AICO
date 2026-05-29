import subprocess
import os

class SimpleEngineV1:
    """
    Iteration 1: Minimalist Subprocess Wrapper.
    Focus: Simplicity and Agnosticism via CLI templates.
    """
    def __init__(self):
        self.model = "qwen2.5:0.5b"
        self.engine_cmd = ["ollama", "run"]

    def set_model(self, model_name):
        self.model = model_name

    def get_models(self):
        """Agnostic model listing: tries common CLI commands."""
        print("[v1] Querying models...")
        try:
            # Try Ollama list
            res = subprocess.run(["ollama", "list"], capture_output=True, text=True, encoding="utf-8", check=True)
            models = []
            lines = res.stdout.strip().splitlines()
            if len(lines) > 1:
                for line in lines[1:]: # Skip header
                    parts = line.split()
                    if parts:
                        name = parts[0]
                        # Junk filter: must contain a colon or alphanumeric only, avoids mid-sentence junk
                        if ":" in name or name.replace("-","").replace(".","").isalnum():
                            if name not in ["NAME", "ID", "SIZE", "MODIFIED"]:
                                models.append(name)
            return sorted(list(set(models)))
        except Exception as e:
            print(f"[v1] Model scan error: {e}")
            return ["No models found / Error"]

    def generate(self, prompt):
        """Direct blocking subprocess call."""
        print(f"[v1] Generating with {self.model}...")
        cmd = self.engine_cmd + [self.model, prompt]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
            return res.stdout.strip()
        except subprocess.CalledProcessError as e:
            return f"<ERROR: {e.stderr}>"

if __name__ == "__main__":
    eng = SimpleEngineV1()
    print("Found Models:", eng.get_models())
    # Example usage:
    # print(eng.generate("Say hello!"))
