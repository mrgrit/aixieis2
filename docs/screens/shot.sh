#!/usr/bin/env bash
# 명령 하나를 tmux 안에서 실행하고, 끝나면 그 터미널 화면을 PNG로 저장한다.
#
#   docs/screens/shot.sh <이름> <작업폴더> <열> <행> <명령...>
#   예) docs/screens/shot.sh 2-1 "$PWD/org" 128 12 bin/check
#
# 결과: docs/screens/<이름>.ansi(원본 텍스트), docs/screens/<이름>.png
# 프롬프트는 책에 실을 수 있도록 'student@lab:<폴더>$'로 바꿔 보여 준다.
# API 키 변수는 지우고 실행한다(구독 로그인 전용).
set -euo pipefail
name=$1; dir=$2; cols=$3; rows=$4; shift 4
here="$(cd "$(dirname "$0")" && pwd)"
sess="shot-$$"
top="$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null || echo "$dir")"
rel="${dir#"$top"}"
shown="~/aixieis2${rel}"
prompt="student@lab:${shown}\$ "
tmux new-session -d -s "$sess" -x "$cols" -y "$rows" -c "$dir" \
  "env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN PS1='$prompt' TERM=xterm-256color bash --norc --noprofile"
sleep 0.5
tmux send-keys -t "$sess" "clear" Enter
sleep 0.3
tmux clear-history -t "$sess"
tmux send-keys -t "$sess" "$*" Enter
# 마지막 줄이 프롬프트로 돌아오면 끝난 것으로 본다(최대 60분).
for _ in $(seq 1 1800); do
  sleep 2
  last=$(tmux capture-pane -t "$sess" -p | sed '/^[[:space:]]*$/d' | tail -1)
  [ "$last" = "${prompt% }" ] && break
done
tmux capture-pane -t "$sess" -e -p -S - > "$here/$name.ansi"
tmux kill-session -t "$sess"
python3 "$here/term2png.py" "$here/$name.ansi" "$here/$name.png" "터미널 — ${shown}"
