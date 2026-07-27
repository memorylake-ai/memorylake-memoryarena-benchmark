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
| Bundled web shopping | `bundled_shopping` (WebShop) | **50-bundle / 300-step intersection** scored across systems (see note) | [`queries/shopping_task_ids.tsv`](queries/shopping_task_ids.tsv) |
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
- **Bundled web shopping** — 150 bundles total (5 categories × 30), 6 sequential purchases
  each (900 steps). **MemoryLake completed the full 150; the Mem0 and RAG baselines each
  ran the first 10 bundles per category, so scoring is performed uniformly on the
  50-bundle / 300-step intersection shared by all systems** (i.e. `item_0`–`item_9` in each
  of `baking / beauty / electronics / grocery / home`). `step-match%` = exact-ASIN match
  per step; `SR` requires all 6 steps to hit.
- **Progressive multi-hop retrieval** — corpus of 100,195 documents (FAISS, text-embedding-3-small
  vectors); of 830 ground-truth queries, 221 carry progressive sub-query decompositions
  (1,641 sub-queries; the original paper cites 256). Each query's sub-queries are answered
  in order and written to memory; the final combined query is answered with all accumulated
  memory. `SR` = correctness of the final query; `PS` = accuracy over answered sub-queries.
  The **controlled four-system comparison uses a fixed 20-query / 142-sub-query subset**
  (matched to the smaller travel / shopping sample sizes).

## MemoryLake-only robustness check (not part of the four-system comparison)

As a sample-size robustness check on the 20-query estimate, MemoryLake **alone** was
additionally run on the **full 221 progressive queries (1,641 sub-queries)**; its scores
are consistent with the 20-query subset. This check does **not** include the three
baselines and supports no claim about relative standing at n=221. Manifest:
[`queries/web_search_memorylake_221_ids.tsv`](queries/web_search_memorylake_221_ids.tsv).

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
