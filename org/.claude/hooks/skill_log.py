#!/usr/bin/env python3
"""PostToolUse(Skill): 어떤 스킬을 언제 불러왔는지 남긴다. 실험 채점의 1차 근거."""
from _common import append, now, read_input

inp = read_input()
ti = inp.get("tool_input") or {}
append("skill-use.jsonl", {"ts": now(), "session_id": inp.get("session_id"),
                           "agent_type": inp.get("agent_type"),
                           "skill": ti.get("skill") or ti.get("name") or ti.get("command"),
                           "args": ti.get("args")})
