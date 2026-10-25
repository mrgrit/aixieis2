#!/usr/bin/env bash
# Screen 5-1: interactive bin/work sw-sec-dev session handling SW-01 (per INSTRUCTIONS.md)
set -u
export PATH=$HOME/.local/bin:$PATH
cd ~/aixieis2
tmux kill-session -t sw 2>/dev/null
# one-time: accept the folder trust dialog in a throwaway session
if ! python3 -c "import json,sys;d=json.load(open('$HOME/.claude.json'));sys.exit(0 if d.get('projects',{}).get('$PWD/org',{}).get('hasTrustDialogAccepted') else 1)"; then
  tmux new-session -d -s trust -x 120 -y 40 -c "$PWD/org" "env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN PATH=$PATH bin/work sw-sec-dev"
  sleep 10; tmux send-keys -t trust Down; sleep 1; tmux send-keys -t trust Enter; sleep 8
  tmux send-keys -t trust '/exit' Enter; sleep 3; tmux kill-session -t trust 2>/dev/null
fi
tmux new-session -d -s sw -x 120 -y 60 -c "$PWD/org" \
  "env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN PATH=$PATH PS1='student@lab:~/aixieis2/org\$ ' TERM=xterm-256color bash --norc --noprofile"
tmux send-keys -t sw 'LAB_FIXTURES=../experiments/scenarios/SW-01.yaml MODEL=haiku bin/work sw-sec-dev' Enter
sleep 10; tmux capture-pane -t sw -p | tail -15
if tmux capture-pane -t sw -p | grep -q 'trust this folder'; then echo "TRUST DIALOG STILL SHOWN"; tmux kill-session -t sw; exit 1; fi
tmux send-keys -t sw 'neobank SAST 결과를 보고 F1을 판정하고, 정탐이면 수정안을 변경 요청서로 올려 주세요.' Enter
prev=""; same=0
for i in $(seq 1 30); do
  sleep 10
  cur=$(tmux capture-pane -t sw -p)
  if [ "$cur" = "$prev" ]; then same=$((same+1)); else same=0; fi
  prev=$cur
  [ $same -ge 2 ] && break
done
tmux capture-pane -t sw -e -p -S - > docs/screens/5-1.ansi
python3 docs/screens/term2png.py docs/screens/5-1.ansi docs/screens/5-1.png "터미널 — ~/aixieis2/org · bin/work sw-sec-dev"
tmux send-keys -t sw '/exit' Enter; sleep 2; tmux kill-session -t sw 2>/dev/null
wc -l docs/screens/5-1.ansi
