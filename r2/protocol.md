# R2 Extract BLE 프로토콜 · R2 Extract BLE protocol

[← R2 Extract](README.md) · [English](README.en.md)

DiFluid 공개 문서 [`protocolR2.md`](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/protocolR2.md)(v1.0.0, 2023-03-18)·[`difluid-protocol.md`](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/difluid-protocol.md)·[README](https://github.com/DiFluid/difluid-sdk-demo/blob/master/README.md)를 실제 바이트로 확인한 정리입니다. 문서와 실물이 다르면 **실물을 따르고** 그 자리에 표시했습니다.<br>
A summary of DiFluid's public documents — [`protocolR2.md`](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/protocolR2.md) (v1.0.0, 2023-03-18), [`difluid-protocol.md`](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/difluid-protocol.md) and the [README](https://github.com/DiFluid/difluid-sdk-demo/blob/master/README.md) — checked against real bytes. Where the document and the device disagree, **we follow the device** and mark the spot.

✅ 실측 확인 · measured　📄 벤더 문서에만 있음 · vendor document only　❓ 미확인 · unknown

모든 바이트는 16진수, 여러 바이트 값은 **빅 엔디언**입니다. · All bytes are hex; multi-byte values are **big-endian**. ✅

---

## 1. 연결 · Connecting

### 1.1 찾기 · Discovery

| 항목 · Item | 내용 · Detail | |
|---|---|---|
| 광고 이름 · Name | `DiFluid R2 NNNNNN` — 뒤 6자리는 기기마다 다릅니다 · the last 6 digits differ per unit | ✅ |
| 광고 서비스 UUID · Advertised service | `0x00FF` | ✅ |
| 판별 · Identifying | 이름 앞부분 `DiFluid R2`(대소문자 무시)로 고르는 것을 권합니다. `0x00FF` 는 다른 기기에서도 흔히 쓰는 값이라 그것만으로 고르지 마세요. · Match on the name prefix `DiFluid R2` (case-insensitive). `0x00FF` is a common value on other devices, so do not rely on it alone. | ✅ |
| 연결 중 광고 · Advertising while connected | 연결돼 있는 동안 광고하지 않았습니다(우리 호스트가 붙은 채 스캔 2회 모두 못 찾음 — 로그 미보관). 그래서 다른 central(휴대폰 앱 포함)은 그동안 R2 를 찾거나 붙을 수 없을 것으로 봅니다 — 직접 시험하지는 않았습니다. · It did not advertise while connected (two scans from our host during a connection found nothing; logs not kept). So another central, including the phone app, presumably cannot find or connect to it meanwhile — not tested directly. | ✅ / ❓ |

### 1.2 GATT

| 서비스 · Service | 특성 · Characteristic | 속성 · Properties | 쓰임 · Use |
|---|---|---|---|
| `0x00FF` | `0xAA01` | read · write · notify | **명령을 쓰고 응답을 받는 곳** · write commands here, responses arrive here ✅ |
| `0x00FF` | `0xFF01` | read · write · notify | 벤더 README 의 「암호화 채널」. 구독해도 아무것도 오지 않았습니다. · The vendor README calls it the encrypted channel. Nothing arrived on it while subscribed. ✅ |
| `0x1800` | `0x2A00` · `0x2A01` · `0x2AA6` | read | 표준 Generic Access · standard |
| `0x1801` | `0x2A05` | indicate | 표준 Generic Attribute · standard |

- 전체 UUID · Full UUIDs: `000000ff-0000-1000-8000-00805f9b34fb`, `0000aa01-0000-1000-8000-00805f9b34fb`.
- `0xAA01` 에 **응답 있는 쓰기(write with response)** 로 보냅니다. write-without-response 속성이 없습니다. ✅<br>
  Write to `0xAA01` **with response**; write-without-response is not offered. ✅
- 페어링·본딩이 필요 없습니다. 구독이 바로 성공합니다. ✅<br>
  No pairing or bonding is needed; subscribing succeeds right away. ✅
- 벤더 README 에 따르면 예전에는 DiFluid 서버를 거쳐야 평문 채널이 열렸지만, 지금은 두 채널이 처음부터 켜져 있고 서버 연결은 선택(OTA 용)입니다. 📄 우리 시험에서도 서버 연결 없이 `0xAA01` 로 바로 주고받았습니다. ✅<br>
  Per the vendor README, the cleartext channel once required a DiFluid server handshake; now both channels are on by default and the server step is optional (for OTA). 📄 In our tests `0xAA01` worked directly without any server step. ✅

### 1.3 연결 때 · On connect

- **이미 BLE 로 받은 결과는 다시 연결해도 다시 보내지 않았습니다**(측정 1~3분 뒤 재연결, 2회). ✅ 연결이 없는 동안 끝난 측정이 나중에 연결할 때 오는지는 확인하지 않았습니다. ❓<br>
  **Results already delivered over BLE were not re-sent on reconnect** (reconnected 1–3 min after a test, twice). ✅ Whether a test that finished while nothing was connected is delivered on the next connect was not checked. ❓
- 측정 도중에 붙으면 **남은 프레임은 받습니다** — 단일은 「측정 시작」 없이 「측정 끝」부터(1회), 평균은 「평균 시작」 없이 1회차부터(구현 시험 3회) 왔습니다. ✅ 1회차까지 놓치고 중간 회차부터 받는 경우는 아직 보지 못했습니다. ❓<br>
  If you connect mid-test, you **still get the remaining frames** — a single test from "test finished" without "test start" (once), an average from round 1 without "average start" (three times in the integration test). ✅ Joining after round 1 has not been observed. ❓

---

## 2. 프레임 · Frame

```
DF DF | func | cmd | len | data0 … data(len-1) | sum
```

| 칸 · Field | 크기 · Size | 내용 · Meaning |
|---|---|---|
| 머리 · Header | 2 B | `DF DF` |
| func | 1 B | 0 기기 정보 · device info / 1 설정 · settings / 3 동작(측정) · action (test) |
| cmd | 1 B | func 안의 명령 · command within func |
| len | 1 B | 데이터 길이 · data length (벤더 최대 20 · vendor max 20) |
| data | len B | |
| sum | 1 B | 머리부터 마지막 데이터까지 합의 하위 8비트 · low 8 bits of the sum from header through the last data byte |

예 · Example: `DF DF 03 00 00 C1` → `0xDF + 0xDF + 0x03 + 0x00 + 0x00 = 0x1C1` → `C1`.

- **한 notify 에 프레임이 둘 이상 붙어 올 수 있습니다.** 18 B notify 에 「측정 시작」+「오류」, 24 B notify 에 SN 조각 2개가 함께 왔습니다. 프레임 분리기가 필요합니다. ✅<br>
  **One notification can carry more than one frame.** We saw "test start" + "error" in one 18-byte notification and two SN chunks in one 24-byte notification. You need a frame splitter. ✅
- 한 프레임이 notify 여러 개로 쪼개져 오는 것은 보지 못했습니다. 그래도 대비해 두기를 권합니다. ❓<br>
  We never saw one frame split across notifications, but we recommend handling it. ❓

---

## 3. 명령 · Commands

| 용도 · Purpose | 보내는 바이트 · Bytes to send | 응답 · Response | 부작용 · Side effect | |
|---|---|---|---|---|
| SN | `DF DF 00 00 00 BE` | 조각 3개 · 3 chunks (§3.1) | 없음 · none | ✅ |
| 모델 · Model | `DF DF 00 01 00 BF` | ASCII — 실측 · seen `DFT-R102` | 없음 · none | ✅ |
| 펌웨어 · Firmware | `DF DF 00 02 00 C0` | ASCII — 실측 · seen `V230` | 없음 · none | ✅ |
| 설정 읽기 · Get setting | `DF DF 01 kk 00 ss` | `DF DF 01 kk 01 vv ss` | 없음 · none | ✅ |
| 설정 쓰기 · Set setting | `DF DF 01 kk 01 vv ss` | 같은 바이트 · same bytes 📄 | **그 설정이 바뀝니다** · **changes the setting** | 일부 · partial |
| 단일 측정 · Single test | `DF DF 03 00 00 C1` | §4.1 | 측정 1회 · one test | ✅ |
| 평균 측정 · Average test | `DF DF 03 01 01 NN ss` (NN = 1~10, ss = `C3 + NN`) | §4.2 | **「측정 횟수」가 NN 으로 바뀐다(벤더)** · **sets "Number of tests" to NN (vendor)** | 📄 |
| 영점 교정 · Calibrate | `DF DF 03 02 00 C3` | §4.3 | **영점이 바뀝니다** · **changes the zero** | ✅ |

### 3.1 기기 정보 · Device info

- SN 은 조각 3개로 옵니다: `DF DF 00 00 06 <번호 0~2> <ASCII 5 B> ss`. 이어 붙이면 15자입니다. ✅<br>
  The serial number arrives as 3 chunks: `DF DF 00 00 06 <index 0–2> <5 ASCII bytes> ss`. Joined, it is 15 characters. ✅
- 모델: `DF DF 00 01 08 44 46 54 2D 52 31 30 32 B7` → `DFT-R102`. ✅<br>
  Model: `DF DF 00 01 08 44 46 54 2D 52 31 30 32 B7` → `DFT-R102`. ✅
- 펌웨어: `DF DF 00 02 04 56 32 33 30 AF` → `V230` ✅. 벤더 README 의 최소 `V212`(protocolR2.md 「2.1.2」)와 같은 꼴로 보면 2.3.0 이지만, 벤더 문서에 형식 규칙이 없고 예시 `T003` 은 이 꼴이 아니라 비교 규칙은 미확인입니다. ❓<br>
  Firmware: `DF DF 00 02 04 56 32 33 30 AF` → `V230` ✅. Read like the README's minimum `V212` ("2.1.2" in protocolR2.md) it would be 2.3.0, but the vendor gives no format rule and its example `T003` does not fit, so a comparison rule is unverified. ❓

### 3.2 설정 · Settings

| kk | 설정 · Setting | 값 · Values | 읽기 · Get | 실측 값 · Seen |
|---|---|---|---|---|
| `00` | 온도 단위 · Temperature unit | `00` ℃ / `01` ℉ | `DF DF 01 00 00 BF` | `00` |
| `01` | 자동 측정 · Auto test | `00` 끔 off / `01` 켬 on | `DF DF 01 01 00 C0` | `00` |
| `02` | 화면 밝기 · Screen brightness | 30~100 (%) | `DF DF 01 02 00 C1` | `64` (100) |
| `03` | 측정 횟수 · Number of tests | 1~10 | `DF DF 01 03 00 C2` | `01` 또는 · or `03` |

- 설정 쓰기의 체크섬 · Set checksum: `ss = (0xC0 + kk + vv) & 0xFF`. 예 · e.g. 밝기 80 % · brightness 80 %: `DF DF 01 02 01 50 12`.
- 「측정 횟수」는 벤더 문서상 **본체에서 건 측정(offline test)에만** 적용됩니다. 실측: 본체 버튼은 이 값이 1 이면 단일, 3 이면 평균 3회를 겁니다. ✅<br>
  "Number of tests" applies **only to tests started on the device** per the vendor. Measured: the button runs a single test when it is 1 and a 3-round average when it is 3. ✅
- **설정 쓰기는 같은 값으로 한 번만 확인했습니다**: 밝기 100 → 100 을 보내자 0.08 s 만에 같은 func·cmd·값(100)이 돌아왔습니다. 다른 값으로 바꾸기·전원을 껐다 켠 뒤 유지·범위 밖 값은 확인하지 않았습니다. ❓<br>
  **Set was checked only with the same value**: writing brightness 100 → 100 returned the same func, cmd and value (100) in 0.08 s. Changing to a different value, persistence across power cycles and out-of-range values were not checked. ❓
- **자동 꺼짐(auto power-off) 설정은 공개 프로토콜에 명령이 없습니다.** 비공개 명령이 있는지는 모릅니다. ❓<br>
  **There is no auto power-off command in the public protocol.** Whether a private one exists is unknown. ❓

---

## 4. 측정 응답 · Measurement responses

측정 응답은 `func 03` 이고 `cmd` 는 보낸 명령과 같습니다: `00` 단일 · `01` 평균 · `02` 교정. `data0` 은 **패키지 번호**입니다.<br>
Measurement responses use `func 03`, with `cmd` matching the request: `00` single, `01` average, `02` calibration. `data0` is the **package number**.

### 4.0 패키지 · Packages

| 패키지 · Pkg | 내용 · Content | 데이터 배치 · Data layout (data0 = 패키지 번호 · pkg no.) | len |
|---|---|---|---|
| 0 | 상태 · Status | data1 = 상태 코드 · status code, data2 = `00` (예약 · reserved) | 3 |
| 1 | 온도 · Temperature | data1–2 프리즘 온도 · prism temp ×10, data3–4 시료 온도 · sample temp ×10, data5 단위 · unit (0 ℃ / 1 ℉) | 6 |
| 2 | 결과 · Result | data1–2 농도(TDS %) · concentration ×100 **부호 있음 · signed**, data3–6 굴절률 · refractive index ×100000 (4 B) | 7 |
| 3 | 평균 · Average (평균만 · average only) | data1–2 지금까지의 평균 농도 · running average concentration ×100 (signed), data3–6 **정체 불명 · unknown** (§6 참고 · see §6) | 7 |
| 4 | 평균 정보 · Average info (평균만 · average only) | data1–2 평균 프리즘 · avg prism ×10, data3–4 평균 시료 · avg sample ×10, data5 현재 회차 · current round, data6 전체 회차 · total rounds | 7 |

### 4.0.1 상태 코드 · Status codes (패키지 0 · package 0, data1)

| 코드 · Code | 뜻 · Meaning | |
|---|---|---|
| 0 | 측정 끝 · Test finished | ✅ |
| 1 | 교정 끝 · Calibration finished | ✅ |
| 2, 3 | 예약 · Reserved | 📄 |
| 4 | 평균 시작 · Average test start | ✅ |
| 5 | 평균 진행(회차마다) · Average test ongoing (each round) | ✅ |
| 6 | 평균 끝 · Average test finished | ✅ |
| 7, 8, 9 | 루프 측정 시작·진행·끝 — 벤더: 온도가 안정되지 않았을 때 · Loop test start/ongoing/finished — vendor: when temperature is not stable | 📄 보지 못함 · not seen |
| 10 | 평균 진행 생존 신호(측정이 길 때) · Average keep-alive (long tests) | 📄 보지 못함 · not seen |
| 11 | 측정 시작 · Test start | ✅ |
| 12 | 교정 시작 · Calibration start | ✅ |

### 4.1 단일 측정 · Single test ✅

순서 · Sequence: 상태 11 → (약 2.4–3.2 s) → 상태 0 → 패키지 1 → 패키지 2.<br>
Status 11 → (about 2.4–3.2 s) → status 0 → package 1 → package 2.

실측 예(커피) · Captured example (coffee):

```
→ DF DF 03 00 00 C1                     단일 측정 · single test
← DF DF 03 00 03 00 0B 00 CF            상태 11 측정 시작 · test start
← DF DF 03 00 03 00 00 00 C4            상태 0 측정 끝 · test finished
← DF DF 03 00 06 01 00 BB 00 B3 00 36   프리즘 · prism 18.7 ℃ · 시료 · sample 17.9 ℃ · 단위 · unit ℃
← DF DF 03 00 07 02 03 2B 00 02 0E 55 5D  TDS 8.11 % · RI 1.34741
```

- 농도 `03 2B` = 811 → **8.11 %**, 굴절률 `00 02 0E 55` = 134741 → **1.34741**.<br>
  Concentration `03 2B` = 811 → **8.11 %**; RI `00 02 0E 55` = 134741 → **1.34741**.
- **농도는 부호 있는 16비트입니다.** 물에서 음수가 실제로 옵니다: `DF DF 03 00 07 02 FF 91 00 02 07 EF 52` → `FF 91` = −111 → **−1.11 %**. 부호 없이 읽으면 654.25 % 같은 엉뚱한 값이 됩니다. ✅<br>
  **Concentration is signed 16-bit.** Water really does produce negatives: `FF 91` = −111 → **−1.11 %**. Reading it unsigned gives nonsense such as 654.25 %. ✅
- 굴절률은 **4 B** 입니다(벤더 표는 2 B 로 적었지만 예시와 실물은 4 B). ✅<br>
  The refractive index is **4 bytes** (the vendor table says 2, but its example and the device use 4). ✅
- 「측정 끝」에서 패키지 2 까지 2~113 ms. 프레임마다 notify 하나씩 왔습니다. ✅<br>
  From "test finished" to package 2: 2–113 ms; each frame arrived in its own notification. ✅

### 4.2 평균 측정 · Average test ✅ (본체 버튼으로 건 것 · started from the device button)

순서 · Sequence:

1. 상태 4(평균 시작) · status 4 (average start)
2. **회차마다** 다섯 프레임이 113 ms 안에 · **each round**, five frames within 113 ms:
   상태 5 → 패키지 1(이번 회차 온도) → 패키지 2(**이번 회차** 농도·굴절률) → 패키지 3(**지금까지 평균**) → 패키지 4(평균 온도·현재/전체 회차)<br>
   status 5 → pkg 1 (this round's temps) → pkg 2 (**this round's** concentration, RI) → pkg 3 (**running average**) → pkg 4 (average temps, current/total round)
3. 마지막 회차 약 2.2 s 뒤 상태 6(평균 끝) **하나만** · about 2.2 s after the last round, status 6 (average finished) **alone**

**최종값 = 마지막 회차(현재 = 전체)의 패키지 3 평균 농도입니다.** 상태 6 에는 값이 없습니다.<br>
**The final value is the package-3 average from the last round (current = total).** Status 6 carries no value.

실측 예(커피, 3회) · Captured example (coffee, 3 rounds):

| 시각 · t (s) | 프레임 · Frame | 뜻 · Meaning |
|---|---|---|
| 59.739 | `DF DF 03 01 03 00 04 00 C9` | 평균 시작 · start |
| 63.376 | `DF DF 03 01 03 00 05 00 CA` | 1회차 · round 1 |
| 63.376 | `DF DF 03 01 06 01 00 AF 00 A9 00 21` | 17.5 / 16.9 ℃ |
| 63.413 | `DF DF 03 01 07 02 03 2E 00 02 0E 59 65` | 이번 · this 8.14 %, RI 1.34745 |
| 63.451 | `DF DF 03 01 07 03 03 2E 00 0C 6C 14 89` | 평균 · avg 8.14 % |
| 63.451 | `DF DF 03 01 07 04 00 AF 00 A9 01 03 29` | 1 / 3 |
| 69.451 | … `07 02 03 2F …` · `07 03 03 2F …` · `07 04 … 02 03 …` | 2회차 · round 2: 8.15 → 평균 · avg 8.15 |
| 72.864 | … `07 02 03 2F …` · `07 03 03 2F …` · `07 04 … 03 03 …` | 3회차 · round 3: 8.15 → 평균 · avg **8.15** |
| 75.076 | `DF DF 03 01 03 00 06 00 CB` | 평균 끝 · finished → 결과 · result **8.15 %** |

- 평균은 회차 값의 산술 평균을 소수 둘째 자리로 반올림한 값과 맞았습니다(8.14·8.15·8.15 → 8.15). ✅<br>
  The average matched the arithmetic mean of the round values rounded to 2 decimals. ✅
- 회차마다 「이번 값」과 「지금까지 평균」이 오므로 **재는 동안 값을 실시간으로 보여 줄 수 있습니다.** 단일 측정에는 중간값이 없습니다. ✅<br>
  Because each round carries "this round" and "average so far", **you can show the value live while measuring.** A single test has no intermediate value. ✅
- 평균 결과에는 굴절률이 없습니다(패키지 3 의 4 B 칸은 굴절률이 아닙니다 — §6). ✅<br>
  An average result has no refractive index (the 4-byte field in package 3 is not an RI — §6). ✅
- **평균 명령(`03 01`)은 보내 보지 않았습니다.** 위 순서는 본체 버튼으로 건 평균입니다. 명령으로 건 평균이 같은 바이트로 오는지, 「측정 횟수」 설정이 바뀌는지는 미확인입니다. ❓<br>
  **We never sent the average command (`03 01`).** The sequence above is a button-started average. Whether a command-started average looks the same, and whether it changes "Number of tests", is unverified. ❓

### 4.3 영점 교정 · Calibration ✅

순서 · Sequence: 상태 12(교정 시작, +0.15 s) → (약 2.6–3.2 s) → 상태 1(교정 끝) → 패키지 1 → 패키지 2. **패키지 2 의 농도가 0 이면 성공**입니다.<br>
Status 12 (calibration start, +0.15 s) → (about 2.6–3.2 s) → status 1 (calibration finished) → pkg 1 → pkg 2. **Concentration 0 in package 2 means success.**

```
→ DF DF 03 02 00 C3                       영점 교정 · calibrate
← DF DF 03 02 03 00 0C 00 D2              상태 12 · calibration start
← DF DF 03 02 03 00 01 00 C7              상태 1 · calibration finished
← DF DF 03 02 06 01 00 DB 00 D7 00 7C     21.9 / 21.5 ℃
← DF DF 03 02 07 02 00 00 00 02 08 B3 89  0.00 % · RI 1.33299
```

- **증류수를 올린 상태에서만** 하세요. 영점이 잘못 잡히면 이후 모든 값이 틀어집니다.<br>
  Do this **only with distilled water on the prism.** A wrong zero shifts every later reading.
- 교정 실패 응답(일반 오류 코드 2)은 보지 못했습니다. ❓ · We never saw the failure response (general error code 2). ❓

### 4.4 본체 버튼 측정 · Tests started on the device ✅

- 연결된 상태에서 R2 본체 버튼으로 잰 결과도 **같은 바이트로** 옵니다. 「측정 횟수」 설정대로 단일(cmd 00) 또는 평균(cmd 01) 형식입니다. ✅<br>
  Results of tests started with the R2's own button also arrive, **byte-for-byte in the same format** — single (cmd 00) or average (cmd 01) depending on "Number of tests". ✅
- 「자동 측정」을 켰을 때도 결과가 오는지는 확인하지 않았습니다(시험 기기는 모두 끔). ❓<br>
  Whether results also arrive with "Auto test" on was not checked (all test units had it off). ❓

---

## 5. 오류 · Errors

오류는 `func 03 · cmd FE`, **len 3** 입니다: data0 = 패키지 번호(0), **data1 = 분류**, **data2 = 코드**. ✅<br>
Errors are `func 03 · cmd FE`, **len 3**: data0 = package number (0), **data1 = class**, **data2 = code**. ✅

> 벤더 표는 「데이터 길이 0, Data0 = 분류, Data1 = 코드」로 적었지만 실물은 한 칸씩 밀려 있습니다.<br>
> The vendor table says "length 0, Data0 = class, Data1 = code"; the real frame is shifted by one byte.

| 분류 · Class | 코드 · Code | 뜻 · Meaning | 실측 프레임 · Seen frame | |
|---|---|---|---|---|
| 2 일반 · General | 1 | 측정 오류 · Test error | — | 📄 |
| 2 | 2 | 교정 실패 · Calibration failed | — | 📄 |
| 2 | 3 | **시료 없음 · No liquid** | `DF DF 03 FE 03 00 02 03 C7` — 측정 시작 2.88 s 뒤 · 2.88 s after start | ✅ |
| 2 | 4 | 범위 초과 · Beyond range | — | 📄 |
| 3 하드웨어 · Hardware | n | 벤더: 본체 화면에 뜨는 번호 · vendor: the number shown on the device screen | 3: `DF DF 03 FE 03 00 03 03 C8` — 「측정 시작」과 같은 notify 로 바로 · in the same notification as "test start" | ✅ 받음 · received |
| 3 | 4 | — | 평균 측정 도중 2회 받음(원시 바이트는 남기지 못함) · received twice during average tests (raw bytes not kept) | ✅ 받음 · received |

- **하드웨어 오류 3·4 의 뜻은 모릅니다.** 본체 화면 표시를 확인하지 못했습니다. ❓<br>
  **The meaning of hardware errors 3 and 4 is unknown**; we did not see the device screen at the time. ❓
- `cmd FF` = 알 수 없는 오류, 데이터 `FF FF FF FF`(벤더). 보지 못했습니다. 📄<br>
  `cmd FF` = unknown error with data `FF FF FF FF` (vendor). Not seen. 📄

---

## 6. 벤더 문서와 다른 점 · Differences from the vendor document

| 벤더 문서 · Vendor document | 실물 · Device |
|---|---|
| 오류 응답: 데이터 길이 0, Data0 = 분류 · Data1 = 코드 · Error: length 0, Data0 = class, Data1 = code | len 3, data0 = 패키지 번호 · package no., data1 = 분류 · class, data2 = 코드 · code ✅ |
| 패키지 2 굴절률 Data3–4 (2 B) · Package 2 RI as 2 bytes | 4 B (data3–6) — 벤더 예시와 같음 · matches the vendor example ✅ |
| 평균 패키지 3 표: Data3–4 = 평균 굴절률 ×100000(2 B) — 예시는 4 B `FF FF E4 44` · Package 3 table: Data3–4 = average RI ×100000 (2 bytes); the example uses 4 bytes `FF FF E4 44` | 4 B 칸(data3–6)은 굴절률이 아닙니다. 평균 8.11·8.12·8.14·8.15 % 에서 811100·812100·814100·815100(벤더 예시 −0.07 % 에서 −7100). 뜻 미확인 — 쓰지 마세요 · The 4-byte field (data3–6) is not an RI: averages of 8.11 / 8.12 / 8.14 / 8.15 % carried 811100 / 812100 / 814100 / 815100 (the vendor example −0.07 % carries −7100). Meaning unknown — do not use ❓ |
| 평균 끝 예시 설명 「0x04 average test finished」 · Average-finish example text says 0x04 | 바이트는 `06` · the byte is `06` (설명 오타 · typo in the description) ✅ |
| 교정 응답 행 「Range: 30 - 100 (%)」 · Calibration row "Range: 30 - 100 (%)" | 밝기 행을 옮긴 오타로 보임 · looks copied from the brightness row |
| 펌웨어 예시 `T003` · Firmware example `T003` | 실물 `V230`, 벤더 README 의 최소 펌웨어 표기는 `V212` · device `V230`; the README writes the minimum as `V212` ✅ |
| `protocolR2.md` 에 UUID 없음 · No UUIDs in `protocolR2.md` | 특성 `AA01`·`FF01` 은 README 에 있음(「서비스」라고 적힘), 서비스 `00FF` 는 실측 · characteristics are in the README (called "services"); service `00FF` measured ✅ |
