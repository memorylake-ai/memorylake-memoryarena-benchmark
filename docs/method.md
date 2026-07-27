# MemoryLake — Method Overview

**MemoryLake** is the memory system we evaluate on the MemoryArena benchmark. It is a
**dual-track** memory that separates *instance knowledge* from *reusable procedure*, and
plugs into MemoryArena through the standard adapter interface (`add_chunk(chunk)` /
`wrap_user_prompt(question)`, with per-`user_id` isolation) — identical to the other
memory baselines.

## Dual track

- **DOC track (per user / session).** Every agent-trajectory chunk is written to a
  per-user knowledge store, organized into two complementary views:
  - a **QA** view — the *resolved* facts / answers a later step can reuse, and
  - a **PROCESS** view — *how* a result was reached.

  At query time both views are retrieved (top-k) and injected as a bounded
  `<memory_context>`. The DOC track is backed by the MemoryLake knowledge/retrieval
  service.

- **SKILL track (per task family, shared).** From completed trajectories we distill
  short, **entity-free reusable procedures** ("skills") — the decisive step plus the
  easy-to-miss pitfall for a *class* of tasks. Skills are de-duplicated into a compact
  library and injected only when the current task is a relevant match.

## Recall & injection

At `wrap_user_prompt`, MemoryLake merges recalls from both tracks into a single
`<memory_context>` block, under **per-task-family token budgets** so that memory never
crowds out the task prompt itself. All LLM calls (distillation, retrieval curation,
judging) use the same task model.

> This directory documents **evaluation settings only**; the MemoryLake implementation is
> maintained separately and is not included here.
