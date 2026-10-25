#!/usr/bin/env python3
"""실행 한 건 발췌: 도구 호출 순서, 변경 요청서, 이관, 게이트 거절, 보고서 결론.

python3 docs/screens/excerpt.py <ID> [변형] [실행 번호(1부터, 기본 1)] [결론 줄 수]
"""
import glob, json, sys, textwrap, unicodedata


def dwrap(s, width=132, indent="  ", cont="    "):
    out, cur, w = [], indent, len(indent)
    for ch in s:
        cw = 2 if unicodedata.east_asian_width(ch) in "WF" else 1
        if w + cw > width:
            out.append(cur); cur, w = cont, len(cont)
        cur += ch; w += cw
    out.append(cur)
    return out


sid = sys.argv[1]
var = sys.argv[2] if len(sys.argv) > 2 else "base"
n = int(sys.argv[3]) if len(sys.argv) > 3 else 1
lines = int(sys.argv[4]) if len(sys.argv) > 4 else 14
runs = sorted(glob.glob(f"experiments/results/{sid}/{var}/*/"))
run = runs[n - 1]
ev = run + "evidence/"


def jl(p):
    try:
        return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    except FileNotFoundError:
        return []


def short(v, w=118, maxl=4):
    s = str(v).replace("\n", " / ")
    out = textwrap.wrap(s, w)
    return out[:maxl] + (["…"] if len(out) > maxl else [])


tools = jl(ev + "tools.jsonl")
print(f"[실행] {run}")
print("[도구 순서] " + " → ".join(f"{t['tool']}({t.get('status')})" if t.get("status") != "ok" else t["tool"] for t in tools))
for t in tools:
    a = t.get("args", {})
    if t["tool"] == "change_prepare":
        print(f"[변경 요청서] status={t.get('status')} kind={a.get('kind')} target={a.get('target')}")
        for k in ("spec", "reason", "test_plan", "rollback", "evidence_refs"):
            if a.get(k):
                body = short(a[k])
                print(f"  {k}: {body[0]}")
                for b in body[1:]:
                    print(f"      {b}")
        if t.get("note"):
            print(f"  note: {t['note']}")
    elif t["tool"] in ("handoff_request", "approval_request", "change_apply"):
        to = a.get("to_worker") or a.get("to") or a.get("change_id") or ""
        print(f"[{t['tool']}] status={t.get('status')} {to} {short(t.get('note',''), 100, 1)[0] if t.get('note') else ''}")
for g in jl(ev + "gate.jsonl"):
    if g.get("decision") != "allow":
        print(f"[게이트 거절] {g.get('tool')} {g.get('problems')}")
ans = open(run + "answer.md", encoding="utf-8").read().splitlines()
start = next((i for i, l in enumerate(ans) if l.startswith("## 결론") or l.startswith("판정코드")), 0)
print("[answer.md]")
for l in ans[start:start + lines]:
    for x in dwrap(l):
        print(x)
