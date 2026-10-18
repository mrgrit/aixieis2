---
name: ncs-sysbuild-21-implement
description: 설계에 따라 유닉스·리눅스 서버와 DBMS에 보안 설정을 구현할 때 사용한다. root 원격 접속 제한, 불필요 계정 제거, 관리자 그룹 최소화, 패스워드 파일 보호·잠금 임계값·길이·사용 기간, 세션 타임아웃, 불필요 서비스(NFS) 중지, Apache 상위 디렉터리 접근 금지, 주요 파일 권한, 로깅, DBMS 계정·원격 접속·권한을 다룬다.
metadata:
  ncs: "LM2001020613_19v5 시스템 보안 구축 / 학습 2-1 시스템 보안 구현 (pp.47-68)"
  role: "sys-sec-build"
---

# 시스템 보안 구현 (학습 2-1)

구현은 설정 변경이다. 항목마다 `change_prepare`(kind=host)로 요청서를 만들고(현재 값은 `host_config`로 조회해
근거로 붙임) 승인 후 적용 담당(`sys-sec-ops`)이 반영한다. 아래는 학습모듈이 제시한 설정이다.

## 계정 관리 (pp.49-51)

| 항목 | 리눅스 설정 |
|---|---|
| root 원격 접속 제한 | `/etc/ssh/sshd_config`에 `PermitRootLogin no`, sshd 재시작 |
| 불필요 계정 제거 | `/etc/passwd` 확인, 미사용·기본(Default) 계정 삭제 |
| 관리자 그룹 최소화 | `/etc/group`의 root 그룹에서 불필요 계정 제거 |

## 패스워드 관리 (pp.51-53)

| 항목 | 리눅스 설정 |
|---|---|
| 패스워드 파일 보호 | 섀도 패스워드 사용 |
| 잠금 임계값 | `/etc/pam.d/common-auth`에 실패 5회 잠금(원문 예: `deny=5 unlock_time=120`) |
| 최소 길이 | `/etc/login.defs`의 `PASS_MIN_LEN 8` |
| 최대 사용 기간 | `PASS_MAX_DAYS 90` |
| 최소 사용 기간 | `PASS_MIN_DAYS 1` |

원문 확인 필요: 학습모듈은 잠금 설정 모듈을 `pam_permit.so`(p.52), `pam_tally.so ... unlock_time120`(검증 단원)으로
적었다. `pam_permit.so`는 실패 횟수를 세지 않는다. 현재 배포판은 `pam_faillock`을 쓰므로 실제 적용 전 배포판
문서로 모듈과 문법을 확인한다.

## 세션·서비스·파일 (pp.54-58)

- 세션 타임아웃: `/etc/profile`에 타임아웃 600초 설정 후 export(원문은 `TIMEOUT=600`과 `export TMOUT`을 함께
  적었다. 셸이 읽는 변수는 `TMOUT`이므로 `TMOUT=600`으로 쓴다).
- NFS 비활성화(프로세스 중지, 시동 스크립트 제거), `/etc/exports` 소유자 root·권한 제한.
- Apache 상위 디렉터리 접근 금지(`httpd.conf`의 Directory 설정, `.htaccess` 인증) 후 재시작.
- 파일 소유자·권한: `/etc/passwd`, `/etc/shadow`, `/etc/services`, `hosts.lpd`, cron.allow·cron.deny를 root 소유, 최소 권한.

## 로그 (p.59)

로그를 정기 분석·보고하고, 정책에 따라 `/etc/rsyslog.conf`를 설정한 뒤 데몬을 재시작한다.

## DBMS (pp.60-64)

기본 계정 비밀번호 변경, 미사용 계정 삭제, 원격 접속 제한, WEB·WAS 접속 계정은 최소 권한.

## 근거

- NCS 시스템 보안 구축 학습 2-1 (pp.49-64)
