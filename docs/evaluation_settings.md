# Evaluation Settings

Settings for the matched system-level comparison on MemoryArena. Four systems are evaluated
under **one agent framework, one base model, and the same task samples / denominators /
official metrics** — the memory backend is the intentionally changed component.

A memory backend is not a single variable: swapping it also changes write policy, extraction,
auxiliary-model calls, consolidation, retrieval, ordering, prompt assembly, context length and
fallback behaviour. What follows therefore identifies the effect of assigning a **complete
backend configuration** under the tested setup. It is neither a representation-only ablation
nor a token-, latency- or cost-matched comparison.

## Systems

- **MemoryLake** — structured multi-track memory (see [`method.md`](method.md)).
- **Mem0** — extractive fact memory.
- **text-embedding-3-small** — naive vector-chunk RAG.
- **Long Context** — no memory system; the full prior-subtask trajectory is flattened
  verbatim into the prompt (a zero-abstraction, full-fidelity control).

## Base model

- Agent and judge model: **gpt-5-mini**, for all systems.
- Note: the MemoryArena v1 paper claims "GPT-5.1-mini", which does not exist in the OpenAI
  API; we adopt `gpt-5-mini`, so absolute scores are not strictly comparable to that
  paper's numbers (they remain comparable *across our four systems*).

## Tasks, datasets and evaluated scale

All data come from the HuggingFace dataset `ZexueHe/memoryarena`. Each task instance is an
ordered sequence of interdependent subtasks; memory accumulates and transfers knowledge
**between subtasks of the same instance**, and is fully isolated **between instances**.

| Task | HF config / source | Evaluated scale (controlled comparison) | Query manifest |
|------|--------------------|------------------------------------------|----------------|
| Formal reasoning · math | `formal_reasoning_math`, `test` | **40 papers / 354 subproblems** (full) | [`../eval/queries/formal_reasoning_math_ids.tsv`](../eval/queries/formal_reasoning_math_ids.tsv) |
| Formal reasoning · physics | `formal_reasoning_phys`, `test` | **20 papers / 86 subproblems** (full) | [`../eval/queries/formal_reasoning_phys_ids.tsv`](../eval/queries/formal_reasoning_phys_ids.tsv) |
| Group travel planning | `group_travel_planner` (TravelPlanner) | **30 groups / 208 member problems** — fixed-ID list, identical across all four systems (of 270 groups) | [`../eval/queries/travel_query_ids.tsv`](../eval/queries/travel_query_ids.tsv) |
| Bundled web shopping | `bundled_shopping` (WebShop) | **50 bundles / 300 steps** — first 10 of each of 5 categories, extracted from the completed 150-bundle runs of all four systems | [`../eval/queries/shopping_task_ids.tsv`](../eval/queries/shopping_task_ids.tsv) |
| Progressive multi-hop retrieval | BrowseComp-Plus | **20 queries / 142 slots** (122 sub-queries + 20 final combined queries) — fixed subset, all four systems | [`../eval/queries/web_search_controlled_20_ids.tsv`](../eval/queries/web_search_controlled_20_ids.tsv) |

## Per-task notes

- **Formal reasoning (math / physics)** — each instance is a paper decomposed into ordered
  subproblems (math 2–16/paper, mean 8.85; physics 2–12/paper, mean 4.3); one paper is one
  memory session, each subproblem's conclusion being the premise of the next. `PS` = mean
  within-paper subproblem accuracy; `SR` = fraction of papers whose *final* subproblem is
  correct. Both use the full benchmark protocol set (40 / 20 papers).
- **Group travel planning** — for each group, the `base_person` itinerary is written to
  memory first; each member (7 slots/day) is planned via ReAct, and later members'
  constraints must reference earlier members' itineraries. `PS` = fraction of members
  passing all slots on all days; `SPS` (soft process score) = satisfaction rate of the
  member's *added* constraint slots relative to `base_person`; `SR` = fraction of groups
  where every member passes. Evaluated on a fixed list of 30 groups (208 members),
  identical across all four systems.
- **Bundled web shopping** — the released set is 150 bundles (5 categories × 30), 6 sequential
  purchases each (900 steps), and **all four systems completed it in full**. The cross-system
  table scores a fixed **50-bundle / 300-step subset — the first 10 bundles of each category**
  — so that the shopping sample is the same order of magnitude as the travel (30 groups) and
  multi-hop (20 queries) samples. The subset is *extracted from the completed 150-bundle runs*,
  not run separately, so no system is measured on data another system did not see.
  `step-match%` = exact-ASIN match per step; `SR` requires all 6 steps to hit.
  Per-bundle numbers: [`../eval/results/per_item_scores.md`](../eval/results/per_item_scores.md).

  | system | 50-bundle subset | full 150-bundle set |
  |---|---|---|
  | text-embedding | **31.00%** (93/300) | 29.67% (267/900) |
  | MemoryLake | 30.00% (90/300) | 29.56% (266/900) |
  | Long Context | 28.33% (85/300) | **30.00%** (270/900) |
  | Mem0 | 24.00% (72/300) | 24.33% (219/900) |

  **The ordering is not stable between the two scales**: the three leading systems span 2.7pp
  at n=50 and 0.4pp at n=900, both well inside what these sample sizes can resolve. Read the
  shopping column as "no system separates from the others", not as a ranking. `SR` is 0/50 for
  every system on the subset, and 0/150 on the full set for every system except Long Context
  (1/150 = 0.7%), so on this task only `step-match%` carries any signal at all.
- **Progressive multi-hop retrieval** — corpus of 100,195 documents (FAISS, text-embedding-3-small
  vectors); of 830 ground-truth queries, 221 carry progressive sub-query decompositions
  (1,641 slots = 1,420 sub-queries + 221 final combined queries; the original paper cites 256
  decompositions). Each query's sub-queries are answered
  in order and written to memory; the final combined query is answered with all accumulated
  memory. `SR` = correctness of the final query; `PS` = accuracy over answered sub-queries.
  The **controlled four-system comparison uses a fixed 20-query / 142-sub-query subset**
  (matched to the smaller travel / shopping sample sizes).

  **How that subset is drawn.** It is a deterministic **proportional stratified sample on
  decomposition depth** — no random seed is involved:

  1. stratify the 221 decomposed queries by depth (`num_subqueries`, i.e. sub-queries plus the
     final combined query);
  2. quota per stratum = `round(stratum_size × 20 / 221)`;
  3. within a stratum, take the lowest query ids.

  | depth | in the 221 | quota | ids |
  |---|---|---|---|
  | 4 | 7 | 1 | 15 |
  | 5 | 30 | 3 | 130, 149, 165 |
  | 6 | 42 | 4 | 11, 121, 124, 160 |
  | 7 | 45 | 4 | 49, 50, 54, 107 |
  | 8 | 45 | 4 | 51, 67, 131, 175 |
  | 9 | 20 | 2 | 126, 132 |
  | 10 | 13 | 1 | 60 |
  | 11 | 11 | 1 | 180 |
  | 12–16 | 8 | 0 | — |
  | | **221** | **20** | **142 slots** |

  Depth is the variable the task is built to stress — a conclusion has to survive every step of
  the chain — so sampling proportionally on it keeps the subset's difficulty profile matched to
  the full 221 rather than skewed toward short or long chains.

  [`../eval/sample_controlled_20.py`](../eval/sample_controlled_20.py) reproduces the manifest
  from [`../eval/queries/web_search_memorylake_221_ids.tsv`](../eval/queries/web_search_memorylake_221_ids.tsv)
  offline — `--verify` checks it against the published list, `--tsv` regenerates it byte for byte.

  **Exact definition of `PS` and `SR`.** For a query *q*, let *S_q* be its **slot count** and
  *a_q ≤ S_q* the slots that produced a non-empty answer, of which *p_q* were judged correct.
  Over the *Q* queries scored:

  ```
  PS(answered)  =  (1/Q) · Σ_q  p_q / a_q        <- what web_ps_score.py prints
  PS(all-slots) =  (1/Q) · Σ_q  p_q / S_q        <- use this for cross-system comparison
  SR            =  (1/Q) · Σ_q  1[final answer of q judged correct]
  ```

  Three properties of this definition are easy to misread, so they are stated explicitly:

  1. **`S_q` counts the final combined query, not just sub-queries.** `slot_coverage.py` takes
     `S_q = len(question)`, and in the dataset `question[0..N-2]` are the sub-queries while
     `question[-1]` is the final combined query. So the controlled subset's **142 slots are
     122 sub-queries + 20 final queries**, and the full set's **1,641 slots are 1,420 + 221**.
     Neither figure is a count of sub-queries alone. The `num_subqueries` column in
     [`../eval/queries/web_search_memorylake_221_ids.tsv`](../eval/queries/web_search_memorylake_221_ids.tsv)
     is this slot count too, despite its name — the column is kept as published so existing
     readers of the manifest do not break.
  2. **The final query is inside `PS`.** `web_ps_score.py` adds it to both *p_q* and *a_q*.
     `PS` and `SR` therefore share an item and are not independent measures of "process" and
     "outcome".
  3. **Both forms are macro-averages over queries** — a mean of per-query ratios, not
     `Σp / Σs` over all slots. A 2-slot query carries the same weight as a 16-slot one.

  **Slot coverage must be reported alongside `PS`.** A sub-query slot yields no answer when
  the agent exhausts its search-iteration budget without emitting one; `web_ps_score.py`
  skips such slots (`if not pred: continue`) rather than scoring them 0, so its `PS`
  denominator is *answered* slots and a system that answers fewer slots is measured on an
  easier denominator. We therefore report both denominators plus coverage:

  | system | slot coverage | `PS` (answered denom.) | `PS` (all-slots denom.) | `SR` |
  |---|---|---|---|---|
  | MemoryLake | 133/142 = 93.7% | 6.7% | **6.7%** | **20.0%** (4/20) |
  | Mem0 | 32/142 = **22.5%** | 3.3% | 1.9% | 0.0% (0/20) |
  | text-embedding | 92/142 = **64.8%** | *8.2%* | 5.6% | 10.0% (2/20) |
  | Long Context | 134/142 = 94.4% | 6.0% | 5.3% | 10.0% (2/20) |

  Under the answered-slot denominator text-embedding's 8.2% is the highest `PS`, but it
  answers only 64.8% of slots; under the all-slots denominator the ordering matches `SR`.
  **Cross-system `PS` comparisons on this task should use the all-slots denominator.**
  Mem0's 22.5% coverage is low enough that neither of its `PS` figures should be read as a
  capability estimate — see the reproducibility note on its memory-write size limit.
  Per-query numbers: [`../eval/results/per_item_scores.md`](../eval/results/per_item_scores.md).

## MemoryLake-only robustness check (not part of the four-system comparison)

As a sample-size robustness check on the 20-query estimate, MemoryLake **alone** was
additionally run on the **full 221 progressive queries (1,641 slots)**; its scores
are consistent with the 20-query subset. This check does **not** include the three
baselines and supports no claim about relative standing at n=221. Manifest:
[`../eval/queries/web_search_memorylake_221_ids.tsv`](../eval/queries/web_search_memorylake_221_ids.tsv).

Slots left unanswered by an exhausted search-iteration budget were re-run and merged
(original answers kept; a re-run answer is used only where the original produced none):

| n=221 | slot coverage | `PS` (answered denom.) | `PS` (all-slots denom.) | `SR` |
|---|---|---|---|---|
| before re-run | 1315/1641 = 80.1% | 11.8% | 9.7% | 16.7% (37/221) |
| **after re-run** | **1538/1641 = 93.7%** | 13.4% | **12.3%** | **26.7%** (59/221) |

The re-run raises coverage to exactly the level of the controlled 20-query subset (93.7%),
so the robustness check and the four-system comparison now rest on the same coverage.
The remaining 103 unanswered slots (6.3%) are cases where the agent reached its iteration
cap without emitting an answer — re-running does not recover them (see reproducibility
notes). Per-query numbers: [`../eval/results/per_item_scores.md`](../eval/results/per_item_scores.md).

## Scoring

Official MemoryArena scripts, with every score independently recomputed from raw result
files (zero deviation on deterministic tasks, <1pp on LLM-judged tasks):

- math / physics — `formal_reasoning_env/eval.py` (gpt-5-mini equivalence judging);
- travel — `travel_planner_env/eval.py` (deterministic difflib slot matching, threshold 0.7);
- shopping — `web_shopping_env/compute_reward.py` (exact ASIN step-match);
- multi-hop retrieval — `web_ps_score.py` / `evaluate_with_openai.py` (gpt-5-mini judge).

Denominators: math / physics fixed at 40 / 20 papers; travel on 30 groups / 208 members;
shopping on the 50-bundle / 300-step subset described above (the full 150-bundle values are
given alongside it); multi-hop retrieval on the controlled n=20 scale for all four systems,
with `PS` on the all-slots denominator (the separate n=221 check covers MemoryLake only).
