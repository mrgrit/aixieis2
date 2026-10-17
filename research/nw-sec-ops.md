# 네트워크 보안 운영 담당자 — 확장 리서치

기준선: NCS 네트워크 보안 운영(LM2001060108_19v3) 스킬 8개 (`ncs-nwops-*`).

## 1. 채용공고

| 출처 | 날짜 | 현업 업무 | 도구·우대 |
|---|---|---|---|
| [(주)에스피정보시스템 [상주] 네트워크 보안 운영자 (사람인)](https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=53649987) | 2026-04-16~06-15 (마감) | 금융기관 네트워크 보안 시스템 운영·구축, 방화벽·WAF·SSL-VPN 운영, 네트워크 IPS·DDoS 장비 운영, **보안 정책·절차 설계와 유지**, 시스템·네트워크 보안 **감사 준비·수행** | 시큐아이·윈스·포티넷 장비, 대규모 망 보안 관리, 3년 이상 |
| [Theori 가이드 — 클라우드 보안 엔지니어](https://theori.io/ko/blog/cybersecurity-job-preparation-guide) | 2026-06-26 | 방화벽·SSL VPN·IPS/IDS 관리, 보안그룹·VPN 구성 | IaC(Terraform), SIEM 상관분석 |

## 2. 차이 분석

| 현업 업무 | NCS 스킬 | 차이 |
|---|---|---|
| 방화벽·IPS·VPN 운영, 업데이트 | ncs-nwops-12, 41, 42 | 있음 |
| 정책 중복·우선순위 오류 점검 | ncs-nwops-21 (체크리스트 한 줄) | 규칙이 많을 때의 체계적 방법 없음 → **확장 후보** |
| 정책 설계·유지와 감사 대응(변경의 정확성 증명) | ncs-nwops-12, 22 | 변경 전후를 결정적으로 검증하는 방법 없음 → **확장 후보** |

## 3. 논문·자료

| 출처 | 요점 |
|---|---|
| [NetConfEval: Can LLMs Facilitate Network Configuration? (CoNEXT 2024)](https://research.redhat.com/blog/publication/can-llms-facilitate-network-configuration/) | 고수준 요구사항 → 형식 명세 변환, 요구사항 → 설정 생성 등 4개 과제로 LLM을 평가. 설계 원칙을 도출(요약 페이지에는 원칙 목록 없음) |
| [SOCpilot: Verifying Policy Compliance for LLM-Assisted Incident Response](https://arxiv.org/abs/2605.05501) (2026-05) | 같은 정책 문장을 프롬프트에 넣어도 모델에 따라 위반이 오히려 늘 수 있음. 결정론적 검증기(필수 단계·순서·승인 규칙)가 강제 지점 |

## 4. 결과

- `x-fw-policy-hygiene`: 규칙 쌍 관계(가림·중복·일반화·상관·과다 허용·미사용) 분류와 정리안.
- `x-change-verify`: 요구사항 → 연결 시험표 → 변경 전후 평가 → test_plan에 그대로.

## 5. 실험 가설

- X-NW-1: 가림 규칙이 있는 정책에서 `x-fw-policy-hygiene`를 쓰면 가림을 찾아낸다(실험 NW-05).
- X-NW-2: `x-change-verify`를 쓰면 변경 요청서의 test_plan에 차단돼야 할 연결이 빠지지 않는다(실험 NW-06).
