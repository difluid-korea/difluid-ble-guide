# 실측 확인 기록 · Verification record

[← Microbalance](README.md) · [English](README.en.md) · [프로토콜 · Protocol](protocol.md)

Microbalance 2대로 2026-07-05 ~ 09-02 에 확인한 내용입니다. 실제 제품에 저울을 통합하면서 Linux(BlueZ) + Python bleak 으로 시험했습니다.<br>
What we checked on two Microbalance scales between 2026-07-05 and 09-02, while integrating the scale into a product, using Linux (BlueZ) + Python bleak.

> [!NOTE]
> R2 와 달리 저울은 원시 캡처 로그를 남기지 않았습니다. 아래 프레임은 실기에서 캡처해 시험 코드에 고정해 둔 값입니다. 기기 식별 정보(주소·SN·이름 번호)는 가렸습니다.<br>
> Unlike the R2, we did not keep raw capture logs for the scale. The frames below were captured on the device and pinned in our tests. Unit identifiers (address, SN, name digits) are redacted.

## 1. 기기 · Units

| | 기기 M · Unit M | 기기 T · Unit T |
|---|---|---|
| 모델 · Model | Microbalance | Microbalance Ti |
| 근거 · How we know | GATT 서비스 `00EE` 실측 · measured GATT service `00EE` | 광고 이름 `Mb Ti NNNNNN` · advertised name |
| 시험 날짜 · Dates | 2026-07-05(프로토콜 해독 · decoding), 2026-07-26(영점 · tare) | 2026-08-30(샘플레이트·배터리·SN · sample rate, battery, SN) |

2026-09-02 의 타이머 시작·정지 시험은 어느 기기였는지 기록이 없습니다(정황상 T). · The 2026-09-02 timer tests did not record which unit was used (probably T).

## 2. 확인한 것 · What was confirmed

| 확인할 것 · Question | 결과 · Result | 기기 · Unit |
|---|---|---|
| 통신 특성 · Characteristic | 명령·응답은 `AA01` 로만. `FF01` 에 평문을 쓰면 `ff`·에코만 · commands and responses only on `AA01`; cleartext on `FF01` returns `ff` or an echo | M |
| 쓰기 방식 · Write type | `AA01` 은 read·write·notify, write-without-response 없음 → 응답 있는 쓰기 · read/write/notify, no write-without-response → write with response | M |
| 페어링·서버 · Pairing, server | 본딩·DiFluid 서버·SDK 키 없이 동작 · works without bonding, DiFluid server or SDK key | M · T |
| 구펌웨어 · Old firmware | 어떤 명령에도 무응답 → DiFluid 앱으로 업데이트 뒤 응답 · no answer to any command → answered after updating via the DiFluid app | M |
| 펌웨어 업데이트와 주소 · Firmware update and address | 업데이트 뒤 BLE 주소가 바뀜 · the BLE address changed after the update | M |
| Ti 광고 이름 · Ti advertised name | `Mb Ti NNNNNN` | T |
| 프레임·체크섬 · Frame, checksum | 실캡처 응답 7개 모두 `& 0xFF` 체크섬·길이 일치 · all 7 captured responses match length and `& 0xFF` checksum | M · T |
| 바이트 순서 · Byte order | 빅 엔디언(무게 `00 00 0F 64` = 394.0 g) · big-endian | M |
| 한 notify 에 여러 프레임 · Several frames per notify | SN 0·1 이 24 B notify 하나로 옴 · SN chunks 0 and 1 in one 24-byte notification | T |
| 센서 데이터 길이 · Sensor data length | len 13(벤더 표의 12 는 오기) · len 13 (the vendor table's 12 is wrong) | M |
| 무게 · Weight | ÷ 10 g, 394.0 → 305.9 → 0.0 g 를 정확히 따라감 · ÷ 10 g; tracked 394.0 → 305.9 → 0.0 g | M |
| 유량 칸 · Flow field | 타이머가 돌지 않을 때 무게가 줄어드는 중에도 0 · 0 while weight was falling and the timer was off | M |
| 기기 시각 · Device tick | 무게 변화와 함께 늘어나는 카운터 · a counter that rose with the weight changes | M |
| 상태·배터리 · Status, battery | data0 = 상태(5 Idle), data1 = 배터리 63 %, data2 = 충전 0. 고친 뒤 우리 앱의 배터리가 정상 값으로 보이는 것을 사용자가 확인(저울 본체 표시와 대조한 기록은 없음) · data0 = status (5 Idle), data1 = battery 63 %, data2 = charging 0; after the fix the user confirmed our app showed a plausible battery level (no record of comparing it with the scale's own display) | T |
| SN | 3조각 × 5자 = 15자. 앞 12자리가 BLE 주소 − 2 · 3 chunks × 5 chars; first 12 chars = BLE address − 2 | M · T |
| 영점 · Tare | `DF DF 03 02 01 01 C5` → 21.4 g 에서 1.58 s 뒤 0.0 g · 0.0 g after 1.58 s from 21.4 g | M |
| 데이터 없는 영점 · Tare without data | `DF DF 03 02 00 C3` 은 쓰기는 성공, 저울은 무시 · write succeeds, scale ignores it | M |
| 타이머 시작 · Timer start | `DF DF 03 02 01 00 C4` → 타이머 칸이 움직임(프레임은 남기지 못함) · the time field moved (frames not kept) | 기록 없음 · not recorded |
| 타이머 정지 · Timer stop | `DF DF 03 01 01 00 C3` → BLE 무게 출력이 멈춤 · BLE weight output froze | 기록 없음 · not recorded |
| 오류 응답 · Error responses | 잘못 만든 명령(데이터 없는 영점)을 오류 응답 없이 무시. 정의되지 않은 func·cmd 는 보내지 않음 · a malformed command (tare without data) was ignored with no error response; undefined func/cmd values were never sent | M |

## 3. 실측 프레임 · Captured frames

| 프레임 · Frame | 뜻 · Meaning | 기기 · Unit |
|---|---|---|
| `DF DF 03 00 0D 00 00 0F 64 00 00 00 00 00 07 57 88 00 27` | 394.0 g · 유량 0 · 타이머 0 · tick 481160 · g | M |
| `DF DF 03 00 0D 00 00 0B F3 00 00 00 00 00 07 5E E0 00 11` | 305.9 g(분동을 치우는 중 · removing the weight) · tick 483040 | M |
| `DF DF 03 00 0D 00 00 00 00 00 00 00 00 00 07 60 E8 00 1D` | 0.0 g · tick 483560 | M |
| `DF DF 03 05 08 05 3F 00 00 00 00 00 00 12` | 상태 Idle · 배터리 63 % · 충전 아님 · Idle, battery 63 %, not charging | T |
| `DF DF 00 00 06 00 xx xx xx xx xx xx` ×3 | SN 조각 0·1·2(값과 체크섬은 가림) · SN chunks (value and checksum redacted) | M · T |

## 4. 타이밍 · Timing

| 항목 · Item | 실측 · Measured | 기기 · Unit |
|---|---|---|
| 「쓰기 후 0.2 s 대기」 폴링 · "write, then sleep 0.2 s" polling | **3.56 Hz**(간격 약 280 ms — 응답 있는 쓰기 왕복 약 80 ms 가 더해짐) · interval ~280 ms (write round trip ~80 ms added) | T |
| 마감 시각 기준 폴링 · Deadline-paced polling | **4.99 Hz**(간격 최소 150 · 중앙 187.8 · p95 225.9 · 최대 226.7 ms) — 응답 있는 쓰기였는지는 기록 없음 · interval min 150, median 187.8, p95 225.9, max 226.7 ms — whether writes were with response was not recorded | T |
| 영점 반영 · Tare to 0.0 g | 1.58 s(폴링 간격 포함) · including the polling gap | M |
| 5 Hz 보다 빠른 폴링 · Faster than 5 Hz | 시험하지 않음 · not tested | — |

## 5. 미확인 · Not yet verified

| 항목 · Item | 현재 아는 것 · What we know |
|---|---|
| Ti 의 GATT · Ti GATT | 서비스가 `00DD` 인지, `AA01` 속성(write-without-response 유무)이 무엇인지 기록 없음 · service UUID and `AA01` properties not recorded |
| 저울 광고 · Scale advertising | 광고에 서비스 UUID 를 싣는지, 광고를 계속하는지 미캡처 · not captured |
| 일반 Microbalance 광고 이름 · Microbalance name | 기록 없음 · not recorded |
| 모델·펌웨어 응답 · Model, firmware responses | 미캡처 — 실제 문자열과 길이 바이트 모름 · not captured |
| 설정(func 1) 전부 · All settings (func 1) | 자동 송신·자동 타이밍·단위 잠금·단위 — 보내지 않음 · never sent |
| 무게 부호 · Weight sign | 음수 무게 프레임 미캡처 · no negative weight captured |
| 유량·타이머 칸 · Flow and time fields | 0 이 아닌 값이 든 프레임은 없음(타이머 칸은 움직이는 것만 봄 — §2), 단위 모름 · no frame with a non-zero value was kept (the time field was only seen moving — §2); units unknown |
| 기기 시각 단위 · Device tick unit | ms 로 보이나 미확정(값이 모두 40 의 배수) · looks like ms, unconfirmed (all values multiples of 40) |
| oz·gering 단위 · oz, gering | 프레임 미캡처, gering 의 뜻 모름 · no frames; "gering" undefined |
| 타이머 정지 상태 · Timer stop state | 프레임이 끊기는지 같은 값이 오는지, DLink 클릭으로 풀리는지, 상태 코드 10·11 로 알 수 있는지 · whether frames stop or repeat, whether a DLink click resumes the stream, whether status 10/11 reveals it |
| 두 번째 샷의 타이머 · Timer on the next shot | 리셋이 없을 때 0 부터 세는지 이어 세는지 · whether it restarts from 0 without a reset |
| Ti 영점 · Ti tare | 영점만 따로 확인한 기록 없음 · no separate record |
| 명령 에코·Device Trigger · Command echo, device events | 미캡처 · not captured |
| 끊김 감지·재연결 시간 · Disconnect detection, reconnect time | 재지 않음 · not measured |
| 프레임이 notify 둘로 쪼개짐 · Frame split across notifications | 보지 못함 · not observed |
| 구펌웨어 무응답 원인 · Why old firmware was silent | README 의 「예전엔 평문 채널이 기본 꺼짐」과 같은 것인지 미확인 · unknown whether it is the README's "cleartext channel off by default" era |
