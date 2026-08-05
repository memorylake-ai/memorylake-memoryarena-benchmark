import json, glob, os, sys, hashlib
from pathlib import Path

# PATH SETUP (differs from the copy used in-tree): this script ships in the benchmark
# companion repo, so the MemoryArena checkout lives under third_party/. Override with
# MEMORYARENA_ROOT if your checkout is elsewhere.
_HERE = Path(__file__).resolve().parent
MA_ROOT = Path(os.getenv("MEMORYARENA_ROOT", _HERE.parent / "third_party" / "MemoryArena"))
if not (MA_ROOT / "env/env_systems/web_search_env").is_dir():
    sys.exit(f"MemoryArena checkout not found at {MA_ROOT}\n"
             f"  git submodule update --init third_party/MemoryArena\n"
             f"  (or set MEMORYARENA_ROOT=/path/to/MemoryArena)")

RUN_DIR = sys.argv[1] if len(sys.argv) > 1 else sys.exit("usage: web_ps_score.py <run_dir>")
DATA = str(MA_ROOT / "env/env_systems/web_search_env/data/browsecomp_all_jsons.jsonl")
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gpt-5-mini")

sys.path.insert(0, str((MA_ROOT / "env/env_systems/web_search_env").resolve()))
from evaluate_with_openai import create_judge_prompt, call_openai_judge, parse_judge_response
import openai
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL") or None)

# Denominator = every query present (no skip; no-answer counts as 0). WEB_SKIP_IDS force-skips;
# WEB_ONLY_IDS restricts to a subset. Per-query judge verdicts are CACHED in RUN_DIR/.judge_cache.json
# keyed by a hash of the query's answers — a query is judged ONCE; unchanged queries reuse the cache.
SKIP_IDS = set(x for x in (os.getenv("WEB_SKIP_IDS") or "").split(",") if x)
ONLY_IDS = set(x for x in (os.getenv("WEB_ONLY_IDS") or "").split(",") if x)
CACHE_FILE = os.path.join(RUN_DIR, ".judge_cache.json")
cache = {}
try:
    if os.path.exists(CACHE_FILE):
        cache = json.load(open(CACHE_FILE))
except Exception:
    cache = {}

gt = {}
for l in open(DATA):
    o = json.loads(l); gt[str(o["id"])] = o

def last_answer(result_path):
    fs = glob.glob(result_path + "/*.json")
    if not fs: return None
    r = json.load(open(fs[0])).get("result", [])
    ans = [e.get("output") for e in r if e.get("type") == "output_text" and e.get("output")]
    return ans[-1] if ans else None

def judge(question, pred, correct):
    if not pred: return False
    try:
        resp = call_openai_judge(client=client, prompt=create_judge_prompt(question, pred, correct),
                                 model=JUDGE_MODEL, max_output_tokens=8000, reasoning_effort=None, system_prompt=None)
        txt = resp.output_text if hasattr(resp, "output_text") else ""
        return bool(parse_judge_response(txt).get("correct", False))
    except Exception as e:
        print(f"    judge err: {str(e)[:80]}", file=sys.stderr); return False

per_query_ps = []; sr_list = []; njudged = 0; ncached = 0
for qd in sorted(glob.glob(f"{RUN_DIR}/query_*")):
    qid = os.path.basename(qd).split("_")[1]
    if qid in SKIP_IDS:
        continue
    if ONLY_IDS and qid not in ONLY_IDS:
        continue
    g = gt.get(qid)
    if not g: continue
    qs, ans = g["question"], g["answer"]
    N = len(qs)
    subpreds = [last_answer(f"{qd}/subqueries/subquery_{i}") for i in range(1, N)]
    fpred = last_answer(f"{qd}/final_query")
    sig = hashlib.md5(json.dumps([subpreds, fpred], ensure_ascii=False).encode()).hexdigest()
    c = cache.get(qid)
    if c and c.get("sig") == sig:
        answered, passed, final_ok = c["answered"], c["passed"], c["final_ok"]; ncached += 1
        tag = "cached"
    else:
        passed = 0; answered = 0
        for i in range(1, N):
            pred = subpreds[i-1]
            if not pred: continue
            answered += 1
            if judge(qs[i-1], pred, ans[i-1]): passed += 1
        final_ok = False
        if fpred:
            answered += 1
            final_ok = judge(qs[-1], fpred, ans[-1])
            if final_ok: passed += 1
        cache[qid] = {"sig": sig, "answered": answered, "passed": passed, "final_ok": bool(final_ok)}
        njudged += 1; tag = "judged"
    ps = (passed / answered) if answered else 0.0
    per_query_ps.append(ps); sr_list.append(1 if final_ok else 0)
    print(f"q{qid}: {passed}/{answered} (PS={ps*100:.0f}%) final={'✓' if final_ok else '✗'} [{tag}]", flush=True)

try:
    json.dump(cache, open(CACHE_FILE, "w"), ensure_ascii=False)
except Exception:
    pass

n = len(per_query_ps) or 1
print(f"\n===== {RUN_DIR.split('/')[-1]} =====")
print(f"queries scored (denominator): {len(per_query_ps)}  [judged {njudged}, cached {ncached}]")
print(f"PS (mean per-query pass rate over answered subtasks) = {sum(per_query_ps)/n*100:.1f}%")
print(f"SR (final correct)          = {sum(sr_list)/n*100:.1f}%")
