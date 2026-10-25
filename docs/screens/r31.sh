#!/usr/bin/env bash
# 3.8 실습 명령 (원고 그대로)
python3 experiments/run.py SW-01 --model haiku
T="$(ls -td experiments/results/SW-01/base/*/ | head -1)transcript.jsonl"
echo "# 1) 세션 시작: 무엇이 읽혔나"
jq -c 'select(.type=="system" and .subtype=="init")
  | {model, permissionMode, apiKeySource,
     ncs_skills: ([.skills[] | select(startswith("ncs-"))] | length),
     mcp: [.mcp_servers[].name]}' "$T"
echo "# 2) 루프: 모델이 낸 도구 호출과 답"
jq -r 'select(.type=="assistant") | .message.content[]
  | if .type=="tool_use" then "tool  \(.name) \(.input | tostring | .[0:70])"
    elif .type=="text" then "text  \(.text | .[0:70])" else empty end' "$T"
echo "# 3) 훅이 실행된 시점"
jq -r 'select(.type=="system" and .subtype=="hook_response")
  | "\(.hook_name) exit=\(.exit_code)"' "$T"
echo "# 4) 루프 종료"
jq -c 'select(.type=="result") | {num_turns, duration_ms, stop_reason, is_error}' "$T"
