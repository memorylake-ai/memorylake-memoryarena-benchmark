# eval

Everything needed to reproduce the published numbers: the exact items evaluated, the per-item
scores, and the one scoring script that is not part of MemoryArena.

```
eval/
├── queries/                  the exact items evaluated in each task
├── results/                  per-item scores behind every published number
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

## Usage

All three scripts locate the MemoryArena checkout at `../third_party/MemoryArena`; override
with `MEMORYARENA_ROOT` if yours is elsewhere. `web_ps_score.py` calls an LLM judge and needs
`OPENAI_API_KEY` (plus `OPENAI_BASE_URL` for a gateway); the other two are offline.

```bash
# score a run: writes per-query verdicts and caches them in <run_dir>/.judge_cache.json
JUDGE_MODEL=gpt-5-mini python eval/web_ps_score.py <run_dir>

# restrict to the controlled 20-query subset
WEB_ONLY_IDS="$(paste -sd, eval/queries/web_search_controlled_20_ids.tsv)" \
  python eval/web_ps_score.py <run_dir>

# coverage + both PS denominators, from the cache (no LLM calls)
python eval/slot_coverage.py <run_dir>
```

## The PS denominator

`web_ps_score.py` skips sub-query slots that produced no answer (`if not pred: continue`)
instead of scoring them 0, so the PS it prints is measured over *answered* slots. A system
that answers fewer slots is therefore measured on an easier denominator, and slot coverage
varied more than fourfold across the four systems compared here (22.5% to 94.4%).

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
