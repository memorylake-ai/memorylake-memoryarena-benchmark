# MemoryLake — Method Overview

**MemoryLake** is a structured **multi-track** memory system. It connects through
MemoryArena's standard memory-service interface and uses **one generic configuration
across all five tasks, with no task-specific adaptation**. The interface has two calls:

- `add_chunk(chunk)` — writes each completed subtask's trajectory and outcome to memory;
- `wrap_user_prompt(question)` — returns the retrieved memory context for each new
  subtask, prepended to the question as the agent's input.

Memory is isolated per instance: each task instance gets an independent `user_id` and is
reset before it starts.

## Design principle: presence policies matched to workload heterogeneity

MemoryLake is organized around a single design principle: **memory content of different
natures should follow different presence policies.** At the representation level, three
tracks coexist:

1. **Confirmed conclusions** of completed subtasks are maintained as an ordered record and
   made **deterministically present** at every subsequent subtask, bypassing
   retrieval-similarity uncertainty.
2. **Supporting evidence** from prior trajectories — both declarative findings and
   procedural traces — is stored for **on-demand semantic retrieval**.
3. **Reusable problem-solving experience** (skills) is consolidated for **cross-subtask
   transfer**.

At recall time, the three tracks are assembled into a single **bounded** context under an
overall length budget, with redundant content filtered. On any internal-service failure,
the system degrades to returning empty context and continues — it never blocks the agent.

The design hypothesis: confirmed conclusions must be unconditionally present, procedural
evidence should be retrieved on demand, and transferable skills should be reused across
subtasks — a single representation (pure fact entries or pure chunks) cannot structurally
satisfy all three.

## Representation differences from the baselines

| System | Memory representation | Recall mechanism |
|--------|-----------------------|------------------|
| Long Context | None (verbatim trajectory flattened into the context) | No retrieval; everything unconditionally present |
| Mem0 | Extractive fact entries | Similar-fact recall |
| text-embedding-3-small | Raw trajectory chunks (vectors) | Similar-chunk recall |
| **MemoryLake** | Multi-track: confirmed conclusions, supporting evidence, reusable skills | Deterministic conclusion presence + on-demand retrieval + skill reuse, within a bounded assembly |

## Disclosure scope

This description is deliberately at the **representation and policy level**. Implementation
specifics — storage layout, indexing and consolidation mechanisms, assembly heuristics —
are proprietary and omitted. This does not affect interpretability of the evaluation: the
interface, task protocols, metrics, and denominators are fully specified in
[`evaluation_settings.md`](evaluation_settings.md), and all systems are scored by the
benchmark's official scripts.

> This directory documents evaluation settings and method only; the MemoryLake
> implementation is not included.
