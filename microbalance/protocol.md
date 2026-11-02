# Microbalance · Ti BLE 프로토콜 · BLE protocol

[← Microbalance](README.md) · [English](README.en.md)

DiFluid 공개 문서 [`protocolMicrobalance.md`](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/protocolMicrobalance.md)(v1.0.0, 2024-12-24)·[`difluid-protocol.md`](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/difluid-protocol.md)·[README](https://github.com/DiFluid/difluid-sdk-demo/blob/master/README.md)를 실제 저울로 확인한 정리입니다. 문서와 실물이 다르면 **실물을 따르고** 그 자리에 표시했습니다.<br>
A summary of DiFluid's public documents — [`protocolMicrobalance.md`](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/protocolMicrobalance.md) (v1.0.0, 2024-12-24), [`difluid-protocol.md`](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/difluid-protocol.md) and the [README](https://github.com/DiFluid/difluid-sdk-demo/blob/master/README.md) — checked on real scales. Where the document and the device disagree, **we follow the device** and mark the spot.

✅ 실측 확인 · measured　📄 벤더 문서에만 있음 · vendor document only　❓ 미확인 · unknown

실측 기기는 두 대입니다 — **M**: 일반 Microbalance, **T**: Microbalance Ti. 표시 옆 글자는 어느 기기에서 확인했는지입니다([실측 기록](verification.md)).<br>
Two units were measured — **M**: Microbalance, **T**: Microbalance Ti. The letter next to a mark says which unit it was checked on ([verification](verification.md)).

모든 바이트는 16진수, 여러 바이트 값은 **빅 엔디언**입니다. · All bytes are hex; multi-byte values are **big-endian**. ✅ M

---

## 1. 연결 · Connecting

### 1.1 찾기 · Discovery

| 항목 · Item | 내용 · Detail | |
|---|---|---|
| 광고 이름 · Name | Ti: `Mb Ti NNNNNN`(뒤에 6자리 번호). `DiFluid` 로 시작하지 않습니다. · Ti: `Mb Ti NNNNNN` (a 6-digit number); it does not start with `DiFluid`. | ✅ T |
| | 일반 Microbalance 의 광고 이름은 기록이 없습니다. · No record of the Microbalance's advertised name. | ❓ |
| 서비스 UUID · Service UUID | Microbalance `0x00EE` | ✅ M |
| | Microbalance Ti `0x00DD` | 📄 |
| 광고의 서비스 UUID · UUID in advertising | 벤더: 서비스 UUID 와 같은 값을 광고한다. 저울 광고는 캡처하지 않았습니다. · Vendor: the same UUID is advertised. We did not capture scale advertising. | 📄 |
| 판별 권장 · Recommended match | 벤더 권고대로 광고의 서비스 UUID(`00EE`·`00DD`)로 고르되, 저울이 광고에 UUID 를 싣는지는 확인하지 못했으니 UUID 로 못 찾으면 이름(Ti 는 `Mb Ti`)으로 보조하세요. 이름 앞부분 `DiFluid` 로 고르면 같은 회사 굴절계 R2(`DiFluid R2 NNNNNN`)가 잡힙니다. `MB`·`Micro` 처럼 짧은 앞부분은 이름이 그렇게 시작하는 다른 기기(키보드·마우스 등)까지 잡게 됩니다(추론). · Match on the advertised service UUID as the vendor advises, but we never confirmed that the scale advertises it — if nothing matches, fall back to the name (Ti: `Mb Ti`). A `DiFluid` prefix also catches the R2 refractometer (`DiFluid R2 NNNNNN`). Short prefixes such as `MB` or `Micro` would also catch any other device whose name starts that way, such as keyboards and mice (inference). | 📄 · ✅ R2 |

전체 UUID · Full UUIDs: `000000ee-0000-1000-8000-00805f9b34fb` (Microbalance) · `000000dd-0000-1000-8000-00805f9b34fb` (Ti) · 특성 · characteristic `0000aa01-0000-1000-8000-00805f9b34fb`.

### 1.2 GATT

| 서비스 · Service | 특성 · Characteristic | 속성 · Properties | 쓰임 · Use | |
|---|---|---|---|---|
| `0x00EE` | `0xAA01` | read · write · notify | **명령을 쓰고 응답을 받는 곳(평문)** · write commands, receive responses (cleartext) | ✅ M |
| `0x00EE` | `0xFF01` | — | 벤더 README 의 「암호화 채널」. 평문을 쓰면 `ff` 나 에코만 돌아왔습니다. · The vendor README's encrypted channel. Writing cleartext returned only `ff` or an echo. | ✅ M |
| `0x00DD` (Ti, 벤더 · vendor 📄) | `0xAA01` | — | Ti 에서도 평문 프로토콜이 그대로 동작했습니다. 서비스·특성 속성은 기록하지 않았습니다. · The cleartext protocol worked on the Ti too; its service and characteristic properties were not recorded. | ✅ T / ❓ |

- **`0xAA01` 로 통신하세요.** 벤더 문서의 Microbalance 절은 「AA01」 바로 아래에 「FF01 로 통신하라」고 적었지만, 실물과 반대입니다. ✅ M<br>
  **Use `0xAA01`.** The vendor's Microbalance section says "AA01" and then "use FF01"; the device does the opposite. ✅ M
- `0xAA01` 에 **응답 있는 쓰기(write with response)** 로 보냅니다. write-without-response 속성이 없었습니다. ✅ M<br>
  Write to `0xAA01` **with response**; write-without-response was not offered. ✅ M
- 페어링·본딩, DiFluid 서버, SDK 키가 필요 없었습니다. ✅ M·T 연결 → `0xAA01` 구독 → 명령 쓰기만으로 응답이 옵니다. ✅ M (T 도 같은 순서로 응답했지만, 우리 드라이버가 `AA01` 이 있으면 `AA01` 을 고르는 방식이라 T 에서 실제로 쓴 특성은 기록이 없습니다. 벤더는 `AA01` 📄)<br>
  No pairing, bonding, DiFluid server or SDK key was needed. ✅ M·T Connect, subscribe to `0xAA01`, write commands. ✅ M (the Ti answered the same way, but our driver picks `AA01` when present, so the characteristic actually used on the Ti was not recorded; the vendor says `AA01` 📄)

### 1.3 연결 순서(우리가 쓴 것) · Connection sequence (what we used)

1. 연결 · connect ✅ M·T
2. `0xAA01` notify 구독 · subscribe to `0xAA01` notifications ✅ M (T 는 고른 특성 기록 없음 · characteristic not recorded on T)
3. SN `DF DF 00 00 00 BE` ✅ M·T · 펌웨어 · firmware `DF DF 00 02 00 C0` (T 에서만 보냄, 응답 미캡처 · sent on T only, response not captured ❓)
4. 센서 데이터 `DF DF 03 00 00 C1` 을 0.2 s 마다(5 Hz) · sensor data every 0.2 s (5 Hz) ✅ M·T
5. 상태 `DF DF 03 05 00 C6` 을 5 s 마다(배터리) · status every 5 s (battery) ✅ T

다섯 단계를 이 순서 그대로 돈 것은 T 입니다. M 은 펌웨어·상태 요청 없이 1~4 로 확인했습니다. · The full five-step sequence ran on T; M was checked with steps 1–4, without the firmware and status requests.

MTU 교환이나 자동 송신 설정 같은 사전 준비는 필요 없었습니다. · No MTU exchange or auto-send setup was needed.

### 1.4 펌웨어 · Firmware

- 최소 펌웨어: Microbalance `V300`, Ti `V010`. 📄<br>
  Minimum firmware: Microbalance `V300`, Ti `V010`. 📄
- **구펌웨어 저울은 어떤 명령에도 응답하지 않았습니다.** DiFluid 앱으로 펌웨어를 올린 뒤에야 응답했습니다. ✅ M<br>
  **A scale on old firmware answered no command at all.** It answered only after a firmware update through the DiFluid app. ✅ M
- **펌웨어를 올리자 BLE 주소가 바뀌었습니다.** 업데이트 전에 저장한 주소로는 다시 연결되지 않습니다. ✅ M<br>
  **The firmware update changed the BLE address.** An address saved before the update no longer connects. ✅ M
- 실제 펌웨어 버전 문자열은 캡처하지 못했습니다. ❓<br>
  We did not capture an actual firmware version string. ❓

---

## 2. 프레임 · Frame

R2 와 같은 DiFluid 공통 형식입니다. · The same DiFluid frame format as the R2.

```
DF DF | func | cmd | len | data0 … data(len-1) | sum
```

- `sum` = 머리부터 마지막 데이터까지 합의 하위 8비트(`& 0xFF`). 실캡처 응답이 모두 이 규칙에 맞았습니다. ✅ M·T<br>
  `sum` = low 8 bits of the sum from the header through the last data byte. Every captured response matched. ✅ M·T
- 계산이 쉬운 꼴: 데이터가 없으면 `sum = (0xBE + func + cmd) & 0xFF`, 데이터 1 B 면 `sum = (0xBF + func + cmd + data) & 0xFF`.<br>
  Shortcut: with no data, `sum = (0xBE + func + cmd) & 0xFF`; with one data byte, `sum = (0xBF + func + cmd + data) & 0xFF`.
- 응답은 요청의 func·cmd 를 그대로 돌려줍니다. ✅ M·T<br>
  A response carries the request's func and cmd. ✅ M·T
- **한 notify 에 프레임이 둘 이상 붙어 올 수 있습니다.** SN 응답 0·1 이 24 B notify 하나로 왔습니다. 길이 바이트로 잘라 처리하세요. ✅ T<br>
  **One notification can carry more than one frame.** SN chunks 0 and 1 arrived in one 24-byte notification. Split by the length byte. ✅ T
- 한 프레임이 notify 둘로 쪼개지는 경우는 보지 못했습니다. ❓<br>
  A frame split across two notifications was not observed. ❓
- 벤더 데모 앱(uni-app)은 쓰기 직전에 첫 바이트를 1 줄이는데, 그 프레임워크 사정입니다. 프레임은 `DF DF` 그대로 보내면 됩니다. ✅ M<br>
  The vendor's uni-app demo decrements the first byte before writing; that is a framework quirk. Send frames as `DF DF …` unchanged. ✅ M

---

## 3. 명령 · Commands

func `0` 기기 정보 · `1` 설정 · `3` 데이터·제어 (`2` 는 비어 있음). 아래 바이트는 체크섬까지 계산해 확인했습니다.<br>
func `0` device info · `1` settings · `3` data and control (`2` is unused). All bytes below were checked, checksum included.

| 용도 · Purpose | 보내는 바이트 · Bytes to send | 부작용 · Side effect | |
|---|---|---|---|
| SN | `DF DF 00 00 00 BE` | 없음 · none | ✅ M·T |
| 모델 · Model | `DF DF 00 01 00 BF` | 없음 · none | 📄 |
| 펌웨어 · Firmware | `DF DF 00 02 00 C0` | 없음 · none | 보냈으나 응답 미캡처 · sent, response not captured ❓ |
| **센서 데이터 · Sensor data** | `DF DF 03 00 00 C1` | 없음 · none | ✅ M·T |
| **상태 · Status** | `DF DF 03 05 00 C6` | 없음 · none | ✅ T |
| **영점 · Tare** (전원 버튼 클릭 · Power click) | `DF DF 03 02 01 01 C5` | 영점 · tares | ✅ M |
| 타이머 시작 · Timer start (DLink 클릭 · click) — 벤더: 정지 상태 풀기도 같은 명령 · vendor: also leaves the stop state | `DF DF 03 02 01 00 C4` | 타이머 · timer | 시작 ✅(기종 기록 없음) · 정지 풀기 📄(무게가 다시 흐르는지 ❓) · start ✅ (unit not recorded) · leaving stop 📄 (whether weight resumes ❓) |
| 타이머 정지 · Timer stop (DLink press) | `DF DF 03 01 01 00 C3` | ⚠ **무게 송출이 멈춤**(§7) · **weight output freezes** (§7) | ✅ |
| 정보 화면 · Info screen (DLink 더블 · double) | `DF DF 03 03 01 00 C5` | 화면 전환 · screen | 📄 |
| 단위 전환 · Unit toggle (전원 더블 · Power double) | `DF DF 03 03 01 01 C6` | 단위가 바뀜 · unit changes | 📄 |
| DLink 길게 · long (예약 · reserved) | `DF DF 03 04 01 00 C6` | — | 📄 |
| ⚠ **전원 끄기 · Power off** (전원 길게 · Power long) | `DF DF 03 04 01 01 C7` | **저울이 꺼짐 · turns the scale off** | 📄 |

설정(func 1)은 Get = 데이터 없음, Set = 데이터 1 B 이고, Set 의 응답은 설정한 값을 돌려줍니다(벤더). **우리는 func 1 을 하나도 보내지 않았습니다.** 📄<br>
Settings (func 1): Get has no data, Set carries 1 byte and echoes the value (vendor). **We never sent any func 1 command.** 📄

| 설정 · Setting | cmd | 값 · Values | Get | Set 예 · Set example |
|---|---|---|---|---|
| 센서 데이터 자동 송신 · Sensor data auto-send | `00` | 0 끔 off · 1 켬 on | `DF DF 01 00 00 BF` | 켬 · on `DF DF 01 00 01 01 C1` |
| 자동 타이밍 시작 · Auto detect timing | `01` | 0 · 1 | `DF DF 01 01 00 C0` | 켬 · on `DF DF 01 01 01 01 C2` |
| 자동 타이밍 정지 · Auto stop timing | `02` | 0 · 1 | `DF DF 01 02 00 C1` | 켬 · on `DF DF 01 02 01 01 C3` |
| 단위 전환 잠금 · Unit switch lock | `03` | 0 · 1 | `DF DF 01 03 00 C2` | 켬 · on `DF DF 01 03 01 01 C4` |
| 무게 단위 · Weight unit | `04` | 0 g · 1 oz · 2 gering | `DF DF 01 04 00 C3` | g `DF DF 01 04 01 00 C4` |

- 자동 송신의 주기·기본값, 자동 타이밍의 감지 조건, 「gering」 단위의 뜻은 벤더 문서에 없습니다. ❓<br>
  The auto-send interval and default, what the auto-timing features detect, and what "gering" means are not in the vendor document. ❓
- 벤더 설명: 단위 잠금을 켜면 전원 버튼 더블클릭으로는 단위가 바뀌지 않고, 프로토콜(func 1·cmd 4)로는 바뀝니다. 📄<br>
  Vendor: with the unit lock on, double-clicking the power button no longer changes the unit, but func 1 · cmd 4 still does. 📄

---

## 4. 센서 데이터 · Sensor data (func 3 · cmd 0)

응답은 **len 13**(프레임 19 B)입니다. 벤더 표는 12 로 적었지만 벤더 예시와 실물은 13 입니다. ✅ M<br>
The response has **len 13** (19-byte frame). The vendor table says 12; its example and the device say 13. ✅ M

| 바이트 · Bytes | 내용 · Content | |
|---|---|---|
| data0–3 | **무게** · **weight** — g 모드에서 ÷ 10(0.1 g) · ÷ 10 in gram mode (0.1 g) | ✅ M |
| | 부호(음수 무게)는 캡처하지 못했습니다. 영점 뒤 컵을 들면 음수가 나올 수 있으니 부호 있게 읽기를 권합니다(가정). · Sign not captured (no negative weight seen). Read it as signed, since lifting a cup after tare can go negative (assumption). | ❓ |
| data4–5 | 유량 · flow — 벤더: ×10. **타이머가 돌지 않을 때는 무게가 줄어드는 중에도 0 이었습니다.** · Vendor: ×10. **It stayed 0 while weight was falling and the timer was not running.** | ✅ M / ❓ |
| data6–7 | 타이머 · time — 고정해 둔 실캡처는 모두 0. 타이머를 시작하면 움직이는 것은 봤으나(§7.2) 그 프레임은 남기지 못했고, 단위는 미확인 · all pinned captures were 0; it was seen moving after a timer start (§7.2) but those frames were not kept; unit unknown | ❓ |
| data8–11 | 기기 시각 · device tick — 계속 늘어나는 카운터(ms 로 보이며 실측 값은 모두 40 의 배수) · an increasing counter (looks like ms; every captured value was a multiple of 40) | ✅ M / ❓ |
| data12 | 단위 · unit — 0 g ✅ · 1 oz(무게 ×1000) · 2 gering(×10) 📄 | ✅ M |

실측 예(394.0 g 분동을 치우는 동안) · Captured (while removing a 394.0 g weight):

```
DF DF 03 00 0D 00 00 0F 64 00 00 00 00 00 07 57 88 00 27   394.0 g · tick 481160
DF DF 03 00 0D 00 00 0B F3 00 00 00 00 00 07 5E E0 00 11   305.9 g · tick 483040
DF DF 03 00 0D 00 00 00 00 00 00 00 00 00 07 60 E8 00 1D     0.0 g · tick 483560
```

- 무게 `00 00 0F 64` = 3940 → **394.0 g**. 무게가 88 g 줄어든 사이에도 유량 칸은 `00 00` 이었습니다.<br>
  Weight `00 00 0F 64` = 3940 → **394.0 g**. The flow field stayed `00 00` while 88 g came off.
- 유량이 필요하면 무게 변화로 직접 계산하세요. 기기 시각(data8–11)을 쓰면 BLE 수신 지터와 무관한 시간 축을 얻을 수 있습니다(단위는 미확인).<br>
  If you need flow, compute it from the weight series. The device tick (data8–11) gives a time base free of BLE jitter (unit unconfirmed).
- 자동 송신을 켜지 않으면 **요청 한 번에 응답 한 프레임**입니다. 샘플레이트는 폴링이 정합니다([실측 기록](verification.md)의 타이밍). ✅ M·T<br>
  Without auto-send it is **one frame per request**; the polling rate sets the sample rate (see timing in [verification](verification.md)). ✅ M·T

---

## 5. 상태·배터리 · Status and battery (func 3 · cmd 5) ✅ T

응답은 len 8: **data0 = 상태 코드**, **data1 = 배터리 %**, data2 = 충전 중(1)/아님(0), data3–7 = 예약.<br>
Response len 8: **data0 = status code**, **data1 = battery %**, data2 = charging (1) / not (0), data3–7 = reserved.

```
→ DF DF 03 05 00 C6
← DF DF 03 05 08 05 3F 00 00 00 00 00 00 12     상태 · status 5 (Idle) · 배터리 · battery 63 % · 충전 아님 · not charging
```

- **data0 을 배터리로 읽으면 쉬는 저울이 모두 「5 %」로 보입니다.** 5 는 상태 코드 Idle 입니다. 배터리는 data1 입니다. ✅ T<br>
  **Reading data0 as the battery shows every idle scale at "5 %".** 5 is the Idle status; the battery is data1. ✅ T
- 배터리는 이 요청으로만 얻습니다. · The battery is only available through this request.

| 상태 코드 · Code | 뜻 · Meaning | | 상태 코드 · Code | 뜻 · Meaning |
|---|---|---|---|---|
| 0 | 꺼짐 · Power down | | 8 | OTA 중 · OTA in progress |
| 1 | 충전 중 · Charging | | 9 | OTA 실패 · OTA failed |
| 2 | 저전력 1 · Low power mode 1 | | 10 | 타이머 진행 · Timing in progress |
| 3 | 저전압 종료 · Low-battery shutdown | | 11 | 타이머 일시정지 · Timer pause |
| 4 | 시작 중 · Startup | | 12 | 예약 · Reserved |
| **5** | **대기 · Idle** ✅ | | 13 | 저전력 2 · Low power mode 2 |
| 6 | 기기 정보 표시 · Show device info | | 14 | 자동 타이밍 정지 · Auto stop timing trigger |
| 7 | 영점 중 · Tare in progress | | | |

실측된 값은 5 하나뿐이고 나머지는 벤더 표입니다. 📄 상태 1(충전 중)과 data2(충전 플래그)의 관계는 정의돼 있지 않습니다. ❓<br>
Only 5 was observed; the rest is the vendor table. 📄 How status 1 (charging) relates to data2 (charging flag) is not defined. ❓

---

## 6. 기기 정보 · Device info (func 0)

- SN 은 조각 3개로 옵니다: `DF DF 00 00 06 <번호 0~2> <ASCII 5 B> ss`. 이어 붙이면 15자입니다. ✅ M·T<br>
  The SN arrives as 3 chunks: `DF DF 00 00 06 <index 0–2> <5 ASCII bytes> ss`, 15 characters joined. ✅ M·T
- **우리 두 기기의 SN 은 BLE 주소에서 나온 값이었습니다**(앞 12자리 = 주소 − 2 의 16진 표기, 뒤에 `000`). SN 을 로그나 공개 자료에 남기면 기기 주소가 드러납니다. ✅ M·T<br>
  **On both our units the SN was derived from the BLE address** (first 12 characters = address − 2 in hex, then `000`). Logging or publishing the SN exposes the address. ✅ M·T
- 모델(cmd 1)은 보내지 않았고, 펌웨어(cmd 2) 응답은 캡처하지 못했습니다. 벤더 문서의 모델·펌웨어 예시는 R2 문서에서 옮겨 온 값이라 실제 저울 응답이 아닙니다(§9). ❓<br>
  Model (cmd 1) was never sent and the firmware (cmd 2) response was not captured. The vendor's model and firmware examples were carried over from the R2 document and are not real scale responses (§9). ❓

---

## 7. 영점과 타이머 · Tare and timer

Func 3 의 cmd 1~4 는 영점·타이머 전용 명령이 아니라 **저울 버튼 두 개(DLink · 전원)를 누르는 흉내**입니다. 데이터 `00` = DLink, `01` = 전원입니다.<br>
Func 3 cmd 1–4 are not dedicated tare/timer commands: they **simulate the two buttons** (DLink and Power). Data `00` = DLink, `01` = Power.

### 7.1 영점 · Tare ✅ M

- `DF DF 03 02 01 01 C5`(전원 버튼 클릭). 21.4 g 에서 보내자 **1.58 s 뒤 0.0 g** 가 됐습니다(폴링으로 잰 값 — 당시 폴링 주기는 기록 없음).<br>
  `DF DF 03 02 01 01 C5` (Power button click). From 21.4 g it read **0.0 g after 1.58 s** (measured by polling; the polling interval was not recorded).
- **데이터 바이트를 빠뜨린 `DF DF 03 02 00 C3` 은 체크섬이 맞아 쓰기는 성공하지만, 저울이 아무 반응 없이 무시합니다.** 벤더 본문의 「How to Tare」가 데이터 바이트를 적지 않아 생기기 쉬운 실수입니다.<br>
  **`DF DF 03 02 00 C3` (data byte missing) has a valid checksum and the write succeeds, but the scale silently ignores it.** The vendor's "How to Tare" text omits the data byte, which makes this easy to get wrong.
- Ti 에서 영점만 따로 확인한 기록은 없습니다. ❓ · No separate tare record on the Ti. ❓

### 7.2 타이머 · Timer

- 시작: `DF DF 03 02 01 00 C4`(DLink 클릭). 벤치에서 보낸 뒤 무게 응답의 타이머 칸이 움직이는 것을 보고 합격으로 판정했습니다. 그 프레임은 남기지 못해 §4 의 실캡처는 모두 0 입니다. ✅(기종 기록 없음 · unit not recorded) 벤더는 같은 명령이 정지 상태도 푼다고 적었습니다. 📄<br>
  Start: `DF DF 03 02 01 00 C4` (DLink click). On the bench we saw the time field of the weight response move after sending it; those frames were not kept, so every capture in §4 shows 0. ✅ The vendor says the same command also leaves the stop state. 📄
- 정지: `DF DF 03 01 01 00 C3`(DLink press). **보내면 저울이 정지 상태로 들어가면서 BLE 무게 출력까지 멈췄습니다.** 그 뒤로는 컵을 치워도 무게가 변하지 않았습니다. ✅(기종 기록 없음 · unit not recorded)<br>
  Stop: `DF DF 03 01 01 00 C3` (DLink press). **The scale entered its stop state and its BLE weight output froze.** Removing the cup no longer changed the weight. ✅
- 정지 상태에서 프레임이 끊기는지 같은 값으로 계속 오는지, DLink 클릭으로 풀면 무게가 다시 흐르는지는 확인하지 못했습니다. ❓<br>
  Whether frames stop or keep repeating the same value in the stop state, and whether a DLink click restores the weight stream, is unknown. ❓
- **타이머를 0 으로 되돌리는 명령이 없습니다.** 📄 벤더도 click/press 구분이 일관되지 않다고 적고 「향후 수정」을 예고했습니다.<br>
  **There is no timer reset command.** 📄 The vendor itself notes the click/press inconsistency and promises a fix.
- 그래서 우리는 **샷 시간을 저울 타이머로 재지 않고 직접 잽니다.** 무게를 계속 써야 하는 기능에서는 타이머 정지를 보내지 마세요.<br>
  So we **time shots ourselves rather than with the scale's timer.** Do not send timer stop if you rely on the weight stream.

### 7.3 버튼 흉내와 기기 이벤트 · Button simulation and device events

- 응답의 데이터 `0`·`1` 은 보낸 명령의 응답이고, `2`·`3` 은 **사용자가 저울 버튼을 직접 누른 것(Device Trigger)** 입니다(cmd 1 은 `1` 이 기기 발생). 📄 그렇다면 요청 없이 올 것으로 보이지만, 벤더가 그렇게 적지는 않았고 우리도 캡처하지 못했습니다(추론). ❓<br>
  Response data `0`/`1` acknowledge your command; `2`/`3` mean **the user pressed a button on the scale (Device Trigger)** (for cmd 1, `1` is the device event). 📄 That suggests they arrive unrequested, but the vendor does not say so and we never captured one (inference). ❓
- ⚠ **`DF DF 03 04 01 01 C7`(전원 길게)은 저울을 끕니다.** 벤더 문서가 아무 경고 없이 예시로 실었으니 그대로 시험하지 마세요.<br>
  ⚠ **`DF DF 03 04 01 01 C7` (Power long press) turns the scale off.** The vendor lists it as an example without a warning — do not run it blindly.

---

## 8. 오류 · Errors

Microbalance 문서에는 오류 응답이 정의돼 있지 않습니다(R2 문서는 cmd 254·255 를 정의합니다). 실물도 이해하지 못한 명령을 **오류 없이 무시**했습니다. 명령의 결과는 무게·상태 변화로 확인하세요. ✅ M<br>
The Microbalance document defines no error responses (the R2 document defines cmd 254/255). The device also **silently ignored** a command it did not understand. Confirm results through weight or status changes. ✅ M

---

## 9. 벤더 문서와 다른 점 · Differences from the vendor document

| 벤더 문서 · Vendor document | 실물·바로잡은 값 · Device / corrected |
|---|---|
| Microbalance: 「Characteristic value: AA01」 아래 「FF01 채널로 통신」 · "AA01", then "use FF01" | **AA01 로 통신**. FF01 은 암호화 채널(README)이고 평문에는 `ff`·에코만 · **Use AA01**; FF01 is the encrypted channel (README) and answers cleartext with `ff` or an echo ✅ M |
| 쓰기 방식 언급 없음 · Write type not stated | 응답 있는 쓰기 필수(write-without-response 없음) · write with response (no write-without-response) ✅ M |
| README 가 `ff01`·`aa01` 을 「두 서비스」라 부름 · README calls them "two services" | 제품별 서비스(`00EE` 등) 아래의 **특성** · **characteristics** under the product's service ✅ M |
| 센서 데이터 응답 길이 12 · Sensor data length 12 | **13**(예시·실물) · **13** (example and device) ✅ M |
| 모델 응답 예시 · Model response example `DF DF 01 08 44 46 54 2D 53 31 30 31 B7` | func `00` 이 빠짐 → `DF DF 00 01 08 … B7` · the func byte `00` is missing |
| 펌웨어 응답 예시 · Firmware response example `DF DF 00 02 17 56 30 30 31 BE` | 길이 0x17 인데 데이터 4 B → `DF DF 00 02 04 56 30 30 31 AB`. `V001` 은 최소 펌웨어보다 낮아 실제 응답일 수 없음 · length 0x17 with 4 data bytes; `V001` is below the minimum firmware |
| SN·모델·펌웨어 예시 · SN, model, firmware examples | R2 문서의 예시를 옮겨 온 값(SN 은 바이트까지 같음) — 시험 고정값으로 쓰지 말 것 · carried over from the R2 document — do not use as test fixtures |
| 「Get Auto Detect Timing」 예시 · example `DF DF 01 01 01 C0` | 길이 01 인데 데이터 없음 → `DF DF 01 01 00 C0` · length 01 with no data |
| 「Set Auto Send」 해석 · reading 「0x00 = On」 | 데이터는 `01` — 오타 · the data is `01`; typo |
| 「How to Tare」: Func 3 · Cmd 2 만 적음 · gives only Func 3 · Cmd 2 | 데이터 `01` 이 꼭 필요. 빠지면 조용히 무시 · data `01` is required; without it the scale ignores the command ✅ M |
| 타이머 정지의 부작용 언급 없음 · No side effect for timer stop | **BLE 무게 송출이 멈춤** · **the BLE weight output freezes** ✅ |
| 타이머 리셋 없음 · No timer reset | 그대로 — 저울 타이머로 샷을 재기 어려움 · unchanged; hard to time shots with it |
| 롱프레스 예시 · Long-press example `DF DF 03 04 01 01 C7` | **저울 전원 끄기**인데 경고 없음 · **powers the scale off**, no warning |
| 바이트 순서·체크섬 `& 0xFF`·무게 부호·유량 단위·시간 단위 미기재 · Byte order, `& 0xFF`, weight sign, flow and time units not stated | 빅 엔디언 ✅ · `& 0xFF` ✅ · 나머지 ❓ · big-endian ✅, `& 0xFF` ✅, the rest ❓ |
| 오류 응답 정의 없음 · No error responses | 실물도 잘못 만든 영점 명령을 조용히 무시(정의되지 않은 func·cmd 는 미시험) · the device silently ignored a malformed tare (undefined func/cmd untested) ✅ M |
| 2024-12-24 개정(Ti·UUID 추가)인데 버전 1.0.0 그대로, 개정 이력 없음 · Revised 2024-12-24 (Ti, UUIDs) but still v1.0.0, no change log | 무엇이 바뀌었는지 확인 불가 · cannot tell what changed ❓ |
