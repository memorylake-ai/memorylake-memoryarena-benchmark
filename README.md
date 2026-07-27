# MemoryArena Benchmark with MemoryLake

Companion release for ***Workload-Dependent Returns to Memory Representation Structure: A
Controlled Study on MemoryArena*** — evaluation settings, task-sampling manifests, and
protocol documentation for a controlled comparison of four agent memory systems across all
five MemoryArena task domains.

## Why this study

First-generation memory benchmarks define memory as *post-hoc recall of past conversation or
text* and rank systems by question-answering accuracy. As mainstream systems approach
saturation on those benchmarks, both their discriminative power and their external validity
have come into question: **being able to remember is not the same as being able to use
memory to get things done.**

[MemoryArena](https://arxiv.org/abs/2602.16313) addresses this with a
**Memory–Agent–Environment closed loop**: each task instance is an ordered sequence of
*interdependent* subtasks, so knowledge acquired early must be written to memory and
correctly retrieved later — otherwise the later subtasks are informationally
under-specified. Its protocol reports a **Process Score (PS)** for subtask-level completion
and a **Success Rate (SR)** for whether the task's actual goal was reached.

This project asks what those two measures are usually assumed to answer together: **across
task domains, when does a memory representation's process-level completeness predict its
practical outcome, and when does it not?** We answer it with a **single-variable controlled
comparison** — one agent framework, one base model, one batch of task samples, one scoring
protocol, with the **memory layer as the only experimental variable**:

- **MemoryLake** — structured multi-track memory (confirmed conclusions, supporting
  evidence, reusable skills, each under a different presence policy)
- **Mem0** — extractive fact memory
- **text-embedding-3-small** — naive vector-chunk RAG
- **Long Context** — no memory system; the full trajectory flattened verbatim into the
  prompt, as a zero-abstraction, full-fidelity control

## Headline findings

- **Structured multi-track memory attains the best result on the primary metric of four of
  the five tasks**, with its advantage largest on workloads with recognizable structure.
- Its largest success-rate gain appears where dependency chains are short and reuse must be
  exact — **physics reasoning: SR 60.0% vs 45.0%** for the runner-up long-context baseline.
- **PS and SR do not always move together.** On progressive multi-hop retrieval the
  process-level gap among memory-augmented systems is small (**PS 8.9% vs 7.2% and 7.8%**)
  while final-success differences are large (**SR 23.5% vs 12.5% and 0%**). A small
  process-level gap can hide a much larger gap in final success — the reverse of what a
  process-level comparison alone would suggest.
- **The clear exception is group travel planning**, a workload dominated by high-volume,
  homogeneous verbatim replay, where full verbatim context outperforms every memory
  representation.

Together: **memory representation structure should be matched to the structure of the
workload it serves, and that match should be validated against task outcomes (SR) rather
than process-level completeness (PS) alone.**

## Documentation

- [`docs/method.md`](docs/method.md) — how MemoryLake is organized, and how its
  representation differs from the baselines.
- [`docs/evaluation_settings.md`](docs/evaluation_settings.md) — base model, per-task
  datasets and evaluated scale, metric definitions, and scoring procedure.
- [`docs/queries/`](docs/queries/) — the exact items evaluated in each task.

This repository documents the *evaluation*; the MemoryLake implementation is not included
(see the disclosure scope in [`docs/method.md`](docs/method.md)).

## Reproducibility notes on MemoryArena v1

Three issues confirmed during reproduction affect how the original benchmark paper
(arXiv:2602.16313v1) should be cited:

1. Its base model "GPT-5.1-mini" does not exist in the OpenAI API; we use `gpt-5-mini`, so
   our absolute scores are not directly comparable to its results table.
2. The progressive decomposition count measured in the dataset is **221**, not the 256 cited.
3. On the 20-query multi-hop subset, the reported numbers could not be reproduced with the
   benchmark's public evaluation method, and no reproducible sampling list is provided.

None of these affect the relative comparison among our four systems, which share identical
measured data and protocol.

## Citation

```bibtex
@article{zhan2026workload,
  title={Workload-Dependent Returns to Memory Representation Structure:
         A Controlled Study on MemoryArena},
  author={Zhan, Chaoqun and Zhou, Qiang and Li, Guannan and Wang, Qianjin},
  note={MemoryLake Team},
  year={2026}
}

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
