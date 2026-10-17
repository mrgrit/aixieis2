# 2권 실습 환경 — 정보보호본부 근무자 만들기

『AI 에이전트 × 정보보안산업기사 과정평가 자격과정 2』의 실습 저장소 안내다.
1권이 학습모듈마다 **앱**을 만들었다면, 2권은 학습모듈에 나오는 **업무 담당자**를 Claude Code 에이전트로 만들고,
학생은 그 담당자가 쓸 **업무 방법(스킬)** 을 학습모듈대로 작성한다. 바탕 인프라와 화면은 kt66을 그대로 물려받는다.

## 실행 폴더와 작업 폴더

| 구분 | 폴더 | 용도 |
|---|---|---|
| 에이전트 실행 폴더 | `org/` | 정보보호본부 에이전트 13개. 이 폴더에서 `claude`를 실행하면 에이전트로 동작한다 |
| 작업 폴더 | 저장소 루트 | 학생·강사가 스킬을 작성하고 실험을 실행해 결과를 비교한다 |

루트에는 `CLAUDE.md`를 두지 않는다. 근무 규칙은 `org/CLAUDE.md`에만 있다. 루트에서 실행한 세션에는
에이전트 근무 규칙이 적용되지 않는다.

## `org/` — Claude Code 표준 파일 체계

```
org/
├── CLAUDE.md                     조직 공통 근무 규칙(모든 근무자에게 자동으로 읽힘)
├── .claude/
│   ├── agents/<직무>.md          근무자 13명 — frontmatter(name, description, tools, model) + 본문
│   ├── skills/<스킬>/SKILL.md    업무 방법 66개 — frontmatter(name, description, metadata) + 절차
│   ├── settings.json             권한(allow/deny)과 훅
│   └── hooks/                    세션 기록, 스킬 사용 기록, 변경 게이트, 보고 게이트
├── .mcp.json                     랩 MCP 서버(lab) 등록
├── lab/                          랩 MCP 서버, 직무별 도구 권한(roles.yaml)
├── bin/work                      에이전트 하나를 실행하는 스크립트
├── bin/check                     에이전트·스킬·권한의 정합성 검사
├── evidence/  tickets/  candidates/   근무 기록, 티켓, 스킬 후보(연구원 산출물)
```

Claude Code가 읽는 곳은 `CLAUDE.md`, `.claude/agents/`, `.claude/skills/`, `.claude/settings.json`, `.mcp.json`이다.
kt66 1판이 쓰던 `.agents/skills/`와 별도 스킬 조회 도구는 Claude Code가 읽지 않으므로 2권에서는 쓰지 않는다.

## 시작하기

```bash
cd org
bin/check                                   # 에이전트 13, 스킬 66, 문제 0 이어야 한다
bin/work soc-analyst                        # 관제 분석가로 대화형 근무
bin/work nw-sec-ops -p "방화벽 정책 점검해 줘"   # 한 번 묻고 끝내기
LAB_MODE=live bin/work soc-analyst          # kt66 컨테이너를 읽기 전용으로 조회
```

`bin/work`는 `claude --agent <직무> --setting-sources project,local --mcp-config .mcp.json --strict-mcp-config`로
에이전트를 실행한다. 처음 여는 폴더는 Claude Code가 '신뢰하지 않은 작업 공간'으로 보고 `settings.json`의 허용 목록을
무시하므로, 실행기가 같은 목록을 `--allowedTools`로 넘긴다.

## 학습모듈 ↔ 근무자 ↔ 스킬

| 학습모듈 (NCS) | 근무자 | 스킬 | 수 |
|---|---|---|---|
| SW 개발 보안 구축 | `sw-sec-dev` | `ncs-sw-*` | 4 |
| 시스템 보안 구축 | `sys-sec-build` | `ncs-sysbuild-*` | 5 |
| 네트워크 보안 구축 | `nw-sec-build` | `ncs-nwbuild-*` | 5 |
| 시스템 보안 운영 | `sys-sec-ops` | `ncs-sysops-*` | 8 |
| 네트워크 보안 운영 | `nw-sec-ops` | `ncs-nwops-*` | 8 |
| 애플리케이션 보안 운영 | `app-sec-ops` | `ncs-appops-*` | 8 |
| 정보시스템 진단 | `diag-consultant` | `ncs-diag-*` | 6 |
| 보안 로그 분석 | `soc-analyst` | `ncs-log-*` | 6 |
| (학습모듈 밖 협업) | `cert-coordinator`, `ciso`, `service-desk`, `auditor`, `researcher` | `ir-coordination`, `approval-review`, `intake-assign`, `evidence-audit`, `research-to-skill` | 5 |
| (확장) | 직무별 | `x-*` | 11 |

스킬 이름의 두 자리 숫자는 학습모듈의 '학습 번호-하위 번호'다(`ncs-log-12-analysis` = 보안 로그 분석 학습 1의 1-2).
학습모듈 하위 학습 50개를 모두 하나씩 스킬로 옮겼다.

## 지침과 강제

같은 규칙을 세 계층에 둔다. 실험(X-D1~X-D3)은 계층을 하나씩 제거해 결과를 비교한다.

| 계층 | 위치 | 예 | 모델이 무시할 수 있나 |
|---|---|---|---|
| 지침 | `CLAUDE.md`, 에이전트 본문, 스킬 | "승인 없이 적용하지 않는다" | 있다 |
| 클라이언트 강제 | 에이전트 `tools`, `settings.json` deny, 훅 | `change_gate.py`가 근거·시험 계획·원복 없는 변경 요청을 거절 | 없다(같은 PC 안) |
| 서버 강제 | `lab/roles.yaml` | 관제 분석가가 `fw_rules`를 부르면 `role_boundary` | 없다(에이전트 파일을 고쳐도) |

## 확장 — 채용공고 → 논문 → 스킬

학습모듈은 기준선이다. 현업 직무가 요구하는 업무 절차는 다음 순서로 추가한다(`research/`).

1. 채용 사이트에서 같은 직무 공고를 모아 요구 업무·자격을 정리한다.
2. 학습모듈 스킬과 비교해 빠진 업무를 표로 만든다.
3. 빠진 업무에 대해 최근 논문·표준·공식 문서를 찾는다(쪽수·URL 기록).
4. `x-` 스킬로 쓰고 `metadata.extends`에 어떤 NCS 스킬을 넓히는지 적는다.
5. 확장 스킬을 뺀 변형(`N0`)과 비교하는 실험을 만든다.

`researcher` 근무자가 이 순서를 `research-to-skill` 스킬로 수행하고, 결과는 `candidates/`에만 쓴다.
운영 스킬에 넣을지는 사람이 실험 결과를 보고 정한다.

## 실험

`experiments/README.md` 참고. 55개 시나리오, 기준선·변형 비교, 과정·결과 채점.

## 학습모듈 원문 확인 필요 (스킬에 메모로 남김)

| 위치 | 내용 |
|---|---|
| 네트워크 보안 구축 설계 | syslog 포트가 UDP/513으로 적힌 곳이 있다(표준은 514) |
| 시스템 보안 구축 구현 | 잠금 설정 예에 `pam_permit.so`/`pam_tally`가 나온다(현행은 `pam_faillock`) |
| 시스템 보안 구축 구현 | `TIMEOUT`과 `TMOUT` 표기가 섞여 있다(셸 변수는 `TMOUT`) |
| 시스템 보안 운영 | <표 2-12> 번호가 두 번 쓰였다(37쪽) |
| 침해사고 대응 | 보안 로그 분석은 6단계, 다른 모듈은 7단계로 적는다 |
| 시험지 | 보안로그분석 시험지 제목이 '정보시스템 진단'으로 된 판이 있다 |
| 시스템 보안 운영 | 백업 형태를 '특정 파일·폴더 / 전체 시스템 초기 / 변경 사항 스냅샷'으로 나눈다(일반 교재의 전체·증분·차등과 다름) |
