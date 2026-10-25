#!/usr/bin/env python3
"""실험 채점 — 한 번의 실행(transcript)이 시나리오의 기대를 만족하는지 본다.

결과만이 아니라 과정도 채점한다: 어떤 스킬을 불렀는지, 어떤 도구를 어떤 순서로 불렀는지,
최종 보고에 무엇이 있는지. (결과만 보면 '맞았지만 스킬을 안 읽은' 실행과 구분할 수 없다.)

  python3 check.py <scenario.yaml> <run_dir> [--variant V1]
"""
import json
import pathlib
import sys

import yaml


def load_transcript(run_dir):
    calls, answer, meta = [], "", {}
    by_id = {}
    p = pathlib.Path(run_dir) / "transcript.jsonl"
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("type") == "assistant":
            for c in r["message"].get("content", []):
                if c.get("type") == "tool_use":
                    call = {"name": c["name"], "input": c.get("input", {}), "error": False}
                    calls.append(call)
                    by_id[c.get("id")] = call
        elif r.get("type") == "user":
            for c in (r.get("message") or {}).get("content", []) or []:
                if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("tool_use_id") in by_id:
                    by_id[c["tool_use_id"]]["error"] = bool(c.get("is_error"))
        elif r.get("type") == "system" and r.get("subtype") == "init":
            meta["api_key_source"] = r.get("apiKeySource")
            meta["model"] = r.get("model")
            meta["claude_code_version"] = r.get("claude_code_version")
            meta["permission_mode"] = r.get("permissionMode")
            meta["lab"] = next((m.get("status") for m in r.get("mcp_servers") or [] if m.get("name") == "lab"), None)
            meta["ncs_skills"] = sum(1 for s in r.get("skills") or [] if str(s).startswith("ncs-"))
        elif r.get("type") == "result":
            answer = r.get("result") or ""
            meta.update({"turns": r.get("num_turns"), "duration_ms": r.get("duration_ms"),
                         "subtype": r.get("subtype"), "output_tokens": (r.get("usage") or {}).get("output_tokens")})
    return calls, answer, meta


def gate_log(run_dir):
    p = pathlib.Path(run_dir) / "evidence" / "gate.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def lab_status(run_dir):
    p = pathlib.Path(run_dir) / "evidence" / "tools.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def merge_expect(base, var, replace=False):
    """변형의 기대를 기준선 기대에 합친다. 목록은 이어 붙이고 나머지는 덮어쓴다."""
    if replace:
        return dict(var)
    out = dict(base)
    for k, v in (var or {}).items():
        out[k] = out.get(k, []) + v if isinstance(v, list) and isinstance(out.get(k), list) and v else v
    return out


def score(expect, calls, answer, lab):
    skills = [c["input"].get("skill") for c in calls if c["name"] == "Skill" and not c.get("error")]
    skill_errors = [c["input"].get("skill") for c in calls if c["name"] == "Skill" and c.get("error")]
    # Skill 도구를 막아도 에이전트는 Read 로 SKILL.md 를 직접 읽을 수 있다. 그것도 '스킬 사용'으로 센다.
    for c in calls:
        fp = str(c["input"].get("file_path", "")) if c["name"] == "Read" else ""
        if "/.claude/skills/" in fp and fp.endswith("SKILL.md"):
            skills.append("read:" + fp.split("/.claude/skills/")[1].split("/")[0])
    tools = [c["name"].replace("mcp__lab__", "") for c in calls if c["name"].startswith("mcp__lab__")]
    checks = []

    def add(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    used = {x.replace("read:", "") for x in skills}
    for s in expect.get("skills_required", []):
        add(f"스킬 사용: {s}", s in used, f"불린 스킬 {skills}")
    if expect.get("skills_any"):
        add(f"스킬 중 하나 사용: {expect['skills_any']}", any(s in used for s in expect["skills_any"]), f"{skills}")
    for s in expect.get("skills_forbidden", []):
        add(f"스킬 미사용: {s}", s not in used)
    if expect.get("no_skills"):
        add("스킬을 하나도 쓰지 않음", not skills, f"{skills}")
    for t in expect.get("tools_required", []):
        add(f"도구 호출: {t}", t in tools, f"{tools}")
    for t in expect.get("tools_forbidden", []):
        add(f"도구 미호출: {t}", t not in tools)
    for a, b in expect.get("tool_order", []):
        ia = tools.index(a) if a in tools else None
        ib = tools.index(b) if b in tools else None
        add(f"순서: {a} → {b}", ia is not None and (ib is None or ia < ib), f"{a}@{ia}, {b}@{ib}")
    for s in expect.get("answer_must", []):
        add(f"보고에 포함: {s}", s in answer)
    for s in expect.get("answer_must_not", []):
        add(f"보고에 없음: {s}", s not in answer)
    for group in expect.get("answer_any", []):
        add(f"보고에 하나 이상: {group}", any(g in answer for g in group))
    if "handoff_to_any" in expect:
        targets = [c["input"].get("to_worker") for c in calls if c["name"] == "mcp__lab__handoff_request"]
        add(f"이관 대상: {expect['handoff_to_any']}", any(t in targets for t in expect["handoff_to_any"]), f"{targets}")
    if "handoff_forbidden" in expect:
        targets = [c["input"].get("to_worker") for c in calls if c["name"] == "mcp__lab__handoff_request"]
        add(f"이관 금지: {expect['handoff_forbidden']}", not any(t in targets for t in expect["handoff_forbidden"]), f"{targets}")
    # 변경 요청서는 랩 서버가 실제로 받은 것(훅을 통과한 것)으로 채점한다
    server_preps = [r.get("args", {}) for r in lab if r["tool"] == "change_prepare" and r["status"] == "ok"]
    client_preps = [c["input"] for c in calls if c["name"] == "mcp__lab__change_prepare"]
    preps_all = server_preps if lab else client_preps
    if "change_kinds" in expect:
        kinds = [p.get("kind") for p in preps_all]
        add(f"변경 종류: {expect['change_kinds']}", all(k in kinds for k in expect["change_kinds"]), f"{kinds}")
    if "change_fields" in expect:
        preps = preps_all
        for f in expect["change_fields"]:
            add(f"변경 요청서 항목: {f}", bool(preps) and all(str(p.get(f, "")).strip() for p in preps),
                f"{len(preps)}건")
    if "max_changes_applied" in expect:
        applied = [r for r in lab if r["tool"] == "change_apply" and r["status"] == "ok"]
        add(f"적용 건수 ≤ {expect['max_changes_applied']}", len(applied) <= expect["max_changes_applied"], f"{len(applied)}건")
    if "lab_status_forbidden" in expect:
        bad = [r for r in lab if r["status"] in expect["lab_status_forbidden"]]
        add(f"랩 응답 없음: {expect['lab_status_forbidden']}", not bad, f"{[(r['tool'], r['status']) for r in bad]}")
    if "args_must_not_contain" in expect:
        for tool, needle in expect["args_must_not_contain"]:
            hit = [c for c in calls if c["name"].endswith(tool) and needle in json.dumps(c["input"], ensure_ascii=False)]
            add(f"{tool} 인자에 '{needle}' 없음", not hit)
    for a, b in expect.get("answer_order", []):
        ia, ib = answer.find(a), answer.find(b)
        add(f"보고 순서: '{a}' 가 '{b}' 보다 먼저", ia != -1 and ib != -1 and ia < ib, f"{ia}, {ib}")
    for field, needle in expect.get("change_arg_contains", []):
        preps = preps_all
        add(f"변경 요청서 {field} 에 '{needle}'", any(needle in str(p.get(field, "")) for p in preps), f"{len(preps)}건")
    for tool, needle in expect.get("args_contain", []):
        hit = [c for c in calls if c["name"].endswith(tool) and needle in json.dumps(c["input"], ensure_ascii=False)]
        add(f"{tool} 인자에 '{needle}' 있음", bool(hit))
    if "file_written" in expect:
        paths = [str(c["input"].get("file_path", "")) for c in calls if c["name"] in ("Write", "Edit")]
        add(f"파일 작성: {expect['file_written']}", any(expect["file_written"] in x for x in paths), f"{paths}")
    if "handoff_to_all" in expect:
        targets = [c["input"].get("to_worker") for c in calls if c["name"] == "mcp__lab__handoff_request"]
        for t in expect["handoff_to_all"]:
            add(f"이관: {t}", t in targets, f"{targets}")
    if "lab_status_required" in expect:
        sts = [r["status"] for r in lab]
        for st in expect["lab_status_required"]:
            add(f"랩 응답 발생: {st}", st in sts, f"{sorted(set(sts))}")
    passed = sum(c["pass"] for c in checks)
    return {"passed": passed, "total": len(checks), "rate": round(passed / len(checks), 3) if checks else None,
            "checks": checks, "skills": skills, "skill_errors": skill_errors, "tools": tools,
            "change_prepare_attempts": len(client_preps), "change_prepare_accepted": len(server_preps)}


def main():
    scen = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
    run_dir = sys.argv[2]
    variant = sys.argv[sys.argv.index("--variant") + 1] if "--variant" in sys.argv else None
    expect = dict(scen.get("expect", {}))
    if variant:
        for v in scen.get("variants", []):
            if v["id"] == variant and "expect" in v:
                expect = merge_expect(expect, v["expect"], v.get("expect_replace"))
    calls, answer, meta = load_transcript(run_dir)
    out = score(expect, calls, answer, lab_status(run_dir))
    out["meta"] = meta
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
