import json
import urllib.request
import urllib.error

class SimpleEngineV1:
    """
    Iteration 2: REST API Wrapper.
    Focus: Near-zero overhead and model persistence via direct API calls.
    """
    def __init__(self, base_url="http://localhost:11434"):
        self.model = "qwen2.5:0.5b"
        self.base_url = base_url

    def set_model(self, model_name):
        self.model = model_name

    def get_models(self):
        """Query Ollama API for available models."""
        print("[v2] Querying API for models...")
        try:
            url = f"{self.base_url}/api/tags"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                models = [m['name'] for m in data.get('models', [])]
                return sorted(models)
        except Exception as e:
            print(f"[v2] API Model scan error: {e}")
            return ["No models found / Server down"]

    def get_embedding(self, text, embed_model="nomic-embed-text"):
        """Direct API call to /api/embeddings for true semantic vectors."""
        payload = {
            "model": embed_model,
            "prompt": text,
            "keep_alive": "5m"
        }
        try:
            url = f"{self.base_url}/api/embeddings"
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), 
                                         headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode())
                return res_data.get("embedding", None)
        except Exception:
            return None

    def generate(self, prompt, **kwargs):
        """Direct API call to /api/generate."""
        import re
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,  # Changed to True for live feedback
            "keep_alive": "5m"
        }
        
        if kwargs:
            payload["options"] = kwargs
        
        import sys
        print(f"[v2] API Generating with {self.model} (Opts: {kwargs})...")
        try:
            url = f"{self.base_url}/api/generate"
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), 
                                         headers={'Content-Type': 'application/json'})
            
            full_response = []
            with urllib.request.urlopen(req) as response:
                for line in response:
                    if line:
                        chunk = json.loads(line.decode('utf-8'))
                        text_chunk = chunk.get("response", "")
                        full_response.append(text_chunk)
                        # Echo to the console so the user sees live progress
                        print(text_chunk, end="", flush=True)
            print() # Clear the line after the generation finishes
            
            text = "".join(full_response).strip()
            # Strip DeepSeek <think> tags to avoid blowing out context/DCX
            text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
            return text
        except urllib.error.URLError as e:
            return f"<API ERROR: {e.reason}>"
        except Exception as e:
            return f"<ERROR: {e}>"

if __name__ == "__main__":
    eng = SimpleEngineV1()
    print("Found Models:", eng.get_models())
    # Example usage:
    # print(eng.generate("Say hello!"))
