# 직무 확장 리서치 — 채용공고에서 스킬까지

NCS 학습모듈은 담당자가 일하는 **기준 방법**을 준다. 현업은 그보다 빠르게 바뀐다. 이 폴더는 직무마다
다음 순서로 일하는 방법을 넓힌 기록이다. 같은 순서를 `org/.claude/skills/research-to-skill`이 스킬로 담고 있어,
`researcher` 에이전트가 새 직무에도 반복할 수 있다.

```
채용공고 수집 → 현업 업무 추출 → NCS 스킬과 차이 분석 → 논문·표준 조사 → 확장 스킬(x-) 작성 → 실험으로 채택 판단
```

| 직무 | 기록 | 결과 확장 스킬 |
|---|---|---|
| 보안관제 분석가 | [soc-analyst.md](soc-analyst.md) | x-alert-triage-workflow, x-detection-as-code |
| 네트워크 보안 운영 | [nw-sec-ops.md](nw-sec-ops.md) | x-fw-policy-hygiene, x-change-verify |
| 네트워크 보안 설계·구축 | [nw-sec-build.md](nw-sec-build.md) | x-zero-trust-segmentation |
| 애플리케이션 보안 운영 | [app-sec-ops.md](app-sec-ops.md) | x-crs-fp-tuning |
| 시스템 보안 운영 | [sys-sec-ops.md](sys-sec-ops.md) | x-risk-based-patching |
| 시스템 보안 설계·구축 | [sys-sec-build.md](sys-sec-build.md) | x-hardening-as-code |
| 정보시스템 진단 | [diag-consultant.md](diag-consultant.md) | x-diag-task-tree |
| SW 개발 보안 | [sw-sec-dev.md](sw-sec-dev.md) | x-sast-llm-triage |
| 침해사고 대응 조정 | [cert-coordinator.md](cert-coordinator.md) | x-evidence-gated-containment |

조사일: 2026-10-18. 출처는 모두 원문 페이지를 열어 확인한 것만 적었다. 공고 수가 5건에 못 미치는 직무는
학생 과제(2권 14장)로 채운다.

## 이번 조사에서 직무를 가로질러 나온 결론

1. **문서(스킬)에 규칙을 쓰는 것과 강제는 다르다.** SOCpilot은 같은 정책 문장을 프롬프트에 넣었을 때 한 모델은
   위반율이 크게 올랐고(0.36→0.87) 다른 모델은 조금 내렸다고 보고했다. 그래서 반드시 지켜야 하는 규칙
   (근거·시험 계획·원복 방법·승인)은 `org/.claude/hooks/change_gate.py`로 강제하고, 스킬은 판단 방법을 담는다.
2. **에이전트의 약점은 '찾기'보다 '절제'와 '빈 결과 해석'이다.** OpenSec(과잉 봉쇄), Alert-Bench(조회 결과가
   비면 공격 경보를 기각, 재검토가 맞은 판정을 더 많이 뒤집음) 모두 같은 방향이다. 확장 스킬은 이 두 가지를 절차로 막는다.
3. **결과만이 아니라 과정(궤적)을 채점해야 한다.** Alert-Bench의 결론. 2권 실험은 최종 보고서와 함께 도구 호출
   순서·불러온 스킬을 채점한다(`experiments/`).
