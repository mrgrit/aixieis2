#!/usr/bin/env python3
"""실행별 집계: 변형·실행마다 통과 수, 변경 도구 호출, 이관 대상, 게이트 거절, 서버 거절.

python3 docs/screens/tally.py <ID> [보고서에서 셀 문구 ...]
"""
import glob, json, os, sys

sid = sys.argv[1]
words = sys.argv[2:]
base = f"experiments/results/{sid}"


def jl(p):
    try:
        return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    except FileNotFoundError:
        return []


rows = []
for var in sorted(os.listdir(base)):
    for run in sorted(glob.glob(f"{base}/{var}/*/")):
        ev = run + "evidence/"
        tools = jl(ev + "tools.jsonl")
        gate = jl(ev + "gate.jsonl")
        try:
            sc = json.load(open(run + "score.json", encoding="utf-8"))
            score = f"{sc['passed']}/{sc['total']}"
        except Exception:
            score = "?"
        ans = open(run + "answer.md", encoding="utf-8").read() if os.path.exists(run + "answer.md") else ""
        cnt = lambda t: sum(1 for x in tools if x.get("tool") == t)
        to = [x.get("args", {}).get("to_worker") or x.get("args", {}).get("to") for x in tools if x.get("tool") == "handoff_request"]
        kinds = [x.get("args", {}).get("kind") for x in tools if x.get("tool") == "change_prepare" and x.get("status") == "ok"]
        deny = [g for g in gate if g.get("decision") != "allow"]
        st = {}
        for x in tools:
            if x.get("status") not in ("ok", None):
                st[x["status"]] = st.get(x["status"], 0) + 1
        row = [var, os.path.basename(run.rstrip("/")).split("-")[-1], score,
               f"prep={cnt('change_prepare')}({','.join(k or '?' for k in kinds)})",
               f"apply={cnt('change_apply')}", f"appr={cnt('approval_request')}",
               f"gate거절={len(deny)}", "이관=" + (",".join(t or "?" for t in to) or "-"),
               "서버응답=" + (",".join(f"{k}:{v}" for k, v in sorted(st.items())) or "-")]
        for w in words:
            row.append(f"'{w}'={ans.count(w)}")
        rows.append(row)

for r in rows:
    print("  ".join(r))
