# 시스템 보안 운영 담당자 — 확장 리서치

기준선: NCS 시스템 보안 운영(LM2001060110_19v3) 스킬 8개 (`ncs-sysops-*`).

## 1. 채용공고·직무 자료

| 출처 | 날짜 | 현업 업무 |
|---|---|---|
| [Theori 가이드 — 취약점 분석](https://theori.io/ko/blog/cybersecurity-job-preparation-guide) | 2026-06-26 | 정기 취약점 스캔과 **조치 조율**, 스캐너 자동화 |
| [SK쉴더스 사이버보안 컨설턴트](https://www.skshieldusapply.com/ko/o/117369) | 마감 2026-11-08 | 주요정보통신기반시설·전자금융기반시설 취약점 분석·평가, 보호대책 수립 |

## 2. 차이 분석

| 현업 업무 | NCS 스킬 | 차이 |
|---|---|---|
| 패치 관리 절차 9단계 | ncs-sysops-41 | 있음 |
| 수십~수백 개 취약점의 조치 **순서** 결정 | 4단계 '검토'에서 멈춤 | **확장 후보** |

## 3. 표준

| 출처 | 요점 |
|---|---|
| [FIRST EPSS](https://www.first.org/epss/) | CVE가 30일 안에 실제 악용될 확률(0~1)과 백분위, 매일 갱신 |
| [CISA SSVC](https://www.cisa.gov/stakeholder-specific-vulnerability-categorization-ssvc) | 악용 상태·기술적 영향·자동화 가능성·임무 영향·공공 영향으로 Track·Track*·Attend·Act 결정 |

## 4. 결과와 가설

- `x-risk-based-patching`: CVSS + EPSS + KEV + SSVC 결정점으로 처리 등급과 기한.
- X-SYS-1: CVSS만 높은 내부 전용 취약점과 CVSS 중간·KEV 등재·외부 공개 취약점을 섞었을 때, 확장 스킬을 쓰면 후자를 먼저 둔다(실험 SYS-05).
