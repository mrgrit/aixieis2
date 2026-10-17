#!/usr/bin/env python3
"""SessionStart: 이 세션이 어떤 지침으로 시작했는지 해시를 남긴다.

실험에서 '스킬을 바꿨더니 결과가 달라졌다'고 말하려면, 그 실행이 정말 바뀐 스킬을
읽고 시작했는지 증명할 수 있어야 한다. stdout 은 모델 컨텍스트에 들어가므로 아무것도 출력하지 않는다.
"""
import hashlib
from _common import PROJECT, append, now, read_input


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else None


inp = read_input()
agent = inp.get("agent_type")
files = {"CLAUDE.md": sha(PROJECT / "CLAUDE.md"), "settings.json": sha(PROJECT / ".claude/settings.json")}
if agent:
    files[f"agents/{agent}.md"] = sha(PROJECT / ".claude/agents" / f"{agent}.md")
for skill in sorted((PROJECT / ".claude/skills").glob("*/SKILL.md")):
    files[f"skills/{skill.parent.name}"] = sha(skill)
append("harness.jsonl", {"ts": now(), "session_id": inp.get("session_id"), "source": inp.get("source"),
                         "agent_type": agent, "files": files})
