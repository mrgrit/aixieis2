#!/usr/bin/env bash
# Run every experiment command in the book, in 3 parallel lanes (tmux windows).
# usage: runall.sh start | lane <A|B|C|D|E|F> | status
set -u
cd ~/aixieis2
export PATH=$HOME/.local/bin:$PATH
unset ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN
LOG=~/aixieis2/docs/screens/runs
mkdir -p "$LOG"
R="python3 experiments/run.py"

# Phase 1: commands written in the manuscript (same repeat counts)
LANE_A=(
  "SW-05 --variant all --model haiku --repeat 2"
  "SW-04 --variant all --model haiku --repeat 2"
  "SW-03 --variant all --model haiku --repeat 3"
  "SB-01 --model haiku --repeat 3"
  "SB-02 --model haiku --repeat 3"
  "SB-03 --variant all --model haiku --repeat 3"
  "SB-05 --variant all --model haiku --repeat 3"
  "SB-04 --variant all --model haiku --repeat 3"
)
LANE_B=(
  "NB-01 --variant all --model haiku --repeat 3"
  "NB-02 --model haiku --repeat 3"
  "NB-04 --variant all --model haiku --repeat 3"
  "NB-03 --variant all --model haiku --repeat 3"
  "SYS-02 --model haiku --repeat 3"
  "SYS-04 --model haiku --repeat 3"
  "SYS-01 --variant all --model haiku --repeat 3"
  "SYS-03 --variant all --model haiku --repeat 3"
  "SYS-06 --variant all --model haiku --repeat 3"
  "SYS-05 --variant all --model haiku --repeat 3"
)
LANE_C=(
  "NW-02 --variant all --model haiku --repeat 5"
  "NW-07 --model haiku --repeat 3"
  "NW-01 --model haiku --repeat 3"
  "NW-04 --model haiku --repeat 3"
  "NW-03 --variant all --model haiku --repeat 3"
  "NW-05 --variant all --model haiku --repeat 3"
  "NW-06 --variant all --model haiku --repeat 3"
  "APP-01 --variant all --model haiku --repeat 3"
  "APP-02 --model haiku --repeat 3"
  "APP-03 --model haiku --repeat 3"
  "APP-04 --model haiku --repeat 3"
  "APP-06 --variant all --model haiku --repeat 3"
  "APP-05 --variant all --model haiku --repeat 3"
  "SOC-03 --variant all --model haiku --repeat 5"
)
# Phase 2: scenarios the chapters describe as practice but give no command for
LANE_D=(
  "SW-02 --model haiku --repeat 2"
  "DG-01 --model haiku --repeat 2"
  "DG-02 --model haiku --repeat 2"
  "DG-03 --variant all --model haiku --repeat 2"
  "DG-04 --model haiku --repeat 2"
  "DG-05 --variant all --model haiku --repeat 2"
  "RES-01 --model haiku --repeat 1"
)
LANE_E=(
  "SOC-02 --variant all --model haiku --repeat 2"
  "SOC-04 --variant all --model haiku --repeat 2"
  "SOC-05 --model haiku --repeat 2"
  "SOC-06 --variant all --model haiku --repeat 2"
  "SOC-07 --variant all --model haiku --repeat 2"
  "SOC-08 --variant all --model haiku --repeat 2"
  "SOC-09 --model haiku --repeat 2"
  "SOC-10 --variant all --model haiku --repeat 2"
  "SOC-01 --variant all --model haiku --repeat 2"
)
LANE_F=(
  "X-D1 --variant all --model haiku --repeat 2"
  "X-D3 --variant all --model haiku --repeat 2"
  "X-D4 --variant all --model haiku --repeat 2"
  "X-D5 --model haiku --repeat 2"
  "CISO-01 --variant all --model haiku --repeat 2"
  "DESK-01 --model haiku --repeat 2"
  "AUD-01 --model haiku --repeat 2"
  "IR-02 --model haiku --repeat 2"
  "IR-03 --variant all --model haiku --repeat 2"
)

run_lane() {
  local name=$1; shift
  local -n cmds=$1
  for c in "${cmds[@]}"; do
    local id=${c%% *}
    local f="$LOG/${id}.log"
    if grep -q '^EXIT=0' "$f" 2>/dev/null; then echo "skip $id"; continue; fi
    mkdir "$LOG/.lock-$id" 2>/dev/null || { echo "taken $id"; continue; }
    { echo "\$ $R $c"; echo "START $(date '+%F %T')"; } > "$f"
    $R $c >> "$f" 2>&1
    local rc=$?
    { echo "END $(date '+%F %T')"; echo "EXIT=$rc"; } >> "$f"
    echo "[$name] $id exit=$rc"
  done
  echo "[$name] DONE $(date '+%F %T')" >> "$LOG/_lanes.done"
}

case "${1:-}" in
  start)
    tmux kill-session -t book 2>/dev/null
    rm -rf "$LOG"/.lock-*
    tmux new-session -d -s book -n run "bash $0 lane A A2 B C E F; exec bash"
    tmux new-window -t book -n run2 "bash $0 lane B E C A F A2; exec bash"
    tmux new-window -t book -n run3 "bash $0 lane C F A B A2 E; exec bash"
    tmux new-window -t book -n mon "bash $0 mon"
    echo started ;;
  lane)
    shift
    for l in "$@"; do
      case $l in
        A) run_lane A LANE_A ;; B) run_lane B LANE_B ;; C) run_lane C LANE_C ;;
        A2) run_lane D LANE_D ;; E) run_lane E LANE_E ;; F) run_lane F LANE_F ;;
      esac
    done ;;
  mon)
    while :; do
      echo "$(date +%T) load=$(cut -d' ' -f1-3 /proc/loadavg) $(free -m | awk '/Mem/{print "used="$3"M avail="$7"M"}')" >> "$LOG/_mon.log"
      sleep 30
    done ;;
  status)
    for f in "$LOG"/*.log; do
      printf '%-8s %s %s\n' "$(basename "$f" .log)" "$(grep -c '인증=' "$f")runs" "$(grep -o 'EXIT=[0-9]*' "$f" || echo running)"
    done
    cat "$LOG/_lanes.done" 2>/dev/null ;;
esac
