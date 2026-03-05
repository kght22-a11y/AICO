AICO: LLM Parsing Master Guide
Project Overview

AICO (Self-Assembling Unikernel AI, SAU-AI) is a constitutional AI system that compiles itself from a JSON specification (the Rulebook) at boot time. It is executable, verifiable, and fully specified.

Important principle:

Rulebook defines WHAT the system must do.

Controller determines HOW to implement.

Supplemental training guides models but cannot contradict the rulebook.

Three Core Parts

Rulebook (JSON)

AICO_FINAL_ARCHITECTED.json

Immutable, ~3.5k lines now, target ~50k lines.

Specifies limits, prohibitions, governance, safety invariants.

Controller reads & enforces; never modifies.

Models & Training

Hallucination storms, parallel cognition transformer, interruption handling.

Training info is supplemental: teaches the Controller patterns, real hardware behaviors, and recovery strategies.

Must respect Rulebook constraints.

Substrate / Base Inference Engine

Minimal CPU-only runtime at boot.

Responsible for:

Parsing Rulebook

Compiling drivers

Orchestrating subsystems (nervous system, mascot, comms, introspection)

After nest building → Controller compiles full inference engine, which loads the complete AICO system.

Boot Flow & Post-Nest Handling

Bare-metal boot → CPU cores active, no GPU or NIC.

Boot-time inference engine → drivers compiled, safety checks performed.

Nest building → Controller uses boot engine to build full inference engine.

Post-nest sleep / physical inspection → NIC fixed; on resume, comms subsystem manages NIC without Controller awareness of the internet.

Subsystems & Roles
Subsystem	Role	Notes
Controller	Bi-directional universal compiler	Compiles drivers, builds inference engine, enforces rulebook
Introspection	Safety monitor	Audits graphs before compilation, enforces constraints
Nervous System	Real-time scheduler	Low-latency loops, thermal-aware resource allocation
Mascot (dual)	External memory/provenance manager	Inner mascot on device, outer mascot on SBC ensures inner mascot uptime and resets
Comms	Hallucination & communication	Filters all external interactions through DCX pipeline

Mascot Duty Example:

Inner mascot: on device/ROV, outside firewall (“diving bell”)

Outer mascot: on SBC, ensures inner mascot is running and resets from immutable ROM on a periodic/mildly random schedule.

Streams & Real-time Operations

controller_stream, introspection_stream, nervous_system_stream, comms_stream

Handles parallel input, interruptions, latency constraints, and context integration

Thermal-aware execution; sustained targets 70–80°C, emergency cutoff 90°C

Provenance logging via immutable WORM / Merkle chain; shadow logs accessed subconsciously by Introspection

Safety & Architecture Principles

3-Upgrade Rule: Draft → Refine → Polish → LOCK

Shibboleth Test: PWM fan header verification before granting memory controller access

Phantom Limb: Network hardware logically enabled but physically disabled during nest building

Context Snapback: Amnesia-based correction for hallucinations

Emergency Mode: Temporary thermal override with mandatory logging

Rulebook vs Implementation:

Rulebook = constraints, prohibitions, requirements

Implementation = learned by Controller; may optimize within rulebook boundaries

Development Guidelines

Define WHAT cannot be violated, not how to implement

Include: boundaries, prohibitions, requirements, failure modes

Exclude: implementation details, algorithms, optimization strategies

Every rule must be verifiable by Introspection

Training Strategy

Start with synthetic bootstrap – teaches parsing and execution of Rulebook

Fine-tune on real hardware – patterns, device quirks, latency

Deploy with aggressive barriers for unknown subsystems; learn incrementally

Testing & Evaluation

Real hardware essential

Simulations alone insufficient due to thermal & timing constraints

Metrics: interruption recovery, parallel processing efficiency, context integration, latency adherence

LLM Parsing Recommendations

Rulebook = ground truth; supplemental files must never contradict it

Parse all JSON entries to understand subsystem responsibilities

Treat boot-time inference engine as scaffold; full inference engine is built by Controller at nest completion

Mascot duality and streams provide real-time guarantees and safety enforcement