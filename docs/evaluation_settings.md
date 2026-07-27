# Evaluation Settings

Settings used when evaluating **MemoryLake** on the MemoryArena benchmark.

## Agent & judge

- Task-agent model: **GPT-5-mini** (served via an OpenAI-compatible API).
- Judge model (for tasks scored by a model judge): **GPT-5-mini**.

## Tasks, datasets & query selection

| Task | Environment / dataset | Split / selection |
|------|-----------------------|-------------------|
| Formal reasoning — math | HF `ZexueHe/memoryarena`, config `formal_reasoning_math` | `test` split |
| Formal reasoning — physics | HF `ZexueHe/memoryarena`, config `formal_reasoning_phys` | `test` split |
| Travel planning | TravelPlanner-based environment | up to 30 steps |
| Web shopping | WebShop-based environment | MemoryArena split |
| Web search | BrowseComp-Plus (progressive) | **221 queries** — see [`queries/web_search_query_ids.tsv`](queries/web_search_query_ids.tsv) |

## Web search specifics

- **Progressive, multi-subquery**: each of the 221 queries is decomposed into
  **4–16 subqueries** (mean 7.4, median 7) followed by one final combined query.
- Retrieval agent over the BrowseComp-Plus corpus: **top-k = 10** passages,
  **per-snippet cap = 512 tokens**, **max 35 agent iterations**.
- Memory is written **once per completed subquery** (progressive accumulation); the final
  combined query *reads* memory but does not write.

## Memory (MemoryLake) settings

- Knowledge-retrieval **top-k = 10**.
- Per-task-family injection budgets bound the size of the injected `<memory_context>`.
- Trajectory-synthesis for web search: **disabled** in the reported runs.

## Scoring

Official MemoryArena scorers are used:

- **PS** (progress / per-step pass rate) and **SR** (final success rate) for formal
  reasoning and web search.
- **SPS / PS / SR** for travel planning; **step-match** (exact selection match) for web
  shopping.
