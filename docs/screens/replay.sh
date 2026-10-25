#!/usr/bin/env bash
# 일괄 실행 때 남긴 로그에서 실행 명령과 실행별 결과 줄을 그대로 보여 준다.
#   docs/screens/replay.sh <ID> ...
for id in "$@"; do
  f=docs/screens/runs/$id.log
  s=$(sed -n 's/^START //p' "$f"); e=$(sed -n 's/^END //p' "$f")
  head -1 "$f"
  grep -vE '^(\$ |START |END |EXIT=)' "$f"
  echo "  (실행 $s ~ ${e#* })"
done
