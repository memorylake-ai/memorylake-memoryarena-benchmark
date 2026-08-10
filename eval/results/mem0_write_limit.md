# Mem0's per-write size limit on progressive multi-hop retrieval

Why the four-system comparison scores Mem0 from a **capped re-run**, and what the cap changes.
Uncapped, **Mem0's `SR` of 0.0% reflects never reaching the final query, not answering it
incorrectly** — so it measures the harness rather than the memory system.

> ⚠️ **Mem0 is the only system that runs modified.** The cap is a code change no other backend
> received, so Mem0's cell is not resource-matched to the other three; it is gated on
> `memory_system_name == "mem0"` so nothing else is affected. This is a deliberate trade: the
> uncapped run cannot be read as a capability estimate at all, while the capped one is
> comparable on slot coverage (84.5%, against 64.8–94.4% for the others) at the cost of an
> environment difference that must be stated wherever the number appears.

## The failure

The environment writes the **full agent trace** into memory after each sub-query
(`browsecomp_plus_env.py`, `run_subqueries`):

```python
memory_entry = f"Subquery {i+1}: {subquery}\n\nPredicted Answer: {answer}"
if trace_summary:
    memory_entry += f"\n\nTrace: {trace_summary}"      # every search result, verbatim
self.memory_client.add(memory_entry)
```

Measured over 132 such writes: **median 58,217 tokens, p90 190,965, max 216,751.** The Mem0
cloud API rejects any single write above **100,000 tokens**, so most writes fail:

```
POST https://api.mem0.ai/v3/memories/add/ -> 400
mem0.exceptions.ValidationError: "Messages contain 216,751 tokens, which exceeds the limit of 100,000."
```

The failure then escalates rather than degrading: `add()` raises → `/env/step` returns 500 →
`run_search.py` retries the query three times → the query is skipped entirely. Sixty env-side
500s appear in the original run log, and the visible symptom is missing data, not a low score.

This is why Mem0 answered only **32 of 142** sub-query slots and reached the final combined
query on **0 of 20** queries. `SR` is computed solely from the final query, so it could not
have been anything other than 0.0%.

The other three systems are unaffected: their memory backends impose no comparable per-write
ceiling, so the same oversized entries are accepted.

## The change, and why it is gated

[`../patches/mem0_write_cap.patch`](../patches/mem0_write_cap.patch) caps a single write inside
`/memory/add`. Two details matter:

**It is gated on the memory system name.** Truncating unconditionally would alter the input of
every backend — those entries are equally large for MemoryLake — and silently change the very
comparison being measured. The cap applies only when `memory_system_name == "mem0"` **and**
`MEM_ADD_MAX_TOKENS` is set; unset means upstream behaviour.

**It backs off on rejection rather than assuming a token ratio.** Mem0's tokenizer does not
agree with `o200k_base`: a chunk we measured at 90,000 `o200k` tokens was reported by Mem0 as
**238,335** — a factor of 2.65. Guessing that ratio is fragile, so the patch halves the cap on
each limit rejection until the write is accepted:

| our cap (`o200k`) | Mem0 reported | outcome |
|---|---|---|
| 90,000 | 238,335 | rejected |
| 45,000 | 119,218 | rejected |
| 22,500 | ~59,600 | accepted |

Starting at **32,000** (≈ 84.8k by Mem0's count) was accepted on the first attempt for all 132
writes in the run below, so the back-off never fired — it remains as protection against a
future change in either tokenizer or limit.

## How much of the trace survives

| | |
|---|---|
| writes | 132 |
| writes exceeding the cap | **85 (64%)** |
| retention among truncated writes | min 15% · median 26% · max 97% |
| **overall content retained** | **3,304,763 / 10,906,240 tokens = 30.3%** |
| limit rejections during the run | **0** (60 env-side 500s before) |

So Mem0 receives roughly **the first third of each trace**. That is the precise sense in which
Mem0's cell is not resource-matched to the other three: it is scored on less input, not on a
different metric.

## Result

| | slot coverage | `PS` (answered denom.) | `PS` (all-slots denom.) | `SR` | reached final query |
|---|---|---|---|---|---|
| original run | 32/142 = 22.5% | 3.3% | 1.9% | 0.0% (0/20) | **0/20** |
| **with the cap** (used in the comparison) | **120/142 = 84.5%** | 10.7% | **8.9%** | **15.0%** (3/20) | **20/20** |

**The decisive movement is `0/20 → 20/20` reaching the final query**, which settles what the
0.0% meant: with the cap Mem0 answers the question the metric asks, without it the metric had
nothing to score.

Worth noting for its own sake: Mem0 scores *better* on a third of the trace than it did on all
of it, which suggests writing a verbatim search transcript into memory is not merely wasteful
but actively harmful — it is process log, not memory content. Testing that properly means
applying the same cap to the other three systems, which has not been done; until then the
observation is a hypothesis, not a finding.

### Per query

`passed/answered` sub-queries, `✓/✗` = final combined query correct. `N` = total slots.

| query | N | original | with the cap |
|---|---|---|---|
| 11 | 6 | 0/1 ✗ | 0/6 ✗ |
| 15 | 4 | 0/0 ✗ | 1/2 ✗ |
| 49 | 7 | 0/2 ✗ | 0/7 ✗ |
| 50 | 7 | 0/1 ✗ | 2/6 ✓ |
| 51 | 8 | 0/2 ✗ | 2/7 ✓ |
| 54 | 7 | 2/6 ✗ | 3/7 ✗ |
| 60 | 10 | 0/2 ✗ | 0/10 ✗ |
| 67 | 8 | 0/1 ✗ | 0/6 ✗ |
| 107 | 7 | 0/1 ✗ | 1/7 ✗ |
| 121 | 6 | 0/1 ✗ | 0/5 ✗ |
| 124 | 6 | 0/0 ✗ | 0/2 ✗ |
| 126 | 9 | 0/3 ✗ | 0/9 ✗ |
| 130 | 5 | 0/2 ✗ | 0/3 ✗ |
| 131 | 8 | 0/1 ✗ | 0/7 ✗ |
| 132 | 9 | 0/0 ✗ | 0/6 ✗ |
| 149 | 5 | 0/3 ✗ | 0/5 ✗ |
| 160 | 6 | 0/1 ✗ | 0/4 ✗ |
| 165 | 5 | 0/1 ✗ | 0/3 ✗ |
| 175 | 8 | 0/1 ✗ | 2/8 ✓ |
| 180 | 11 | 1/3 ✗ | 2/10 ✗ |

Nine queries had **zero** answered sub-queries beyond the first one or two in the original run —
the point at which the accumulated trace crosses 100k tokens and every subsequent write fails.

## Reproducing

```bash
cd third_party/MemoryArena
git apply ../../eval/patches/mem0_write_cap.patch

MEM_ADD_MAX_TOKENS=32000 python memory/server.py        # cap active for mem0 only
# ... run the multi-hop task against this memory server ...

python ../../eval/web_ps_score.py  <run_dir>
python ../../eval/slot_coverage.py <run_dir>
```

Omit `MEM_ADD_MAX_TOKENS` (or set it to `0`) to get upstream behaviour with the patch applied.
`[MEMTRUNC]` lines on the memory server's stdout record every write's decision, which is where
the retention figures above come from.
