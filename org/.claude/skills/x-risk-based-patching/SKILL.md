---
name: x-risk-based-patching
description: 패치할 취약점이 많아 순서를 정해야 할 때 CVSS(심각도)만이 아니라 EPSS(악용 가능성), CISA KEV(실제 악용 목록), SSVC 결정점(악용 상태·기술적 영향·자동화 가능성·임무 영향)을 함께 써서 우선순위와 처리 기한을 정한다. 확장 스킬.
metadata:
  track: "extension"
  role: "sys-sec-ops"
  extends: "ncs-sysops-41-update-plan, ncs-sysops-21-improve-plan"
  sources: "research/sys-sec-ops.md"
---

# 위험 기반 패치 우선순위 (확장)

NCS 4-1의 4단계는 "공개 취약성과 패치 내용을 검토한다"에서 멈춘다. 현업은 검토 결과로 **순서**를 정해야
한다. CVSS는 '얼마나 심각한가', EPSS는 '앞으로 30일 안에 악용될 확률', KEV는 '이미 악용되고 있는가'를 말한다.

## 절차

1. 대상 취약점마다 `vuln_feed`로 CVSS, EPSS(0~1과 백분위), KEV 등재 여부, 패치 유무를 모은다.
2. 영향받는 자산의 중요도와 노출(외부 공개 여부)을 `asset_inventory`로 붙인다.
3. SSVC식으로 결정한다.

   | 질문 | 값 |
   |---|---|
   | 악용 상태 | 없음 / 공개 PoC / 실제 악용(KEV 등재) |
   | 기술적 영향 | 부분 / 전체(시스템 장악) |
   | 자동화 가능성 | 아니오 / 예(대량 자동 공격 가능) |
   | 임무·공공 영향 | 낮음 / 중간 / 높음(자산 중요도) |

4. 결과를 네 가지 처리로 나눈다.

   | 처리 | 뜻 | 기한(조직 기준을 먼저 쓴다) |
   |---|---|---|
   | Act | 리더 수준 주의, 가능한 한 빨리 조치 | 예) 즉시~7일 |
   | Attend | 관리자 주의, 표준 일정보다 빨리 | 예) 단기 |
   | Track* | 표준 일정, 더 자주 모니터링 | 정기 패치 주기 |
   | Track | 표준 일정 | 정기 패치 주기 |

5. 근거를 남긴다: 취약점마다 네 값과 처리 결과. CVSS가 높아도 EPSS가 낮고 KEV가 아니며 내부 전용이면
   Track일 수 있다. 반대로 CVSS가 중간이어도 KEV 등재 + 외부 공개 + 핵심 자산이면 Act다.

## 출처

- FIRST EPSS — https://www.first.org/epss/
- CISA SSVC — https://www.cisa.gov/stakeholder-specific-vulnerability-categorization-ssvc
- 기한 예시는 NCS 정보시스템 진단의 조치 기간 구분(즉시·단기·중기·장기)과 맞춰 조직 기준으로 정한다.
