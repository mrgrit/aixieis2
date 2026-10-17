# 애플리케이션 보안 운영 담당자 — 확장 리서치

기준선: NCS 애플리케이션 보안 운영(LM2001060109_19v3) 스킬 8개 (`ncs-appops-*`).

## 1. 채용공고

| 출처 | 날짜 | 현업 업무 |
|---|---|---|
| [(주)에스피정보시스템 네트워크 보안 운영자 (사람인)](https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=53649987) | 2026-04~06 | 금융기관 방화벽·**웹 애플리케이션 방화벽**·SSL-VPN 운영, 보안 정책 설계·유지 |

WAF 전담 공고를 원문으로 확인하지 못했다(검색 결과가 제품 소개 위주). 14장 과제로 보완한다.

## 2. 차이 분석

| 현업 업무 | NCS 스킬 | 차이 |
|---|---|---|
| 과차단 복구와 정책 수정 | ncs-appops-32 | '정책 수정·검증'만 있고 수정 방법이 없음 → **확장 후보** |
| 패러노이아 레벨 상향·차단 모드 전환 | 없음 | **확장 후보** |

## 3. 표준·논문

| 출처 | 요점 |
|---|---|
| [OWASP CRS — False Positives and Tuning](https://coreruleset.org/docs/2-how-crs-works/2-3-false-positives-and-tuning/) | 규칙 파일 수정 금지, 구성 시점(CRS 뒤)·실행 시점(CRS 앞) 예외 구분, 가장 좁은 범위(변수 단위) 우선, 7단계 튜닝 흐름 |
| [ModSec-Learn: Boosting ModSecurity with Machine Learning (arXiv 2406.13547, 2024)](https://www.researchgate.net/publication/381579515_ModSec-Learn_Boosting_ModSecurity_with_Machine_Learning) | CRS 규칙 발동 여부를 특징으로 규칙별 가중치 학습. 오탐률 1%에서 PL3·PL4 탐지율이 약 68.6%(기본)→약 99%. SQLi만 평가 |

## 4. 결과와 가설

- `x-crs-fp-tuning`: CRS 공식 튜닝 절차를 변경 요청서 항목으로.
- X-APP-1: 과차단 시나리오에서 확장 스킬을 쓰면 '규칙 전체 비활성화' 대신 '변수 단위 예외'를 제안한다(실험 APP-05).
- 연구 과제(실험 아님): ModSec-Learn식 가중치 학습은 학습 데이터가 필요해 4장 이후 심화 과제로 둔다.
