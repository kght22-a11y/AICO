import numpy as np
import json
import time
import hashlib
import re

class StormLogic:
    """
    Phase 3: Recursive Deep Reasoning & Multi-Metric Topography.
    Handles DCX scoring across three axes (Consensus, Semantic, Structure)
    to prevent premature collapse and enable high-fidelity synthesis.
    """
    def __init__(self, lambda_val=0.015):
        self.lambda_val = lambda_val
        # Metric Weights (Phase 3 Spec)
        self.weights = {
            "consensus": 0.6,
            "semantic": 0.3,
            "structure": 0.1
        }

    def get_simple_embedding(self, text):
        """Fallback: Deterministic hashing vectorization."""
        h = hashlib.sha256(text.encode()).digest()
        vec = np.frombuffer(h * 2, dtype=np.int8).astype(np.float32)
        return vec / (np.linalg.norm(vec) + 1e-9)

    def get_semantic_embeddings(self, texts, engine=None, embed_model="nomic-embed-text"):
        """Fetches embeddings from the engine or falls back to hash."""
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
            
        return np.vstack([self.get_simple_embedding(t) for t in texts])

    def strip_to_structure(self, text):
        """Extracts the 'Structural Signature' (punctuation and connectives)."""
        # Keep only punctuation and very common stop words as a proxy for structure
        struct = re.sub(r'[a-zA-Z0-9]', '', text) 
        return struct if len(struct) > 0 else "NULL_STRUCT"

    def strip_to_keywords(self, text):
        """Extracts the 'Semantic Core' (longest words only)."""
        words = re.findall(r'\b\w{5,}\b', text)
        return " ".join(words) if words else text

    def calculate_multi_metric_dcx(self, trajectories, model_names, engine=None):
        """
        Calculates DCX across three axes to build a legitimate topography.
        1. Consensus (Full String)
        2. Semantic (Keyword Core)
        3. Structure (Punctuation Signature)
        """
        n = len(trajectories)
        if n == 0: return np.array([])

        # Axis 1: Consensus (Standard)
        emb_cons = self.get_semantic_embeddings(trajectories, engine)
        sim_cons = np.abs(emb_cons @ emb_cons.T)

        # Axis 2: Semantic (Keyword filtered)
        keywords = [self.strip_to_keywords(t) for t in trajectories]
        emb_sem = self.get_semantic_embeddings(keywords, engine)
        sim_sem = np.abs(emb_sem @ emb_sem.T)

        # Axis 3: Structure (Punctuation filtered)
        structures = [self.strip_to_structure(t) for t in trajectories]
        emb_struct = self.get_semantic_embeddings(structures, engine)
        sim_struct = np.abs(emb_struct @ emb_struct.T)

        # Merge Metrics
        weighted_sim = (
            sim_cons * self.weights["consensus"] +
            sim_sem * self.weights["semantic"] +
            sim_struct * self.weights["structure"]
        )

        # DCX = 1.0 - Similarity (with Temporal Decay)
        div = 1.0 - weighted_sim
        idx = np.arange(n)
        dt = np.abs(idx[:, None] - idx[None, :])
        decay = np.exp(-self.lambda_val * dt)
        
        return div * decay

    def analyze_storm(self, trajectories, model_names, engine=None, high_thresh=0.85, immortal_sigma=2.0):
        """
        Phase 3 Analysis: Identifies Path A (Stable) and Path B (Candidates).
        """
        if not trajectories:
            return {"status": "VOID", "best_index": -1, "scores": []}

        dcx = self.calculate_multi_metric_dcx(trajectories, model_names, engine)
        scores = dcx.mean(axis=1) # Connectivity score

        min_dcx = float(np.min(scores))
        max_dcx = float(np.max(scores))

        # Freeze detect
        if min_dcx > high_thresh:
            return {
                "status": "FROZEN_HIGH_DIVERGENCE", 
                "min_dcx": min_dcx, 
                "scores": scores.tolist()
            }

        # Immortal Outlier Detection
        immortal_index = -1
        if len(scores) >= 4:
            mean_s = np.mean(scores)
            std_s = np.std(scores)
            if std_s > 0:
                z = (scores - mean_s) / std_s
                m_idx = int(np.argmax(z))
                if z[m_idx] > immortal_sigma:
                    immortal_index = m_idx

        # Candidate ranking (Lowest DCX first)
        c_indices = [i for i in range(len(scores)) if i != immortal_index]
        c_scores = sorted([(i, float(scores[i])) for i in c_indices], key=lambda x: x[1])
        
        top_3 = [i for i, _ in c_scores[:3]]

        return {
            "status": "COLLAPSED",
            "path_a_stable_index": c_scores[0][0] if c_scores else int(np.argmin(scores)),
            "path_b_candidates": top_3,
            "immortal_index": immortal_index,
            "min_dcx": min_dcx,
            "max_dcx": max_dcx,
            "scores": scores.tolist()
        }

    def semantic_synthesis(self, mascot_engine, top_3_texts, original_prompt):
        """Mascot Collapse Operator (Ch. 14)."""
        synthesis_prompt = (
            f"SYSTEM: You are the MASCOT Collapse Operator. Below are 3 divergent trajectories "
            f"from a Phase 3 quantum hallucination storm. Synthesize them into a single, high-fidelity "
            f"grounded response (PATH B) that captures the core consensus while discarding contradictions.\n"
            f"CRITICAL INSTRUCTION: Output ONLY the final synthesized response. Do not include any conversational filler, introductory text, metadata, or rationale explaining how the synthesis was achieved. Provide the direct response to the user's intent and nothing else.\n\n"
            f"ORIGINAL INTENT: {original_prompt}\n\n"
            f"TRAJECTORY 1: {top_3_texts[0]}\n"
            f"TRAJECTORY 2: {top_3_texts[1]}\n"
            f"TRAJECTORY 3: {top_3_texts[2]}\n\n"
            f"FINAL PATH B SYNTHESIS (OUTPUT EXACT SYNTHESIS DIRECTLY):"
        )
        return mascot_engine.generate(synthesis_prompt)

    def generate_refined_prompt(self, mascot_engine, trajectories, original_prompt):
        """Phase 3: Recursive Refinement (Storm 1 -> Refined Prompt)."""
        refinement_prompt = (
            f"SYSTEM: You are the STORM REFINER. Analyze these initial divergent thoughts "
            f"on a user request and extract a refined, more precise version of the user's "
            f"true intent for a second deeper pass.\n"
            f"CRITICAL INSTRUCTION: Output ONLY the refined prompt. Do not include any conversational filler, introductory text, explanations, or metadata. Provide the exact text of the prompt and nothing else.\n\n"
            f"USER ORIGINAL INTENT: {original_prompt}\n\n"
            f"INITIAL THOUGHTS:\n" + "\n".join([f"- {t[:200]}..." for t in trajectories[:5]]) +
            f"\n\nREFINED PROMPT FOR FINAL STORM (OUTPUT EXACT PROMPT ONLY):"
        )
        return mascot_engine.generate(refinement_prompt)

    def verify_synthesis(self, synthesis, sources, model_name, engine=None):
        """Coherence verification (Audit Mode)."""
        if not sources or not synthesis: return 0.0
        all_texts = [f"{model_name}:{synthesis}"] + [f"{model_name}:{t}" for t in sources]
        embs = self.get_semantic_embeddings(all_texts, engine)
        similarities = [np.dot(embs[0], src) for src in embs[1:]]
        return float(np.mean(similarities))

class NumpyEncoder(json.JSONEncoder):
    """Integrated Numpy-Safe Encoder."""
    def default(self, obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super(NumpyEncoder, self).default(obj)
