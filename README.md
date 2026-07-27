# MemoryArena Benchmark with MemoryLake

Companion release for ***Workload-Dependent Returns to Memory Representation Structure: A
Controlled Study on MemoryArena*** — evaluation settings, task-sampling manifests, and
protocol documentation for a controlled, memory-layer-only comparison of four agent memory
systems across all five MemoryArena task domains.

## Overview

How memory is evaluated in language-model agents is changing. First-generation memory
benchmarks define memory as *post-hoc recall of past conversation or text* and rank systems
by question-answering accuracy. As mainstream systems approach saturation on those
benchmarks, both their discriminative power and their external validity have come into
question: **being able to remember is not the same as being able to use memory to get
things done.**

[MemoryArena](https://arxiv.org/abs/2602.16313) addresses this with a
**Memory–Agent–Environment closed loop**: each task instance is an ordered sequence of
*interdependent* subtasks, and the agent must write conclusions, constraints, and
experience acquired in early subtasks into memory, then retrieve and apply them correctly
in later subtasks — otherwise the later subtasks are informationally under-specified. The
protocol reports two measures per task: a **Process Score (PS)**, capturing subtask-level
completion, and a **Success Rate (SR)**, capturing whether the task's actual goal was
reached.

This project asks a question those two measures are usually assumed to answer together:
**across task domains, when does a memory representation's process-level completeness
predict its practical outcome, and when does it not?** To answer it, we run a
**single-variable controlled comparison** — one agent framework, one base model, one batch
of task samples, one scoring protocol, with the **memory layer as the only experimental
variable**.

## Systems compared

| System | Memory representation | Recall mechanism |
|--------|-----------------------|------------------|
| **MemoryLake** | Structured multi-track: confirmed conclusions, supporting evidence, reusable skills | Deterministic conclusion presence + on-demand retrieval + skill reuse, within a bounded assembly |
| Mem0 | Extractive fact entries | Similar-fact recall |
| text-embedding-3-small | Raw trajectory chunks (vectors) | Similar-chunk recall |
| Long Context | None — verbatim trajectory flattened into the prompt | No retrieval; everything unconditionally present |

**MemoryLake** is organized around one design principle: *memory content of different
natures should follow different presence policies* — confirmed conclusions must be
unconditionally present, procedural evidence should be retrieved on demand, and
transferable skills should be reused across subtasks. See
[`docs/method.md`](docs/method.md).

The **Long Context** configuration is a deliberate zero-abstraction, full-fidelity control:
it bounds what any memory representation must beat to justify abstracting at all.

## Task domains

The five MemoryArena domains cover four qualitatively different **memory workloads**, so a
representation can be probed from several angles:

| Domain | Memory workload it probes |
|--------|---------------------------|
| Formal reasoning — math / physics | Procedural knowledge reuse; exact reuse of specific intermediate results along a dependency chain |
| Group travel planning | Constraint tracking over high-volume, fine-grained, homogeneous slot information |
| Bundled web shopping | Exact state re-reference (ASIN compatibility chains across sequential purchases) |
| Progressive multi-hop retrieval | Intermediate-finding aggregation into one final decision over a long horizon |

## Protocol

- **One base model** — `gpt-5-mini` for every system's agent and judge.
- **Identical samples and denominators** within each comparison row.
- **Official scoring** — every score is produced by the task's official MemoryArena
  evaluation script, then **recomputed by an independent program from raw result files**
  (zero deviation on deterministic tasks; <1pp on LLM-judged tasks).
- **Full disclosure** of sample sizes and scoring protocols, including the highest-token
  task (multi-hop retrieval) reported at two evaluation scales so the sensitivity of SR
  estimates to sample size is visible rather than hidden.

Exact per-task datasets, evaluated scale, and metric definitions:
[`docs/evaluation_settings.md`](docs/evaluation_settings.md).

## Headline findings

- **Structured multi-track memory attains the best result on the primary metric of four of
  the five tasks**, and its advantage is largest on workloads with recognizable structure.
- Its largest success-rate gain appears where dependency chains are short and reuse must be
  exact — **physics reasoning: SR 60.0% vs 45.0%** for the runner-up long-context baseline
  (math shows a smaller but consistent gap).
- **PS and SR do not always move together.** On progressive multi-hop retrieval the
  process-level gap among the memory-augmented systems is comparatively small (**PS 8.9% vs
  7.2% and 7.8%**), yet final-success differences are large (**SR 23.5% vs 12.5% and 0%**),
  while long context collapses as some trajectories overflow the context window. A small
  process-level gap can hide a much larger gap in final success — the reverse of what a
  process-level comparison alone would suggest.
- **The one clear exception is group travel planning**, a workload dominated by high-volume,
  homogeneous verbatim replay, where full verbatim context outperforms every memory
  representation.

Together these support a simple practical principle: **memory representation structure
should be matched to the structure of the workload it serves, and that match should be
validated against task outcomes (SR) rather than process-level completeness (PS) alone.**

## Repository contents

```
docs/
├── method.md                 MemoryLake method overview (representation & policy level)
├── evaluation_settings.md    Systems, base model, per-task datasets, scale, scoring
└── queries/                  Exact items evaluated per task
    ├── formal_reasoning_math_ids.tsv        40 papers
    ├── formal_reasoning_phys_ids.tsv        20 papers
    ├── travel_query_ids.tsv                 30 groups (fixed-ID subset of 270)
    ├── shopping_task_ids.tsv               150 bundles (scored on the 50-bundle intersection)
    ├── web_search_controlled_20_ids.tsv     20 queries — controlled four-system subset
    └── web_search_memorylake_221_ids.tsv   221 queries — MemoryLake-only robustness check
```

**Scope.** This repository documents the evaluation: interface, task protocols, sampling
lists, metrics, and denominators. The **MemoryLake implementation is not included** — the
system is described at the representation and policy level, while storage layout, indexing
and consolidation mechanisms, and assembly heuristics are proprietary. This does not affect
interpretability of the comparison: all systems are scored by the benchmark's official
scripts, and the paper's claims concern representation-level design — *which content is
present unconditionally versus retrieved on demand* — rather than any implementation detail.

## Reproducibility notes on MemoryArena v1

During reproduction we confirmed several issues in the original benchmark paper
(arXiv:2602.16313v1) that affect how its numbers should be cited. Three bear directly on
this work:

1. The task base model is given as "GPT-5.1-mini", which does not exist in the OpenAI API
   (that generation offers `gpt-5.1` and `gpt-5.1-codex-mini`); we use `gpt-5-mini`, so our
   absolute scores are not directly comparable to the original paper's results table.
2. The progressive decomposition count measured in the HuggingFace dataset is **221**,
   while the paper cites 256.
3. On the 20-query multi-hop subset, the originally reported numbers could not be
   reproduced with the benchmark's public evaluation method, and no reproducible
   query-sampling list or script version is provided.

None of these affect the relative comparison among our four systems — which share identical
measured data and protocol — but they do affect alignment with the original paper's
absolute numbers.

## Citation

```bibtex
@article{zhan2026workload,
  title={Workload-Dependent Returns to Memory Representation Structure:
         A Controlled Study on MemoryArena},
  author={Zhan, Chaoqun and Zhou, Qiang and Li, Guannan and Wang, Qianjin},
  note={MemoryLake Team},
  year={2026}
}
```

The benchmark itself:

```bibtex
@article{he2026memoryarena,
  title={MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Session
         Agentic Tasks},
  author={He, Zexue and others},
  journal={arXiv preprint arXiv:2602.16313},
  year={2026}
}
```

## Contact

MemoryLake Team — `contact@zbyte-inc.com`
