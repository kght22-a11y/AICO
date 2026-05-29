import subprocess
import threading
import queue
import time

class ThreadedEngineV2:
    """
    Iteration 2: State-Managed Threaded Class.
    Focus: Reliability and Non-blocking (from UI perspective).
    """
    def __init__(self):
        self.current_model = None
        self.is_busy = False
        self.result_queue = queue.Queue()

    def list_models(self, provider="ollama"):
        """Abstracted model listing."""
        if provider == "ollama":
            try:
                res = subprocess.run(["ollama", "list"], capture_output=True, text=True)
                return [l.split()[0] for l in res.stdout.splitlines()[1:] if l.strip()]
            except: return []
        return ["local-cli-only"]

    def generate_async(self, prompt, model):
        """Spawns a thread to run the generation."""
        if self.is_busy:
            return False
        
        def worker():
            self.is_busy = True
            try:
                print(f"[v2] Threaded worker starting: {model}")
                # Agnostic approach: templates could be injected here
                cmd = ["ollama", "run", model, prompt]
                res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
                self.result_queue.put(res.stdout.strip() if res.returncode == 0 else f"Error: {res.stderr}")
            finally:
                self.is_busy = False

        threading.Thread(target=worker, daemon=True).start()
        return True

    def check_result(self):
        """Poll the queue for results."""
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None

if __name__ == "__main__":
    eng = ThreadedEngineV2()
    models = eng.list_models()
    if models:
        print(f"Testing with {models[0]}")
        eng.generate_async("Status report.", models[0])
        while eng.is_busy:
            print("[v2] Busy...")
            time.sleep(0.5)
        print("Result:", eng.check_result())
