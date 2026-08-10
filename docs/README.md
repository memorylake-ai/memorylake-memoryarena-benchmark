# MemoryLake on MemoryArena — Evaluation Settings

This directory documents **how MemoryLake was evaluated** on the MemoryArena benchmark, as
a matched system-level comparison against three baselines (Mem0,
text-embedding-3-small RAG, and a no-memory Long Context configuration): the datasets and
evaluated sample sizes, the agent / memory / judge configuration, and a short method
overview.

**Scope:** settings and documentation only. The MemoryLake implementation is not included
(consistent with the accompanying paper's disclosure scope — representation and policy are
described; storage, indexing, consolidation, and assembly are proprietary).

## Contents

- [`method.md`](method.md) — MemoryLake method overview (structured multi-track memory:
  confirmed conclusions / supporting evidence / reusable skills, under distinct presence
  policies).
- [`evaluation_settings.md`](evaluation_settings.md) — the four systems, base model,
  per-task datasets, evaluated scale, and scoring.
- [`../eval/queries/`](../eval/queries/) — the exact items evaluated per task:
  - [`formal_reasoning_math_ids.tsv`](../eval/queries/formal_reasoning_math_ids.tsv) — 40 papers (`id`, `paper_name`, `num_questions`)
  - [`formal_reasoning_phys_ids.tsv`](../eval/queries/formal_reasoning_phys_ids.tsv) — 20 papers
  - [`travel_query_ids.tsv`](../eval/queries/travel_query_ids.tsv) — 30 groups (`id`; fixed-ID subset of 270)
  - [`shopping_task_ids.tsv`](../eval/queries/shopping_task_ids.tsv) — 150 bundles (`category`, `task_file`); all four systems completed the full set, so the cross-system comparison is scored on all 150
  - [`web_search_controlled_20_ids.tsv`](../eval/queries/web_search_controlled_20_ids.tsv) — 20 queries (`query_id`, `num_slots`); the controlled four-system multi-hop subset
  - [`web_search_memorylake_221_ids.tsv`](../eval/queries/web_search_memorylake_221_ids.tsv) — 221 queries; MemoryLake-only robustness check (not part of the four-system comparison)
