# eval

Everything needed to reproduce the published numbers: the exact items evaluated, the per-item
scores, and the one scoring script that is not part of MemoryArena.

```
eval/
├── queries/                  the exact items evaluated in each task
├── results/                  per-item scores behind every published number
│   └── mem0_write_limit.md   why Mem0's multi-hop SR is 0.0% (diagnostic, not a comparison)
├── patches/                  patches against the pinned MemoryArena checkout
├── sample_controlled_20.py   rebuild/verify the controlled 20-query subset (offline)
├── web_ps_score.py           multi-hop PS/SR scorer (not in MemoryArena)
├── slot_coverage.py          slot coverage + both PS denominators, from the judge cache
└── merge_slots.py            slot-level merge of multi-hop runs, original-run-first
```

## Which scorer belongs to which task

Four of the five tasks are scored by MemoryArena's own code, reachable through the submodule
once it is checked out (`git submodule update --init third_party/MemoryArena`). Only the
multi-hop scorer is ours:

| Task | Scorer | Where |
|---|---|---|
| Formal reasoning · math / physics | `formal_reasoning_env/eval.py` | MemoryArena |
| Group travel planning | `travel_planner_env/eval.py` | MemoryArena |
| Bundled web shopping | `web_shopping_env/compute_reward.py` | MemoryArena |
| Progressive multi-hop retrieval | **`eval/web_ps_score.py`** (+ upstream `evaluate_with_openai.py` for the judge) | **here** |

MemoryArena ships no end-to-end scorer for the progressive multi-hop task — it provides the
judge (`evaluate_with_openai.py`) but not the per-query PS/SR aggregation — which is why
`web_ps_score.py` exists.

## Reproducing the controlled 20-query subset

The subset is a deterministic proportional stratified sample on decomposition depth — no random
seed. `sample_controlled_20.py` rebuilds it from `queries/web_search_memorylake_221_ids.tsv`
offline, with no LLM calls and no need for the raw BrowseComp-Plus dataset:

```bash
python eval/sample_controlled_20.py            # show the strata, quotas and selected ids
python eval/sample_controlled_20.py --verify    # check against the published manifest
python eval/sample_controlled_20.py --tsv       # regenerate the manifest byte for byte
```

The rule and the per-stratum quotas are documented in
[`../docs/evaluation_settings.md`](../docs/evaluation_settings.md). The original selection
script was not preserved; this rule was recovered from the published subset and reproduces it
exactly, so it is a verified reconstruction rather than the original code.

## Usage

All three scripts locate the MemoryArena checkout at `../third_party/MemoryArena`; override
with `MEMORYARENA_ROOT` if yours is elsewhere. `web_ps_score.py` calls an LLM judge and needs
`OPENAI_API_KEY` (plus `OPENAI_BASE_URL` for a gateway); the other two are offline.

```bash
# score a run: writes per-query verdicts and caches them in <run_dir>/.judge_cache.json
JUDGE_MODEL=gpt-5-mini python eval/web_ps_score.py <run_dir>

# restrict to the controlled 20-query subset
WEB_ONLY_IDS="$(tail -n +2 eval/queries/web_search_controlled_20_ids.tsv | cut -f1 | paste -sd, -)" \
  python eval/web_ps_score.py <run_dir>

# coverage + both PS denominators, from the cache (no LLM calls)
python eval/slot_coverage.py <run_dir>
```

## Mem0's per-write size limit

Mem0's multi-hop `SR` of 0.0% is a *write failure*, not a recall failure: the environment
writes the full agent trace into memory (median 58k tokens, max 217k) while the Mem0 cloud API
rejects any single write above 100k tokens, so writes fail, the query aborts, and Mem0 reached
the final combined query on **0 of 20** queries.

[`results/mem0_write_limit.md`](results/mem0_write_limit.md) documents the diagnosis and the
capped re-run (`0/20 -> 20/20` reaching the final query), and
[`patches/mem0_write_cap.patch`](patches/mem0_write_cap.patch) is the change it used — gated on
`memory_system_name == "mem0"` and `MEM_ADD_MAX_TOKENS`, so no other backend's input is altered.

Those scores are a **modified baseline** and are not part of the four-system comparison; they
exist to identify the cause. The comparison uses Mem0's original run.

## The PS denominator

`web_ps_score.py` skips sub-query slots that produced no answer (`if not pred: continue`)
instead of scoring them 0, so the PS it prints is measured over *answered* slots. A system
that answers fewer slots is therefore measured on an easier denominator, and slot coverage
varied more than fourfold across the four systems compared here (22.5% to 94.4%).

With `S_q` the slot count of query *q*, `a_q` the slots it answered and `p_q` those judged
correct, over `Q` scored queries:

```
PS(answered)  = (1/Q) · Σ_q p_q / a_q      # printed by web_ps_score.py
PS(all-slots) = (1/Q) · Σ_q p_q / S_q      # printed by slot_coverage.py — use this
SR            = (1/Q) · Σ_q 1[final answer correct]
```

Both are **macro-averages over queries**, not `Σp / Σs` over slots, and `S_q = len(question)`
**includes the final combined query** — the 142 slots of the controlled subset are 122
sub-queries plus 20 final queries. The final query is counted in `PS` as well as `SR`, so the
two are not independent. Full statement in
[`../docs/evaluation_settings.md`](../docs/evaluation_settings.md).

`slot_coverage.py` reports coverage together with both denominators. **Cross-system PS
comparisons should use the all-slots denominator**; see
[`../docs/evaluation_settings.md`](../docs/evaluation_settings.md) for the tabulated values.

## Raising coverage without disturbing scored answers

`merge_slots.py` merges several runs of the same queries at slot granularity, taking each
slot's answer from the **first** source that produced one. Passing the original run first means
a re-run can only fill slots the original left empty — it can never replace an answer that was
already scored:

```bash
python eval/merge_slots.py <out_dir> ALL <original_run> <rerun_1> <rerun_2>
python eval/web_ps_score.py <out_dir>
```

First-wins rather than last-wins is deliberate. Scoring the same 20 queries twice under
different output budgets produced SR 20.0% and 15.0%, so preferring the newer answer would
have silently replaced correct answers with incorrect ones — a re-run is not automatically
better, only additional.
