#!/usr/bin/env python3
"""Slot coverage and both PS denominators for a progressive multi-hop run.

`web_ps_score.py` skips sub-query slots that produced no answer rather than scoring them 0,
so its PS denominator is *answered* slots: a system that answers fewer slots is measured on
an easier denominator. This reads the judge cache that `web_ps_score.py` writes and reports
coverage plus both denominators, so cross-system comparisons can use the all-slots one.

    usage: slot_coverage.py <run_dir> [--ids a,b,c | --ids-file FILE]

Reads <run_dir>/.judge_cache.json — no LLM calls, no re-judging.
Override the MemoryArena checkout with MEMORYARENA_ROOT.
"""
import json, os, sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
MA_ROOT = Path(os.getenv("MEMORYARENA_ROOT", _HERE.parent / "third_party" / "MemoryArena"))
DATA = MA_ROOT / "env/env_systems/web_search_env/data/browsecomp_all_jsons.jsonl"

if len(sys.argv) < 2:
    sys.exit(__doc__)
run_dir = Path(sys.argv[1])
cache_path = run_dir / ".judge_cache.json"
if not cache_path.is_file():
    sys.exit(f"no judge cache at {cache_path} — run web_ps_score.py first")
if not DATA.is_file():
    sys.exit(f"dataset not found at {DATA}\n"
             f"  git submodule update --init third_party/MemoryArena\n"
             f"  (or set MEMORYARENA_ROOT=/path/to/MemoryArena)")

ids = None
if "--ids" in sys.argv:
    ids = [x for x in sys.argv[sys.argv.index("--ids") + 1].split(",") if x]
elif "--ids-file" in sys.argv:
    raw = Path(sys.argv[sys.argv.index("--ids-file") + 1]).read_text().split()
    ids = [x.strip() for x in raw if x.strip() and not x.startswith("#")]

slots = {}
for line in DATA.open():
    o = json.loads(line)
    slots[str(o["id"])] = len(o["question"])       # sub-queries + final combined query

cache = json.load(cache_path.open())
qs = [q for q in (ids or cache.keys()) if q in cache and q in slots]
if not qs:
    sys.exit("no overlapping queries between the cache and the requested ids")

answered = sum(cache[q]["answered"] for q in qs)
total = sum(slots[q] for q in qs)
n = len(qs)
ps_answered = 100 * sum(cache[q]["passed"] / cache[q]["answered"] if cache[q]["answered"] else 0.0
                        for q in qs) / n
ps_allslots = 100 * sum(cache[q]["passed"] / slots[q] for q in qs) / n
sr_hits = sum(1 for q in qs if cache[q]["final_ok"])

print(f"run                  : {run_dir}")
print(f"queries              : {n}")
print(f"slot coverage        : {answered}/{total} = {100*answered/total:.1f}%")
print(f"PS (answered denom.) : {ps_answered:.1f}%   <- what web_ps_score.py reports")
print(f"PS (all-slots denom.): {ps_allslots:.1f}%   <- use this for cross-system comparison")
print(f"SR (final correct)   : {100*sr_hits/n:.1f}%  ({sr_hits}/{n})")

short = [(q, cache[q]["answered"], slots[q]) for q in qs if cache[q]["answered"] < slots[q]]
if short:
    print(f"\nqueries with unanswered slots: {len(short)}")
    for q, a, t in sorted(short, key=lambda r: r[1] - r[2])[:15]:
        print(f"  {q:>6}  {a}/{t}")
    if len(short) > 15:
        print(f"  … and {len(short)-15} more")
