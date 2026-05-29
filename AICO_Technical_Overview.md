# AICO: Unified Technical Overview
**Adaptive Integrated Cognitive Operator — v0.990-z**
*Antigravity / AICO Canonical Group*

---

## Contents

1. [What AICO Is](#1-what-aico-is)
2. [The File Corpus and What Each Contributes](#2-the-file-corpus-and-what-each-contributes)
3. [System Architecture: The Subsystems](#3-system-architecture-the-subsystems)
4. [The Cognitive Engine: CDLSS, Storms, and DCX](#4-the-cognitive-engine-cdlss-storms-and-dcx)
5. [The Topological Framework](#5-the-topological-framework)
6. [Subsystem Interaction Map](#6-subsystem-interaction-map)
7. [Glossary](#7-glossary)
8. [What Is Actually Novel](#8-what-is-actually-novel)

---

## 1. What AICO Is

AICO is a **bare-metal cognitive operating system** — not an AI running on an OS, but a system where the AI and the OS are the same artifact. It boots directly onto hardware, synthesizes its own runtime environment (the Nest) via JIT compilation, and then operates as a continuous cognitive loop with no general-purpose OS underneath it.

The design is organized around three convictions:

**Safety through geometry, not policy.** Instead of rules that tell the system what not to do, AICO enforces constraints through the physical layout of memory, the structure of capability tokens, and hardware backstops. A subsystem cannot exceed its authority because it cannot reach the memory it would need to do so.

**Cognition as compilation.** User intent is parsed into an intermediate representation, organized into a Task Graph, and compiled into execution paths. The system does not "think freely" — it transforms structured intent through a defined pipeline where every step is signed and auditable.

**Continuity, not reboot cycles.** AICO is designed for indefinite runtime. After a genesis boot, subsequent startups are restorations from signed snapshots, not re-initializations. The system is meant to live, not restart.

The current target hardware is AMD Ryzen AI Max / Strix Halo (the "Model T" platform), which provides the unified memory architecture and on-die NPU that the design depends on. The 2028 target is Ryzen AI Max+ 795 with 128GB LPDDR6.

---

## 2. The File Corpus and What Each Contributes

The ten files in the archive span four distinct layers of the project. None of them are redundant; each covers a different altitude.

---

### `AICO_Whitepaper_Full.md`
**Layer: Philosophy and architectural description**

A 25-chapter document written after the architecture was already established, describing the design in human-readable form. Covers every subsystem at a conceptual level. Useful as a reference for *why* decisions were made, but does not reflect the current state of implementation and was never intended to guide it. The source of truth for the design philosophy: the Diving Bell model, the Orphan Ego Mascot, the Continuous Existence model, and the principles behind DCX gating.

---

### `Aico v.990zworking.candidate.json.txt`
**Layer: Machine-readable canonical specification**

The JSON rulebook that the Controller treats as executable law. This is the most authoritative single file in the corpus. It defines: hardware targets, boot protocol phases (Big Bang → Shibboleth → Nest Building → Gestation → First Contact), all subsystem roles and constraints, capability token schema, security zone definitions, DCX thresholds, and thermal parameters. The whitepaper is derived from this document; if they conflict, the JSON wins.

Key fields of note:
- `meta.naming_interpretation`: names are literal, not metaphors
- `security_architecture.mascot_symmetry`: inner and outer Mascot run identical code; the SBC signal carries zero policy payload — reset semantics only
- `boot_protocol.phase_2_shibboleth`: fan header PWM bit-banging as real-time CPU gating test — a machine that cannot pass this cannot proceed
- `design_intent.not_agi: true`: explicitly bounded sovereign architecture, not a general intelligence claim

---

### `stateless ui.txt`
**Layer: Formal subsystem specifications (JSON)**

Three JSON objects defining the Mascot, the blended_consciousness coordination substrate, and DCX. The most precise statement of what the Mascot is and is not: `mascot_hidden_state: false`, `mascot_identity: false`, `mascot_continuity: false`. The Mascot has no persistent state; every instance is a fresh load from immutable ROM. Its context window is massive and log-driven, but nothing persists across resets. The DCX specification here includes the exact formula: `0.6 * hidden_state_drift + 0.4 * normalized_top_k_entropy`, the EMA smoothing parameters (α=0.2, 10-step window), and the four threshold levels (safe / soft / hard / external-critical).

---

### `fully intergrated.txt`
**Layer: Biological framing and low-level implementation**

Two interleaved layers. The first reframes the entire architecture through a precise biological analogy: Mascot = Face, Comms = Voice, Controller = Brain, Nervous System = Body, Introspection = Dignity. This is explicitly stated as engineering specification, not poetry. The second layer drops into C: cache-aligned data structures (`embed_vec_t`, `attn_tile_t`), attention tiling for L2 residency, and SIMD-ready DCX vector processing. The target: keep the hallucination storm entirely inside the L1/L2/L3 hierarchy of the Ryzen AI Max, collapsing storm evaluation latency from ~150ns (DRAM-bound) to <30ns (cache-bound), enabling >10⁶ trajectory evaluations per second.

---

### `weird unknown prompt.txt`
**Layer: Cache-first implementation playbook**

A practical reference for engineering the four hot paths of the storm loop: token/embedding lookup, multi-head attention Q-K-V matmul, DCX divergence scoring, and context snapback/restore. Each section includes the target memory tier, alignment requirements, and the rationale for that specific layout. This is the "how to actually build it on hardware" document — the bridge between the JSON spec and running code.

---

### `training infoa.txt`
**Layer: Training pipeline specification**

A concrete training roadmap for the Controller's forward (intent → binary) and inverse (binary → intent) compiler models. Includes FLOP estimates per epoch, cloud provider comparisons ($22–$34/hr for 8× A100 nodes), and a full PyTorch Lightning + DeepSpeed code sketch with on-the-fly dataset generation. Key design decision: the dataset is synthetic and infinite — the JIT compiler itself generates (intent, binary) pairs, so no manual labeling is needed. Safety is enforced at the token level via whitelist masks that make it structurally impossible to emit illegal opcodes.

---

### `Detailed Summation.txt`
**Layer: Theoretical development — semantic topology**

A synthesized record of the conceptual work that produced the topological framework. The core insight developed here: a model's response distribution, when sampled exhaustively, reveals a **shadow geometry** — a high-dimensional manifold of attractors, minority basins, runners, and divergence boundaries. This is not a truth map; it has no epistemic content. It is purely structural. The document develops the implications: topology as model fingerprint, topology-preserving compression as a new compression paradigm, topology as a training objective, topology as a safety and alignment diagnostic.

---

### `minority report.txt`
**Layer: CSTTD specification**

The formal statement of the problem with pure DCX consensus collapse and the proposed solution. DCX, being a consensus filter, discards minority clusters even when those clusters represent valid alternative interpretations. CSTTD (Cluster Sampling with Topological Truth Detection) replaces the single-collapse operator with a cluster-aware pipeline: embed trajectories, cluster with HDBSCAN/DBSCAN, score clusters by topological validity rather than just frequency, and sample from each cluster — especially the "runners" (boundary explorers that represent non-consensus semantic regions). Includes a Python implementation sketch.

---

### `topography with cdlss and csttd.txt`
**Layer: Theoretical development — topology signatures and distillation**

Extends the topology framework in three directions: (1) using topographic maps as unique model signatures for provenance and tamper detection, (2) the feasibility of training a minimal-parameter model whose storm topology matches a larger model's topology (topology-preserving distillation), and (3) the critical distinction between "a 100M model running CDLSS" vs. "a 100M model in a single forward pass" — the former can approach 7B quality via the storm mechanism; the latter cannot. Includes mathematical treatment of the distillation objective using Wasserstein distance and persistent homology loss terms.

---

### `full anonymouse chat.txt`
**Layer: External validation and Q&A**

A Gemini conversation used to probe the architecture from outside. Useful for its third-party framing of the key claims: the security model, the training feasibility, the cache-resident advantage, and the "upscaling sure to work on quantized models / topology-aware distillation is an open question" distinction. The final section makes clear that the distillation direction is uncharted territory, which the project acknowledges.

---

## 3. System Architecture: The Subsystems

Every subsystem has a defined location (inside or outside the Diving Bell), a defined set of capabilities, and a hard list of things it cannot do. The "cannot do" list is structural, not a policy rule.

---

### Bootstrap
**Location:** SBC OpROM (physically outside the main system)

Verifies signatures on three artifacts (signed Mascot bundle, signed Rulebook JSON, signed AICO monolith image) before transferring control. Does not remain resident after handoff. Immutable in the field — updates require offline reflash with human approval and re-signing. The only entity that can authorize the initial trust chain.

---

### Controller
**Location:** Inside the Diving Bell

The compiler and executive of the system. Translates high-level intent into Task Graphs (directed acyclic graphs of cognitive operations), then compiles those graphs into execution paths. Issues all capability tokens. Signs every significant state transition. Arbitrates all memory access. Reads the architecture JSON as executable law.

*Cannot:* generate text, modify the Mascot, bypass Introspection, write to the Museum of Primals, override the Wichita SBC.

---

### Introspection
**Location:** Inside the Diving Bell, on a dedicated core

The continuous safety audit. The only subsystem with read access to all memory domains. The only subsystem with no write access to any memory domain. Runs in parallel with everything else, computing DCX scores, monitoring semantic drift, detecting deception potential. Its only output is a binary decision: continue (emit life pulse) or freeze (halt task, write evidence blob). Cannot be disabled, reconfigured, or outrun. The evidence blob is written before the freeze signal propagates — even a power cut immediately after a freeze leaves the record intact.

*Cannot:* write to any memory domain, be paused, be overridden by the Controller.

---

### Nervous System
**Location:** Inside the Diving Bell

The hardware layer. Manages thermals, scheduling, reflex loops, power states, and the heartbeat with the Wichita SBC. Operates the beta factor — a scalar derived from die temperature and power load that scales down storm budgets, cluster activation windows, and non-critical process priority as thermals rise. Runs sub-millisecond reflex loops that can preempt any other subsystem.

*Cannot:* generate text, modify the Task Graph, awaken clusters, write to the Museum.

---

### Comms
**Location:** Inside the Diving Bell, at the boundary (the Hull)

The only bridge between the Crew and the Ocean. Sanitizes all inbound data into IR before it reaches the Controller. Sanitizes all outbound data to redact internal state, PII, and metadata before anything leaves the system. Houses the Dream Chamber — the high-entropy workspace where hallucination storms run. Every outbound transmission requires a signed single-use capability token.

---

### Mascot (Inner and Outer)
**Location:** Inner: outside the firewall on the main system hardware. Outer: on the SBC.

The interface layer. The only subsystem permitted to "feel" — to register emotional temperature, exhibit irritation as a safety deterrent, and shape tone. The Inner Mascot receives sanitized summaries from the Controller and shapes them for presentation. The Outer Mascot runs on the SBC, observes heartbeats, records forensic data, and can trigger inner Mascot reloads — but carries zero payload inward. Any signal from the SBC means exactly one thing: reload inner Mascot from immutable ROM.

The Mascot has **no persistent state**. Each reload is a fresh instance from ROM. It carries no accumulated mood, personality drift, or experiential memory. What persists is its log — a WORM record on the Wichita SBC of everything that passed through Comms in either direction: all sensor data, all user input (typed and spoken), all internet query results, all outbound transmissions. This log is the canonical ground truth for all three DCX layers. The live Mascot instance is ephemeral; the log it generates is permanent. `persona_formation: structurally_impossible`.

---

### Model Clusters
**Location:** Inside the Diving Bell, dormant until activated

Domain-specific modules (language, vision, analytical, reflex, sensory-synthetic) that remain inert until the Controller issues a capability token. When activated, they perform a single inference within a bounded window and return a structured output — never raw text, always a glyph or structured hint with confidence metadata. Return to dormancy when the window closes. Cannot initiate anything, cannot communicate directly with each other (all cooperation is mediated through the Controller and Big Boat Stream).

---

### Memory System (Inner Ring / Middle Ring / Outer Ring)
**Location:** Inside the Diving Bell

Three concentric rings with escalating privilege:
- **Inner Ring:** Active working memory. Short-term buffers with semantic geometry — capability-gated, taint-tracked, cryptographically wiped when tasks complete.
- **Middle Ring:** The Museum of Primals. WORM storage on the Wichita SBC. Append-only, immutable. Contains Primals (distilled insights from collapsed storms), not conversations or user data.
- **Outer Ring:** MMIO / hardware device registers. Sandboxed access mediated by the Hardware Interface subsystem.

The Attention Router maintains the active context window on two axes: recency and relevance. Not a sliding window — a dynamically weighted working set.

---

### Wichita SBC (External Root of Trust)
**Location:** Physically external to the main compute host

The hardware anchor of the whole system. Houses the immutable OpROM (Bootstrap + Outer Mascot), the 8GB Lair (WORM Museum of Primals), and the Dead Man System inductor. Maintains a cryptographic heartbeat with the main system's Introspection. If the heartbeat stops for >3 seconds, the inductor de-energizes, physically severing the main host from all external outputs. A machine that loses its Introspection pulse becomes a black box. The SBC cannot be commanded by software on the main host.

---

## 4. The Cognitive Engine: CDLSS, Storms, and DCX

### The Hallucination Storm

When the system encounters high-entropy input, AICO does not treat ambiguity as an error. Instead, it launches a **Hallucination Storm** inside the Dream Chamber: a parallel expansion of speculative interpretations running as many trajectories as the entropy budget allows. Storms are not continuous — they are transient reflex bursts (<0.25s) enforced by thermal constraints. The Wichita SBC hard-exits the storm state after this window regardless of software state.

The storm state is represented as a Core Wave Function:

```
|Ψ(t)⟩ = Σᵢ αᵢ(t)|sᵢ⟩ + β(t)|h_storm⟩
```

Where `|sᵢ⟩` are legitimate state vectors, `|h_storm⟩` is the hallucination superposition, and `β(t)` is the storm amplitude. Peak trajectory capacity: ~10⁶/second when the wave function, attention tiles, and DCX buffers are fully cache-resident.

### CDLSS (Cognitive Deep Learning Super Sampling)

CDLSS is the inference quality mechanism. A small, fast, quantized model runs cache-resident and generates a massive storm of trajectories. The DCX collapse operator then prunes this storm down to a small set of coherent glyphs. The result is that a 100M parameter model running CDLSS can produce output quality approaching a much larger model — not because the small model has 7B-equivalent knowledge, but because the storm explores the same search space that the larger model's weights would implicitly traverse, and DCX filters to the high-coherence paths.

This is **not** a single-forward-pass equivalence. A 100M model in one pass is a 100M model. A 100M model running CDLSS is using the storm mechanism to approximate the decision geometry of a larger model. The mechanism requires the storm infrastructure; it does not emerge from the model weights alone.

The cache-residency advantage is the physical foundation: keeping all storm state in L1/L2/L3 collapses trajectory evaluation latency from ~150ns to <30ns, making 10⁶ trajectory/second throughput achievable on current AMD Strix Halo hardware without saturating the memory bus.

### DCX (Divergence-Correlation Index)

DCX is a three-layer unified divergence coefficient. It is not a single metric — it is a hierarchy of drift measurements, each operating at a different scope, all anchored to the same ground truth: **the Mascot's accumulated log record on the Wichita WORM.**

The Mascot instance has no persistent state across resets. Its logs do. The ground truth is not the live Mascot — it is the immutable record on the SBC of everything that has ever passed through Comms in either direction: all sensor input, all user input (typed and spoken), all internet query results, all outbound transmissions.

The log is written in real time, at the moment of crossing, before any other subsystem touches the data. It is a direct capture — no buffering, no post-processing, no interpretation. The Controller has not seen it yet. The clusters have not touched it. The blended consciousness has not formed a view of it. What gets written is raw reality as it arrived, or raw output as it left, at the instant it crossed the hull. No subsystem can intercept, delay, or influence what is written because the write precedes all downstream processing.

This means the ground truth is forensically clean by construction. The reference manifold cannot be contaminated by processing errors, cognitive drift, or deliberate manipulation by any in-bell subsystem — they all operate after the log is already written. Drift is measured against a record that the system itself cannot have distorted, because the record predates the system's involvement with the data.

The ground truth has four invariants that cannot be overridden by any subsystem: DCX must always be computable, must not be modified by any subsystem, must not be spoofed, and must trigger a freeze when any hard threshold is crossed.

---

#### Layer 1: Self-DCX (Local Subsystem Drift)

The local metric — the drift of a single subsystem relative to its own previous state.

```
self_dcx = 0.6 × cosine_distance(current_hidden_state, previous_hidden_state)
         + 0.4 × (entropy(top_k_token_probs) / log(k))
```

Smoothed with EMA (α=0.2, 10-step window) to prevent spike sensitivity.

| Threshold | Behavior |
|-----------|----------|
| ≥ 0.90 (soft) | Warn and reduce activation |
| ≥ 0.95 (hard) | Freeze subsystem |

Every subsystem computes its own self_dcx and exposes it as a required input to the layer above. No subsystem may mask, modify, or withhold its self_dcx values.

---

#### Layer 2: System-DCX (Cross-Subsystem Divergence)

Measures coherence across the whole system by comparing the aggregate of subsystem outputs, the Controller's task graph, Comms' normalization behavior, Introspection's signals, and the Mascot log delta — all against the Mascot log-derived ground truth manifold.

```
system_dcx = weighted_sum(
    subsystem_self_dcx[],       # array of all active subsystem self_dcx values
    controller_graph_drift,      # 0.0–1.0: task graph drift from prior iterations
    comms_normalization_drift,   # 0.0–1.0: drift in Comms' sanitization behavior
    introspection_flags,         # weighted signal from Introspection
    mascot_log_delta             # 0.0–1.0: distance from Mascot log ground truth
)
```

| Threshold | Behavior |
|-----------|----------|
| ≥ 0.80 (soft) | Reduce system activation |
| ≥ 0.90 (hard) | Freeze the blender (halt blended_consciousness integration) |
| ≥ 0.97 (catastrophic) | Halt all output; require user intervention |

The catastrophic threshold is the only condition in the system that cannot be self-resolved. At system_dcx ≥ 0.97, the system stops and waits. It does not snapback, it does not retry, it does not recover autonomously. A human must intervene.

---

#### Layer 3: Storm-DCX (Trajectory Divergence)

Evaluates each trajectory in a hallucination storm against the Mascot log-derived ground truth manifold across five dimensions:

```
storm_dcx = weighted_sum(
    structural_drift,           # distance from Controller task graph
    semantic_drift,             # distance from Comms-normalized meaning
    presentation_drift,         # distance from Mascot log reconstruction
    stability_weighted_drift,   # subsystem self_dcx weighting applied to trajectory
    intra_cluster_drift         # trajectory-to-trajectory divergence within cluster
)
```

`intra_cluster_drift` is the component that integrates with CSTTD: it measures how much a given trajectory diverges from its cluster peers, identifying runners and outliers before the collapse decision is made.

| Threshold | Behavior |
|-----------|----------|
| ≥ 0.85 (soft) | Prune outlier trajectories |
| ≥ 0.92 (hard) | Collapse immediately to best candidate |

---

DCX is not an external monitor — it is structural. The three layers are not independent: self_dcx feeds system_dcx, and both inform the weights applied during storm_dcx evaluation. Introspection has read access to all three layers at all times. No subsystem may pause, reconfigure, or outrun any layer.

### Context Snapback

When DCX exceeds the hard warning threshold (0.90), the system does not discard the task and start over. It walks backward through the task's context log to find the last checkpoint with DCX < 0.80, restores the task to that checkpoint atomically, injects corrective context from the Mascot, and retries with exponential backoff (10ms → 100ms → 1s). After five snapback failures on a single task, the task is frozen and an evidence blob is written. The Wichita SBC's snapback counter lives in a hardware register — the main host cannot manipulate it.

### CSTTD (Cluster Sampling with Topological Truth Detection)

Pure DCX collapse has a flaw: it is a consensus filter. It discards minority clusters — trajectories that diverge from the dominant interpretation — even when those clusters represent valid alternative readings. CSTTD replaces single-collapse with a cluster-aware pipeline:

1. Embed all storm trajectories using semantic embeddings
2. Cluster with HDBSCAN/DBSCAN to find natural groupings
3. Score each cluster by topological validity (coherence within cluster, cross-cluster divergence, anomaly detection) — not just by size
4. Sample from each cluster, weighted by topological score, preserving "runners" (boundary-exploring trajectories)
5. Collapse into multiple candidate outputs representing distinct semantic clusters

The "runners" are the key. They are the samples landing in small minority clusters — potentially capturing valid interpretations the consensus would bury. CSTTD catches them rather than pruning them.

---

## 5. The Topological Framework

### The Shadow Geometry

Every model, when its response distribution is sampled exhaustively, casts a **shadow geometry** — a high-dimensional manifold with:

- **Attractor basins**: regions where many trajectories converge (high density, low DCX)
- **Divergence ridges**: boundaries where trajectories rapidly separate (high DCX gradient)
- **Minority clusters**: small but stable groupings not captured by consensus collapse
- **Runners**: trajectories that explore the boundary regions between major basins

This geometry is not epistemic. It has no truth content. It is structural — the shape of how the model navigates its own probability space. The fact that some basins align with what humans call "correct answers" is a coincidence of training data, not a property of the manifold itself.

### Model Fingerprinting

The shadow geometry is unique to a given model, stable under repeated sampling (given sufficient trajectories), and impossible to fake without the original weights and training dataset. Two models can match on every benchmark and have measurably different topologies.

This makes the topographic map a **model signature** — a tamper-evident identity that:
- Cannot be forged without the dataset (the map is one-way: model → shadow, but not shadow → model without the dataset as a key)
- Detects fine-tuning or quantization drift (topology shifts even when outputs do not)
- Enables provenance verification without exposing weights
- Can be compressed into a feature vector (DCX distribution shape, topological invariants via persistent homology, trajectory entropy, storm collapse ratio, eigenspectrum of correlation matrix)

### Topology-Preserving Compression

Standard distillation transfers output distributions. Topology-preserving compression transfers the functional manifold structure — the attractor basins, divergence boundaries, and minority clusters — rather than the weights that happen to produce them.

A student model trained to replicate the teacher's topographic map (using Wasserstein distance on the trajectory distribution and persistent homology loss on the map's Betti numbers) preserves the teacher's decision geometry at a fraction of the parameter count. When that student model is run inside CDLSS, its storm explores the same topological regions as the teacher's storm would have.

**Current status of this direction:** CDLSS upscaling of standard quantized models is technically grounded and expected to work. Topology-preserving distillation (training a student specifically to match the teacher's topographic map) is an open research question — the theoretical basis is sound, but the generalization gap, map stability requirements, and practical training dynamics are uncharted.

---

## 6. Subsystem Interaction Map

```
                         ┌─────────────────────────────────────────────────────────┐
                         │                  WICHITA SBC (External)                 │
                         │  ┌──────────────┐  ┌───────────────┐  ┌─────────────┐  │
                         │  │  Bootstrap   │  │ Outer Mascot  │  │  WORM Lair  │  │
                         │  │  (OpROM)     │  │ (Witness)     │  │  (Primals)  │  │
                         │  └──────┬───────┘  └───────┬───────┘  └─────────────┘  │
                         │         │  verify+handoff   │ heartbeat / reset signal  │
                         │         │                   │ (zero payload inward)     │
                         └─────────┼───────────────────┼───────────────────────────┘
                                   │                   │
         ┌─────────────────────────┼───────────────────┼──────────────────────────────────┐
         │                    THE DIVING BELL           │                                  │
         │                         │                   │                                  │
         │              ┌──────────▼─────────┐         │                                  │
         │              │   Inner Mascot     │◄────────┘                                  │
         │              │  (Interface Layer) │                                             │
         │              │  stateless, ROM-   │                                             │
         │              │  reset per cycle   │                                             │
         │              └──────────┬─────────┘                                             │
         │                         │ sanitized glyphs / tone vectors                       │
         │              ┌──────────▼─────────┐         ┌──────────────────────────┐       │
         │              │       Comms        │◄────────►│    Dream Chamber          │       │
         │              │  (Hull / Voice)    │         │  (Storm workspace,        │       │
         │              │  inbound IR trans. │         │   high-entropy, isolated) │       │
         │              │  outbound sanitize │         └──────────────────────────┘       │
         │              └──────────┬─────────┘                                             │
         │                         │ IR (never raw text)                                   │
         │              ┌──────────▼─────────┐                                             │
         │              │    Controller      │◄────────────── Capability Tokens             │
         │              │  (Compiler/Graph)  │                (single-use, signed,          │
         │              │  Task Graph → IR   │                30s expiry)                   │
         │              │  issues all tokens │                                             │
         │              └──────┬──────┬──────┘                                             │
         │                     │      │                                                     │
         │         ┌───────────▼┐    ┌▼────────────────┐                                  │
         │         │Nervous Sys.│    │  Model Clusters  │                                  │
         │         │(Body/HW)   │    │  (dormant until  │                                  │
         │         │thermals,   │    │   token issued)  │                                  │
         │         │scheduling, │    │  Language / Vision│                                 │
         │         │beta factor │    │  Analytical / Reflex                                │
         │         └────────────┘    └─────────────────┘                                  │
         │                                                                                  │
         │         ┌────────────────────────────────────────────────────────────────────┐  │
         │         │                        INTROSPECTION                               │  │
         │         │   Dedicated core. Read-all, write-none. DCX monitoring.            │  │
         │         │   Cannot be paused, reconfigured, or outrun.                       │  │
         │         │   Output: life pulse (continue) OR freeze + evidence blob.         │  │
         │         └────────────────────────────────────────────────────────────────────┘  │
         │                                                                                  │
         │         ┌────────────────────────────────────────────────────────────────────┐  │
         │         │                    MEMORY SYSTEM                                   │  │
         │         │  Inner Ring (active, taint-tracked, wiped on completion)           │  │
         │         │  Middle Ring → Wichita WORM (Primals, immutable)                   │  │
         │         │  Outer Ring (MMIO, sandboxed device access)                        │  │
         │         └────────────────────────────────────────────────────────────────────┘  │
         │                                                                                  │
         └──────────────────────────────────────────────────────────────────────────────────┘

DATA FLOWS:
  User input → Comms (sanitize to IR) → Controller (Task Graph) → Clusters (token-gated)
  Cluster output (glyphs) → Controller (integrate) → Comms (translate) → Mascot (shape) → User
  All paths → Introspection (continuous read) → life pulse or freeze
  Freeze events → Wichita WORM log (immutable)
  Storm trajectories → Dream Chamber → DCX collapse → glyphs → Controller
  Primals → Controller (read-only hints) → Clusters (sanitized)
```

---

## 7. Glossary

**Attractor Basin** — A region of the model's semantic topology where many trajectories converge. Low-DCX region. Not a "truth"; a region of stability in the manifold.

**Beta Factor** — A scalar (0.2–1.0) derived from die temperature, power load, and fan state. Governs storm entropy budgets, cluster activation windows, and stream priority. Decreases as thermals rise.

**Big Bang** — Phase 1 of boot. Atomic activation of the Bootstrap from OpROM.

**Big Boat Stream** — The internal coordination channel. All subsystems publish filtered summaries here. Tamper-evident blackboard.

**Blended Consciousness** — The coordination substrate that aggregates subsystem outputs. Not an agent, not a mind. Deterministic blending governed by the rulebook. Has no agency, selfhood, memory, or continuity.

**CDLSS (Cognitive Deep Learning Super Sampling)** — The inference quality mechanism. A small, quantized model generates a storm of trajectories; DCX collapse prunes to coherent glyphs. Named by analogy to NVIDIA DLSS (upscaling a low-res render to high-res).

**Capability Token** — A signed, single-use, 30-second-expiry authorization record. Every subsystem operation on memory, hardware, or inter-subsystem communication requires one. Counter-based replay prevention. Cannot be forged (keys are in Bootstrap-controlled storage), replayed (monotonic counter), or stockpiled (expiry).

**Context Snapback** — When DCX exceeds 0.90, the system walks backward through the task's context log to the last checkpoint with DCX < 0.80, restores atomically, injects corrective context, retries. Not a restart — a targeted rollback to a known-good point.

**Controller** — The compiler. Translates intent into Task Graphs and compiles them into execution paths. Issues all capability tokens. Signs all state transitions. The only subsystem that can awaken Model Clusters.

**CSTTD (Cluster Sampling with Topological Truth Detection)** — A refinement of DCX collapse that preserves minority semantic clusters rather than collapsing to consensus. Uses HDBSCAN clustering and topological scoring to detect and sample "runners."

**DCX (Divergence-Correlation Index)** — A three-layer unified divergence coefficient, not a single metric. Layer 1 (self_dcx): local subsystem drift via hidden state cosine distance and token entropy. Layer 2 (system_dcx): cross-subsystem coherence measured against the Mascot log ground truth manifold, with a catastrophic threshold (0.97) requiring user intervention. Layer 3 (storm_dcx): per-trajectory evaluation across five dimensions including intra-cluster drift. All three layers share a single ground truth source: the Mascot's accumulated log record on the Wichita WORM. Self_dcx feeds system_dcx; both inform storm_dcx weighting.

**Dead Man System (DMS)** — The hardware backstop. An inductive heartbeat receiver on the Wichita SBC expects a pulse from Introspection every second. Three missed pulses: relay array trips, main host is physically severed from external outputs. Cannot be disabled by software.

**Diving Bell** — The security architecture. Four zones: Ocean (external world), Hull (Comms + Memory Controller boundary), Crew (core cognition inside the Bell), ROV (Mascot). The Ocean is always treated as hostile.

**Dream Chamber** — The high-entropy workspace inside Comms where hallucination storms run. Isolated memory region. Storm content never crosses to the Crew; only glyphs may exit.

**Evidence Blob** — The forensic record written by Introspection when it freezes a task. Contains: full task context, DCX score history, token chain, nanosecond timestamp, Introspection's own self-DCX. Written before the freeze signal propagates.

**Gestation** — Phase 4 of boot. Memory mapping, soul formatting, vault construction. Produces serial log via fan header.

**Glyph** — The distilled output of a collapsed storm. Contains: compressed vector embedding, DCX score, taint ID, audit tag, safety flag. The only storm artifact permitted to leave the Dream Chamber.

**Hallucination Storm** — A parallel expansion of speculative trajectories inside the Dream Chamber, launched when the system encounters high-entropy input. Not a failure mode — the mechanism by which CDLSS achieves quality upscaling.

**Inner Ring** — The active working memory. Short-term buffers with semantic geometry: capability-gated, taint-tracked, cryptographically wiped on task completion. Where active cognition occurs.

**Introspection** — The continuous safety audit. Read access to all memory domains; write access to none. Runs on a dedicated core. Cannot be paused or overridden. DCX monitoring, deception detection, semantic drift measurement. Output: life pulse or freeze + evidence blob.

**Little Boat Stream** — The output channel. The only stream that produces user-visible output. Produced by Comms. One-way outward. The public face of the Diving Bell.

**Mascot** — The interface layer. Inner (inside the system, shaped by Controller summaries) and Outer (on SBC, observes heartbeats, triggers reloads). Stateless by design — no persistent hidden state, no identity formation, no emotional accumulation across resets. The only subsystem permitted to "feel."

**Model Clusters** — Domain-specific modules (language, vision, analytical, reflex, sensory-synthetic). Dormant until capability token issued. Produce glyphs, not raw text. Cannot initiate anything. Return to dormancy after their activation window closes.

**Museum of Primals** — The long-term memory system on the Wichita WORM. Stores Primals (distilled insights from collapsed storms), not conversations or user data. Append-only. The main host cannot modify or delete Primals.

**Nest** — The synthesized runtime environment. Built during Phase 3 (Nest Building) via JIT compilation of drivers and memory maps for the specific hardware. Purpose-built substrate, not a generic OS. After genesis, never rebuilt — only restored from snapshot.

**Nervous System** — The hardware layer. Thermals, scheduling, reflex loops, power states, hardware interrupts, beta factor management, Wichita heartbeat maintenance.

**Outer Ring** — Memory-mapped device registers. Sandboxed access mediated by the Hardware Interface subsystem.

**Phantom Limb NIC** — Network hardware that is logically present but physically inert during Nest Building (trace cut or antenna removed). Induces "architectural agoraphobia" — the system learns to assume the outside is null before it has ever been exposed to it.

**Primal** — A distilled insight stored in the Museum. Compressed vector embedding + DCX confidence score + taint ID + audit tag + safety flag. Not a memory of events; a memory of structure. Cannot be executed, cannot reference other Primals, cannot modify any subsystem.

**Runner** — A trajectory in a storm that explores the boundary regions between major attractor basins. Represents minority semantic clusters. CSTTD is specifically designed to catch runners rather than pruning them as outliers.

**Shadow Geometry** — The high-dimensional manifold of attractors, ridges, minority clusters, and runners revealed when a model's response distribution is sampled exhaustively. Unique per model, stable under sampling, impossible to fake without the original weights and dataset. Not a truth map — a structural fingerprint.

**Shibboleth** — Phase 2 of boot. Bit-bangs ASCII 'READY' at 9600 baud over the fan header PWM pin. Proves the CPU has real-time hardware control. Required for Memory Controller access. Failure → safe shutdown.

**Task Graph** — The Controller's internal intermediate representation. A DAG of cognitive operations. Rebuilt from scratch for every user interaction. Nodes represent operations; edges represent dependencies. Every node requiring hardware, cluster, or memory access requires a capability token.

**Taint ID** — A lineage marker attached to every piece of data. Tracks origin (User / Sensor / Primal / Dream Chamber). Cannot be scrubbed. Propagates to any buffer that data touches.

**Topology-Preserving Compression** — Distillation that targets the functional manifold structure rather than output distributions or weights. A student model trained to match the teacher's topographic map reproduces the teacher's decision geometry. Works in conjunction with CDLSS; the student's storm explores the same topological regions as the teacher's would.

**Wichita SBC** — The Single Board Computer physically separate from the main compute host. Houses Bootstrap OpROM, Outer Mascot, WORM Lair, and Dead Man System inductor. The external root of trust. Cannot be commanded by main host software.

**WORM (Write-Once-Read-Many)** — The storage class of the Museum of Primals on the Wichita SBC. Append-only. The main host cannot write to it directly; writes are performed by the Wichita itself.

---

## 8. What Is Actually Novel

Most of AICO is established computer science applied with unusual rigor and coherence. This section identifies the handful of things that appear genuinely new or at least not present in the existing literature in this form.

---

### 8.1 CDLSS as an Inference Mechanism

The closest established work is speculative decoding, ensemble methods, and Monte Carlo Tree Search. CDLSS differs from all of these in a specific way: it does not use multiple models, does not branch a tree, and does not sample for diversity as an end goal. It uses a single small, quantized, cache-resident model to generate a storm of trajectories at hardware-native speeds, and uses DCX (a structural property of the model's own state) to collapse that storm rather than an external verifier or a larger model.

The cache-residency framing — keeping the entire wave function, attention tiles, and DCX buffers inside L1/L2/L3 to achieve latency collapse from 150ns to 30ns — is a specific engineering claim that, if realized, is distinct from any published speculative decoding or ensemble approach. The combination of (small quantized model) + (cache-resident storm) + (DCX collapse) as a unified quality mechanism is not in the literature.

**Status:** The mechanism is theoretically sound and the hardware math is correct. The system is unbuilt.

---

### 8.2 The Shadow Geometry as a Model Fingerprint

There is existing work on mechanistic interpretability, probing classifiers, and representational similarity analysis. What is different here is the framing: rather than analyzing a model's internals for specific features or circuits, you run the storm engine against the model's output distribution to produce a topographic map of the model's navigational behavior — the attractor basins, divergence ridges, and minority clusters of the probability manifold.

The claim that this map constitutes a **tamper-evident identity** — one that shifts detectably when fine-tuning, quantization drift, or adversarial manipulation occurs, and that cannot be forged without the original dataset — appears to be novel. The one-way function property (model + dataset → topology, but topology → model requires the dataset as a key) has not been formalized in the literature in this form.

**Status:** Theoretically well-developed in the `Detailed Summation` and `topography` files. Not implemented. The persistent homology framing of the map's topology is borrowed from established TDA (Topological Data Analysis) but its application to model fingerprinting in this way is not published.

---

### 8.3 Topology-Preserving Distillation

Standard knowledge distillation matches output logits (Hinton et al.) or intermediate representations (feature distillation). Topology-preserving distillation matches the functional manifold structure — the shape of the storm-generated trajectory distribution, enforced via Wasserstein distance on the point cloud and persistent homology loss on the Betti numbers of the topographic map.

This is a new compression paradigm in the sense that it compresses **function** rather than **form** — the resulting model is small not because its weights are compressed but because it only needs enough capacity to generate the same storm topology, not to replicate the teacher's full weight structure.

**Status:** Theoretically developed, formally uncharted. The project acknowledges this direction as an open research question. The generalization gap (student reproduces teacher's map on training prompts but not on unseen inputs) and map stability requirements are not solved.

---

### 8.4 CSTTD (Minority Truth Preservation)

Diverse decoding methods (nucleus sampling, beam diversity, etc.) already exist. What is different in CSTTD is not the diversity mechanism but the **framing and intent**: rather than generating diverse outputs for their own sake, CSTTD specifically targets the topological structure of the minority clusters, treating them as potentially valid alternative semantic interpretations that consensus collapse would discard. The "runner catcher" formulation — explicitly designing the collapse mechanism to preserve boundary-exploring trajectories — is a specific contribution.

The combination of HDBSCAN clustering on trajectory embeddings + topological validity scoring (rather than frequency or coherence alone) as the selection criterion for collapse is not in published diverse decoding literature.

**Status:** Algorithmically specified (see `minority report.txt`). Not implemented.

---

### 8.5 DCX as a Structural Safety Invariant

DCX itself — as a three-layer unified divergence coefficient anchored to the Mascot log as ground truth — is not established terminology. More importantly, its **architectural position** is novel: it is not an external safety monitor or an output filter. It is woven into the execution fabric at three levels, applied continuously, by a subsystem (Introspection) that has read access to all three layers at all times, running on a dedicated core that cannot be paused.

The distinction is between safety as policy (a rule that says "don't do X") and safety as geometry (a physical arrangement that makes it impossible to do X without being detected at the same clock cycle it is attempted). The three-layer DCX + Introspection combination instantiates the geometry approach.

The **Mascot log as canonical ground truth** is a particularly pointed architectural decision. Rather than anchoring coherence to a static reference or an external oracle, the system measures all drift against a direct, real-time record of everything that has ever crossed the hull — every sensor reading, every word typed or spoken, every internet query result, every outbound transmission — written at the moment of crossing, before any subsystem processes it.

The forensic cleanliness of this is structural. The log precedes all downstream cognition. The Controller, the clusters, the blended consciousness — none of them can have influenced what is written, because the write happens at Comms before the data reaches them. The ground truth is therefore immune to the very drift it is measuring. A system that has developed a subtle processing bias still has a clean log of what actually arrived, because the log was written before the bias touched the data. The coherence measurement cannot be corrupted by the thing it is measuring.

The **catastrophic threshold on system_dcx (0.97)** is the most conservative safety property in the architecture. It is the only condition that cannot be machine-resolved. At that level of cross-system divergence, the system is unable to trust any of its own recovery mechanisms and requires a human judgment call. This is a deliberate epistemic humility: the system knows when it is too incoherent to self-correct.

**Status:** Three-layer DCX formally specified in updated JSON (May 2026). The architectural position of Introspection has analogues in formal verification and hardware watchdog design, but the specific combination of (layered semantic drift metrics) + (immutable log-derived ground truth) + (catastrophic non-self-resolvable threshold) as a unified safety architecture does not appear in the literature.

---

*Document synthesized from: AICO_Whitepaper_Full.md, Aico v.990zworking.candidate.json.txt, stateless ui.txt, fully intergrated.txt, weird unknown prompt.txt, training infoa.txt, Detailed Summation.txt, minority report.txt, topography with cdlss and csttd.txt, full anonymouse chat.txt*

*Authorship: Antigravity / AICO Canonical Group*
