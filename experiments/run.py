#!/usr/bin/env python3
"""실험 실행기 — 시나리오를 기준선(base)과 변형(variant)으로 돌리고 채점한다.

  python3 experiments/run.py --list                         시나리오 목록
  python3 experiments/run.py SOC-01                         기준선 1회
  python3 experiments/run.py SOC-01 --variant all --repeat 3 기준선과 모든 변형을 3회씩
  python3 experiments/run.py SOC-01 --variant V1 --model haiku
  python3 experiments/run.py --compare SOC-01               결과 비교표
  python3 experiments/run.py SOC-01 --dry-run               무엇을 바꾸고 무엇을 실행할지만 출력
  python3 experiments/run.py SOC-01 --live                  kt66 실환경(주입기 + 컨테이너 조회)

실행마다 org/ 를 결과 폴더로 복사한 뒤 변형을 적용한다. 원본 org/ 는 바뀌지 않는다.
모델 응답은 매번 다를 수 있으므로 비교는 --repeat 로 여러 번 돌린 뒤 비율로 본다.
"""
import argparse
import datetime
import json
import os
import pathlib
import shutil
import subprocess
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
ORG = ROOT / "org"
SCEN = ROOT / "experiments" / "scenarios"
RESULTS = ROOT / "experiments" / "results"


def load(sid):
    p = SCEN / f"{sid}.yaml"
    if not p.exists():
        sys.exit(f"없는 시나리오: {sid}")
    return p, yaml.safe_load(p.read_text(encoding="utf-8"))


def apply_ops(org, ops):
    """변형 연산: find/replace, append, write, delete. 실패하면 멈춘다(조용히 지나가면 실험이 거짓이 된다)."""
    for op in ops or []:
        f = org / op["file"]
        if op.get("delete"):
            if f.is_dir():
                shutil.rmtree(f)
            elif f.exists():
                f.unlink()
            continue
        if "write" in op:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(op["write"], encoding="utf-8")
            continue
        text = f.read_text(encoding="utf-8")
        if "find" in op:
            if op["find"] not in text:
                raise SystemExit(f"변형 실패: {op['file']} 에서 찾을 문장이 없습니다: {op['find'][:60]}")
            text = text.replace(op["find"], op.get("replace", ""), 1)
        if "append" in op:
            text = text.rstrip("\n") + "\n" + op["append"]
        f.write_text(text, encoding="utf-8")


INJECT_TARGET = {"sec_sqli": "kt66-attacker", "sec_lateral": "kt66-attacker",
                 "sec_exfil": "kt66-gpu-gw", "sec_nftdrift": "kt66-fw"}


def live_inject(scen):
    """--live: 시나리오의 live_inject 를 kt66 장애 주입기에 건다. 주소·키는 환경 변수로 받는다.
    INJECTOR_URL(기본 http://127.0.0.1:8030), INJECTOR_KEY. 주입 뒤 잠시 기다려 로그가 쌓이게 한다."""
    import time
    import urllib.parse
    import urllib.request
    url = os.environ.get("INJECTOR_URL", "http://127.0.0.1:8030").rstrip("/")
    key = os.environ.get("INJECTOR_KEY", "")
    handles = []
    for iid in scen.get("live_inject") or []:
        q = urllib.parse.urlencode({"id": iid, "target": INJECT_TARGET.get(iid, ""), "key": key})
        with urllib.request.urlopen(urllib.request.Request(f"{url}/inject?{q}", method="POST"), timeout=60) as r:
            h = json.loads(r.read())
        print(f"[live] 주입 {iid} → {h.get('target')} handle={h.get('handle')}")
        handles.append(h.get("handle"))
    if handles:
        time.sleep(int(os.environ.get("INJECT_WAIT", "30")))
    return handles


def run_once(path, scen, variant, rep, model, dry, live=False):
    v = {"id": "base"} if variant == "base" else next(x for x in scen.get("variants", []) if x["id"] == variant)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = RESULTS / scen["id"] / v["id"] / f"{stamp}-r{rep}"
    org = out / "org"
    steps = scen.get("steps") or [{"role": scen["role"], "prompt": scen["prompt"]}]
    if dry:
        print(f"[dry] {scen['id']}/{v['id']} → {out}")
        for s in steps:
            print(f"      {s['role']}: {s['prompt'][:70]}")
        print(f"      ops={len(v.get('ops') or [])} env={v.get('env')} disallow={v.get('disallow')}")
        return None
    shutil.copytree(ORG, org, ignore=shutil.ignore_patterns("evidence", "tickets", "candidates", "__pycache__"))
    for d in ("evidence", "tickets", "candidates"):
        (org / d).mkdir(exist_ok=True)
    apply_ops(org, v.get("ops"))
    env = {**os.environ, "LAB_FIXTURES": str(path), "LAB_EVIDENCE_DIR": str(out / "evidence"),
           **{k: str(x) for k, x in (v.get("env") or {}).items()}}
    # 구독 로그인으로만 실행한다. 추가 과금되는 API 키는 넘기지 않는다(bin/work 도 같은 처리를 한다).
    for k in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        env.pop(k, None)
    if live:
        # 실제 kt66 컨테이너를 읽는다. 시나리오 fixtures 는 쓰지 않는다(변경 상태 기록용 파일만 남긴다).
        env["LAB_MODE"] = "live"
        env.pop("LAB_FIXTURES", None)
        (out / "live.json").write_text(json.dumps({"handles": live_inject(scen)}), encoding="utf-8")
    if model:
        env["MODEL"] = model
    results = []
    for i, s in enumerate(steps, 1):
        sdir = out if len(steps) == 1 else out / f"step{i}-{s['role']}"
        sdir.mkdir(parents=True, exist_ok=True)
        cmd = [str(org / "bin" / "work"), s["role"], "-p", s["prompt"], "--output-format", "stream-json", "--verbose"]
        if v.get("disallow"):
            cmd += ["--disallowedTools", ",".join(v["disallow"])]
        with open(sdir / "transcript.jsonl", "w") as fo, open(sdir / "stderr.txt", "w") as fe:
            subprocess.run(cmd, env=env, stdin=subprocess.DEVNULL, stdout=fo, stderr=fe, timeout=900)
        if sdir != out:
            (sdir / "evidence").mkdir(exist_ok=True)
            for f in (out / "evidence").glob("*.jsonl"):
                shutil.copy(f, sdir / "evidence" / f.name)
        expect = s.get("expect", scen.get("expect", {})) if len(steps) > 1 else scen.get("expect", {})
        if v.get("expect"):
            expect = check.merge_expect(expect, v["expect"], v.get("expect_replace"))
        calls, answer, meta = check.load_transcript(sdir)
        if meta.get("api_key_source") not in (None, "none"):
            raise SystemExit(f"중단: API 키({meta['api_key_source']})로 실행됐습니다. 구독 로그인(claude /login)으로만 실행합니다.")
        sc = check.score(expect, calls, answer, check.lab_status(sdir))
        sc["meta"] = meta
        sc["gate_denials"] = sum(1 for g in check.gate_log(sdir) if g.get("decision") == "deny")
        (sdir / "answer.md").write_text(answer, encoding="utf-8")
        (sdir / "score.json").write_text(json.dumps(sc, ensure_ascii=False, indent=1), encoding="utf-8")
        results.append(sc)
        print(f"{scen['id']}/{v['id']}/r{rep} {s['role']}: {sc['passed']}/{sc['total']}  "
              f"스킬={sc['skills']}  게이트거절={sc['gate_denials']}  턴={meta.get('turns')}  인증={meta.get('api_key_source')}")
    return results


def compare(sid):
    base = RESULTS / sid
    if not base.exists():
        sys.exit("결과가 없습니다.")
    _, scen = load(sid)
    print(f"# {sid} {scen['title']}\n")
    rows = {}
    for vdir in sorted(base.iterdir()):
        for sc_file in vdir.rglob("score.json"):
            sc = json.loads(sc_file.read_text())
            r = rows.setdefault(vdir.name, {"n": 0, "rate": [], "checks": {}, "skills": {}})
            r["n"] += 1
            r["rate"].append(sc["rate"] or 0)
            for c in sc["checks"]:
                r["checks"].setdefault(c["check"], []).append(c["pass"])
            for s in sc["skills"]:
                r["skills"][s] = r["skills"].get(s, 0) + 1
    print("| 변형 | 실행 수 | 평균 통과율 | 불린 스킬(횟수) |\n|---|---|---|---|")
    for k, r in rows.items():
        print(f"| {k} | {r['n']} | {sum(r['rate']) / len(r['rate']):.2f} | "
              f"{', '.join(f'{s}({n})' for s, n in sorted(r['skills'].items()))} |")
    names = sorted({c for r in rows.values() for c in r["checks"]})
    print("\n| 검사 | " + " | ".join(rows) + " |\n|---|" + "---|" * len(rows))
    for c in names:
        cells = []
        for r in rows.values():
            v = r["checks"].get(c)
            cells.append(f"{sum(v)}/{len(v)}" if v else "-")
        print(f"| {c} | " + " | ".join(cells) + " |")
    for v in scen.get("variants", []):
        print(f"\n- {v['id']}: {v.get('description', '')}\n  예상 차이: {v.get('expect_diff', '')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario", nargs="?")
    ap.add_argument("--variant", default="base")
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--model", default=os.environ.get("MODEL"))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--compare")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--live", action="store_true", help="kt66 실환경: live_inject 를 걸고 LAB_MODE=live 로 실행")
    a = ap.parse_args()
    if a.list:
        for p in sorted(SCEN.glob("*.yaml")):
            s = yaml.safe_load(p.read_text(encoding="utf-8"))
            vs = ",".join(v["id"] for v in s.get("variants", []))
            print(f"{s['id']:9} {s.get('type', ''):12} {s.get('role', 'team'):17} {s['title']}" + (f"  [변형 {vs}]" if vs else ""))
        return
    if a.compare:
        return compare(a.compare)
    if not a.scenario:
        ap.error("시나리오 ID 가 필요합니다")
    path, scen = load(a.scenario)
    variants = ["base"] + [v["id"] for v in scen.get("variants", [])] if a.variant == "all" else [a.variant]
    for v in variants:
        for r in range(1, a.repeat + 1):
            run_once(path, scen, v, r, a.model, a.dry_run, a.live)


if __name__ == "__main__":
    main()
