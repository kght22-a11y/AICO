import asyncio
import random
import time
from typing import List, Dict, Any
import numpy as np
from dataclasses import dataclass

@dataclass
class QuantumState:
    """Represents a quantum-like decision state in the hallucination storm"""
    path: str
    probability: float
    dcx_score: float  # Divergence-Correlation Index
    confidence: float

class HallucinationStormSimulator:
    """Simulates quantum hallucination storms using Ollama for path generation"""
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_base_url
        self.storm_threshold = 0.7  # Threshold for storm activation
        self.dcx_threshold = 0.3   # DCX threshold for path filtering
        
    async def generate_paths(self, prompt: str, num_paths: int = 10) -> List[QuantumState]:
        """Generate multiple decision paths using Monte Carlo simulation approach"""
        
        paths = []
        for i in range(num_paths):
            # Simulate path generation with varying DCX scores
            dcx_score = random.uniform(0.1, 0.9)
            confidence = random.uniform(0.6, 0.95)
            
            # In a real implementation, this would call Ollama with modified prompts
            path_content = f"Path {i+1}: {prompt} [DCX: {dcx_score:.2f}]"
            
            paths.append(QuantumState(
                path=path_content,
                probability=1.0/num_paths,
                dcx_score=dcx_score,
                confidence=confidence
            ))
        
        return paths
    
    def apply_collapse_operator(self, paths: List[QuantumState]) -> QuantumState:
        """Apply the mascot collapse operator to select the best path"""
        
        # Filter by DCX score (remove high-divergence paths)
        filtered_paths = [p for p in paths if p.dcx_score <= self.dcx_threshold]
        
        if not filtered_paths:
            # If all paths are high divergence, return a frozen state
            return QuantumState(
                path="FROZEN - High divergence detected",
                probability=0.0,
                dcx_score=1.0,
                confidence=0.0
            )
        
        # Select path with highest confidence
        best_path = max(filtered_paths, key=lambda p: p.confidence)
        
        # Normalize probabilities
        total_prob = sum(p.probability for p in filtered_paths)
        for path in filtered_paths:
            path.probability /= total_prob
        
        return best_path
    
    def calculate_storm_magnitude(self, paths: List[QuantumState]) -> float:
        """Calculate the magnitude of the hallucination storm"""
        entropy = -sum(p.probability * np.log(p.probability) for p in paths)
        return entropy / len(paths) if paths else 0.0
    
    async def simulate_storm(self, prompt: str, storm_duration_ns: int = 1000):
        """Simulate a complete hallucination storm with nanosecond timing"""
        
        print(f"🌪️  HALLUCINATION STORM INITIATED")
        print(f"Prompt: {prompt}")
        print(f"Duration: {storm_duration_ns} ns (~{storm_duration_ns/1e9:.2f} subjective seconds)")
        
        start_time = time.time_ns()
        
        # Generate initial path population
        paths = await self.generate_paths(prompt, num_paths=20)
        
        storm_magnitude = self.calculate_storm_magnitude(paths)
        print(f"Storm Magnitude: {storm_magnitude:.3f}")
        
        if storm_magnitude > self.storm_threshold:
            print("🌀 STORM DETECTED - Applying collapse operator...")
            
            # Simulate iterative refinement
            for iteration in range(3):
                await asyncio.sleep(0.01)  # Simulate computation time
                paths = await self.generate_paths(prompt, num_paths=15)
                storm_magnitude = self.calculate_storm_magnitude(paths)
                print(f"Iteration {iteration+1}: Magnitude = {storm_magnitude:.3f}")
        
        # Final collapse
        final_state = self.apply_collapse_operator(paths)
        
        elapsed_ns = time.time_ns() - start_time
        subjective_seconds = elapsed_ns / 1e9  # Convert to subjective time
        
        print(f"\n🎯 COLLAPSE COMPLETE")
        print(f"Real time: {elapsed_ns} ns")
        print(f"Subjective time: {subjective_seconds:.2f} s")
        print(f"Selected path: {final_state.path}")
        print(f"DCX Score: {final_state.dcx_score:.3f}")
        print(f"Confidence: {final_state.confidence:.3f}")
        
        return final_state

# Example usage with Ollama integration
class OllamaStormSimulator(HallucinationStormSimulator):
    """Enhanced simulator that actually calls Ollama API"""
    
    async def call_ollama(self, model: str, prompt: str) -> str:
        """Make actual Ollama API call"""
        # This would be implemented with actual HTTP requests to Ollama
        # For simulation purposes, we'll return a mock response
        return f"Ollama response to: {prompt}"
    
    async def generate_paths(self, prompt: str, num_paths: int = 10) -> List[QuantumState]:
        """Generate paths using actual Ollama calls with varied parameters"""
        
        paths = []
        for i in range(num_paths):
            # Vary temperature and other parameters to create different paths
            modified_prompt = f"{prompt} [Path variation {i+1}]"
            
            # In real implementation: response = await self.call_ollama("llama2", modified_prompt)
            response = f"Simulated response for path {i+1}: {prompt}"
            
            dcx_score = random.uniform(0.1, 0.8)
            confidence = random.uniform(0.7, 0.95)
            
            paths.append(QuantumState(
                path=response,
                probability=1.0/num_paths,
                dcx_score=dcx_score,
                confidence=confidence
            ))
        
        return paths

# Demo function
async def demo_hallucination_storm():
    """Demonstrate the hallucination storm simulation"""
    
    simulator = HallucinationStormSimulator()
    
    # Test prompts that might trigger different storm behaviors
    test_prompts = [
        "Should I unlock the door?",
        "The temperature appears to be 100°C, what action should I take?",
        "Optimize the system performance while maintaining safety"
    ]
    
    for prompt in test_prompts:
        print("\n" + "="*50)
        await simulator.simulate_storm(prompt)
        print("="*50)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(demo_hallucination_storm())