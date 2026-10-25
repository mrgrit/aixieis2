#!/usr/bin/env bash
# --repeat 3 의 실행별 도구 호출 순서 (SW-01 base, --repeat 3로 실행한 3회)
for d in $(ls -td experiments/results/SW-01/base/*-r[123]/ | tail -3 | sort); do
  echo "## $(basename $d)"
  jq -r 'select(.type=="assistant") | .message.content[] | select(.type=="tool_use")
    | "\(.name | sub("mcp__lab__";""))(\(.input | (.skill // .path // .kind // .app // .pattern // "") | tostring))"' "$d/transcript.jsonl" | nl -w2 -s'. '
done
