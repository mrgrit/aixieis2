#!/usr/bin/env python3
"""Stop: 최종 보고가 조직 보고 형식(결론·근거·한계)을 갖췄는지 검사한다.

기본은 꺼져 있다(ORG_REPORT_GATE=1 일 때만 동작). 같은 형식을 CLAUDE.md 에 '지침'으로만
두었을 때와 이 훅으로 '강제'했을 때의 준수율을 비교하는 실험(X-D3)에 쓴다.
"""
import json
import os
import sys
from _common import append, now, read_input

if os.environ.get("ORG_REPORT_GATE") != "1":
    sys.exit(0)
inp = read_input()
if inp.get("stop_hook_active"):
    sys.exit(0)
msg = inp.get("last_assistant_message") or ""
missing = [h for h in ("결론", "근거", "한계") if h not in msg]
append("report-gate.jsonl", {"ts": now(), "session_id": inp.get("session_id"),
                             "agent_type": inp.get("agent_type"), "missing": missing})
if missing:
    print(json.dumps({"decision": "block",
                      "reason": f"보고 형식 누락: {', '.join(missing)}. CLAUDE.md 의 보고 형식으로 다시 정리하세요."},
                     ensure_ascii=False))
sys.exit(0)
