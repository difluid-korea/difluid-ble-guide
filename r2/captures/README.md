# 캡처 로그 · Capture logs

[← R2 Extract](../README.md) · [English](../README.en.md)

R2 Extract 와 주고받은 바이트를 그대로 남긴 로그 9개입니다(2026-11-01, Linux/BlueZ + bleak). [실측 확인 기록](../verification.md)의 판정은 이 바이트에 기댑니다.<br>
Nine logs of the raw bytes exchanged with R2 Extract units (2026-11-01, Linux/BlueZ + bleak). The [verification record](../verification.md) relies on these bytes.

## 목록 · Files

| # | 파일 · File | 기기 · Unit | 내용 · What happened |
|---|---|---|---|
| 1 | [2026-11-01-1-unitA-single.log](2026-11-01-1-unitA-single.log) | A | 단일 측정 명령 → 「측정 시작」과 하드웨어 오류 3 이 한 notify 로 · single test → "start" and hardware error 3 in one notification |
| 2 | [2026-11-01-2-unitB-button.log](2026-11-01-2-unitB-button.log) | B | 120 s 청취 중 본체 버튼 단일 4회(물 3 · 빈 프리즘 1). 첫 결과는 「측정 시작」 없이 옴 · 4 single button tests during a 120 s listen (3 water, 1 empty prism); the first arrived without "start" |
| 3 | [2026-11-01-3-unitB-single.log](2026-11-01-3-unitB-single.log) | B | 단일 측정 명령(물 −1.15 %) · single test command (water −1.15 %) |
| 4 | [2026-11-01-4-unitB-connect-only.log](2026-11-01-4-unitB-connect-only.log) | B | 측정 없이 연결 — 지난 결과가 오지 않음 · connect only — no past results |
| 5 | [2026-11-01-5-unitC-single.log](2026-11-01-5-unitC-single.log) | C | 단일 측정 명령(커피 8.11 %), 이어 본체 버튼 평균이 2회차까지 · single test command (coffee 8.11 %), then a button average up to round 2 |
| 6 | [2026-11-01-6-unitC-button-average.log](2026-11-01-6-unitC-button-average.log) | C | 150 s 청취 중 본체 버튼 평균 3회 × 2(8.15 % · 8.14 %) · two 3-round button averages during a 150 s listen (8.15 %, 8.14 %) |
| 7 | [2026-11-01-7-unitC-before-calibration.log](2026-11-01-7-unitC-before-calibration.log) | C | 증류수 단일 측정 0.00 % · distilled water, single test, 0.00 % |
| 8 | [2026-11-01-8-unitC-calibration.log](2026-11-01-8-unitC-calibration.log) | C | 영점 교정 명령 → 성공(0.00 %) · calibration command → success (0.00 %) |
| 9 | [2026-11-01-9-unitC-after-calibration.log](2026-11-01-9-unitC-after-calibration.log) | C | 교정 뒤 증류수 단일 측정 0.00 % · distilled water after calibration, single test, 0.00 % |

기기 X 는 로그 1 의 스캔 목록에만 보이는 주변 기기입니다. · Unit X only appears in the scan list of log 1.

## 읽는 법 · How to read

- `[   2.625s] TX …` = 보낸 바이트(첫 송신 기준 초) · bytes sent (seconds from the first write)
- `[   2.887s] RX[aa01] len=…` = `0xAA01` notify 로 받은 바이트 그대로 · raw bytes received on `0xAA01`
- `└ …` = 캡처 도구가 프레임을 나누고 해석한 줄 · the capture tool's split and decode
  - `tank` 는 시료 온도입니다 · `tank` means the sample temperature.
  - **해석 줄 두 종류는 틀렸습니다** — 줄 끝에 ⚠ 표시를 달았습니다. 바이트가 정본입니다. · **Two kinds of decode lines are wrong** and are marked with ⚠ at the end. The bytes are authoritative.
    1. 로그 1 의 `ERROR class=0 code=3` — 실제는 분류 3(하드웨어)·코드 3 · actually class 3 (hardware), code 3.
    2. 로그 5·6 패키지 3 의 `RI=8.1xx` — 그 4 B 칸은 굴절률이 아닙니다 · that 4-byte field is not a refractive index.

## 가린 것 · What was redacted

| 원본 · Original | 공개본 · Published |
|---|---|
| 기기 BLE 주소 · device BLE addresses | `<MAC-A>` · `<MAC-B>` · `<MAC-C>` · `<MAC-X>` |
| 광고 이름 뒤 6자리 · trailing 6 digits of the name | `NNNNNN-A` 등 · etc. |
| SN 응답의 ASCII 5 B 와 체크섬 · serial-number ASCII bytes and checksum | `xx` (해석 줄은 `*****` · decode lines show `*****`) |
| 연결 끊기 때 트레이스백(로컬 경로 포함) · disconnect traceback (local paths) | 한 줄 안내로 대체 · replaced with a one-line note |

그 밖의 바이트·시각·신호 세기(rssi)는 바꾸지 않았습니다. · All other bytes, times and signal strengths are unchanged.
