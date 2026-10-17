# 보안관제 분석가 — 확장 리서치

기준선: NCS 보안로그 분석(LM2001060307_16v1) 스킬 6개 (`ncs-log-*`).

## 1. 채용공고·직무 자료

| 출처 | 날짜 | 현업 업무(요약) | 도구·자격 |
|---|---|---|---|
| [Theori, 사이버 보안 취업 준비 가이드 — 보안관제](https://theori.io/ko/blog/cybersecurity-job-preparation-guide) | 2026-06-26 | 실시간 트래픽을 보고 공격 여부 판단, 24/365 교대 | SIEM(Splunk·ArcSight·QRadar), Wireshark 로그 분석, Python 우대, 정보보안기사 |
| [(주)시큐아이 보안관제 부문 경력 채용 (사람인)](https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=34303015) | 2018-07 (마감) | 관제 운영, 위협 분석, 악성코드 분석, **탐지 룰 개발**, 상관분석 도구 개발, CERT 사고 분석 | SIEM·ESM, IDS/IPS, 포렌식 장비, 정보보안기사·CISSP 등 |

공고 수가 부족하다(2건, 그중 1건은 오래됨). 2권 14장 과제로 최근 1년 공고 5건 이상을 더 모은다.

## 2. 차이 분석

| 현업 업무 | NCS 스킬 | 차이 |
|---|---|---|
| 경보 하나의 정탐·오탐 판정 | ncs-log-12-analysis | 있음 |
| 여러 장비 상관분석 | ncs-log-22-correlation | 있음 |
| 탐지 룰 개발 | ncs-log-31/32 | 있음. 다만 적용 **후** 모니터링으로만 평가 |
| 대량 경보를 유형별로 빠르게 분류(트리아지) | 없음 | **확장 후보** |
| 탐지 룰을 적용 전에 표본으로 시험·버전 관리 | 없음 | **확장 후보** |

## 3. 논문·표준

| 출처 | 방법 | 결과 | 한계 |
|---|---|---|---|
| [CORTEX: Collaborative LLM Agents for High-Stakes Alert Triage](https://arxiv.org/abs/2510.00311) (2025-09) | 경보를 7개 워크플로 중 하나로 라우팅 → 워크플로별 증거 수집 에이전트 → 하나라도 대응 필요면 대응 필요(보수적 결합) → 감사 가능한 구조화 보고 | 최고 단일 에이전트 대비 actionable F1 0.66→0.78, 오탐률 24.9%→14.2% | 지연 약 152초, 토큰 약 2.36만(도구 단일 에이전트의 수 배). 시나리오 수 제한, 프롬프트 인젝션 민감 |
| [Benchmarking LLM Agents for SOC Alert Triage](https://neurips.cc/virtual/2026/168137) (NeurIPS 2026 워크숍) | 경보 하나에서 출발해 주변 텔레메트리를 직접 조회하는 대화형 벤치마크(6,235회 조사) | 모든 구성이 공격 경보의 40.4% 이상을 놓침. 조회 결과가 비면 공격 경보를 더 기각. 재검토 단계는 맞은 판정을 고친 것보다 망친 것이 많음 | 워크숍 포스터. 한 공격 시나리오(4일) |
| [Sigma 규칙 구조](https://sigmahq.io/docs/basics/rules.html) | YAML 규칙(logsource·detection·condition·falsepositives·level·status), SIEM 쿼리로 변환 | — | falsepositives 필드는 변환기가 무시 → 실제 제외는 detection 안에 |

## 4. 결과

- `x-alert-triage-workflow`: 유형 라우팅표, 유형별 필수 증거, 보수적 결합, 0건 조회 처리, 판정 번복 규칙.
- `x-detection-as-code`: Sigma 형식, 공격·정상 표본 사전 시험, NCS <표 3-14> 기준과 비교.

## 5. 실험 가설

- X-SOC-1: 혼합 경보 묶음에서 `x-alert-triage-workflow`를 쓰면 '조회 0건 → 기각' 오류가 줄어든다(실험 SOC-07).
- X-SOC-2: 재검토를 시킬 때 '새 증거 없이 번복 금지' 규칙이 있으면 맞은 판정의 번복이 줄어든다(실험 SOC-08).
