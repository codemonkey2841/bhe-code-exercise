import os, sys, time, json, statistics, tracemalloc
from datetime import datetime, timezone
from sieve import Sieve

HISTORY_PATH = "./profile_history.jsonl"

CASES = [
    {"n": 100, "iterations": 50, "expected": 547},
    {"n": 10_000, "iterations": 10, "expected": 104_743},
    # {"n": 1_000_000, "iterations": 3, "expected": 15_485_867},
    # {"n": 10_000_000, "iterations": 2, "expected": 179_424_691},
    # {"n": 100_000_000, "iterations": 1, "expected": 2_038_074_751},
]

def hbytes(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024: return f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}TB"

def htime(s):
    if s < 1e-3: return f"{s * 1e6:.1f}us"
    if s < 1: return f"{s * 1e3:.1f}ms"
    return f"{s:.2f}s"


label = sys.argv[1]
ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
print(f"Profiling label={label!r}")

cases = []
for c in CASES:
    n, reps, exp = c["n"], c["iterations"], c["expected"]
    print(f"Measure for {n}")
    times = []
    r = None
    for _ in range(reps):
        s = Sieve()
        t0 = time.perf_counter()
        r = s.nth_prime(n)
        times.append(time.perf_counter() - t0)
    # mem in a separate run, tracemalloc wrecks timing
    s = Sieve()
    tracemalloc.start()
    s.nth_prime(n)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    cases.append({
        "n": n, "result": r, "expected": exp, "correct": exp == r,
        "repeats": reps, "time_s_min": min(times),
        "time_s_median": statistics.median(times), "peak_mem_bytes": peak,
    })

run = {"label": label, "timestamp": ts, "cases": cases}

# grab last run for the delta column
prev = None
if os.path.exists(HISTORY_PATH):
    with open(HISTORY_PATH) as f:
        lines = [ln for ln in f if ln.strip()]
    if lines: prev = json.loads(lines[-1])

print(f"\nLabel:     {run['label']}")
print(f"Timestamp: {run['timestamp']}")
if prev:
    print(f"Prev:      {prev['label']} ({prev['timestamp']})")
print()
print(f"{'n':>12}  {'time':>10}  {'peak mem':>10}  {'vs prev':>10}  ok")
prev_by_n = {x["n"]: x for x in (prev or {}).get("cases", [])}
for c in cases:
    n = c["n"]; t = c["time_s_min"]; m = c["peak_mem_bytes"]
    ok = "y" if c["correct"] else "n"
    d = ""
    if n in prev_by_n:
        pt = prev_by_n[n]["time_s_min"]
        if pt > 0: d = f"{(t / pt - 1) * 100:+.0f}%"
    print(f"{n:>12,}  {htime(t):>10}  {hbytes(m):>10}  {d:>10}  {ok}")

with open(HISTORY_PATH, "a") as f:
    f.write(json.dumps(run) + "\n")
print(f"\nAppended to {HISTORY_PATH}")
