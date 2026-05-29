# Storm Rebuild Guide: Quantum Hallucination Engine

## 1. Vision & Core Principles
*   **Aesthetics**: Windows 95 Retro (Grey `#C0C0C0`, Blue `#000080`, Comic Sans MS).
*   **Inference Agnostic**: The system must be a wrapper that can adapt to any backend (Ollama, llama.cpp, Local API).
    *   **Engine Parsing**: On startup, the UI must query the active engine for a model list.
    *   **Stage-Specific Models**: Users should be able to select different models for different stages (e.g., a small model for rephrasing, large for main trajectories).
*   **Modular Architecture**: Every feature besides "Enter Prompt -> Get Answer" must be toggleable (ON/OFF).
*   **Memory Management**: 
    *   **Rolling Context**: Active memory for immediate inference.
    *   **Long-Term Bio-Log**: Instead of "deleting" memory, the system must cut-and-paste overflow or purged context into a persistent `.txt` or `.ndjson` log for permanent record.

---

## 2. Four-Phase Build Roadmap

### Phase 1: The Foundation (Minimal Viable Storm)
*   **UI**: Basic Win95 frame with a prompt entry, EXECUTE button, and output stream.
*   **Agnostic Engine**: Implementation of a provider-agnostic interface that accepts a prompt and returns a string.
*   **Capture**: Automatic logging of every Input/Output pair.
*   **Context**: Implementation of the "Rolling Context" window.
*   **Archiving**: First pass of the "Long-Term Bio-Log" (cut/paste purged context to file).

### Phase 2: Refined Storm Parameters
*   **Parameter Controls**:
    *   **Trajectories (N)**: Dropdown menu with values from 5 to 50 (increments of 5).
    *   **Temperature**: Slider or input from 0.0 to 1.0.
    *   **DCX Thresholds**: Low-Limit `0.2`, High-Limit `0.85`.
*   **Collapse Operator (The Mascot)**:
    *   **Selectable Mascot**: The model used for synthesis/collapse is selectable and can be different from the trajectory generator.
    *   **Semantic Synthesis**: If $N > 5$, the Mascot semantically combines the top 3 results into a single "Convergent" response.
*   **Vector DCX Logic**:
    *   **Multi-Model Ground Truth**: The DCX scoring engine should utilize embeddings from all available/involved models to build the correlation matrix. This ensures that "Perfect Correlation" (1.0) is mathematically impossible due to inherent model bias differences, preventing premature collapse.
*   **Visuals**: Implementation of the standard `ttk.Progressbar` for background generation.

### Phase 3: Recursive Deep Reasoning
*   **2-Prompt Depth**: The system enters a multi-layered reasoning loop.
    *   **Input** -> **Storm 1** -> **Refined Prompt** -> **Storm 2** -> **Final Result**.
*   **Dual-Path Generation**:
    *   **Path A (The Stable)**: The trajectory with the absolute lowest DCX (highest correlation).
    *   **Path B (The Synthesis)**: A semantic combination of the top 3 trajectories.
    *   Both paths should be displayed or available for comparison.

### Phase 4: Ghost Memories & Modular Polish
*   **Ghost Memories (RAG)**: The "Long-Term Bio-Log" is indexed. When context is sparse or a keyword triggers a "forgotten" topic, the system retrieves relevant snippets from the Bio-Log and injects them as "Ghost Memories" into the prompt.
*   **Intelligent Rephrasing**: Automatic prompt refinement using the "small model" logic.
*   **Shadow Chain Logging**: Forensic logging of divergent "hallucination" paths.
*   **Theme Packs**: Extension of the Win95 theme to include custom icons and Comic Sans sound-alikes.
*   **Toggle System**: A master "Enhancements" panel to individual switch on/off DCX, Semantic Synthesis, and Recursive Depth.

---

## 3. Implementation Checklist
*   [ ] **Progress Indicators**: PROGRESS BAR is mandatory for all generations.
*   [ ] **Model Selector**: Dropdowns must refresh from the inference engine API.
*   [ ] **No Cache Residency**: Ensure all logic is hardware-independent RAM/VRAM based.
*   [ ] **Comic Sans**: Ensure all labels and buttons utilize the specified font for maximum effect.
