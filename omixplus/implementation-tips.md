# 구현 팁 · Implementation tips

[← Omix Plus](README.md) · [English](README.en.md) · [프로토콜 · Protocol](protocol.md)

180커피로스터스 수신기의 규칙을 정리했다. 근거는 [프로토콜](protocol.md)과 [확인 기록](verification.md).<br>
Rules taken from the receiver built by 이승진 (180 Coffee Roasters). See the [protocol](protocol.md) and [verification](verification.md) pages for the evidence.

## 1. 쓰지 않는다 · Do not write

- 명령이 하나도 확인되지 않았다. `FF01`·`FF02` 에 write 속성이 있어도 보내지 않는다. 측정은 사용자가 본체에서 한다.<br>
  No command has been confirmed. Even though `FF01` and `FF02` allow writes, send nothing; the user measures on the device.
- R2·저울용 명령(`DF DF 03 00 00 C1` 등)을 Omix 에 그대로 보내지 않는다. 같은 바이트가 기기마다 다른 동작이다.<br>
  Do not send R2 or scale commands (such as `DF DF 03 00 00 C1`) to an Omix; the same bytes do different things on different devices.

## 2. MTU 를 먼저 확인한다 · Check the MTU first

- 색도 응답이 126 B 다. 기여자 수신기는 MTU 129 이상을 준비 조건으로 쓴다. MTU 23 에서는 20 B 로 잘려 왔고, 잘린 프레임은 되살릴 수 없다. 129 미만의 다른 값에서 어떻게 오는지는 모른다.<br>
  The color response is 126 B. The contributor's receiver waits for an MTU of 129 or more. At MTU 23 it arrived cut to 20 B, and a cut frame cannot be recovered. Behavior at other MTUs below 129 is unknown.
- Windows 에서는 연결 직후 MTU 가 늦게 올라갈 수 있다. MTU 를 확인한 뒤 측정하도록 안내한다. 잘린 프레임(헤더의 len + 6 보다 짧은 notify)을 받으면 다시 연결한 뒤 측정하게 한다.<br>
  On Windows the MTU can go up shortly after connecting. Tell the user to measure only after the MTU is confirmed. If a cut frame arrives (a notification shorter than len + 6 from its header), reconnect and measure again.
- Linux(BlueZ)·macOS 에서는 확인하지 않았다.<br>
  Not checked on Linux (BlueZ) or macOS.

## 3. 측정 하나로 묶는다 · Group one measurement

- 응답 3종을 data0–11(측정 식별자)로 묶는다. 순서를 가정하지 않는다.<br>
  Group the three responses by data0–11 (the measurement ID). Do not assume an order.
- 같은 응답이 다시 오면 버린다. 더 오래된 식별자의 결과가 최신 결과를 덮지 않게 한다(식별자의 u64 → u32 순으로 비교).<br>
  Drop repeated responses. Never let a result with an older ID replace a newer one (compare the u64, then the u32).
- 다른 식별자끼리는 합치지 않는다.<br>
  Never merge responses with different IDs.

## 4. 값 없음 · Missing values

- 수분이 음수면 「값 없음」이다. 0 으로 바꾸지 않는다. 밀도는 0 이 「값 없음」이다.<br>
  A negative moisture means "no value"; do not turn it into 0. A density of 0 means "no value".
- data16–19 는 뜻을 모른다. 값을 받을지 말지 정하는 데 쓰지 않는다.<br>
  data16–19 is undecoded; do not use it to decide whether to accept a value.
- 화면 표시는 소수 한 자리(색도·수분·밀도·온도)로 했다.<br>
  Values were shown to one decimal place (color, moisture, density, temperature).

## 5. 분쇄 모드 · Ground mode

- 시료 모드가 `01 05`(분쇄)이면 색도를 분쇄 색도로 따로 저장한다. 홀빈의 수분·밀도를 덮지 않는다.<br>
  With sample mode `01 05` (ground), store the color as a ground color. Do not overwrite the whole-bean moisture and density.
- 모드를 모르는 값(`01 04`·`01 05` 외)이 오면 수분·밀도를 쓰지 않는다.<br>
  For a mode other than `01 04` or `01 05`, do not use moisture or density.

## 6. Windows 파일 쓰기 · File writes on Windows

- 결과를 파일로 넘기는 경우, 다른 프로그램이 그 파일을 잠깐 읽고 있으면 교체가 실패할 수 있다. 임시 파일에 쓰고 교체를 짧게 몇 번 다시 시도한다. 실패해도 BLE 연결은 끊지 않는다.<br>
  If results are handed over in a file, replacing it can fail while another program briefly has it open. Write to a temporary file and retry the replace a few times; do not drop the BLE connection on failure.
