import numpy as np
import json
import time
import hashlib

class StormLogic:
    """
    Phase 2: Refined Storm Logic.
    Handles DCX scoring, multi-model ground truth, and semantic synthesis.
    """
    def __init__(self, lambda_val=0.015):
        self.lambda_val = lambda_val

    def get_simple_embedding(self, text):
        """
        Fallback embedding: deterministic hashing vectorization.
        Ensures ground-truth differences between models.
        """
        # Create a 64-dim vector based on text hash
        h = hashlib.sha256(text.encode()).digest()
        vec = np.frombuffer(h * 2, dtype=np.int8).astype(np.float32)
        return vec / (np.linalg.norm(vec) + 1e-9)

    def calculate_dcx_matrix(self, trajectories, model_names):
        """
        Vectorized DCX calculation with Multi-Model Ground Truth.
        Perfect correlation is impossible due to model-specific biases.
        """
        n = len(trajectories)
        if n == 0: return np.array([])

        # Generate model-biased embeddings
        embeddings = []
        for i, (text, model) in enumerate(zip(trajectories, model_names)):
            # Bias the hash with the model name to ensure inter-model divergence
            biased_text = f"{model}:{text}"
            embeddings.append(self.get_simple_embedding(biased_text))
        
        embs = np.vstack(embeddings)
        
        # Similarity Matrix (Cosine)
        sim = np.abs(embs @ embs.T)
        
        # Temporal Decay
        idx = np.arange(n)
        dt = np.abs(idx[:, None] - idx[None, :])
        decay = np.exp(-self.lambda_val * dt)
        
        # DCX = Sim * Decay
        dcx_matrix = sim * decay
        
        # Zero out self-correlation to 1.0 is handled naturally by math,
        # but the multi-model bias makes inter-model 1.0 nearly impossible.
        return dcx_matrix

    def analyze_storm(self, trajectories, model_names, low_thresh=0.2, high_thresh=0.85):
        """
        Analyzes the storm and finds the best candidates or triggers a freeze.
        """
        if not trajectories:
            return {"status": "VOID", "best_index": -1, "scores": []}

        dcx = self.calculate_dcx_matrix(trajectories, model_names)
        # Connectivity score = mean correlation with others
        scores = dcx.mean(axis=1)
        
        min_dcx = np.min(scores)
        max_dcx = np.max(scores)
        
        # If the most coherent thought is still above high_thresh, it's too diverged
        # (Meaning even the "best" doesn't correlate well with the cluster)
        if min_dcx > high_thresh:
            return {"status": "FROZEN_HIGH_DIVERGENCE", "best_index": -1, "scores": scores}
            
        # Top 3 indices
        top_3_idx = np.argsort(scores)[:3]
        
        return {
            "status": "COLLAPSED",
            "best_index": np.argmin(scores),
            "top_3_indices": top_3_idx.tolist(),
            "min_dcx": float(min_dcx),
            "max_dcx": float(max_dcx),
            "scores": scores.tolist()
        }

    def semantic_synthesis(self, mascot_engine, top_3_texts, original_prompt):
        """
        Uses the Mascot model to converge the top 3 results.
        """
        synthesis_prompt = (
            f"SYSTEM: You are the MASCOT Collapse Operator. Below are 3 divergent trajectories "
            f"from a quantum hallucination storm. Synthesize them into a single, high-fidelity "
            f"grounded response that captures the core consensus while discarding contradictions.\n\n"
            f"ORIGINAL INTENT: {original_prompt}\n\n"
            f"TRAJECTORY 1: {top_3_texts[0]}\n"
            f"TRAJECTORY 2: {top_3_texts[1]}\n"
            f"TRAJECTORY 3: {top_3_texts[2]}\n\n"
            f"FINAL SYNTHESIS:"
        )
        return mascot_engine.generate(synthesis_prompt)

    def generate_refined_prompt(self, mascot_engine, trajectories, original_prompt):
        """
        Phase 3: Deep Reasoning. Summarizes initial thoughts into a better prompt.
        """
        refinement_prompt = (
            f"SYSTEM: You are the STORM REFINER. Analyze these initial divergent thoughts "
            f"on a user request and extract a refined, more precise version of the user's "
            f"true intent for a second deeper pass.\n\n"
            f"USER ORIGINAL INTENT: {original_prompt}\n\n"
            f"INITIAL THOUGHTS:\n" + "\n".join([f"- {t[:200]}..." for t in trajectories[:5]]) +
            f"\n\nREFINED PROMPT FOR FINAL STORM:"
        )
        return mascot_engine.generate(refinement_prompt)

if __name__ == "__main__":
    # Quick Test
    logic = StormLogic()
    trajs = ["The cat is blue", "The cat is cyan", "A azure feline"]
    models = ["model_a", "model_b", "model_c"]
    result = logic.analyze_storm(trajs, models)
    print(json.dumps(result, indent=2))
