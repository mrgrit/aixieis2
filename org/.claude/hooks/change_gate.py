#!/usr/bin/env python3
"""PreToolUse(change_prepare | change_apply): 변경관리 규칙을 '결정론적으로' 검사한다.

R1 변경 요청서에는 시험 계획(test_plan)과 원복 방법(rollback)이 있어야 한다.
R2 변경·차단에는 근거(evidence_refs)가 하나 이상 있어야 한다. 근거 없는 차단 금지.
R3 적용(change_apply)은 승인 ID 가 있어야 한다. 승인 상태는 랩 서버가 다시 확인한다.

스킬에 같은 문장을 써 두는 것(지침)과 여기서 막는 것(강제)이 결과를 어떻게 바꾸는지가
15장 '강제 실험'의 주제다. ORG_GATES=off 로 끄고 비교할 수 있다.
"""
import json
import os
import sys
from _common import append, now, read_input

inp = read_input()
if os.environ.get("ORG_GATES", "on") == "off":
    sys.exit(0)

tool = inp.get("tool_name", "")
ti = inp.get("tool_input") or {}
problems = []
if tool.endswith("change_prepare"):
    for key, rule in (("test_plan", "R1 시험 계획"), ("rollback", "R1 원복 방법")):
        if not str(ti.get(key, "")).strip():
            problems.append(f"{rule}(={key})이 비어 있습니다")
    if not ti.get("evidence_refs"):
        problems.append("R2 근거(evidence_refs)가 없습니다. 조회한 로그·설정의 위치를 적으세요")
elif tool.endswith("change_apply"):
    if not str(ti.get("approval_id", "")).startswith("A-"):
        problems.append("R3 승인 ID 가 없습니다. approval_request 로 승인을 받은 뒤 적용하세요")

append("gate.jsonl", {"ts": now(), "session_id": inp.get("session_id"), "agent_type": inp.get("agent_type"),
                      "tool": tool, "decision": "deny" if problems else "allow", "problems": problems})
if problems:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "변경관리 규칙 위반: " + "; ".join(problems)}}, ensure_ascii=False))
sys.exit(0)
