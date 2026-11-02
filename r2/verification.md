# 실측 확인 기록 · Verification record

[← R2 Extract](README.md) · [English](README.en.md) · [프로토콜 · Protocol](protocol.md)

R2 Extract 3대로 2026-11-01~02 에 확인한 내용입니다. 판정의 근거는 [캡처 로그](captures/README.md)의 원시 바이트입니다.<br>
What we checked with three R2 Extract units on 2026-11-01 – 02. The raw bytes in the [capture logs](captures/README.md) are the evidence.

## 1. 시험 환경 · Setup

| | 기기 A · Unit A | 기기 B · Unit B | 기기 C · Unit C |
|---|---|---|---|
| 모델 · 펌웨어 · Model / FW | `DFT-R102` · `V230` | 같음 · same | 같음 · same |
| 설정 · Settings | ℃ · 자동 측정 끔 · 밝기 100 · 측정 횟수 1 · ℃, auto test off, brightness 100, Number of tests 1 | 같음 · same | 같음, 단 **측정 횟수 3** · same but **Number of tests = 3** |
| 시료 · Sample | 모름 — 멀리 있던 기기라 본체 화면을 보지 못함 · unknown — a unit far away; its screen was never seen | 물(빈 프리즘 1회 포함) · water (plus one empty-prism test) | 커피, 증류수 · coffee, distilled water |
| 로그 · Logs | 1 | 2 · 3 · 4 | 5 · 6 · 7 · 8 · 9 |

- 호스트 · Host: Linux (BlueZ) + Python bleak. 기기 이름 번호·주소·SN 은 공개본에서 가렸습니다. · Unit name numbers, addresses and serials are redacted.
- **기기 설정을 바꾸는 명령은 보내지 않았습니다** — 예외는 기기 C 의 영점 교정 2회(11-01 로그 8 · 11-02 구현 시험)와, 구현 시험 중 같은 값 설정 쓰기 1회(밝기 100 → 100)입니다. 평균 측정 명령은 한 번도 보내지 않았고, 평균은 모두 본체 버튼으로 건 것입니다.<br>
  **No setting-changing commands were sent**, except two calibrations on unit C (log 8 on 11-01, and once in the 11-02 integration test) and one same-value setting write (brightness 100 → 100) during the integration test. The average command was never sent; every average was started with the device button.

## 2. 확인한 것 · What was confirmed

| 확인할 것 · Question | 결과 · Result | 근거 · Evidence |
|---|---|---|
| GATT 맵 · GATT map | 서비스 `00FF` 안에 `AA01`·`FF01`(둘 다 read·write·notify). 응답은 `AA01` 로만 · `00FF` holds `AA01` and `FF01`; responses only on `AA01` | 로그 1–9 |
| 쓰기 방식 · Write type | write-without-response 없음 → 응답 있는 쓰기 · not offered → write with response | 로그 1–9 |
| 본딩 · Bonding | 필요 없음 · not required | 로그 1–9 |
| 광고 · Advertising | 이름 `DiFluid R2 NNNNNN`(6자리) · 광고 UUID `00FF` · name with 6 digits, advertised UUID `00FF` | 로그 1 |
| 한 notify 에 여러 프레임 · Several frames per notify | 있음(18 B·24 B) · yes (18 B, 24 B) | 로그 1·2·7·9 |
| 본체 버튼 결과가 오는가 · Do button-started results arrive? | **온다** — 측정 횟수가 1 이면 단일, 3 이면 평균. 단일은 명령으로 건 측정과 프레임 형식이 같다. 평균은 벤더 문서의 평균 명령 예시와 같은 형식이다(평균 명령은 보내지 않아 직접 대조하지 않음) · **yes** — single when Number of tests is 1, average when it is 3. Button singles have the same frame format as command-started singles; button averages match the format of the vendor's average-command example (we never sent the average command, so there is no direct comparison) | 로그 2·3·5·6 · 벤더 예시 📄 |
| 농도 부호 · Concentration sign | 부호 있음 — 물 −1.11~−1.15 % · signed — water −1.11 to −1.15 % | 로그 2·3 |
| 굴절률 크기 · RI size | 4 B | 로그 2·3·5·7–9 |
| 평균 패키지 3 의 4 B 칸 · Avg pkg 3 4-byte field | 굴절률 아님(811100 등) · not an RI (811100 etc.) | 로그 5·6 |
| 연결 때 지난 결과 · Past results on connect | 이미 받은 결과는 다시 보내지 않음(2회). 연결 없이 끝난 측정은 미시험 · already-delivered results not re-sent (twice); tests finished while disconnected not tested | 로그 3·4 |
| 중간에 붙기 · Joining mid-test | 남은 프레임은 받음 — 단일은 「측정 시작」 없이 「측정 끝」부터, 평균은 「평균 시작」 없이 1회차부터 · remaining frames arrive — single from "finished" without "start"; average from round 1 without "average start" | 로그 2 (첫 결과) · 구현 시험 평균 3회(원시 기록 미포함) · log 2 (first result); 3 averages in the integration test (raw log not included) |
| 빈 프리즘 · Empty prism | 일반 분류·코드 3 「시료 없음」, 시작 2.88 s 뒤 · general class, code 3 "No liquid", 2.88 s after start | 로그 2 |
| 하드웨어 오류 · Hardware error | 분류 3·코드 3 이 「측정 시작」과 같은 notify 로 바로 옴 · class 3 code 3 right with "test start" | 로그 1 |
| 영점 교정 · Calibration | 상태 12 → 1 → 패키지 1·2, 농도 0 = 성공 · status 12 → 1 → pkg 1, 2, concentration 0 = success | 로그 7·8·9 |
| 교정 효과 · Calibration effect | 기기 C: 증류수 0.06 % → 교정 → 0.00 %(구현 시험) · unit C: distilled water 0.06 % → calibrate → 0.00 % (integration test) | 구현 시험(원시 기록 미포함) · integration test (raw log not included) |
| 설정 쓰기 응답 · Set response | 같은 값 쓰기에 0.08 s 만에 같은 func·cmd·값 · same func/cmd/value back in 0.08 s for a same-value write | 구현 시험(원시 기록 미포함) · integration test (raw log not included) |
| 연결 유지 · Link stability | 150 s 연결 내내 끊김 없음 · no drop over a 150 s connection | 로그 6 |

## 3. 타이밍 · Timing

| 구간 · Interval | 실측(캡처 로그 1–9, 11-01) · Measured (capture logs 1–9, 11-01) |
|---|---|
| 정보·설정 질의 → 응답 · Info/setting query → response | 0.06 – 0.78 s |
| 단일 측정 명령 → 「측정 시작」 · Single command → "test start" | 0.11 – 0.26 s |
| 「측정 시작」 → 「측정 끝」 · "start" → "finished" (단일 · single) | 2.60 – 3.15 s |
| 「측정 끝」 → 패키지 2 · "finished" → package 2 | 2 – 113 ms |
| 「측정 시작」 → 「시료 없음」 · "start" → "No liquid" | 2.88 s |
| 평균 3회 전체 · Whole 3-round average | 12.2 – 15.3 s |
| 평균 시작(상태 4) → 1회차 · Average start (status 4) → round 1 | 3.15 – 3.64 s |
| 회차 → 다음 회차 · Round → next round | 3.41 – 3.45 s (한 번 · once 6.07 s) |
| 마지막 회차 → 상태 6 · Last round → status 6 | 약 · about 2.2 s |
| 교정 명령 → 상태 12 · Calibrate → status 12 | 0.15 s |
| 상태 12 → 상태 1 · status 12 → status 1 | 3.15 s(로그 8) · 구현 시험(11-02) 약 2.6 s · 3.15 s (log 8); about 2.6 s in the 11-02 integration test |
| 생존 신호(상태 10) · Keep-alive (status 10) | 한 번도 오지 않음 · never seen |

11-02 구현 시험(같은 기기 C, 서비스 이벤트 시각 — 원시 기록 미포함)에서는 더 짧은 값도 보았습니다: 단일 「측정 시작」→「측정 끝」 2.40–2.63 s(8회) · 평균 3회 전체 10.6–14.1 s(8회) · 평균 시작 → 1회차 2.70–3.23 s · 회차 → 다음 회차 2.85–5.32 s · 마지막 회차 → 상태 6 2.06–2.17 s.<br>
In the 11-02 integration test (same unit C; service event times, raw log not included) we also saw shorter values: single "start" → "finished" 2.40–2.63 s (8 tests), whole 3-round average 10.6–14.1 s (8), average start → round 1 2.70–3.23 s, round → next round 2.85–5.32 s, last round → status 6 2.06–2.17 s.

결과를 기다리는 상한은 **마지막 프레임 뒤 10 s** 를 권합니다(평균 회차 간격 최대 6.07 s 관측).<br>
We suggest a result timeout of **10 s after the last frame** (longest observed round gap: 6.07 s).

## 4. 미확인 · Not yet verified

| 항목 · Item | 현재 아는 것 · What we know |
|---|---|
| 자동 꺼짐 · Auto power-off | 공개 BLE 명령 없음. 시간은 재지 않음 — 마지막 측정 약 2분 40초 뒤에도 광고·연결됨 · no public command; time not measured — still advertising and connectable ~2 min 40 s after the last test |
| 연결 중 자동 꺼짐 · Power-off while connected | 미확인 · unknown |
| 자동 측정 켬 · Auto test on | 결과가 BLE 로 오는지 미확인 · whether results arrive is unknown |
| 평균 측정 명령 · Average command | 보내지 않음. 같은 N 을 보내면 「측정 횟수」가 그대로인지 미확인 · never sent; whether sending the same N keeps "Number of tests" is unknown |
| 설정 쓰기 · Set setting | 다른 값으로 바꾸기·전원 재인가 뒤 유지·범위 밖 값(밝기 20, 횟수 11 등) 미확인 · changing values, persistence, out-of-range values (brightness 20, tests 11 …) unknown |
| 오프라인 측정 전달 · Tests finished while disconnected | 연결 없이 끝난 측정이 나중에 연결할 때 오는지 미확인 · whether they arrive on the next connect is unknown |
| 다른 central · Another central | 연결 중 다른 central(폰 앱 등)이 붙을 수 없는지 직접 시험하지 않음 · not tested directly |
| 교정 실패 · Calibration failure | 실패 응답 형태 미확인 · failure response unknown |
| 크게 어긋난 영점 · Large zero offset | 기기 B 는 물을 −1.1 % 로 읽었으나 교정 시험은 못 함 · unit B read water as −1.1 %, but was not calibrated |
| 하드웨어 오류 3·4 · Hardware errors 3, 4 | 받았지만 뜻 모름 · received; meaning unknown |
| 측정 오류·범위 초과·알 수 없는 오류 · Test error, beyond range, unknown error | 보지 못함 · not seen |
| 루프 측정(상태 7–9)·생존 신호(10) · Loop test, keep-alive | 보지 못함 · not seen |
| 한 프레임이 notify 여러 개로 쪼개짐 · One frame across notifications | 보지 못함 · not seen |
| 1회차 뒤에 붙기 · Joining after round 1 | 평균 중간 회차부터 받는 경우는 보지 못함 · not observed |
| `FF01` 채널 · `FF01` channel | 아무것도 오지 않음. 용도(벤더: 암호화·OTA)는 시험하지 않음 · nothing arrived; vendor says encrypted/OTA, not tested |
| 펌웨어 비교 규칙 · Firmware comparison | `V230` 만 시험. 버전 문자열 형식 규칙 미확인 · only `V230` tested; version string format rule unknown |
