---
name: x-hardening-as-code
description: 서버 보안 설정(하드닝)을 CIS 벤치마크 같은 합의된 기준의 항목 ID로 관리하고, 점검을 반복 가능한 코드(점검 스크립트·컴플라이언스 도구)로 만들어 구현 전후와 정기 점검에서 같은 결과가 나오게 할 때 사용한다. 확장 스킬.
metadata:
  track: "extension"
  role: "sys-sec-build"
  extends: "ncs-sysbuild-21-implement, ncs-sysbuild-22-verify"
  sources: "research/sys-sec-build.md"
---

# 하드닝을 코드로 (확장)

NCS 2-1·2-2는 설정 항목을 사람이 파일을 열어 바꾸고 다시 열어 확인한다. 현업은 같은 기준을 수십~수백 대에
반복 적용해야 하므로, 기준을 **항목 ID**로 부르고 점검을 **코드**로 만든다.

## 절차

1. 기준을 고른다: 운영체제별 CIS 벤치마크(합의 기반 권고), 국내 기준(주요정보통신기반시설 취약점 분석·평가
   항목)과 조직 정책. NCS 항목과 기준 항목 ID를 짝지은 대응표를 만든다.
2. 항목마다 점검을 코드로 쓴다: 무엇을 읽고(파일·명령), 어떤 값이면 양호인지, 결과 형식(JSON 한 줄).
3. 구현 전 점검 → 변경 → 구현 후 점검. 두 결과의 차이가 변경 요청서와 일치해야 한다.
4. 정기 점검에 같은 코드를 쓴다. 결과가 바뀐 항목만 사람이 본다(드리프트).
5. 예외는 코드가 아니라 예외 대장에 남긴다(사유, 승인자, 만료일).

## 대응표 예

| NCS 항목 | 리눅스 점검 | 양호 기준 |
|---|---|---|
| root 원격 접속 제한 | `sshd -T | grep permitrootlogin` | `no` |
| 최소 길이 | `/etc/login.defs`의 PASS_MIN_LEN 또는 pwquality minlen | 조직 기준 이상(NCS 예 8) |
| 최대 사용 기간 | PASS_MAX_DAYS | 90 이하 |

## 출처

- CIS Benchmarks — https://www.cisecurity.org/cis-benchmarks
- NCS 시스템 보안 구축 학습 2-1·2-2 항목
