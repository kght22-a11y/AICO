import os
from research.ggml_bridge import GGMLBridge

class GGMLEngineV1:
    """
    Engine mimicking SimpleEngineV1 but routes to the C-level GGML CDLSS implementation.
    """
    def __init__(self):
        self.bridge = GGMLBridge()
        self.current_model = "gpt-2-117M/ggml-model.bin"  # Default generic model path
        self.models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ggml-master", "models"))
        
    def set_model(self, model_name):
        self.current_model = model_name

    def get_models(self):
        """Scan the models directory for .bin or .gguf files."""
        models = []
        if os.path.exists(self.models_dir):
            for root, _, files in os.walk(self.models_dir):
                for f in files:
                    if f.endswith(".bin") or f.endswith(".gguf"):
                        rel_path = os.path.relpath(os.path.join(root, f), self.models_dir)
                        models.append(rel_path.replace("\\", "/"))
        
        if not models:
            models = ["gpt-2-117M/ggml-model.bin (Mock)", "llama-2-7b.gguf (Mock)"]
        return models

    def get_embedding(self, text, embed_model="nomic-embed-text"):
        # For simplicity, returning None forces the UI to use hash-based embeddings.
        # Alternatively, we could hook into a ggml embedding model here.
        return None

    def generate(self, prompt, temperature=0.7, num_predict=256, num_thread=4, cdlss_trajectories=10, cdlss_dcx=0.85):
        """
        In the real system, parameters like trajectories and dcx should be passed dynamically.
        For now, we pass them down via the bridge.
        """
        model_path = os.path.join(self.models_dir, self.current_model)
        
        # If it's a mock, just pass the name
        if "Mock" in self.current_model:
            model_path = "mock_path"

        # Note: cdlss_trajectories and dcx could be added to kwargs or class state 
        # based on how UI passes them. For now we use the bridge defaults or kwargs if provided.
        res = self.bridge.run_inference(
            model_path=model_path,
            prompt=prompt,
            num_trajectories=cdlss_trajectories,
            dcx_threshold=cdlss_dcx,
            temp=temperature,
            n_predict=num_predict
        )
        return res
