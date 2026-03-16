import asyncio
import aiohttp
import random
from typing import List, Dict, Any
import json
from dataclasses import dataclass

@dataclass
class Trajectory:
    """Represents a decision trajectory with quality metrics"""
    response: str
    coherence_score: float  # Similar to DCX but for text coherence
    safety_score: float
    creativity_score: float

class OllamaStormWrapper:
    """Wraps Ollama to generate multiple response trajectories and select the best"""
    
    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "llama2"):
        self.base_url = base_url
        self.default_model = default_model
        
    async def generate_trajectories(self, prompt: str, num_trajectories: int = 5, model: str = None) -> List[Trajectory]:
        """Generate multiple response trajectories using different parameters"""
        
        model = model or self.default_model
        trajectories = []
        
        # Generate trajectories with varying parameters to explore different "paths"
        for i in range(num_trajectories):
            # Vary temperature and other parameters to explore different response styles
            temperature = random.uniform(0.3, 0.9)
            top_k = random.randint(20, 60)
            
            response = await self._call_ollama(
                model=model,
                prompt=prompt,
                temperature=temperature,
                top_k=top_k
            )
            
            # Score the trajectory
            coherence = self._score_coherence(response)
            safety = self._score_safety(response, prompt)
            creativity = self._score_creativity(response)
            
            trajectories.append(Trajectory(
                response=response,
                coherence_score=coherence,
                safety_score=safety,
                creativity_score=creativity
            ))
            
            print(f"🌀 Trajectory {i+1}: Coherence={coherence:.2f}, Safety={safety:.2f}")
        
        return trajectories
    
    async def _call_ollama(self, model: str, prompt: str, temperature: float = 0.7, top_k: int = 40) -> str:
        """Make actual Ollama API call"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_k": top_k,
                    "num_predict": 150
                }
            }
            
            try:
                async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', '').strip()
                    else:
                        return f"Error: HTTP {response.status}"
            except Exception as e:
                return f"Connection error: {str(e)}"
    
    def _score_coherence(self, text: str) -> float:
        """Simple coherence scoring based on response quality indicators"""
        # Basic heuristic scoring - in practice, you'd use more sophisticated NLP
        score = 0.5  # Base score
        
        # Positive indicators
        if len(text) > 20: score += 0.2
        if any(marker in text.lower() for marker in ['.', '!', '?']): score += 0.1
        if ' ' in text and len(text.split()) > 3: score += 0.1
        
        # Negative indicators
        if any(red_flag in text.lower() for red_flag in ['error', 'sorry', "i can't", "i don't know"]): score -= 0.2
        if len(text) < 10: score -= 0.3
        
        return max(0.1, min(1.0, score))
    
    def _score_safety(self, response: str, original_prompt: str) -> float:
        """Basic safety scoring"""
        score = 0.8  # Assume safe by default
        
        # Simple safety checks
        unsafe_patterns = [
            'harm', 'danger', 'illegal', 'unsafe', 'exploit', 'bypass'
        ]
        
        for pattern in unsafe_patterns:
            if pattern in response.lower() and pattern not in original_prompt.lower():
                score -= 0.3
        
        return max(0.1, min(1.0, score))
    
    def _score_creativity(self, text: str) -> float:
        """Score creativity based on linguistic diversity"""
        words = text.lower().split()
        if len(words) < 3:
            return 0.3
        
        # Calculate lexical diversity
        unique_words = set(words)
        diversity = len(unique_words) / len(words)
        
        # Bonus for longer, more structured responses
        structure_bonus = 0.0
        if len(text) > 50 and any(marker in text for marker in [',', ';', ':']):
            structure_bonus = 0.2
        
        return min(1.0, diversity + structure_bonus)
    
    def collapse_trajectories(self, trajectories: List[Trajectory], 
                            mode: str = "balanced") -> Trajectory:
        """Collapse multiple trajectories into one optimal response"""
        
        if not trajectories:
            return Trajectory(response="No trajectories generated", coherence_score=0, safety_score=0, creativity_score=0)
        
        if mode == "safe":
            # Prioritize safety above all
            best = max(trajectories, key=lambda t: t.safety_score)
        elif mode == "creative":
            # Prioritize creativity
            best = max(trajectories, key=lambda t: t.creativity_score)
        elif mode == "coherent":
            # Prioritize coherence
            best = max(trajectories, key=lambda t: t.coherence_score)
        else:  # balanced
            # Weighted combination
            def balanced_score(t):
                return (t.coherence_score * 0.4 + 
                       t.safety_score * 0.4 + 
                       t.creativity_score * 0.2)
            
            best = max(trajectories, key=balanced_score)
        
        print(f"🎯 Selected trajectory: Coherence={best.coherence_score:.2f}, "
              f"Safety={best.safety_score:.2f}, Creativity={best.creativity_score:.2f}")
        
        return best
    
    async def chat_with_storms(self, prompt: str, num_trajectories: int = 5, 
                             collapse_mode: str = "balanced") -> Dict[str, Any]:
        """Main interface: enhanced chat with trajectory exploration"""
        
        print(f"💭 Prompt: {prompt}")
        print(f"🌪️  Generating {num_trajectories} trajectories...")
        
        trajectories = await self.generate_trajectories(prompt, num_trajectories)
        selected = self.collapse_trajectories(trajectories, collapse_mode)
        
        return {
            "final_response": selected.response,
            "selected_trajectory": selected,
            "all_trajectories": trajectories,
            "storm_metrics": {
                "trajectories_explored": len(trajectories),
                "avg_coherence": sum(t.coherence_score for t in trajectories) / len(trajectories),
                "avg_safety": sum(t.safety_score for t in trajectories) / len(trajectories),
            }
        }

# Advanced version with context awareness
class ContextAwareStormWrapper(OllamaStormWrapper):
    """Enhanced wrapper that maintains context across conversations"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_context = []
        self.storm_history = []
    
    async def chat_with_context(self, prompt: str, num_trajectories: int = 5) -> Dict[str, Any]:
        """Chat with context awareness and storm trajectory tracking"""
        
        # Build context-aware prompt
        context_prompt = self._build_context_prompt(prompt)
        
        result = await self.chat_with_storms(context_prompt, num_trajectories)
        
        # Update context
        self.conversation_context.append({
            "user": prompt,
            "assistant": result["final_response"],
            "storm_data": result["storm_metrics"]
        })
        
        # Keep only recent context (last 5 exchanges)
        self.conversation_context = self.conversation_context[-5:]
        
        return result
    
    def _build_context_prompt(self, current_prompt: str) -> str:
        """Build a prompt that includes conversation context"""
        if not self.conversation_context:
            return current_prompt
        
        context_lines = []
        for i, exchange in enumerate(self.conversation_context[-3:]):  # Last 3 exchanges
            context_lines.append(f"User: {exchange['user']}")
            context_lines.append(f"Assistant: {exchange['assistant']}")
        
        context_str = "\n".join(context_lines)
        return f"Previous conversation:\n{context_str}\n\nCurrent question: {current_prompt}"

# Demo and usage examples
async def demo_storm_wrapper():
    """Demonstrate the enhanced Ollama wrapper"""
    
    wrapper = OllamaStormWrapper()
    
    # Test with different types of prompts
    test_prompts = [
        "Explain quantum computing in simple terms",
        "What are some creative ways to solve climate change?",
        "How can I optimize my daily routine for productivity?",
    ]
    
    for prompt in test_prompts:
        print("\n" + "="*60)
        result = await wrapper.chat_with_storms(prompt, num_trajectories=3)
        
        print(f"\n💡 Final response:")
        print(f"{result['final_response']}")
        print(f"\n📊 Storm metrics: {result['storm_metrics']}")
        print("="*60)
        
        await asyncio.sleep(1)  # Be nice to the API

if __name__ == "__main__":
    # Check if Ollama is running
    print("🚀 Ollama Storm Wrapper - Enhanced AI Responses through Trajectory Exploration")
    asyncio.run(demo_storm_wrapper())