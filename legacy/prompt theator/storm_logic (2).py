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

    def get_semantic_embeddings(self, texts, engine=None, embed_model="nomic-embed-text"):
        """Attempts to get a true NLP embedding, falls back to SHA-256 hash."""
        if engine:
            embs = []
            success = True
            for text in texts:
                emb = engine.get_embedding(text, embed_model)
                if emb is None:
                    success = False
                    break
                vec = np.array(emb, dtype=np.float32)
                vec = vec / (np.linalg.norm(vec) + 1e-9)
                embs.append(vec)
            if success:
                return np.vstack(embs)
            
        # Fallback to SHA-256
        embs = []
        for text in texts:
            embs.append(self.get_simple_embedding(text))
        return np.vstack(embs)

    def calculate_dcx_matrix(self, trajectories, model_names, engine=None):
        """
        Vectorized DCX calculation with Multi-Model Ground Truth.
        Perfect correlation is impossible due to model-specific biases.
        """
        n = len(trajectories)
        if n == 0: return np.array([])

        # Generate model-biased embeddings
        biased_texts = [f"{model}:{text}" for text, model in zip(trajectories, model_names)]
        embs = self.get_semantic_embeddings(biased_texts, engine)
        
        # Similarity Matrix (Cosine)
        sim = np.abs(embs @ embs.T)

        # DCX = Divergence (0=same, 1=most divergent) — invert similarity
        div = 1.0 - sim

        # Temporal Decay
        idx = np.arange(n)
        dt = np.abs(idx[:, None] - idx[None, :])
        decay = np.exp(-self.lambda_val * dt)

        # DCX = Divergence * Decay
        dcx_matrix = div * decay

        return dcx_matrix

    def analyze_storm(self, trajectories, model_names, engine=None, low_thresh=0.2, high_thresh=0.85, immortal_sigma=2.0):
        """
        Analyzes the storm and finds the best candidates or triggers a freeze.
        Includes Immortal Outlier Detection: a trajectory that diverges >immortal_sigma
        standard deviations below the cluster mean is preserved as a separate path
        rather than culled by DCX pruning.
        """
        if not trajectories:
            return {"status": "VOID", "best_index": -1, "scores": []}

        dcx = self.calculate_dcx_matrix(trajectories, model_names, engine)
        # Connectivity score = mean DCX divergence with others
        scores = dcx.mean(axis=1)

        min_dcx = np.min(scores)
        max_dcx = np.max(scores)

        # Freeze if even the most similar trajectory is still above high_thresh
        # (total divergence — no stable cluster exists to collapse)
        if min_dcx > high_thresh:
            return {"status": "FROZEN_HIGH_DIVERGENCE", "best_index": -1,
                    "min_dcx": float(min_dcx), "max_dcx": float(max_dcx),
                    "scores": scores.tolist()}

        # --- Immortal Outlier Detection ---
        # High DCX score = most divergent from cluster = sticks out like a sore thumb
        immortal_index = -1
        if len(scores) >= 4:
            mean_score = np.mean(scores)
            std_score = np.std(scores)
            if std_score > 0:
                z_scores = (scores - mean_score) / std_score
                most_divergent_idx = int(np.argmax(z_scores))  # highest DCX = most outlier
                if z_scores[most_divergent_idx] > immortal_sigma:  # +2 sigma above mean
                    immortal_index = most_divergent_idx

        # Top 3 by lowest DCX (most convergent = most grounded)
        candidate_indices = [i for i in range(len(scores)) if i != immortal_index]
        candidate_scores = [(i, scores[i]) for i in candidate_indices]
        candidate_scores.sort(key=lambda x: x[1])  # ascending: lowest DCX first
        top_3_idx = [i for i, _ in candidate_scores[:3]]

        return {
            "status": "COLLAPSED",
            "best_index": candidate_scores[0][0] if candidate_scores else int(np.argmin(scores)),
            "top_3_indices": top_3_idx,
            "immortal_index": immortal_index,
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

    def verify_synthesis(self, synthesis, sources, model_name, engine=None):
        """
        Audit Mode: Compares the synthesis back to the source trajectories.
        Returns a coherence score (0.0 to 1.0).
        """
        if not sources or not synthesis:
            return 0.0
            
        all_texts = [f"{model_name}:{synthesis}"] + [f"{model_name}:{t}" for t in sources]
        embs = self.get_semantic_embeddings(all_texts, engine)
        
        s_emb = embs[0]
        source_embs = embs[1:]
        
        # Calculate mean similarity to all sources
        similarities = [np.dot(s_emb, src) for src in source_embs]
        coherence = np.mean(similarities)
        
        return float(coherence)

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
