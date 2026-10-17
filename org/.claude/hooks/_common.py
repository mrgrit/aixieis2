"""훅 공통 함수. 훅은 지침이 아니라 '강제'다 — 모델이 무엇을 생각하든 같은 결과를 낸다."""
import datetime
import json
import os
import pathlib
import sys

PROJECT = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", pathlib.Path(__file__).resolve().parents[2]))


def evidence_dir():
    d = os.environ.get("LAB_EVIDENCE_DIR") or str(PROJECT / "evidence" / "manual")
    p = pathlib.Path(d)
    if not p.is_absolute():
        p = PROJECT / p
    p.mkdir(parents=True, exist_ok=True)
    return p


def read_input():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="seconds")


def append(name, rec):
    with open(evidence_dir() / name, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
