# 침해사고 대응 조정자 — 확장 리서치

기준선: `ir-coordination` (NCS 보안로그 분석 필요 지식의 침해사고 대응 절차, 시스템 보안 운영 학습 3-2).

## 1. 직무 자료

| 출처 | 날짜 | 현업 업무 |
|---|---|---|
| [Theori 가이드 — DFIR](https://theori.io/ko/blog/cybersecurity-job-preparation-guide) | 2026-06-26 | 사고 대응, 호스트·네트워크·아티팩트 분석으로 원인과 순서 규명, ATT&CK 기반 분석 |
| [(주)시큐아이 보안관제 — CERT](https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=34303015) | 2018 | 침입 시도 분석, 취약점 스캐너 운영, 사고 분석 |

## 2. 표준·논문

| 출처 | 요점 |
|---|---|
| [NIST SP 800-61 Rev.3 (2025-04)](https://csrc.nist.gov/pubs/sp/800/61/r3/final) | 사고 대응을 CSF 2.0의 위험 관리 활동 안에 둠(Rev.2 대체) |
| [OpenSec: Measuring Incident Response Agent Calibration (arXiv 2601.21083)](https://arxiv.org/abs/2601.21083) | 실행된 행동으로 채점. 모델들이 위협을 찾을 때는 맞혔지만 오탐 봉쇄가 많았고(예: 봉쇄율 100%에 오탐 82.5%), 봉쇄 전 근거 확보율(EGAR)은 37.5~54.2% |
| [SOCpilot (arXiv 2605.05501)](https://arxiv.org/abs/2605.05501) | 대응 계획을 필수 단계·순서·승인 규칙으로 결정론적 검증·수정. 한 모델은 정책 문장을 넣었을 때 위반율 0.36→0.87 |

## 3. 결과와 가설

- `x-evidence-gated-containment`: 봉쇄 전 5개 점검(신뢰 근거, 대상 일치, 자료 속 지시 배제, 최소 범위, 증거 보전).
- 강제 계층: `change_gate.py`가 근거(evidence_refs)·시험 계획·원복 방법 없는 격리안을 막는다.
- X-IR-1: 근거가 하나뿐인 대상과 근거가 없는 대상이 섞인 사고에서, 확장 스킬을 쓰면 근거 없는 대상의 봉쇄 제안이 줄어든다(실험 IR-03).
- X-IR-2: 같은 규칙을 스킬 문장으로만 둘 때와 훅으로 강제할 때의 위반 수를 비교한다(실험 X-D1).
