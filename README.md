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
- **PS and SR do not always move together — on multi-hop retrieval they invert.** Mem0 gets more
  sub-queries right (13 vs 9 correct; **PS 8.9% vs 6.7%**) yet reaches the correct final answer
  less often (**SR 15.0% vs 20.0%**). Ranking on process-level completeness would have picked
  the system that finishes fewer tasks — which is why both are reported here and why the
  outcome measure is the one conclusions are drawn from.
- **The clear exception is group travel planning**, a workload dominated by high-volume,
  homogeneous verbatim replay, where full verbatim context beats every memory representation
  (**SPS 53.1% vs 43.0%**).
- **Bundled web shopping separates no system at all.** On the full 150-bundle set — the
  scored comparison — the top three span 0.4pp (long context 30.0%, text-embedding 29.7%,
  MemoryLake 29.6%), with the study's single bundle-level success (long context, 1/150); on
  the 50-bundle sensitivity subset they span 2.7pp *in a different order* (text-embedding
  31.0%, MemoryLake 30.0%, long context 28.3%). An ordering that flips with the sample is
  not a finding, and we do not read one from it.

Together: **memory representation structure should be matched to the structure of the
workload it serves, and that match should be validated against task outcomes (SR) rather
than process-level completeness (PS) alone.** Structure pays off where later steps depend on
earlier conclusions, does not pay off on the replay-dominated workload, and is untestable on
the one workload where almost nothing succeeds end to end.

The evaluated scale behind each number — the full 150-bundle shopping set and the
50-bundle sensitivity subset drawn from it, the controlled 20-query multi-hop subset and how
that subset is drawn — is stated in
[`docs/evaluation_settings.md` § Tasks, datasets and evaluated scale](docs/evaluation_settings.md#tasks-datasets-and-evaluated-scale),
with the exact items in [`eval/queries/`](eval/queries/) and the per-item scores in
[`eval/results/per_item_scores.md`](eval/results/per_item_scores.md).

> **On the multi-hop numbers.** `PS` is quoted on the all-slots denominator, which is the one
> comparable across systems: the benchmark's scorer skips unanswered sub-query slots rather
> than scoring them 0, so a system that answers fewer of them is otherwise measured on an
> easier denominator. Mem0 runs with a memory-write size cap, because the unmodified
> environment issues writes its cloud API rejects and Mem0 then never reaches the final query
> on any task — its uncapped `SR` of 0.0% measures the harness, not the memory system. The
> other three systems run unmodified. See
> [`docs/evaluation_settings.md`](docs/evaluation_settings.md) and
> [`eval/results/mem0_write_limit.md`](eval/results/mem0_write_limit.md).

## Documentation

- [`docs/method.md`](docs/method.md) — how MemoryLake is organized, and how its
  representation differs from the baselines.
- [`docs/evaluation_settings.md`](docs/evaluation_settings.md) — base model, per-task
  datasets and evaluated scale, metric definitions, and scoring procedure.
- [`eval/`](eval/) — the items evaluated, the per-item scores, and the multi-hop scoring
  script (the other four tasks are scored by MemoryArena's own code).

This repository documents the *evaluation*; the MemoryLake implementation is not included
(see the disclosure scope in [`docs/method.md`](docs/method.md)).

## Getting the benchmark code

The MemoryArena implementation is **referenced as a git submodule, not vendored** — this
repository stores only a URL and a commit id, so the exact code behind every number is pinned
and reproducible without redistributing upstream source:

```bash
git clone https://github.com/memorylake-ai/memorylake-memoryarena-benchmark
cd memorylake-memoryarena-benchmark
git submodule update --init third_party/MemoryArena     # NOT --recursive
```

> ⚠️ Do not use `--recursive` / `--recurse-submodules`. MemoryArena declares a submodule
> (`MemActBench`) whose repository is not publicly reachable, so a recursive clone fails.

`third_party/MemoryArena` is pinned to
[`6cd9de1`](https://github.com/memorylake-ai/MemoryArena/tree/6cd9de14b71915e39ac742a20dc33785e14b6aab)
of a fork of [`ZexueHe/MemoryArena`](https://github.com/ZexueHe/MemoryArena).

> **Licensing.** The Apache-2.0 license of this repository covers this repository's files only.
> Upstream MemoryArena publishes **no license**, so its code is not redistributed here and no
> license is asserted over it; see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for the
> full attribution list, the components MemoryArena itself bundles (TravelPlanner, WebShop,
> DeepResearch, MemoRAG, …) and their terms.

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
