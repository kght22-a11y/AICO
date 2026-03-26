import asyncio
import numpy as np
from typing import List
from sklearn.metrics.pairwise import cosine_similarity
from unittest.mock import MagicMock, patch

# Mocking Ollama for verification
class MockOllama:
    def generate(self, model, prompt, options):
        seed = options.get('seed', 0)
        # Create different responses based on seeds
        responses = {
            0: "The system is allergic to leaks because it enforces security at the architectural level.",
            100: "AICO's 'allergic to leaks' philosophy means that any data leak triggers a physical shutdown.",
            200: "Data sovereignty is a core principle, making the system highly resistant to unauthorized exfiltration.",
            300: "I am a helpful assistant who likes to talk about cats and dogs.", # Drifted response
            400: "AICO prevents leaks by using a Diving Bell model and capability tokens."
        }
        return {'response': responses.get(seed, "Default response")}

    def embeddings(self, model, prompt):
        # Create deterministic embeddings for testing
        # We'll make one vector significantly different (the 300 seed one)
        if "cats and dogs" in prompt:
            return {'embedding': [0.1, 0.9, 0.1, 0.1]}
        return {'embedding': [0.9, 0.1, 0.1, 0.1]}

# Import the class from the main file but mock the ollama dependency
from storm_ollama import AICOStorm

async def verify_logic():
    print("[*] Verifying AICO Storm Logic with Mocked Ollama...")
    
    # Patch ollama inside the class or globally
    with patch('ollama.generate', side_effect=MockOllama().generate), \
         patch('ollama.embeddings', side_effect=MockOllama().embeddings):
        
        storm = AICOStorm(model="llama3", num_trajectories=5, drift_threshold=0.3)
        result = await storm.run_storm("Explain the 'allergic to leaks' policy.")
        
        print("\n--- VERIFICATION OUTPUT ---")
        print(result)
        print("\n[*] Logic verification complete.")

if __name__ == "__main__":
    asyncio.run(verify_logic())
