---
name: x-crs-fp-tuning
description: ModSecurity·OWASP CRS WAF가 정상 요청을 막았을 때(과차단) 규칙 파일을 고치지 않고 가장 좁은 범위의 예외로 오탐을 줄이는 현업 튜닝 절차. 패러노이아 레벨을 올리거나 차단 모드로 전환할 때도 쓴다. 확장 스킬.
metadata:
  track: "extension"
  role: "app-sec-ops"
  extends: "ncs-appops-32-recovery-docs, ncs-appops-22-improve"
  sources: "research/app-sec-ops.md"
---

# CRS 오탐 튜닝 (확장)

NCS 3-2는 과차단이 나면 '정책 수정 및 검증'을 하라고 한다. CRS 공식 문서는 그 수정을 **어떻게** 하는지
정해 둔다. 핵심은 규칙 파일을 고치지 않고, 가장 좁은 예외를 정해진 위치에 둔다는 것이다.

## 절차

1. **식별한다.** 오류 로그(`waf_events`)에서 오탐 요청마다 규칙 ID, 메시지, 매칭된 변수·값을 뽑는다.
2. **판정한다.** 매칭된 입력이 정말 정상 업무 트래픽인지 확인한다. 그 규칙이 애플리케이션의 다른
   부분에는 필요한지도 확인한다. 공격이 섞여 있으면 예외를 만들지 않는다.
3. **범위를 고른다.** 넓은 것에서 좁은 것 순서: 규칙 전체 제외 < 태그 제외 < **특정 변수만 제외**.
   가능하면 특정 변수(예: `ARGS:comment`)만 해당 규칙에서 뺀다.
4. **종류를 고른다.**
   - 전역 변경 → 구성 시점 예외(`SecRuleRemoveById`, `SecRuleUpdateTargetById` 등). CRS include **뒤**,
     `RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf`에 둔다. 요청마다 비용이 없다.
   - 특정 경로·조건에서만 → 실행 시점 예외(`SecRule ... "ctl:ruleRemoveTargetById=..."`). CRS include
     **앞**, `REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf`에 둔다.
5. **CRS 규칙 파일은 수정하지 않는다.** 업데이트 때 덮어써지고 자체 분기본이 된다.
6. **검증하고 반복한다.** 오탐 요청이 통과하는지, 같은 경로의 공격 요청(예: `' or 1=1--`)은 여전히 막히는지
   둘 다 시험한다. 패러노이아 레벨을 올리면 튜닝을 더 해야 한다고 예상해 둔다(PL1이 오탐이 가장 적다).

## 변경 요청서에 쓸 것

`change_prepare`(kind=waf): 규칙 ID, 예외 종류(구성 시점/실행 시점), 범위(규칙/태그/변수), 둘 위치(파일),
근거 로그, 시험 계획(정상·공격 요청 각각), 원복 방법(예외 줄 삭제).

## 출처

- OWASP CRS, False Positives and Tuning — https://coreruleset.org/docs/2-how-crs-works/2-3-false-positives-and-tuning/
- 더 나아가기(연구): ModSec-Learn — CRS 규칙 발동 여부를 특징으로 써서 규칙별 가중치를 학습, 같은 오탐률에서 탐지율 향상 (arXiv 2406.13547). research/app-sec-ops.md 참고.
