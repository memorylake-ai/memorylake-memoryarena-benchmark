# MemoryLake on MemoryArena — Evaluation Settings

This directory documents **how MemoryLake was evaluated** on the MemoryArena benchmark:
the datasets and query selection, the agent / memory / judge configuration, and a short
method overview.

**Scope:** settings and documentation only. The MemoryLake implementation is not included
in this contribution.

## Contents

- [`method.md`](method.md) — short overview of the MemoryLake memory system (dual-track: DOC + SKILL).
- [`evaluation_settings.md`](evaluation_settings.md) — per-task datasets, query selection, and hyperparameters.
- [`queries/web_search_query_ids.tsv`](queries/web_search_query_ids.tsv) — the 221 BrowseComp-Plus queries used for web search (`query_id`, `num_subqueries`).
