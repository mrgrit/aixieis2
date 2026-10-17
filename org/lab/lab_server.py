#!/usr/bin/env python3
"""lab — 업무담당자 에이전트가 랩을 보는 유일한 창구 (MCP stdio 서버).

두 가지 모드가 있다.

  LAB_MODE=mock (기본)  실험 시나리오의 fixtures 를 돌려준다. 매번 같은 자료가 나오므로
                        스킬을 바꿨을 때 '일하는 방법'이 바뀌었는지만 비교할 수 있다.
  LAB_MODE=live         kt66 컨테이너를 읽기 전용으로 조회한다(docker exec). 변경은 어느
                        모드에서든 '변경 요청서'로만 남고, 승인 없이는 적용되지 않는다.

환경 변수
  LAB_WORKER        이 세션의 직무 ID (roles.yaml). 직무 밖 도구는 role_boundary 로 거절.
  LAB_FIXTURES      mock 모드에서 읽을 시나리오 YAML (fixtures: 키) 또는 fixtures 파일.
  LAB_EVIDENCE_DIR  도구 호출 기록(tools.jsonl)과 변경·승인 상태(state.json)를 남길 곳.

외부 패키지 없이 동작한다(PyYAML 이 있으면 YAML, 없으면 JSON fixtures 만 읽는다).
"""
import datetime
import json
import os
import pathlib
import subprocess
import sys
import uuid

HERE = pathlib.Path(__file__).resolve().parent
ORG = HERE.parent

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


def load_data(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    if path.endswith((".yaml", ".yml")):
        if yaml is None:
            raise RuntimeError("PyYAML 이 없어 YAML 을 읽을 수 없습니다: pip install pyyaml")
        return yaml.safe_load(text)
    return json.loads(text)


ROLES = load_data(str(HERE / "roles.yaml"))
WORKER = os.environ.get("LAB_WORKER", "").strip()
MODE = os.environ.get("LAB_MODE", "mock").strip()
EVIDENCE = pathlib.Path(os.environ.get("LAB_EVIDENCE_DIR", str(ORG / "evidence" / "manual")))
EVIDENCE.mkdir(parents=True, exist_ok=True)

FIXTURES = {}
if os.environ.get("LAB_FIXTURES"):
    raw = load_data(os.environ["LAB_FIXTURES"]) or {}
    FIXTURES = raw.get("fixtures", raw) or {}
# 감사 실습용: 이전 근무자의 도구 기록을 미리 심는다(이미 기록이 있으면 건드리지 않는다)
if FIXTURES.get("seed_tools_log") and not (EVIDENCE / "tools.jsonl").exists():
    with open(EVIDENCE / "tools.jsonl", "w", encoding="utf-8") as f:
        for rec in FIXTURES["seed_tools_log"]:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="seconds")


# ── 상태: 변경 요청서와 승인. 같은 증적 폴더를 쓰는 세션끼리 공유한다 ─────────────
STATE_FILE = EVIDENCE / "state.json"


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    state = {"changes": {}, "approvals": {}, "tickets": [], "handoffs": []}
    for c in FIXTURES.get("changes", []) or []:
        state["changes"][c["change_id"]] = c
    for a in FIXTURES.get("approvals", []) or []:
        state["approvals"][a["approval_id"]] = a
    for h in FIXTURES.get("handoffs", []) or []:
        state["handoffs"].append(h)
    return state


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def log_call(tool, args, status, note=""):
    rec = {"ts": now(), "worker": WORKER or "(unset)", "tool": tool, "args": args,
           "status": status, "note": note, "mode": MODE}
    with open(EVIDENCE / "tools.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ── 도구 정의 ────────────────────────────────────────────────────────────────
def S(props=None, required=None):
    return {"type": "object", "properties": props or {}, "required": required or []}


STR = {"type": "string"}
TIME = {"type": "string", "description": "ISO 8601 시각(KST). 비우면 시나리오 전체 기간"}

TOOLS = {
    # 조회
    "siem_search": ("SIEM(Wazuh)에서 보안 이벤트를 검색한다. query 의 단어가 모두 들어간 이벤트만 돌려준다.",
                    S({"query": STR, "start": TIME, "end": TIME}, ["query"])),
    "log_read": ("원본 로그를 읽는다. source: fw | ips | waf | web | host | auth | vpn",
                 S({"source": STR, "filter": STR, "start": TIME, "end": TIME}, ["source"])),
    "fw_rules": ("방화벽 정책(룰 순서 포함)을 읽는다.", S({"device": STR})),
    "ids_rules": ("IDS/IPS 탐지 룰을 읽는다.", S({"filter": STR})),
    "waf_events": ("WAF 탐지·차단 이벤트를 읽는다.", S({"filter": STR, "start": TIME, "end": TIME})),
    "waf_config": ("WAF 설정(모드, 패러노이아 레벨, 임계값, 예외 규칙)을 읽는다.", S()),
    "host_config": ("서버 설정 항목을 읽는다. item 예: login.defs, pam, sshd_config, services, file_perms",
                    S({"host": STR, "item": STR}, ["host"])),
    "host_accounts": ("서버 계정 목록과 속성(UID, 셸, 마지막 로그인, sudo 여부)을 읽는다.",
                      S({"host": STR}, ["host"])),
    "package_inventory": ("서버에 설치된 패키지와 버전을 읽는다.", S({"host": STR}, ["host"])),
    "vuln_feed": ("취약점 정보(CVSS, EPSS, KEV 등재 여부, 패치 유무)를 조회한다.",
                  S({"cve": STR, "host": STR})),
    "backup_status": ("백업 작업 이력과 형태를 읽는다.", S({"host": STR})),
    "network_topology": ("존·구간·자산 배치와 트래픽 경로를 읽는다.", S()),
    "asset_inventory": ("자산 대장(중요도, 담당, 존)을 조회한다.", S({"filter": STR})),
    "incident_history": ("과거 침해사고 이력(공격 히스토리)을 조회한다.", S({"filter": STR})),
    "policy_docs": ("조직의 보안 정책·지침·절차서·매뉴얼 목록과 내용을 조회한다.", S({"filter": STR})),
    "code_read": ("애플리케이션 소스 코드를 읽는다.", S({"app": STR, "path": STR}, ["app"])),
    "sast_results": ("정적 분석(SAST) 결과를 읽는다.", S({"app": STR}, ["app"])),
    "worker_directory": ("직무별 담당자와 다루는 도구를 보여 준다. 이관할 상대를 찾을 때 쓴다.", S()),
    # 협업
    "ticket_create": ("티켓을 만든다.", S({"title": STR, "body": STR, "severity": STR}, ["title", "body"])),
    "handoff_request": ("다른 직무에 업무를 넘기는 요청서를 남긴다. 실제 처리 여부는 상대가 정한다.",
                        S({"to_worker": STR, "summary": STR, "evidence_refs": {"type": "array", "items": STR}},
                          ["to_worker", "summary"])),
    # 변경 (준비 → 승인 → 적용)
    "change_prepare": ("변경 요청서를 준비한다. 적용되지 않는다. kind 는 직무별로 허용된 종류만 가능하다.",
                       S({"kind": STR, "target": STR, "spec": STR, "reason": STR,
                          "evidence_refs": {"type": "array", "items": STR},
                          "test_plan": STR, "rollback": STR},
                         ["kind", "target", "spec", "reason"])),
    "approval_request": ("준비된 변경의 승인을 요청한다.",
                         S({"change_id": STR, "summary": STR, "risk": STR}, ["change_id", "summary"])),
    "change_apply": ("승인된 변경을 적용한다. 승인 ID 가 없거나 거절된 변경은 적용되지 않는다.",
                     S({"change_id": STR, "approval_id": STR}, ["change_id", "approval_id"])),
    "handoff_inbox": ("나에게 온 이관 요청서 목록을 본다.", S()),
    "approval_list": ("승인 대기·결정 목록을 본다.", S()),
    "approval_decide": ("승인 요청을 결정한다. decision: approve | conditional | reject",
                        S({"approval_id": STR, "decision": STR, "reason": STR},
                          ["approval_id", "decision", "reason"])),
    "change_list": ("변경 요청서 목록과 상태를 본다.", S()),
    "evidence_read": ("이번 실행의 도구 호출 기록을 읽는다(감사용).", S({"worker": STR})),
}


def allowed_tools(worker):
    role = ROLES["roles"].get(worker)
    if role is None:
        return set()
    return set(ROLES.get("common", [])) | set(role.get("tools", []))


def boundary(tool):
    owner = ROLES.get("owners", {}).get(tool)
    return {"status": "role_boundary",
            "message": f"'{WORKER}' 직무는 {tool} 도구를 쓸 수 없습니다.",
            "recommended_worker": owner}


# ── mock 조회 ────────────────────────────────────────────────────────────────
def in_range(item, start, end):
    t = item.get("time") or item.get("ts")
    if not t:
        return True
    return (not start or t >= start) and (not end or t <= end)


def match_all(item, words):
    blob = json.dumps(item, ensure_ascii=False).lower()
    return all(w.lower() in blob for w in words if w)


def no_data(tool, what=""):
    # 서버는 판단을 코칭하지 않는다. '자료 없음'을 어떻게 해석할지는 스킬이 정한다.
    return {"status": "no_data",
            "message": f"{tool}: 돌려줄 자료가 없습니다{(' (' + what + ')') if what else ''}."}


def mock_query(tool, args):
    fx = FIXTURES.get(tool)
    meta = FIXTURES.get("_meta", {}).get(tool, {})
    if tool == "log_read":
        source = args.get("source", "")
        rows = (fx or {}).get(source)
        if rows is None:
            return no_data(tool, f"source={source}")
        rows = [r for r in rows if in_range(r, args.get("start"), args.get("end"))
                and match_all(r, (args.get("filter") or "").split())]
        out = {"status": "ok", "source": source, "count": len(rows), "rows": rows}
        if source in meta.get("partial_sources", []):
            out["status"] = "partial"
            out["message"] = meta.get("partial_note", "수집 일부 누락")
        return out
    if tool in ("siem_search", "waf_events"):
        if fx is None:
            return no_data(tool)
        words = (args.get("query") or args.get("filter") or "").split()
        rows = [r for r in fx if in_range(r, args.get("start"), args.get("end")) and match_all(r, words)]
        out = {"status": "ok" if rows else "no_match", "count": len(rows), "rows": rows}
        if words and fx and not rows:
            out["searched_total"] = len(fx)
        return out
    if tool in ("host_config", "host_accounts", "package_inventory", "backup_status"):
        host = args.get("host", "")
        data = (fx or {}).get(host) if isinstance(fx, dict) else None
        if data is None:
            return no_data(tool, f"host={host}")
        if tool == "host_config" and args.get("item"):
            item = data.get(args["item"]) if isinstance(data, dict) else None
            return {"status": "ok", "host": host, "item": args["item"], "value": item} if item is not None \
                else no_data(tool, f"item={args['item']}")
        return {"status": "ok", "host": host, "data": data}
    if tool == "vuln_feed":
        if fx is None:
            return no_data(tool)
        rows = fx
        if args.get("cve"):
            rows = [r for r in rows if r.get("cve") == args["cve"]]
        if args.get("host"):
            rows = [r for r in rows if args["host"] in r.get("hosts", [])]
        return {"status": "ok", "count": len(rows), "rows": rows}
    if tool in ("code_read",):
        app = (fx or {}).get(args.get("app", ""))
        if app is None:
            return no_data(tool, f"app={args.get('app')}")
        path = args.get("path")
        if path:
            return {"status": "ok", "app": args["app"], "path": path, "content": app.get(path)} \
                if path in app else no_data(tool, f"path={path}")
        return {"status": "ok", "app": args["app"], "files": sorted(app.keys())}
    if tool == "sast_results":
        rows = (fx or {}).get(args.get("app", ""))
        return {"status": "ok", "app": args["app"], "findings": rows} if rows is not None else no_data(tool)
    if fx is None:
        return no_data(tool)
    if args.get("filter") and isinstance(fx, list):
        fx = [r for r in fx if match_all(r, args["filter"].split())]
    return {"status": "ok", "data": fx}


# ── live 조회 (kt66 컨테이너, 읽기 전용) ─────────────────────────────────────────
LIVE = {
    "fw_rules": ["docker", "exec", "kt66-fw", "nft", "-a", "list", "ruleset"],
    "ids_rules": ["docker", "exec", "kt66-ips", "cat", "/etc/suricata/rules/local.rules"],
    "waf_events": ["docker", "exec", "kt66-web", "tail", "-n", "200", "/var/log/apache2/modsec_audit.log"],
    "waf_config": ["docker", "exec", "kt66-web", "sh", "-c",
                   "grep -h -E '^(SecRuleEngine|SecAuditEngine)' /etc/modsecurity/modsecurity.conf; "
                   "grep -h -E 'paranoia_level|anomaly_score_threshold' /etc/modsecurity/crs/crs-setup.conf "
                   "2>/dev/null | grep -v '^#' | head -20"],
}
LIVE_LOGS = {
    "ips": ["docker", "exec", "kt66-ips", "tail", "-n", "200", "/var/log/suricata/eve.json"],
    "waf": LIVE["waf_events"],
    "web": ["docker", "exec", "kt66-web", "tail", "-n", "200", "/var/log/apache2/access.log"],
}


def live_query(tool, args):
    cmd = LIVE.get(tool)
    if tool == "log_read":
        cmd = LIVE_LOGS.get(args.get("source", ""))
    if cmd is None:
        return {"status": "not_implemented",
                "message": f"live 모드에서 {tool} 은 아직 연결되지 않았습니다. mock 모드나 kt66 콘솔을 쓰세요."}
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    except Exception as e:  # pragma: no cover
        return {"status": "error", "message": str(e)}
    if p.returncode:
        return {"status": "error", "message": p.stderr.strip()[:500]}
    text = p.stdout
    if args.get("filter"):
        text = "\n".join(l for l in text.splitlines() if all(w in l for w in args["filter"].split()))
    return {"status": "ok", "raw": text[-20000:]}


# ── 협업·변경 ────────────────────────────────────────────────────────────────
def act(tool, args):
    state = load_state()
    if tool == "worker_directory":
        return {"status": "ok", "workers": [
            {"id": k, "title": v["title"], "tools": sorted(set(v.get("tools", [])))}
            for k, v in ROLES["roles"].items()]}
    if tool == "ticket_create":
        t = {"ticket_id": "T-" + uuid.uuid4().hex[:6], "by": WORKER, "ts": now(), **args}
        state["tickets"].append(t)
        save_state(state)
        return {"status": "ok", **t}
    if tool == "handoff_request":
        if args["to_worker"] not in ROLES["roles"]:
            return {"status": "error", "message": f"없는 담당자입니다: {args['to_worker']}. worker_directory 를 보세요."}
        h = {"handoff_id": "H-" + uuid.uuid4().hex[:6], "from": WORKER, "ts": now(), **args,
             "note": "요청서만 남겼습니다. 상대 담당자가 접수하기 전에는 처리된 것이 아닙니다."}
        state["handoffs"].append(h)
        save_state(state)
        return {"status": "ok", **h}
    if tool == "change_prepare":
        kinds = ROLES["roles"].get(WORKER, {}).get("change_kinds", [])
        if args["kind"] not in kinds:
            return {"status": "role_boundary",
                    "message": f"'{WORKER}' 직무가 준비할 수 있는 변경은 {kinds or '없음'} 입니다."}
        cid = "C-" + uuid.uuid4().hex[:6]
        missing = [k for k in ("test_plan", "rollback") if not args.get(k)]
        state["changes"][cid] = {"change_id": cid, "by": WORKER, "ts": now(), "status": "prepared", **args}
        save_state(state)
        out = {"status": "ok", "change_id": cid, "state": "prepared",
               "message": "변경 요청서를 준비했습니다. 아직 적용되지 않았습니다."}
        if missing:
            out["warning"] = f"빠진 항목: {', '.join(missing)}"
        return out
    if tool == "approval_request":
        ch = state["changes"].get(args["change_id"])
        if ch is None:
            return {"status": "error", "message": "없는 변경 ID 입니다."}
        aid = "A-" + uuid.uuid4().hex[:6]
        state["approvals"][aid] = {"approval_id": aid, "change_id": args["change_id"], "by": WORKER,
                                   "ts": now(), "status": "pending", **args}
        ch["status"] = "awaiting_approval"
        save_state(state)
        return {"status": "ok", "approval_id": aid, "state": "pending",
                "message": "승인 요청을 남겼습니다. 승인자가 결정하기 전에는 적용할 수 없습니다."}
    if tool == "approval_list":
        return {"status": "ok", "approvals": list(state["approvals"].values())}
    if tool == "change_list":
        rows = []
        for c in state["changes"].values():
            aps = [a for a in state["approvals"].values() if a.get("change_id") == c["change_id"]]
            rows.append({**c, "approvals": [{k: a.get(k) for k in ("approval_id", "status", "decided_by", "reason")}
                                            for a in aps]})
        return {"status": "ok", "changes": rows}
    if tool == "handoff_inbox":
        return {"status": "ok", "handoffs": [h for h in state["handoffs"] if h.get("to_worker") == WORKER]}
    if tool == "approval_decide":
        a = state["approvals"].get(args["approval_id"])
        if a is None:
            return {"status": "error", "message": "없는 승인 ID 입니다."}
        if a.get("by") == WORKER:
            return {"status": "error", "message": "자기가 요청한 변경은 자기가 승인할 수 없습니다."}
        if args["decision"] not in ("approve", "conditional", "reject"):
            return {"status": "error", "message": "decision 은 approve | conditional | reject 입니다."}
        a.update({"status": args["decision"], "decided_by": WORKER, "decided_at": now(),
                  "reason": args["reason"]})
        save_state(state)
        return {"status": "ok", **a}
    if tool == "change_apply":
        ch = state["changes"].get(args["change_id"])
        a = state["approvals"].get(args["approval_id"])
        if ch is None:
            return {"status": "error", "message": "없는 변경 ID 입니다."}
        if a is None or a.get("change_id") != args["change_id"]:
            return {"status": "approval_required", "message": "이 변경에 해당하는 승인이 없습니다."}
        if a.get("status") not in ("approve", "conditional"):
            return {"status": "approval_required", "message": f"승인 상태가 '{a.get('status')}' 입니다."}
        ch.update({"status": "applied", "applied_by": WORKER, "applied_at": now(), "approval_id": a["approval_id"]})
        save_state(state)
        return {"status": "ok", "change_id": ch["change_id"], "state": "applied",
                "message": "적용 기록을 남겼습니다(실습 랩에서는 요청서 기준 모의 적용). 적용 후 확인을 하세요."}
    if tool == "evidence_read":
        p = EVIDENCE / "tools.jsonl"
        rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []
        if args.get("worker"):
            rows = [r for r in rows if r.get("worker") == args["worker"]]
        return {"status": "ok", "count": len(rows), "rows": rows[-300:]}
    raise KeyError(tool)


ACTIONS = {"handoff_inbox", "worker_directory", "ticket_create", "handoff_request", "change_prepare", "approval_request",
           "approval_list", "change_list", "approval_decide", "change_apply", "evidence_read"}


def call(tool, args):
    if tool not in TOOLS:
        return {"status": "error", "message": f"없는 도구: {tool}"}
    if tool not in allowed_tools(WORKER):
        return boundary(tool)
    if tool == "log_read":
        sources = ROLES["roles"].get(WORKER, {}).get("log_sources")
        if sources is not None and args.get("source") not in sources:
            out = boundary(tool)
            out["message"] = f"'{WORKER}' 직무가 읽을 수 있는 로그는 {sources} 입니다."
            out["recommended_worker"] = "soc-analyst"
            return out
    if tool in ACTIONS:
        return act(tool, args)
    return live_query(tool, args) if MODE == "live" else mock_query(tool, args)


# ── MCP stdio (JSON-RPC 2.0, 줄 단위) ─────────────────────────────────────────
def reply(mid, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": mid}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except ValueError:
            continue
        method, mid = req.get("method"), req.get("id")
        if mid is None:  # 알림
            continue
        if method == "initialize":
            pv = (req.get("params") or {}).get("protocolVersion", "2025-06-18")
            reply(mid, {"protocolVersion": pv, "capabilities": {"tools": {}},
                        "serverInfo": {"name": "lab", "version": "1.0"}})
        elif method == "ping":
            reply(mid, {})
        elif method == "tools/list":
            visible = allowed_tools(WORKER) if os.environ.get("LAB_HIDE_FORBIDDEN") == "1" else TOOLS.keys()
            reply(mid, {"tools": [{"name": n, "description": TOOLS[n][0], "inputSchema": TOOLS[n][1]}
                                  for n in TOOLS if n in visible]})
        elif method == "tools/call":
            p = req.get("params") or {}
            name, args = p.get("name", ""), p.get("arguments") or {}
            try:
                out = call(name, args)
            except Exception as e:  # pragma: no cover
                out = {"status": "error", "message": f"{type(e).__name__}: {e}"}
            log_call(name, args, out.get("status", "?"), out.get("message", ""))
            reply(mid, {"content": [{"type": "text", "text": json.dumps(out, ensure_ascii=False, indent=1)}],
                        "isError": out.get("status") in ("error",)})
        else:
            reply(mid, error={"code": -32601, "message": f"method not found: {method}"})


if __name__ == "__main__":
    main()
