# 확인 기록 · Verification record

[← Omix Plus](README.md) · [English](README.en.md) · [프로토콜 · Protocol](protocol.md)

기기 확인은 이승진(180커피로스터스)이 Omix Plus 1대로 했다. DiFluid Korea 는 2026-11-02 에 공개 캡처의 바이트를 다시 계산해 맞춰 보았고, 기기로 재현하지는 않았다.<br>
The device checks were done by 이승진 (180 Coffee Roasters) on one Omix Plus. On 2026-11-02 DiFluid Korea recomputed the bytes of the published captures; nothing was reproduced on a device.

## 1. 시험 환경(기여자) · Contributor's setup

| 항목 · Item | 내용 · Detail |
|---|---|
| 기기 · Device | Omix Plus 1대. 광고 이름으로 판별. 모델 문자열·펌웨어 버전 없음 · one unit, identified by its advertised name; no model string or firmware version |
| 호스트 · Host | Windows, WinRT BLE. OS 빌드는 기록 없음 · OS build not recorded |
| 소프트웨어 · Software | Python 3.12, bleak 3.0.2, PyWinRT 3.2.1 |
| 기간 · Period | 2026-10-21 ~ 11-02 (KST). 공개 캡처는 10-21 ~ 10-23 · published captures: 10-21 to 10-23 |
| 방식 · Method | 업무용 수신기가 FF02 notify 를 받아 로그로 남김. 명령 송신 없음 · a production receiver logged FF02 notifications; no commands sent |

## 2. 확인한 것 · What was checked

| 항목 · Item | 결과 · Result | 근거 · Basis |
|---|---|---|
| 측정 채널 · Measurement channel | `00E2`/`FF02` notify 구독으로 결과 수신 · results received by subscribing to `00E2`/`FF02` | ✅ |
| 홀빈 결과 · Whole-bean result | 색도 53.4, 수분 1.2 %, 밀도 387.3 · color 53.4, moisture 1.2 %, density 387.3 | ✅ 기여자의 이전 확인 기록(본체 화면 값)으로 만든 검증과 일치. 화면 사진 없음 · matches a check built from the contributor's earlier record of the screen values; no photo |
| 주변 온습도 · Ambient | 24.7 °C, 31 %RH | ✅ 기여자의 본체 화면 메모와 일치. 사진 없음 · matches the contributor's note of the device screen; no photo |
| 분쇄 모드 · Ground mode | 모드 값 1281, 색도만 유효 · mode 1281, only color valid | ✅ 1회 · once |
| 값 없음 · No value | 수분 음수, 밀도 0 · negative moisture, zero density | ✅ 1회. 기기의 공식 오류 표시인지는 모름 · once; whether this is an official error indication is unknown |
| MTU 23 | 세 응답 모두 20 B 로 잘림, 이어지는 notify 없음 · all three responses cut to 20 B, no continuation | ✅ 1회 · once |
| 길이·체크섬 · Length, checksum | 완전한 프레임 12개 모두 len + 6, `& 0xFF` 합 일치 · all 12 complete frames match | 재계산 · recomputed |
| 바이트 순서 · Byte order | 리틀 엔디언으로만 말이 되는 값이 나옴 · only little-endian gives sensible values | 재계산 · recomputed |
| 측정 식별자 · Measurement ID | data0–7 이 PC 수신 시각 직전의 Unix 시각(초) · data0–7 is a Unix time (s) just before the PC receive time | 재계산 · recomputed |
| 색도 응답 끝 · End of the color response | 31 B·8 B 두 구간의 합이 각각 100(4묶음) · two runs of 31 B and 8 B each sum to 100 (4 sets) | 재계산 · recomputed |

## 3. 캡처 해석 값 · Decoded capture values

[캡처 로그](captures/README.md)의 바이트를 [프로토콜](protocol.md) 배치로 읽은 값이다. 괄호 안은 float 원값.<br>
Values read from the [captures](captures/README.md) with the [protocol](protocol.md) layout. Raw float values in parentheses.

| 묶음 · Set | 측정 식별자 · ID | 모드 · Mode | 색도 · Color | 수분 · Moisture | 밀도 · Density | 온도 · Temp. | 습도 · RH |
|---|---|---|---|---|---|---|---|
| whole-normal | 1792712292 : 803 | 홀빈 · whole | 53.4 (53.402) | 1.2 % (1.244) | 387.3 | 21.9 °C (21.85) | 33 % |
| environment-reference | 1792718496 : 813 | 홀빈 · whole | 66.6 (66.637) | 1.8 % (1.832) | 463.0 | **24.7 °C** (24.72) | **31 %** |
| ground | 1792557056 : 718 | 분쇄 · ground | 56.3 (56.265) | 없음 · none (−1.213) | 없음 · none (0) | 23.2 °C (23.19) | 31 % |
| not-available | 1792538686 : 686 | 홀빈 · whole | 6.0 (6.003) | 없음 · none (−1.040) | 없음 · none (0) | 21.8 °C (21.76) | 45 % |

굵은 값은 기여자 기록상 본체 화면과 맞춘 값이다. DiFluid Korea 는 화면을 보지 못했고 캡처로는 바이트 해석만 확인했다. 밀도는 수치만 재현됐고 단위는 미확인이다. not-available 의 색도 6.0 이 실제 시료의 값인지는 기록이 없다.<br>
Bold values were matched against the device screen according to the contributor's records. DiFluid Korea did not see the screen; the captures only confirm the byte decoding. The density figure reproduces, but its unit is unconfirmed. There is no record of whether the 6.0 color in not-available came from a real sample.

## 4. 타이밍 · Timing

PC 수신 시각 기준(4묶음) · PC receive times (4 sets).

| 구간 · Interval | 실측 · Measured |
|---|---|
| 식별자 시각 → `03/03` 수신 · ID time → `03/03` received | 2.5 – 6.7 s |
| `03/03` → `03/05` | 1.14 – 1.21 s |
| `03/05` → `03/06` | 0 – 55 ms |

식별자 시각은 초 단위라 첫 구간에는 1 s 의 오차가 있다. 기기 시계가 PC 와 얼마나 맞는지는 모른다.<br>
The ID time has 1-second resolution, so the first interval carries up to 1 s of error. How closely the device clock tracks the PC is unknown.

## 5. 미확인 · Not yet verified

| 항목 · Item | 현재 아는 것 · What is known |
|---|---|
| 모델 문자열·펌웨어 · Model string, firmware | 탐색 기록에 표준 `0x180A` 없음. 제조사 전용 조회(DiFluid func 0 등)는 보낸 적 없음. 다른 장치·펌웨어 미확인 · no standard `0x180A` in the discovery record; maker-specific queries (DiFluid func 0 etc.) never sent; other units and firmware unknown |
| 시험 대수 · Units tested | 1대. 초기화한 기기, 다른 펌웨어, 여러 대 동시 수신은 시험 안 함 · one; no reset unit, other firmware or several units at once |
| 페어링 · Pairing | 새 PC 에서 페어링 없이 되는지 모름 · unknown whether a fresh PC works without pairing |
| 쓰기·명령 · Writes, commands | 쓰기 방식(응답 유무), 측정 시작·중단, 설정, 교정, OTA 모두 모름 · write type, start/stop, settings, calibration, OTA all unknown |
| 오류 · Errors | 오류 코드 표, ACK·재전송 규칙 모름 · no error code table, no ACK or retransmission rules |
| 단위·표준 · Units, standards | 밀도 단위, 색도 표준(Common·SCA)·보정과의 관계 · density unit, color standard and calibration |
| 시료 모드 · Sample modes | 홀빈·분쇄 외의 값(예: 생두) 모름 · values other than whole and ground (e.g. green beans) unknown |
| 수분활성도·스크린 사이즈 · Water activity, screen size | 제품은 측정하지만 이 자료에서 해당 칸을 찾지 못함 · the product measures them, but no field was identified here |
| 미해석 칸 · Undecoded fields | [프로토콜 §3.2–3.5](protocol.md#3-결과-응답--result-responses)의 ❓ 칸과 `03/02` 응답 · the ❓ fields and the `03/02` response |
| 식별자 · ID | data0–7 이 정확히 무슨 시각인지, 기기 시계를 무엇이 맞추는지 · what moment data0–7 marks and what sets the device clock |
| 다른 OS · Other OSes | macOS·Linux·Android 수신은 이 자료에 없음 · no macOS, Linux or Android receive data here |
