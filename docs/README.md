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
- [`../eval/queries/`](../eval/queries/) — one manifest per task, listing the exact items
  evaluated. Which manifest belongs to which task, and the sample size behind each, are in
  [`evaluation_settings.md` § Tasks, datasets and evaluated scale](evaluation_settings.md#tasks-datasets-and-evaluated-scale)
  rather than repeated here.
- [`../eval/results/per_item_scores.md`](../eval/results/per_item_scores.md) — the per-item
  scores behind every published number.
