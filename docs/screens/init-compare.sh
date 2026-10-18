#!/usr/bin/env bash
# 화면 2-2: 저장소 루트와 org/에서 시작한 세션이 각각 무엇을 읽었는지 비교한다.
# 세션 시작 기록(stream-json의 init 메시지)에서 근무자 에이전트 수, 스킬 수, 랩 서버 연결 여부만 뽑는다.
# 요청은 "ok" 한 번, 1턴이다(구독 로그인, API 키 변수 제거).
set -uo pipefail
root="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
unset ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN
filter='select(.type=="system" and .subtype=="init")
 | {"폴더": (.cwd|split("/")|.[-1]),
    "근무자": ([.agents[] | select(IN("sw-sec-dev","sys-sec-build","nw-sec-build","sys-sec-ops","nw-sec-ops","app-sec-ops","diag-consultant","soc-analyst","cert-coordinator","ciso","service-desk","auditor","researcher"))] | length),
    "NCS스킬": ([.skills[] | select(startswith("ncs-"))] | length),
    "확장스킬": ([.skills[] | select(startswith("x-"))] | length),
    "랩서버": ([.mcp_servers[].name] | index("lab") != null),
    "인증": .apiKeySource}'

echo '$ cd ~/aixieis2 && claude -p ok --model haiku --max-turns 1 --output-format stream-json --verbose | jq …'
(cd "$root" && claude -p ok --model haiku --max-turns 1 --output-format stream-json --verbose 2>/dev/null | jq -c "$filter")
echo
echo '$ cd ~/aixieis2/org && MODEL=haiku bin/work sw-sec-dev -p ok --max-turns 1 --output-format stream-json --verbose | jq …'
(cd "$root/org" && MODEL=haiku bin/work sw-sec-dev -p ok --max-turns 1 --output-format stream-json --verbose 2>/dev/null | jq -c "$filter")
