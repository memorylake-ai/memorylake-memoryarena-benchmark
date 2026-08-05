#!/usr/bin/env python3
"""Merge multi-hop runs at slot granularity, original-run-first.

Used to raise slot coverage without overwriting scored answers: a slot takes its answer from
the FIRST source directory that produced one, so re-run output only fills slots the original
run left empty. Sources are given in priority order (original first).

    usage: merge_slots.py <out_dir> <ids|ALL> <src_dir> [<src_dir> ...]

Each selected run file is symlinked into <out_dir>, mirroring the query/sub-query layout, so
`web_ps_score.py <out_dir>` scores the merged set without copying data.

Why first-wins rather than last-wins: a later run is not necessarily better. Scoring the same
20 queries twice under different output budgets gave SR 20.0% and 15.0%, so preferring the
newer answer silently replaces some correct answers with incorrect ones. Keeping the original
answer means the re-run can only add coverage, never move a scored slot.

Override the MemoryArena checkout with MEMORYARENA_ROOT.
"""
import glob, json, os, shutil, sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
MA_ROOT = Path(os.getenv("MEMORYARENA_ROOT", _HERE.parent / "third_party" / "MemoryArena"))
DATA = MA_ROOT / "env/env_systems/web_search_env/data/browsecomp_all_jsons.jsonl"

if len(sys.argv) < 4:
    sys.exit(__doc__)
out, ids_arg, srcs = Path(sys.argv[1]), sys.argv[2], [Path(s) for s in sys.argv[3:]]
if not DATA.is_file():
    sys.exit(f"dataset not found at {DATA}\n"
             f"  git submodule update --init third_party/MemoryArena\n"
             f"  (or set MEMORYARENA_ROOT=/path/to/MemoryArena)")

slots = {}
for line in DATA.open():
    o = json.loads(line)
    slots[str(o["id"])] = len(o["question"])

if ids_arg.upper() == "ALL":
    ids = sorted({p.name.split("_", 1)[1] for s in srcs for p in s.glob("query_*")}, key=int)
else:
    ids = [x for x in ids_arg.split(",") if x]


def slot_rel(qid, i, n):
    return f"query_{qid}/final_query" if i == n else f"query_{qid}/subqueries/subquery_{i}"


def answered_file(d, rel):
    """First run file under d/rel that contains a non-empty output_text, else None."""
    for f in sorted(glob.glob(str(d / rel / "*.json"))):
        try:
            res = json.load(open(f)).get("result", [])
        except Exception:
            continue
        if any(isinstance(e, dict) and e.get("type") == "output_text" and e.get("output")
               for e in res):
            return f
    return None


if out.is_dir():
    shutil.rmtree(out)
out.mkdir(parents=True)

filled = collected = 0
contrib = {str(s): 0 for s in srcs}
gaps = []
for qid in ids:
    if qid not in slots:
        continue
    n = slots[qid]
    for i in range(1, n + 1):
        rel = slot_rel(qid, i, n)
        collected += 1
        for s in srcs:                                  # priority order: first wins
            f = answered_file(s, rel)
            if f:
                dst = out / rel
                dst.mkdir(parents=True, exist_ok=True)
                link = dst / Path(f).name
                if not link.exists():
                    link.symlink_to(Path(f).resolve())
                filled += 1
                contrib[str(s)] += 1
                break
        else:
            gaps.append((qid, i, n))

print(f"merged into : {out}")
print(f"slot coverage: {filled}/{collected} = {100*filled/collected:.1f}%   ({len(ids)} queries)")
print("answered slots contributed by source (priority order):")
for s in srcs:
    print(f"  {contrib[str(s)]:>5}  {s}")
if gaps:
    print(f"\nstill unanswered: {len(gaps)} slots")
    by_q = {}
    for q, i, n in gaps:
        by_q.setdefault(q, []).append(i)
    for q, lst in sorted(by_q.items(), key=lambda kv: -len(kv[1]))[:12]:
        print(f"  {q:>6}  {len(lst)} of {slots[q]} slots")
print(f"\nnext: python eval/web_ps_score.py {out}")
