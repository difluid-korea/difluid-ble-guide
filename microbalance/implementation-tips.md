# 구현 팁 · Implementation tips

[← Microbalance](README.md) · [English](README.en.md) · [프로토콜 · Protocol](protocol.md)

저울을 실제 제품에 붙이며 겪은 함정과, 그 뒤 정한 규칙입니다. 규칙은 우리 판단이며 DiFluid 의 권고가 아닙니다.<br>
Pitfalls we hit while integrating the scale into a product, and the rules we adopted. The rules are our own judgment, not DiFluid recommendations.

## 1. 기기 고르기 · Picking the device

- **서비스 UUID(`00EE`·`00DD`)로 먼저 고르세요**(벤더 권고). 다만 저울이 광고에 UUID 를 싣는지는 캡처하지 못했으니, UUID 로 아무것도 안 잡히면 이름(Ti 는 `Mb Ti` — 실측)으로 보조하게 만드세요. 이름 앞부분 `DiFluid` 로 고르면 같은 회사 굴절계 R2(`DiFluid R2 NNNNNN`)가 잡힙니다. 반대로 `MB`·`Micro` 처럼 짧은 앞부분은 이름이 그렇게 시작하는 키보드·마우스 같은 남의 기기까지 저울로 잡게 됩니다(추론 — 실제로 잡힌 적은 없음).<br>
  **Match on the service UUID (`00EE`, `00DD`) first** (vendor advice). We never captured whether the scale advertises it, so if the UUID finds nothing, fall back to the name (Ti: `Mb Ti`, measured). A `DiFluid` name prefix also catches the R2 refractometer (`DiFluid R2 NNNNNN`); short prefixes like `MB` or `Micro` would also catch any keyboard or mouse whose name starts that way (inference — not observed).
- R2 를 저울로 착각하면 위험합니다. **저울에서 무게를 묻는 `DF DF 03 00 00 C1` 이 R2 에서는 「측정 1회」 명령**이라, 5 Hz 폴링이 R2 에 측정 명령을 계속 보내게 됩니다(측정 중에 같은 명령을 다시 받은 R2 가 어떻게 하는지는 시험하지 않았습니다).<br>
  Mistaking an R2 for a scale is harmful: **the scale's weight request `DF DF 03 00 00 C1` is a "run one test" command on the R2**, so 5 Hz polling keeps sending test commands to the R2 (we did not test how the R2 reacts to repeated commands during a test).
- 고른 기기는 주소로 기억하되, **펌웨어를 올리면 주소가 바뀔 수 있습니다.** 업데이트 뒤 연결이 안 되면 다시 찾게 하세요.<br>
  Remember the chosen unit by address, but **a firmware update can change the address.** If it stops connecting after an update, rescan.

## 2. 연결과 쓰기 · Connecting and writing

- 통신은 **`AA01`** 로 합니다. 벤더 문서의 「FF01 로 통신하라」는 틀렸습니다. `FF01` 로 대신 보내는 대비책은 동작하지 않을 것입니다(암호화 채널).<br>
  Talk over **`AA01`**. The vendor's "use FF01" is wrong, and falling back to `FF01` will not work (it is the encrypted channel).
- **응답 있는 쓰기**로 보내세요. · Write **with response**.
- 구펌웨어 저울은 아무 명령에도 응답하지 않았습니다. 응답이 없으면 펌웨어부터 확인하게 안내하세요.<br>
  A scale on old firmware answered nothing. If there is no response at all, have the user check the firmware first.

## 3. 프레임 분리 · Frame splitting

- **notify 하나 = 프레임 하나로 가정하지 마세요.** SN 조각 둘이 notify 하나로 붙어 왔고, 전체를 한 프레임으로 검사했더니 체크섬이 틀려 둘 다 버려졌습니다(그동안 SN 이 비어 보였습니다). 길이 바이트로 잘라 차례로 처리하세요.<br>
  **Do not assume one notification = one frame.** Two SN chunks arrived in one notification; checking the whole buffer as one frame failed the checksum and dropped both (the SN showed as empty). Split by the length byte.
- 체크섬이 틀리면 1바이트 밀어 다음 `DF DF` 를 찾으세요. · On a bad checksum, skip one byte and look for the next `DF DF`.

## 4. 명령 바이트는 전부 맞춰 시험하세요 · Test every byte of a command

- **영점에 데이터 바이트 `01` 을 빠뜨린 `DF DF 03 02 00 C3` 은 체크섬이 맞아 쓰기까지 성공하지만, 저울이 조용히 무시합니다.** 우리는 이것 때문에 3주 동안 영점이 동작하지 않았습니다. 시험이 앞 몇 바이트와 체크섬만 보고 통과시켰기 때문입니다.<br>
  **`DF DF 03 02 00 C3` — tare without the data byte `01` — passes the checksum and the write succeeds, but the scale silently ignores it.** Tare silently did nothing for three weeks for us, because our test only checked the first bytes and the checksum.
- 명령은 **전체 바이트를 고정값으로** 비교해 시험하세요. 벤더 문서에 오류 응답이 없고 잘못 만든 영점 명령도 아무 표시 없이 무시됐으므로, 명령이 먹혔는지는 무게·상태 변화로 확인해야 합니다.<br>
  Test commands **against every byte**. The vendor defines no error responses and a malformed tare was silently ignored, so confirm a command worked through weight or status changes.
- **벤더 문서의 예시를 시험 고정값으로 쓰지 마세요.** SN·모델·펌웨어 예시는 R2 문서에서 옮겨 온 값이고, 펌웨어 예시는 길이 바이트도 틀렸습니다(길이로 자르는 분리기는 그 프레임을 버립니다).<br>
  **Do not use the vendor's examples as test fixtures.** The SN, model and firmware examples were carried over from the R2 document, and the firmware example also has a wrong length byte (a length-based splitter drops it).
- 벤더 롱프레스 예시 `DF DF 03 04 01 01 C7` 은 **저울 전원을 끕니다.** · The vendor's long-press example `DF DF 03 04 01 01 C7` **turns the scale off.**

## 5. 값 해석 · Interpreting values

- **상태 응답의 배터리는 data1 입니다.** data0(상태 코드)을 배터리로 읽어서, 쉬는 저울이 모두 「5 %」로 보인 적이 있습니다.<br>
  **The battery in the status response is data1.** We once read data0 (the status code) as the battery and every idle scale showed "5 %".
- **단위 바이트(data12)를 확인하세요.** 우리 구현은 늘 ÷ 10 g 로 읽었는데, 사용자가 저울에서 단위를 oz 로 바꾸면(전원 버튼 더블클릭) 무게를 틀리게 읽게 됩니다(벤더: oz 는 ×1000). g 가 아니면 경고하거나, 단위를 g 로 정하고 단위 잠금을 거는 방법이 있습니다(우리는 시험하지 않음).<br>
  **Check the unit byte (data12).** We always read ÷ 10 g; if the user switches the scale to oz (double-click Power), the weight is misread (vendor: oz is ×1000). Warn when it is not grams, or set grams and enable the unit lock (we have not tested this).
- **유량 칸을 그대로 「현재 유량」으로 쓰지 마세요.** 타이머가 돌지 않을 때는 무게가 줄어드는 중에도 0 이었습니다. 유량은 무게 변화로 직접 계산하는 편이 안전합니다.<br>
  **Do not use the flow field as live flow.** It stayed 0 while weight was falling and the timer was off. Compute flow from the weight series.
- 무게는 부호 있게 읽기를 권합니다(영점 뒤 컵을 들면 음수가 될 수 있음 — 미캡처).<br>
  Read weight as signed (lifting a cup after tare can go negative — not captured).
- **SN 은 BLE 주소에서 나온 값이었습니다.** 로그·화면·공개 자료에 SN 을 남기면 기기 주소가 드러납니다.<br>
  **The SN was derived from the BLE address.** Logging, displaying or publishing it exposes the address.

## 6. 저울 타이머 · The scale's timer

- **타이머 정지(`DF DF 03 01 01 00 C3`)를 보내면 저울이 정지 상태로 들어가며 BLE 무게 출력이 멈췄습니다.** 그 뒤로는 컵을 치워도 무게가 그대로여서, 무게를 쓰는 기능(컵 치움 감지, 추출 뒤 무게 표시 등)이 모두 멈춘 값을 읽었습니다.<br>
  **Sending timer stop (`DF DF 03 01 01 00 C3`) put the scale in its stop state and froze the BLE weight output.** Removing the cup no longer changed the weight, so every feature that reads weight (cup-removal detection, post-shot weight) saw a frozen value.
- 타이머를 0 으로 되돌리는 명령도 없습니다. 그래서 우리는 **저울 타이머를 쓰지 않고 샷 시간을 직접 잽니다.**<br>
  There is no timer reset either, so **we time shots ourselves instead of using the scale's timer.**

## 7. 샘플레이트 · Sample rate

- 자동 송신을 쓰지 않으면 요청 한 번에 응답 한 프레임이라, **샘플레이트는 폴링 방식이 정합니다.**<br>
  Without auto-send there is one frame per request, so **your polling loop sets the sample rate.**
- 「응답 있는 쓰기 → 0.2 s 쉬기」는 쓰기 왕복(약 80 ms)이 더해져 **3.56 Hz** 에 그쳤습니다. 다음 요청 시각을 마감 기준으로 맞추자 **4.99 Hz** 가 됐습니다.<br>
  "Write with response, then sleep 0.2 s" only reached **3.56 Hz** because the write round trip (~80 ms) adds up. Scheduling each request against a deadline reached **4.99 Hz**.
- 당시 드라이버는 특성이 write-without-response 를 지원하면 응답 없는 쓰기로 바꾸게 돼 있었는데, T 의 `AA01` 속성을 기록하지 않아 4.99 Hz 가 어느 쪽 쓰기로 나왔는지는 모릅니다. 왕복(약 80 ms)이 주기(200 ms)보다 짧으니 응답 있는 쓰기로도 5 Hz 가 나와야 맞습니다(추론). M 은 write-without-response 가 없으므로 아래 예시는 `response=True` 로 씁니다.<br>
  That driver switched to write-without-response when the characteristic offered it; the Ti's `AA01` properties were not recorded, so we do not know which write type produced 4.99 Hz. Since the round trip (~80 ms) is shorter than the 200 ms period, write with response should also reach 5 Hz (inference). Unit M has no write-without-response, so the example below uses `response=True`.
- 쓰기가 한 번 오래 멈추면 밀린 마감을 따라잡으려고 쉬지 않고 연달아 보내게 됩니다. 그래서 다음 마감이 현재 시각보다 뒤처지지 않게 `max` 로 막았습니다(4.99 Hz 를 잰 코드도 이렇게 되어 있습니다).<br>
  If one write stalls, plain deadline pacing fires requests back to back to catch up. We clamp the next deadline to the current time with `max` (the code that measured 4.99 Hz does this).

```python
next_at = loop.time()
while running:
    await client.write_gatt_char(AA01, GET_SENSOR_DATA, response=True)
    next_at = max(next_at + 0.2, loop.time())   # 밀리면 따라잡지 않고 다시 맞춤 · re-anchor, no catch-up burst
    await asyncio.sleep(max(0.0, next_at - loop.time()))
```

## 8. Linux(BlueZ)·bleak 에서 · On Linux (BlueZ) with bleak

- 같은 날 펌웨어 업데이트 뒤에 BlueZ 캐시가 낡아 연결되지 않았습니다. `bluetoothctl remove <주소>` 뒤 어댑터를 리셋하자 연결됐습니다(주소 변경 때문이었는지는 확인하지 않음).<br>
  On the same day, after the firmware update, a stale BlueZ cache blocked connections; `bluetoothctl remove <address>` plus an adapter reset fixed it (we did not check whether the address change caused it).
- 연결 타임아웃으로 포기한 뒤 BlueZ 가 늦게 링크를 완성하면 낡은 연결이 남아, 이후 모든 연결·스캔이 `org.bluez.Error.InProgress` 로 실패했습니다(다른 저울까지). `bluetoothctl disconnect <주소>`(페어링을 지우는 `remove` 가 아님) 뒤 BLE 를 쓰는 우리 앱 프로세스를 다시 시작하자 풀렸습니다(BlueZ 자체를 다시 시작한 것이 아닙니다).<br>
  When BlueZ completed a link after our connect timeout had given up, the leftover connection made every later connect and scan fail with `org.bluez.Error.InProgress` (other scales too). `bluetoothctl disconnect <address>` (not `remove`, which drops the pairing) followed by restarting our own BLE app process — not BlueZ itself — cleared it.
- 연결이 끊긴 것은 bleak 의 disconnected 콜백, 쓰기 실패, 일정 시간 무게 프레임 없음 세 가지로 알아챕니다. 저울 쪽에 하트비트 요구는 없었습니다.<br>
  Detect a lost link three ways: bleak's disconnected callback, a failed write, or no weight frame for a while. The scale required no heartbeat.
