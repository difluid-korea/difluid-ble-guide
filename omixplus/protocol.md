# Omix Plus BLE 프로토콜 · BLE protocol

[← Omix Plus](README.md) · [English](README.en.md)

벤더 문서가 없는 기기다. 이 문서는 이승진(180커피로스터스)의 자료와 [캡처](captures/README.md)를 근거로 하며, 측정 시작·설정 같은 명령은 다루지 않는다.<br>
There is no vendor document for this device. This page is based on material from 이승진 (180 Coffee Roasters) and the [captures](captures/README.md). It does not cover commands such as starting a measurement or settings.

✅ 기여자 실측 · contributor, on a device　재계산 · recomputed from the captures　📄 벤더 문서 · vendor document　❓ 미확인 · unknown

모든 바이트는 16진수, 여러 바이트 값은 **리틀 엔디언**이다(R2·저울과 반대). 재계산<br>
All bytes are hex; multi-byte values are **little-endian** (unlike the R2 and the scales). recomputed

위치는 두 가지로 적는다. `data n` 은 길이 바이트 다음부터 센 위치, 「절대」는 프레임 첫 `DF` 를 0 으로 센 위치(= data n + 5)다.<br>
Offsets are given two ways: `data n` counts from the byte after the length byte; "abs" counts from the first `DF` (= data n + 5).

---

## 1. 연결 · Connecting

### 1.1 찾기 · Discovery

| 항목 · Item | 내용 · Detail | |
|---|---|---|
| 광고 이름 · Name | `Omix Plus` 뒤에 기기 번호. 1대에서 관찰 · `Omix Plus` followed by a unit number; seen on one unit | ✅ |
| 광고의 서비스 UUID · UUID in advertising | 기록 없음 · not recorded | ❓ |
| 판별 · Matching | 이름 앞부분 `Omix` 로 고른다. Plus 가 아닌 Omix 의 이름은 모른다 · match on the `Omix` name prefix; names of Omix models other than the Plus are unknown | ✅ / ❓ |

### 1.2 GATT

탐색 결과 원본: [`captures/gatt-discovery.json`](captures/gatt-discovery.json) (2026-10-20, Windows) · Raw discovery result.

| 서비스 · Service | 특성 · Characteristic | 속성 · Properties | 쓰임 · Use | |
|---|---|---|---|---|
| `0x1800` | `0x2A00` · `0x2A01` | read 등 · read etc. | 표준 GAP · standard GAP | 재계산 |
| `0x1801` | `0x2A05` | indicate · read | 표준 GATT · standard GATT | 재계산 |
| `0x00E1` | `0xFF01` | notify · write | 용도 모름. 기여자 수신기는 구독하지 않음 · purpose unknown; the contributor's receiver does not subscribe | 재계산 · ❓ |
| **`0x00E2`** | **`0xFF02`** | notify · write | **측정 결과가 오는 곳** · **where results arrive** | ✅ 재계산 |

- 탐색 기록에 표준 기기 정보 서비스(`0x180A`)가 없어, 모델 문자열·펌웨어 버전을 이 서비스로는 얻지 못했다. 제조사 전용 조회 방법과 다른 장치·펌웨어의 지원 여부는 모른다. 재계산 · ❓<br>
  The discovery record has no standard Device Information service (`0x180A`), so the model string and firmware version were not obtained through it. Maker-specific queries, and other units or firmware, are unknown. recomputed · ❓
- 탐색 기록에 R2·저울의 평문 특성 `0xAA01` 이 없다. 재계산<br>
  The discovery record has no `0xAA01`, the cleartext characteristic on the R2 and scales. recomputed
- `0xFF02` 의 CCCD(`0x2902`)에 notify 를 켜면 된다. 쓰기(write) 속성이 보이지만 기여자는 아무것도 쓰지 않았다. ✅<br>
  Enable notifications on the `0xFF02` CCCD (`0x2902`). The characteristic also shows write, but the contributor never wrote to it. ✅

### 1.3 MTU

- 가장 긴 응답이 126 B 다. notify 한 번에 실을 수 있는 크기는 ATT MTU − 3 이므로, 이 프레임을 notify 하나로 받으려면 MTU 129 이상이 필요하다. 기여자 수신기는 129 이상을 준비 조건으로 쓴다. 관찰한 MTU 는 23 과 517 둘뿐이고, 그 사이 값에서 기기가 어떻게 보내는지와 제조사의 최소 요구 MTU 는 모른다. 재계산 · ❓<br>
  The longest response is 126 B. A notification carries at most ATT MTU − 3 bytes, so receiving it in one notification takes an MTU of 129 or more; the contributor's receiver uses 129 as its readiness condition. Only MTU 23 and 517 were observed. How the device sends at MTUs in between, and the maker's minimum MTU, are unknown. recomputed · ❓
- MTU 23 일 때는 세 응답이 모두 앞 20 B 만 왔다. 나머지를 담은 notify 는 이어서 오지 않았다(수신 카운터가 2·3·4 로 연속). 잘린 프레임은 복원할 수 없다. ✅ 재계산 · [`mtu23-truncated.jsonl`](captures/mtu23-truncated.jsonl)<br>
  At MTU 23 each of the three responses arrived as its first 20 bytes only. No notification with the rest followed (receive counter 2, 3, 4 in sequence). A cut frame cannot be rebuilt. ✅ recomputed
- MTU 517 일 때는 완전한 프레임이 왔다. ✅<br>
  At MTU 517 complete frames arrived. ✅
- Windows 에서는 서비스 탐색 직후 MTU 협상이 늦게 끝날 수 있어, 기여자 수신기는 MTU 가 129 이상이 될 때까지 기다린 뒤 측정하게 한다. MTU 23 사례가 왜 생겼는지(Android 로 먼저 연결한 뒤 Windows 에서 정상 수신된 이력이 있음)는 확정되지 않았다. ✅ / ❓<br>
  On Windows the MTU exchange can finish shortly after service discovery, so the contributor's receiver waits until the MTU reaches 129 before the user measures. Why the MTU 23 case happened is not settled (full frames arrived on Windows after an earlier Android connection). ✅ / ❓

### 1.4 연결 순서(기여자) · Connection sequence (contributor)

1. 연결 · connect ✅
2. MTU 129 이상 대기(Windows) · wait for MTU ≥ 129 (Windows) ✅
3. `0xFF02` notify 구독. `0xFF01` 은 구독하지 않는다(그쪽 CCCD 실패가 `0xFF02` 수신을 막지 않도록) · subscribe to `0xFF02`; `0xFF01` is left alone so a failed CCCD there cannot block `0xFF02` ✅
4. 사용자가 본체에서 측정 → 결과 notify · the user measures on the device → result notifications ✅

명령은 보내지 않는다. 페어링도 호출하지 않았다. 새 PC 에서 페어링 없이 되는지는 시험하지 않았다. ✅ / ❓<br>
No commands are sent and pairing is never called. Whether a fresh PC works without pairing was not tested. ✅ / ❓

---

## 2. 프레임 · Frame

R2·저울과 같은 DiFluid 공통 형식이다. · The same DiFluid frame format as the R2 and scales.

```
DF DF | func | cmd | len | data0 … data(len-1) | sum
```

- 전체 길이 = len + 6. `sum` = 앞 바이트 전부의 합의 하위 8비트(`& 0xFF`). 공개 캡처의 완전한 프레임 12개가 모두 맞는다. 재계산<br>
  Total length = len + 6. `sum` = low 8 bits of the sum of all preceding bytes. All 12 complete frames in the captures match. recomputed
- notify 하나에 프레임 하나씩 왔다. 한 프레임이 notify 여러 개로 나뉘어 오는 경우는 없었다(MTU 23 에서는 잘렸다, §1.3). 재계산<br>
  Each notification carried one frame. No frame was split across notifications (at MTU 23 it was cut instead, §1.3). recomputed
- 벤더 공통 문서의 「최대 데이터 20 B」는 Omix 에 맞지 않는다. 색도 응답의 len 은 0x78(120)이다. 재계산<br>
  The vendor's general "max data length 20 bytes" does not hold here: the color response has len 0x78 (120). recomputed

---

## 3. 결과 응답 · Result responses

측정 한 번에 `0xFF02` 로 오는 응답이다. 아래 cmd 는 **응답에서 관찰한 값**이며 보내는 명령이 아니다.<br>
Responses arriving on `0xFF02` for one measurement. The cmd values are **what was seen in responses**, not commands to send.

| func | cmd | len | 프레임 · Frame | 내용 · Content | |
|---|---|---|---|---|---|
| `03` | `03` | `2C` (44) | 50 B | 시료 모드·수분·밀도 · sample mode, moisture, density | ✅ 재계산 |
| `03` | `05` | `78` (120) | 126 B | 색도 · roast color | ✅ 재계산 |
| `03` | `06` | `1C` (28) | 34 B | 주변 온도·습도 · ambient temperature and humidity | ✅ 재계산 |
| `03` | `02` | `12` (18) | 24 B | 뜻 모름. 공개 캡처에서 뺐다(§3.5) · unknown; left out of the captures (§3.5) | ❓ |

### 3.1 공통 머리 · Common header (03/03 · 03/05 · 03/06)

| data | 절대 · abs | 형 · Type | 내용 · Content | |
|---|---|---|---|---|
| 0–7 | 5–12 | u64 | Unix 시각(초, UTC)으로 읽힌다. 4묶음 모두 PC 수신 시각보다 2.5–7.9 s 앞섰다. 기기 시계를 무엇이 맞추는지, 측정 시작 시각인지는 모른다 · reads as Unix time (s, UTC); in all 4 sets it was 2.5–7.9 s before the PC receive time. What sets the device clock, and whether it marks the start of the measurement, is unknown | 재계산 · ❓ |
| 8–11 | 13–16 | u32 | 카운터. 10-20 ~ 10-23 사이 686 → 718 → 803 → 813 으로 늘었다 · counter; rose 686 → 718 → 803 → 813 between 10-20 and 10-23 | 재계산 · ❓ |

한 측정의 세 응답은 data0–11 이 같다. 기여자는 이 12 B 를 측정 묶음 키로 쓴다. 여러 기기 사이에서 겹치지 않는지는 모른다. ✅ / ❓<br>
The three responses of one measurement share data0–11; the contributor uses these 12 bytes as the grouping key. Uniqueness across devices is unknown. ✅ / ❓

### 3.2 `03/03` 시료 모드·수분·밀도 · Sample mode, moisture, density (50 B)

| data | 절대 · abs | 형 · Type | 내용 · Content | |
|---|---|---|---|---|
| 12–15 | 17–20 | u32 | 시료 모드 · sample mode — `01 04 00 00` (1025) 홀빈 · whole bean, `01 05 00 00` (1281) 분쇄 · ground. 다른 값 · other values ❓ | ✅ |
| 16–19 | 21–24 | u32 | 뜻 모름. 관측 19 · 23 · 0 · 0. 값을 쓸지 말지 판단하는 데 쓰지 말 것 · unknown; seen 19, 23, 0, 0. Do not use it to accept or reject values | ❓ |
| 20–23 | 25–28 | f32 | 뜻 모름. 7.54 · 9.12(홀빈), 0(분쇄·값 없음) · unknown; 7.54, 9.12 (whole), 0 (ground, no value) | ❓ |
| 24–27 | 29–32 | f32 | **수분 %** · **moisture %** ×1. 음수 = 값 없음 · negative = no value | ✅ |
| 28–31 | 33–36 | f32 | 뜻 모름. 515.0 · 615.7 / 0 · unknown | ❓ |
| 32–35 | 37–40 | — | 관측값 모두 0 · always 0 so far | |
| 36–39 | 41–44 | f32 | **밀도** · **density** ×1. 0 = 값 없음 · 0 = no value. 단위 g/L 는 기여자 앱의 표기이며 제조사 확인은 없다 · "g/L" is the contributor's label, not confirmed by the maker | ✅ / ❓ |
| 40–43 | 45–48 | f32 | 뜻 모름. 72.1 · 86.2 / 0 · unknown | ❓ |

예 · Example ([`whole-normal.jsonl`](captures/whole-normal.jsonl)):

```
DF DF 03 03 2C
64 9E DA 6A 00 00 00 00   23 03 00 00          id 1792712292 (2026-10-22 23:38:12 UTC) : 803
01 04 00 00               13 00 00 00          홀빈 · whole · 19
AE 47 F1 40               98 3E 9F 3F          7.54 · 수분 · moisture 1.24 → 1.2 %
00 C0 00 44               00 00 00 00          515.0 · 0
D8 A3 C1 43               33 33 90 42          밀도 · density 387.3 · 72.1
09                                             sum
```

- 분쇄 모드에서는 수분 칸이 음수, 밀도 칸이 0 이었다(1회). 분쇄 시료의 수분·밀도를 어떻게 보내는지는 확인되지 않았다. ✅ / ❓<br>
  In ground mode the moisture field was negative and density 0 (one capture). How moisture and density are reported for ground samples is not established. ✅ / ❓

### 3.3 `03/05` 색도 · Roast color (126 B)

| data | 절대 · abs | 형 · Type | 내용 · Content | |
|---|---|---|---|---|
| 12–15 | 17–20 | u32 | 4묶음 모두 2. 기여자 수신기는 2 일 때만 색도로 받는다 · 2 in all 4 sets; the contributor's receiver accepts color only when it is 2 | ✅ / ❓ |
| 16–19 | 21–24 | f32 | **색도** · **roast color** ×1, 본체의 Agtron 값 · the device's Agtron value. 표준(Common·SCA)이나 보정 설정과의 관계는 모른다 · relation to the color standard or calibration settings is unknown | ✅ / ❓ |
| 20–23 | 25–28 | f32 | 뜻 모름. 32.03 · 37.59 · 24.0 · 5.85 · unknown | ❓ |
| 24–79 | 29–84 | — | 4묶음 모두 0 · 0 in all 4 sets | |
| 80 | 85 | u8 | 4묶음 모두 1 · 1 in all 4 sets | ❓ |
| 81–111 | 86–116 | u8 ×31 | 합이 4묶음 모두 100. 백분율 분포로 보인다 · sums to 100 in all 4 sets; looks like a percentage distribution | 재계산 · ❓ |
| 112–119 | 117–124 | u8 ×8 | 합이 4묶음 모두 100. 또 하나의 분포로 보인다 · sums to 100 in all 4 sets; looks like a second distribution | 재계산 · ❓ |

두 분포가 무엇의 분포인지(색도 구간, 입도 등)는 모른다. 제품 화면은 배전색 분포를 보여 주지만 대조한 기록은 없다.<br>
What the two distributions describe (color bins, particle size, …) is unknown. The device shows a roast color distribution, but no comparison was recorded.

### 3.4 `03/06` 주변 온습도 · Ambient temperature and humidity (34 B)

| data | 절대 · abs | 형 · Type | 내용 · Content | |
|---|---|---|---|---|
| 12–15 | 17–20 | f32 | **주변 온도 °C** · **ambient temperature °C** ×1 | ✅ |
| 16–19 | 21–24 | i32 | **상대 습도 %RH** · **relative humidity %RH** ×1 | ✅ |
| 20–23 | 25–28 | f32 | 뜻 모름. 100.8 – 101.7 · unknown | ❓ |
| 24–27 | 29–32 | i32 | 뜻 모름. −50 · −50 · 0 · 50 · unknown | ❓ |

본체 화면 24.7 °C · 31 %RH 와 맞춘 기록이 있다([`environment-reference.jsonl`](captures/environment-reference.jsonl)). ✅<br>
Matched against 24.7 °C and 31 %RH on the device screen ([`environment-reference.jsonl`](captures/environment-reference.jsonl)). ✅

### 3.5 `03/02`

24 B 응답도 오지만 뜻을 모른다. 기여자가 식별 정보가 들었는지 확인하지 못해 공개 캡처에서 뺐다. ❓<br>
A 24-byte response also arrives; its meaning is unknown. The contributor could not rule out identifying data in it, so it was left out of the captures. ❓

---

## 4. 받는 순서 · Arrival order

- 4묶음 모두 `03/03` → 1.14–1.21 s 뒤 `03/05` → 0–55 ms 뒤 `03/06` 순이었다(PC 수신 시각 기준). 재계산<br>
  In all 4 sets: `03/03`, then `03/05` 1.14–1.21 s later, then `03/06` 0–55 ms later (PC receive times). recomputed
- 그래도 순서를 가정하지 않는다. 기여자 수신기는 측정 식별자로 묶고, 색도가 먼저 오면 모드를 「모름」으로 두었다가 `03/03` 이 오면 채운다. 같은 응답이 다시 오면 버리고, 더 오래된 식별자의 결과가 최신 결과를 덮지 않게 한다. ✅<br>
  Do not rely on the order anyway. The contributor's receiver groups by measurement ID; if color comes first, the mode stays "unknown" until `03/03` arrives. Repeated responses are dropped, and a result with an older ID never replaces a newer one. ✅
- 분쇄 모드의 색도는 홀빈 색도와 따로 둔다. 홀빈의 수분·밀도를 분쇄 결과로 덮지 않는다. ✅<br>
  Keep the ground-mode color separate from the whole-bean color, and do not let a ground result overwrite whole-bean moisture and density. ✅

---

## 5. 값 범위 · Value ranges

기여자 앱은 수분 0–100, 밀도 0 초과–2000, 색도 0–150, 온도 −40–85, 습도 0–100 밖의 값을 버린다. 입력 방어용 기준이며 기기의 측정 범위가 아니다.<br>
The contributor's app drops moisture outside 0–100, density outside (0, 2000], color outside 0–150, temperature outside −40–85 and humidity outside 0–100. These are input guards, not the device's measuring range.

---

## 6. 벤더 문서와 비교 · Compared with the vendor documents

Omix 문서는 없으므로, 본사의 공통 문서와 다른 기기 문서를 기준으로 비교한다.<br>
With no Omix document, the comparison is against the vendor's general and other-device documents.

| 벤더 문서 · Vendor document | Omix Plus |
|---|---|
| README: Omix 는 WIP · Omix is WIP 📄 | 프로토콜 문서 없음 · no protocol document |
| [`difluid-protocol.md`](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/difluid-protocol.md): 최대 데이터 20 B · max data 20 bytes | 색도 응답 len 120. 벤더의 Omni 문서 예시도 len 68 — 상한으로 보면 안 된다 · color response len 120; the vendor's own Omni example is len 68, so it is not a limit. 재계산 |
| README: `ff01` 암호화, `aa01` 평문 · `ff01` encrypted, `aa01` cleartext | `AA01` 없음. 결과는 `00E2`/`FF02` 에 평문으로 온다. `FF01` 이 암호화 채널인지는 모름 · no `AA01`; results arrive in cleartext on `00E2`/`FF02`; whether `FF01` is an encrypted channel is unknown. 재계산 / ❓ |
| R2·Microbalance: 빅 엔디언 · big-endian ✅ | 리틀 엔디언. 색도 바이트 `F9 9B 55 42` 를 빅 엔디언으로 읽으면 −1.0×10³⁵ · little-endian; the color bytes read big-endian give −1.0×10³⁵. 재계산 |
| [`protocolOmni.md`](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/protocolOmni.md): 서비스 `00E0` + `AA01`, func 3 · cmd 3 = Agtron 결과, 리틀 엔디언 구조체 · service `00E0` + `AA01`, func 3 cmd 3 = Agtron result, little-endian structs 📄 | 서비스·특성이 다르고 `03/03` 은 수분·밀도다. Omni 문서를 Omix 에 그대로 쓸 수 없다. 리틀 엔디언인 점만 같다 · different service and characteristic, and `03/03` carries moisture and density; the Omni document does not apply as is. Only the little-endian layout is shared. 재계산 |
| 기기 정보 func 0(SN·모델·펌웨어) — R2·Omni 문서 · device info func 0 in the R2 and Omni documents 📄 | Omix 에 보낸 적 없음 · never sent to an Omix ❓ |

---

## 7. 모르는 것 · Unknown

[확인 기록 §5](verification.md#5-미확인--not-yet-verified) 참고. · See [verification §5](verification.md#5-미확인--not-yet-verified).
