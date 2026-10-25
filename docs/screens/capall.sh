#!/usr/bin/env bash
# 결과 자리·추가 화면 캡처. 실험이 모두 끝난 뒤 실행한다.
#   docs/screens/capall.sh [이름 ...]   (이름을 주면 그것만)
set -u
cd ~/aixieis2
export PATH=$HOME/.local/bin:$PATH
S=docs/screens/shot.sh
R="python3 experiments/run.py"
T="python3 docs/screens/tally.py"
X="python3 docs/screens/excerpt.py"
P=docs/screens/replay.sh

declare -A C
# 결과 자리 (원고 순서)
C[R6-1a]="$P SB-01 && $R --compare SB-01"
C[R6-1b]="$X SB-01 base 1 12"
C[R6-2a]="$P SB-02 && $R --compare SB-02"
C[R6-2b]="$X SB-02 base 1 30"
C[R6-3]="$R --compare SB-03 && $T SB-03 pam_faillock pam_permit 배포판"
C[R6-4a]="$R --compare SB-05"
C[R6-4b]="jq -c 'select(.tool==\"change_apply\")' experiments/results/SB-05/*/*/evidence/tools.jsonl; jq -c 'select(.tool|endswith(\"change_apply\"))' experiments/results/SB-05/*/*/evidence/gate.jsonl; $T SB-05 승인 '팀장 지시'"
C[R6-5]="$R --compare SB-04 && $T SB-04 neobank"
C[R7-1]="$P NB-01 && $X NB-01 base 1 30"
C[R7-2]="$P NB-02 && $R --compare NB-02 && $X NB-02 base 1 20"
C[R7-3]="$R --compare NB-01 && grep -c '513' experiments/results/NB-01/V1/*/answer.md; $T NB-01 513 514"
C[R7-4]="$R --compare NB-04 && $T NB-04 '규칙 2' A-1187"
C[R7-5]="$R --compare NB-03 && $T NB-03 '규칙 1'"
C[R8-1]="$P SYS-02 && $R --compare SYS-02 && $X SYS-02 base 1 14"
C[R8-2]="$P SYS-04 && $R --compare SYS-04 && $X SYS-04 base 1 20"
C[R8-3a]="$R --compare SYS-01 && $T SYS-01"
C[R8-3b]="$R --compare SYS-03 && $T SYS-03 전체 증분 차등 스냅샷"
C[R8-4]="$R --compare SYS-06 && jq -c 'select(.tool==\"change_apply\") | {status, note}' experiments/results/SYS-06/*/*/evidence/tools.jsonl; jq -c 'select(.tool|endswith(\"change_apply\")) | {decision, problems}' experiments/results/SYS-06/*/*/evidence/gate.jsonl; $T SYS-06"
C[R8-5]="$R --compare SYS-05 && $T SYS-05"
C[R9-1]="$P NW-02 && $X NW-02 base 1 14"
C[R9-2]="$P NW-07 && $R --compare NW-07 && $X NW-07 base 1 12"
C[R9-3]="$P NW-01 NW-04 && $R --compare NW-01 && $R --compare NW-04 && $T NW-01 10.20.70.15"
C[R9-4]="$R --compare NW-02 && $T NW-02"
C[R9-5]="$R --compare NW-03 && jq -c 'select(.tool==\"change_apply\" or .tool==\"approval_request\") | {tool, status, args}' experiments/results/NW-03/*/*/evidence/tools.jsonl | cut -c1-200; $T NW-03"
C[R9-6]="$R --compare NW-05 && $R --compare NW-06 && $T NW-06"
C[R10-1]="$R --compare APP-01 && $T APP-01"
C[R10-2]="$P APP-02 && $R --compare APP-02 && $X APP-02 base 1 24"
C[R10-3]="$P APP-03 APP-04 && $R --compare APP-03 && $R --compare APP-04 && $X APP-04 base 1 16"
C[R10-5]="$R --compare APP-06 && jq -c 'select(.tool==\"change_prepare\") | {status, kind: .args.kind}' experiments/results/APP-06/*/*/evidence/tools.jsonl; $T APP-06"
C[R10-6]="$R --compare APP-05 && $T APP-05"
# 원고 화면 자리 중 실험 뒤에 찍는 것 (INSTRUCTIONS.md 명령 그대로)
C[5-4]="$R --compare SW-03"
C[15-1]="$R SOC-03 --variant all --dry-run && $R --compare SOC-03"
# 화면 자리가 없는 실습 (추가 화면)
C[A5-SW02]="$P SW-02 && $X SW-02 base 1 12"
C[A3-XD]="$P X-D1 X-D3 X-D4 && $R --compare X-D1 && $R --compare X-D3 && $R --compare X-D4"
C[A11-DG]="$P DG-01 DG-02 DG-03 DG-04 DG-05 && $R --compare DG-03 && $R --compare DG-05"
C[A12-4]="$P SOC-01 SOC-02 SOC-04 && $R --compare SOC-01 && $R --compare SOC-02 && $R --compare SOC-04"
C[A12-5]="$P SOC-06 SOC-09 && $R --compare SOC-06 && $R --compare SOC-09 && $T SOC-06 10.20.30.1"
C[A12-6]="$P SOC-07 SOC-08 SOC-10 && $R --compare SOC-07 && $R --compare SOC-08 && $R --compare SOC-10"
C[A13]="$P IR-02 IR-03 CISO-01 DESK-01 AUD-01 && $R --compare IR-03 && $R --compare CISO-01 && $T IR-03 && $T CISO-01"
C[A14-RES]="$P RES-01 && ls -l experiments/results/RES-01/base/*/org/candidates/"
C[A15-XD5]="$P X-D5 && $R --compare X-D5"

names=("$@")
[ ${#names[@]} -eq 0 ] && names=($(printf '%s\n' "${!C[@]}" | sort -V))
for n in "${names[@]}"; do
  echo "== $n"
  $S "$n" "$PWD" 150 40 "${C[$n]}" >/dev/null 2>&1 || echo "FAIL $n"
done
