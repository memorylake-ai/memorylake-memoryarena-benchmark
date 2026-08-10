#!/usr/bin/env python3
"""Rebuild the controlled 20-query multi-hop subset, and verify the published manifest.

The subset is a deterministic proportional stratified sample — there is no random seed:

  1. stratify the 221 progressively-decomposed queries by **decomposition depth**
     (`num_slots` = sub-queries plus the final combined query);
  2. give each stratum a quota of `round(stratum_size * k / 221)`;
  3. within a stratum, take the lowest query ids.

Depth is the variable this task is built to stress — a conclusion has to survive every step of
the chain — so sampling proportionally on it keeps the subset's difficulty profile matched to
the full set instead of skewing it toward short or long chains.

Population and depths come from `queries/web_search_memorylake_221_ids.tsv`, so this runs
offline against files in this repository; the raw BrowseComp-Plus dataset is not needed.

    usage: sample_controlled_20.py [-k 20] [--tsv] [--verify]

    --tsv     emit the manifest format (query_id, num_slots), sorted by id
    --verify  compare against queries/web_search_controlled_20_ids.tsv, exit 1 on mismatch

Note on provenance: the original selection script was not preserved. This rule was recovered
by analysing the published subset and reproduces it exactly (all 20 ids, all 8 strata quotas),
which is what makes the sample verifiable — but it is a reconstruction, not the original code.
"""
import collections, sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
POP = _HERE / "queries" / "web_search_memorylake_221_ids.tsv"
PUBLISHED = _HERE / "queries" / "web_search_controlled_20_ids.tsv"


def read_manifest(path):
    rows = {}
    for i, line in enumerate(path.read_text().splitlines()):
        line = line.strip()
        if not line or (i == 0 and line.lower().startswith("query_id")):
            continue
        qid, depth = line.split("\t")[:2]
        rows[qid.strip()] = int(depth)
    return rows


if not POP.is_file():
    sys.exit(f"population manifest not found: {POP}")

k = int(sys.argv[sys.argv.index("-k") + 1]) if "-k" in sys.argv else 20
depth = read_manifest(POP)
total = len(depth)

strata = collections.defaultdict(list)
for qid, d in depth.items():
    strata[d].append(qid)

picked = []
for d in sorted(strata):
    quota = round(len(strata[d]) * k / total)
    picked += [(d, q) for q in sorted(strata[d], key=int)[:quota]]
picked.sort(key=lambda t: (t[0], int(t[1])))       # by depth, then id
by_id = sorted((q for _, q in picked), key=int)

if "--tsv" in sys.argv:
    print("query_id\tnum_slots")
    for q in by_id:
        print(f"{q}\t{depth[q]}")
    sys.exit(0)

if "--verify" in sys.argv:
    if not PUBLISHED.is_file():
        sys.exit(f"published manifest not found: {PUBLISHED}")
    want = read_manifest(PUBLISHED)
    ok = want == {q: depth[q] for q in by_id}
    print(f"reconstructed : {len(by_id)} queries")
    print(f"published     : {len(want)} queries")
    if ok:
        print("match         : yes — the published subset is exactly reproduced")
        sys.exit(0)
    got = {q: depth[q] for q in by_id}
    print("match         : NO")
    for q in sorted(set(got) | set(want), key=int):
        if got.get(q) != want.get(q):
            print(f"  {q:>6}  reconstructed={got.get(q, '-')}  published={want.get(q, '-')}")
    sys.exit(1)

print(f"population : {total} progressively-decomposed queries "
      f"({sum(depth.values())} slots)")
print(f"target     : k={k}")
print()
print(f"{'depth':>6} {'in population':>14} {'quota':>6}  ids")
for d in sorted(strata):
    quota = round(len(strata[d]) * k / total)
    ids = [q for dd, q in picked if dd == d]
    if quota or ids:
        print(f"{d:>6} {len(strata[d]):>14} {quota:>6}  {','.join(ids)}")
print()
print(f"selected   : {len(by_id)} queries / {sum(depth[q] for q in by_id)} slots")
print(",".join(q for _, q in picked))
