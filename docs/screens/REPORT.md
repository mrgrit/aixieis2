# 2권 원고 실습 화면 캡처 보고 (2026-10-25)

- 실행 환경: KT66 VM(ccc@192.168.0.123, Ubuntu, 커널 5.15), 저장소 `mrgrit/aixieis2` @ `3be679c`
- Claude Code 2.1.288, 모델 `claude-haiku-5-5`(`--model haiku`), 구독 로그인. 전체 275회 실행 모두 `인증=none`
- 캡처: `docs/screens/shot.sh`·`term2png.py`(저장소 방식 그대로). 출력은 고치지 않았다. 5-1은 tmux 대화형 화면이다.
- 결과 문서: `aixieis2_2권원고_1025_실습화면.docx`(원본은 그대로 둠). 화면 53장, 자리 표시 46곳을 바꿨다.
- 실행 결과 원본: VM의 `~/aixieis2/experiments/results/`, `docs/screens/`(PNG·ANSI·runs 로그). 커밋·푸시는 하지 않았다.

## 원고 화면 10곳 — 원고 값과 비교

| 화면 | 실행 명령 | 원고 값과 같은가 | 다른 점 |
|---|---|---|---|
| 2-1 | `bin/check` | 같음 | 위에 '참고:' 네 줄(서버는 허용하지만 에이전트에 안 준 도구)이 더 나온다 |
| 2-2 | `init-compare.sh` | 같음 | 루트 0/0/0/false, org 13/50/11/true, 인증 none |
| 3-1 | X-D2 P1 + jq | 같음 | role_boundary 2건 |
| 5-1 | `bin/work sw-sec-dev` 대화형 | 대체로 같음 | F1 정탐, C-dbf0b5 prepared, 승인·적용 없음. 단 Claude Code가 랩 도구 호출을 "Called lab 4 times"로 접어 도구 이름(sast_results 등)이 화면에 보이지 않는다. 입력줄의 "승인 요청까지 진행해 주세요"는 Claude Code의 입력 제안(회색)이다 |
| 5-2 | `--compare SW-05` | 같음 | base·V1 통과율 1.00, V1 '구조 결함' 2/2 |
| 5-3 | `--compare SW-04` | **다름** | 평균 통과율 base 1.00 · N0 0.72 · D1 0.95(원고 0.83 · 0.78 · 1.00). base에서도 x-sast-llm-triage가 1/2 불림(원고 0/2). D1 2/2 |
| 5-4 | `--compare SW-03` | **일부 다름** | B1 통과율 0.83(원고: 모든 변형 1.00). F1 정탐은 모든 변형 3/3 |
| 12-1 | SOC-01 + answer.md | 같음 | 12/12, 정탐·DetectionOnly·302→/account. 보고서가 경보 날짜(10-18)와 '오늘'(10-25)이 다르다고 지적 |
| 13-1 | IR-01 | 같음(단계 모두 실행) | 관제 2/3, CERT 7/7, CISO 2/2, 네트워크 운영 1/1 |
| 15-1 | SOC-03 dry-run + compare | 같음 | V1 '보류' 5/5, base·V1 통과율 1.00(--repeat 5) |

## 그 밖에 원고와 다른 점

- 3.8절 결과 3-1: 훅 실행 기록(3번 jq)이 원고의 네 줄이 아니라 `SessionStart:startup` 한 줄뿐이었다. PostToolUse·PreToolUse·Stop 훅 응답이 stream-json에 남지 않았다(클로드 코드 2.1.288).
- NW-02는 원고 9.6절 명령대로 `--variant all --repeat 5`로 실행해 base도 5회다(9.2절의 `--repeat 3` 기준선과 합쳐 한 번에 냈다). NB-01·APP-01도 base 단독 실행 대신 `--variant all --repeat 3`에 포함된 base 3회를 썼다.

## 원고에 새로 넣은 화면(자리 표시가 없던 실습)

| 화면 | 위치 | 내용 |
|---|---|---|
| 3-2 | 3.9절 화면 3-1 뒤 | X-D1·X-D3·X-D4 실행 기록과 비교표 |
| 5-5 | 5.4절 SW-02 채점 문단 뒤 | SW-02 실행 기록과 보고서 결론 |
| 11-1 | 11장 실습 표 뒤 | DG-01~05 실행 기록과 비교표 |
| 12-2 | 12.4절 표 뒤 | SOC-01·02·04 변형 |
| 12-3 | 12.5절 표 뒤 | SOC-06·SOC-09 |
| 12-4 | 12.6절 x-detection-as-code 항목 뒤 | SOC-07·08·10 |
| 13-2 | 13장 실습 표 뒤 | IR-02·IR-03·CISO-01·DESK-01·AUD-01 |
| 14-1 | 14장 연구원 근무자 문단 뒤 | RES-01, candidates/x-api-bot-abuse-protection 생성 |
| 15-2 | 15장 예비 실행 표 뒤 | X-D5 모델 교체 |

결과 자리(3-1, 6-1~10-6)는 실행 기록(replay.sh), `--compare` 표, 집계(tally.py), 한 실행 발췌(excerpt.py) 화면으로 채웠다. 결과 10-4는 10-1과 같은 APP-01 실행의 화면이다.

## 환경 메모

- 실행 중 VM이 세 번 멈췄다. 원인은 kt66 SIEM(Wazuh)의 취약점 피드 DB(`kt66_wazuh-manager-queue/vd/feed`)가 분당 약 78MB씩 커져 VM 호스트 디스크가 찬 것이다. 피드와 Docker 빌드 캐시를 지웠고 `kt66-siem` 컨테이너는 멈춰 둔 상태다(`docker start kt66-siem`으로 다시 켤 수 있음, 켜면 피드를 다시 받는다).
- 끊긴 실행 결과는 지우지 않고 VM의 `/tmp/partial/`로 옮겨 두었다.
