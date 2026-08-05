# Evaluation Settings

Settings for the controlled, single-variable comparison on MemoryArena. Four systems are
evaluated under **one agent framework, one base model, and the same task samples /
denominators / official metrics** — the memory layer is the only experimental variable.

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
| Formal reasoning · math | `formal_reasoning_math`, `test` | **40 papers / 354 subproblems** (full) | [`queries/formal_reasoning_math_ids.tsv`](queries/formal_reasoning_math_ids.tsv) |
| Formal reasoning · physics | `formal_reasoning_phys`, `test` | **20 papers / 86 subproblems** (full) | [`queries/formal_reasoning_phys_ids.tsv`](queries/formal_reasoning_phys_ids.tsv) |
| Group travel planning | `group_travel_planner` (TravelPlanner) | **30 groups / 208 member problems** — fixed-ID list, identical across all four systems (of 270 groups) | [`queries/travel_query_ids.tsv`](queries/travel_query_ids.tsv) |
| Bundled web shopping | `bundled_shopping` (WebShop) | **150 bundles / 900 steps** (full) — all four systems completed the full set | [`queries/shopping_task_ids.tsv`](queries/shopping_task_ids.tsv) |
| Progressive multi-hop retrieval | BrowseComp-Plus | **20 queries / 142 sub-queries** — fixed subset, all four systems | [`queries/web_search_controlled_20_ids.tsv`](queries/web_search_controlled_20_ids.tsv) |

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
- **Bundled web shopping** — 150 bundles (5 categories × 30), 6 sequential purchases each
  (900 steps). **All four systems completed the full 150-bundle set**, so scoring uses the
  complete 150-bundle / 900-step protocol set; no intersection subsetting is applied.
  `step-match%` = exact-ASIN match per step; `SR` requires all 6 steps to hit.
  Per-bundle numbers: [`results/per_item_scores.md`](results/per_item_scores.md).

  On the full set the three strongest systems fall within 0.4pp of each other —
  Long Context 30.00% (270/900), text-embedding 29.67% (267/900), MemoryLake 29.56%
  (266/900), Mem0 24.33% (219/900) — i.e. **indistinguishable at this sample size**.
  `SR` is 0/150 for every system except Long Context (1/150 = 0.7%), so on this task
  only `step-match%` carries signal.
- **Progressive multi-hop retrieval** — corpus of 100,195 documents (FAISS, text-embedding-3-small
  vectors); of 830 ground-truth queries, 221 carry progressive sub-query decompositions
  (1,641 sub-queries; the original paper cites 256). Each query's sub-queries are answered
  in order and written to memory; the final combined query is answered with all accumulated
  memory. `SR` = correctness of the final query; `PS` = accuracy over answered sub-queries.
  The **controlled four-system comparison uses a fixed 20-query / 142-sub-query subset**
  (matched to the smaller travel / shopping sample sizes).

  **Slot coverage must be reported alongside `PS`.** A sub-query slot yields no answer when
  the agent exhausts its search-iteration budget without emitting one; `web_ps_score.py`
  skips such slots rather than scoring them 0, so its `PS` denominator is *answered* slots
  and a system that answers fewer slots is measured on an easier denominator. We therefore
  report both denominators plus coverage:

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
  Per-query numbers: [`results/per_item_scores.md`](results/per_item_scores.md).

## MemoryLake-only robustness check (not part of the four-system comparison)

As a sample-size robustness check on the 20-query estimate, MemoryLake **alone** was
additionally run on the **full 221 progressive queries (1,641 sub-queries)**; its scores
are consistent with the 20-query subset. This check does **not** include the three
baselines and supports no claim about relative standing at n=221. Manifest:
[`queries/web_search_memorylake_221_ids.tsv`](queries/web_search_memorylake_221_ids.tsv).

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
notes). Per-query numbers: [`results/per_item_scores.md`](results/per_item_scores.md).

## Scoring

Official MemoryArena scripts, with every score independently recomputed from raw result
files (zero deviation on deterministic tasks, <1pp on LLM-judged tasks):

- math / physics — `formal_reasoning_env/eval.py` (gpt-5-mini equivalence judging);
- travel — `travel_planner_env/eval.py` (deterministic difflib slot matching, threshold 0.7);
- shopping — `web_shopping_env/compute_reward.py` (exact ASIN step-match);
- multi-hop retrieval — `web_ps_score.py` / `evaluate_with_openai.py` (gpt-5-mini judge).

Denominators: math / physics fixed at 40 / 20 papers; shopping on the 50-bundle / 300-step
intersection; multi-hop retrieval on the controlled n=20 scale for all four systems (the
separate n=221 check covers MemoryLake only).
