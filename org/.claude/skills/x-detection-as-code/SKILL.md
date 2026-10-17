---
name: x-detection-as-code
description: 탐지패턴을 Sigma 규칙(YAML)처럼 코드로 작성하고, 공격 로그와 정상 로그 표본으로 미리 시험해 오탐률·정탐률을 수치로 남긴 뒤 운영 담당에게 넘길 때 사용한다. 확장 스킬.
metadata:
  track: "extension"
  role: "soc-analyst"
  extends: "ncs-log-31-pattern-dev, ncs-log-32-pattern-tuning"
  sources: "research/soc-analyst.md"
---

# 탐지 규칙을 코드로 (확장)

NCS 3-1·3-2는 패턴을 만들어 적용한 **뒤에** 모니터링으로 오탐률을 잰다. 현업 탐지 엔지니어링은
적용 **전에** 공격 표본과 정상 표본으로 먼저 시험하고, 규칙을 버전으로 관리한다.

## 절차

1. **규칙을 Sigma 형식으로 쓴다.** 필수 항목: `title`, `logsource`(category/product/service),
   `detection`(selection, filter), `condition`, `falsepositives`, `level`, `status`.
   - `falsepositives`는 설명일 뿐 변환기가 쓰지 않는다. 실제로 걸러야 할 정상 패턴은 `filter`로
     `detection` 안에 넣는다.
2. **공격 표본**으로 시험한다: 분석한 사건의 로그 행(`log_read`)이 규칙에 걸리는가.
3. **정상 표본**으로 시험한다: 같은 장비의 평시 로그(최소 하루치)를 넣었을 때 몇 건이 걸리는가.
4. **수치를 남긴다.** 정탐 = 공격 표본 중 탐지 비율, 오탐률 = 정상 표본 중 탐지 건수 / 전체 탐지 건수.
   조직 기준(NCS 사례: 오탐률 1% 이하, 정탐률 95% 이상)과 비교한다.
5. **넘긴다.** 규칙 원문, 시험 표본 위치, 측정값, 예상 리소스 영향을 붙여 운영 담당에게
   `handoff_request`. 상태는 `experimental`로 두고, 운영 모니터링(3-2)을 거쳐 `stable`로 올린다.

## 예

```yaml
title: 로그인 경로 SQL 인젝션 시도 (Log Only 통과)
status: experimental
logsource: {category: webserver, product: modsecurity}
detection:
  selection:
    uri|endswith: /login
    rule_id: [942100, 942190]
  filter_scanner:
    src_ip: 10.20.32.50        # 허가된 점검 서버(자산 대장)
  condition: selection and not filter_scanner
falsepositives: [허가된 취약점 점검 시간대의 점검 서버]
level: high
```

## 출처

- Sigma 규칙 구조 — https://sigmahq.io/docs/basics/rules.html
- NCS 보안로그 분석 학습 3-2 <표 3-14> 평가 기준
