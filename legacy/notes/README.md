# AICO Storm Wrapper for Ollama

This is a proof-of-concept wrapper for Ollama that implements the **Storm** and **DCX (Divergence-Correlation Index)** concepts from the AICO whitepaper.

## Features
-   **Parallel Cognition**: Launches multiple inference "trajectories" simultaneously.
-   **DCX Scoring**: Calculates the semantic divergence of each trajectory from the group mean using vector embeddings.
-   **Automated Pruning**: Terminates trajectories that drift too far from the group consensus.
-   **Storm Collapse**: Selects the most central and coherent trajectory as the final "Glyph."

## Prerequisites
-   [Ollama](https://ollama.com/) installed and running locally.
-   Python 3.8+
-   A model downloaded (default is `llama3`).

## Installation
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
Run the script to see a demonstration:
```bash
python storm_ollama.py
```

You can also import the `AICOStorm` class into your own projects:
```python
import asyncio
from storm_ollama import AICOStorm

async def run():
    storm = AICOStorm(model="llama3", num_trajectories=5)
    result = await storm.run_storm("Explain why AICO is 'allergic to leaks'.")
    print(result)

asyncio.run(run())
```

## How it Works
The wrapper sends simultaneous requests to Ollama with different seeds and temperatures. It then calculates the cosine similarity between the embeddings of the responses. Responses that are outliers (high divergence) are pruned, and the most representative response is returned. 

This mirrors the "Speculative Reasoning" or "Dream Chamber" process described in Chapters 17 and 18 of the AICO whitepaper.
