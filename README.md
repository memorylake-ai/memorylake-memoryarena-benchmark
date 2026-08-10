# MemoryArena Benchmark with MemoryLake

Companion release for ***MemoryLake on MemoryArena: A Matched Study of Agent Memory
Backends*** — evaluation settings, task-sampling manifests, and protocol documentation for a
matched system-level comparison of four agent memory backends across all five MemoryArena
task domains.

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
practical outcome, and when does it not?** We answer it with a **matched system-level
comparison** — one agent framework, one base model, one batch of task samples, one scoring
protocol, with the **memory backend as the intentionally changed component**. A backend is not
a single variable: swapping it also changes write policy, retrieval, consolidation, prompt
assembly and fallback behaviour at once, so what is measured is the effect of a complete
backend configuration, not of representation structure in isolation:

- **MemoryLake** — structured multi-track memory (confirmed conclusions, supporting
  evidence, reusable skills, each under a different presence policy) →
  [`docs/method.md`](docs/method.md)
- **Mem0** — extractive fact memory
- **text-embedding-3-small** — naive vector-chunk RAG
- **Long Context** — no memory system; the full trajectory flattened verbatim into the
  prompt, as a zero-abstraction, full-fidelity control

Side-by-side representation and recall mechanisms:
[`docs/method.md` § Representation differences](docs/method.md#representation-differences-from-the-baselines).
Base model, per-task samples, metrics and denominators:
[`docs/evaluation_settings.md`](docs/evaluation_settings.md).

## Headline findings

- **Structured multi-track memory attains the best result on the primary metric of three of
  the five tasks** — both formal-reasoning domains and progressive multi-hop retrieval — and
  its advantage is largest on workloads with recognizable structure.
- Its largest success-rate gain appears where dependency chains are short and reuse must be
  exact — **physics reasoning: SR 60.0% vs 45.0%** for the runner-up long-context baseline.
- **PS and SR do not always move together.** On progressive multi-hop retrieval the
  process-level gap over the strongest baseline is about a point (**PS 6.7% vs 5.6%**) while
  the final-success gap is tenfold larger (**SR 20.0% vs 10.0%**). A small process-level gap
  can hide a much larger gap in final success — the reverse of what a process-level comparison
  alone would suggest.
- **The clear exception is group travel planning**, a workload dominated by high-volume,
  homogeneous verbatim replay, where full verbatim context beats every memory representation
  (**SPS 53.1% vs 43.0%**). Bundled shopping separates no
  system at all: on the 50-bundle subset the top three span 2.7pp (text-embedding 31.0%,
  MemoryLake 30.0%, long context 28.3%) and on the full 150-bundle set they span 0.4pp in a
  different order (long context 30.0%, text-embedding 29.7%, MemoryLake 29.6%) — an ordering
  that flips with the sample is not a finding, and we do not read one from it.

Together: **memory representation structure should be matched to the structure of the
workload it serves, and that match should be validated against task outcomes (SR) rather
than process-level completeness (PS) alone.** The one workload where structure does not pay
off is the replay-dominated one, and the one workload that separates nothing is the one whose
end-to-end objective almost nobody reaches.

The evaluated scale behind each number — the 50-bundle shopping subset and the full 150-bundle
set it is drawn from, the controlled
20-query multi-hop subset and how that subset is drawn — is stated in
[`docs/evaluation_settings.md` § Tasks, datasets and evaluated scale](docs/evaluation_settings.md#tasks-datasets-and-evaluated-scale),
with the exact items in [`eval/queries/`](eval/queries/) and the per-item scores in
[`eval/results/per_item_scores.md`](eval/results/per_item_scores.md).

> **On the multi-hop numbers.** `PS` is quoted on the all-slots denominator, which is the one
> comparable across systems: the benchmark's scorer skips unanswered sub-query slots rather
> than scoring them 0, and slot coverage ranged from 22.5% to 94.4% here. Mem0's multi-hop
> figures (`PS` 1.9%, `SR` 0.0%) are reported for completeness but are **not** a capability
> estimate — it answered only 22.5% of slots and reached the final query on 0 of 20 tasks
> because its cloud API rejects the oversized memory writes the environment issues. See the
> coverage table and reproducibility notes in
> [`docs/evaluation_settings.md`](docs/evaluation_settings.md).

## Documentation

- [`docs/method.md`](docs/method.md) — how MemoryLake is organized, and how its
  representation differs from the baselines.
- [`docs/evaluation_settings.md`](docs/evaluation_settings.md) — base model, per-task
  datasets and evaluated scale, metric definitions, and scoring procedure.
- [`eval/`](eval/) — the items evaluated, the per-item scores, and the multi-hop scoring
  script (the other four tasks are scored by MemoryArena's own code).

This repository documents the *evaluation*; the MemoryLake implementation is not included
(see the disclosure scope in [`docs/method.md`](docs/method.md)).

## Reproducibility notes on MemoryArena v1

Three issues confirmed during reproduction affect how the original benchmark paper
(arXiv:2602.16313v1) should be cited:

1. Its base model "GPT-5.1-mini" does not exist in the OpenAI API; we use `gpt-5-mini`, so
   our absolute scores are not directly comparable to its results table.
2. The progressive decomposition count measured in the dataset is **221**, not the 256 cited.
3. On the 20-query multi-hop subset, the reported numbers could not be reproduced with the
   benchmark's public evaluation method, and no reproducible sampling list is provided. Our own
   subset is drawn by a deterministic rule and can be regenerated offline —
   [`eval/sample_controlled_20.py --verify`](eval/sample_controlled_20.py).

None of these affect the relative comparison among our four systems, which share identical
measured data and protocol.

### Undocumented parameters that change scores

Three settings that materially affect scores are not exposed in any config file, so a run
made from the public code will not reproduce published numbers unless they are set
explicitly. Values below are from MemoryArena v1 at the commit we reproduced.

| Setting | Upstream value | Where it lives | Configurable? |
|---|---|---|---|
| Sub-query search-iteration cap | 30 (default), we set **35** | `max_iterations` in the run config | yes |
| **Final-query search-iteration cap** | **30 — the config value is not applied** | `agent/search.py` default | **no** |
| Agent output-token budget | **15000**, we set **32000** | hard-coded in `agent/search.py` | **no** |

The middle row is a defect rather than a default: `BrowseCompPlusEnvironment.run_subqueries`
passes `max_iterations=self.max_iterations` to the agent, but `run_final_query` omits the
argument, so the final combined query silently falls back to the `agent/search.py` default
of 30 while every sub-query of the same task gets the configured 35. **`SR` is computed
solely from the final query**, so the metric most often quoted is the one measured under the
smaller budget.

Measured effect across our 386 final-query runs: 90 (23%) produced no answer, and **79 of
those 90 stopped at exactly 30 tool calls** — the erroneous cap, not the configured one.
Raising the cap is nevertheless not expected to recover most of them: among runs that *did*
answer, the median used 7 tool calls and only 2 of 297 answered at the cap, so a run that
reaches the cap has almost always stopped converging rather than nearly finished. We
estimate a 1–4pp `SR` effect at n=221 and recommend fixing it to remove the confound, not
because it unlocks many answers.

A third failure mode is worth recording because it silently deletes whole tasks rather than
lowering a score: when the agent returns no answer, upstream `agent/search.py` falls back to
`str(full_result)`, which serialises the entire run object (~9 MB) into the answer field and
sends it to the judge; the judge then exceeds its context window, returns 400, the
environment step returns 500, and the whole query is dropped from the results. Mem0 hits a
second instance of the same class of problem: the environment writes the full agent trace
into memory (median 86.5k tokens per write), while the Mem0 cloud API rejects any single
write above 100k tokens, so writes fail, the query aborts mid-chain, and **Mem0 reached the
final query on 0 of 20 multi-hop tasks** — its `SR` of 0.0% reflects never answering rather
than answering incorrectly. Both are implementation limits, not properties of the memory
representations, and both should be fixed before the affected cells are read as capability
measurements.

## Citation

```bibtex
@article{zhan2026memorylake,
  title={MemoryLake on MemoryArena: A Matched Study of Agent Memory Backends},
  author={Zhan, Chaoqun and Zhou, Qiang and Li, Guannan and Huang, Zhenqiang and
          Wang, Qianjin},
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
