---
name: x-diag-task-tree
description: 진단 대상이 많거나 진단이 여러 세션에 걸칠 때, 진단 작업 트리(대상 → 분야 → 항목 → 상태)를 파일로 유지해 맥락을 잃지 않고 빠짐없이 진단할 때 사용한다. 확장 스킬.
metadata:
  track: "extension"
  role: "diag-consultant"
  extends: "ncs-diag-21-method, ncs-diag-22-execute"
  sources: "research/diag-consultant.md"
---

# 진단 작업 트리 (확장)

LLM 기반 모의해킹 연구(PentestGPT)는 모델이 도구 사용·결과 해석 같은 **하위 작업은 잘하지만, 전체 진단의
맥락을 유지하지 못한다**는 것을 보였다. 그래서 진단 전체를 트리로 적어 두고 매 단계 트리를 갱신하게 했다.
NCS 진단도 대상 × 분야 × 항목이 많아 같은 문제가 생긴다.

## 절차

1. 진단을 시작하면 `evidence/diag-tree.md`를 만든다.

```
- [ ] DB-Main (Unix, 내부망, 중요도 상)
  - [ ] 계정 관리
    - [x] root 원격 접속 — 취약 (sshd_config: PermitRootLogin yes) E3
    - [ ] 계정 잠금 임계값
  - [ ] 서비스 관리
  - [ ] 파일 시스템
- [ ] FW-Ext (방화벽)
```

2. 항목 하나를 끝낼 때마다 판정(양호·취약·확인 불가)과 근거 ID를 트리에 적는다.
3. 다음 작업을 고를 때 트리를 보고, 중요도 높은 대상의 미완료 항목부터 한다.
4. 보고서를 쓰기 전에 미완료 항목이 남았는지 확인하고, 남았다면 '한계'에 그대로 옮긴다.

## 출처

- Deng et al., PentestGPT: Evaluating and Harnessing Large Language Models for Automated Penetration Testing, USENIX Security 2024 — https://www.usenix.org/conference/usenixsecurity24/presentation/deng
