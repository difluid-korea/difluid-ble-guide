# 구현 팁 · Implementation tips

[← R2 Extract](README.md) · [English](README.en.md) · [프로토콜 · Protocol](protocol.md)

R2 를 실제 제품에 붙이며 만난 함정과, 그 뒤 정한 규칙입니다. 규칙은 우리 판단이며 DiFluid 의 권고가 아닙니다.<br>
Pitfalls we met while integrating the R2 into a product, and the rules we adopted. The rules are our own judgment, not DiFluid recommendations.

## 1. 저울 코드를 그대로 쓰지 마세요 · Do not reuse scale code as-is

DiFluid 저울(Microbalance)도 같은 프레임 형식을 씁니다. 그런데 **저울에서 무게를 묻는 `DF DF 03 00 00 C1` 은 R2 에서 「단일 측정」** 입니다. 저울 코드를 그대로 R2 에 붙이면 단일 측정 명령을 무게를 묻는 주기(예: 초당 5번)로 계속 보내게 됩니다. 측정 중에 같은 명령을 다시 받은 R2 가 어떻게 하는지는 시험하지 않았습니다. 프레임 분리·체크섬은 함께 써도 되지만, 명령은 기기별로 나누세요.<br>
DiFluid scales (Microbalance) use the same frame format, but **the scale's weight request `DF DF 03 00 00 C1` is "single test" on the R2.** Pointing scale code at an R2 keeps sending the single-test command at the weight-polling rate (e.g. 5 times per second); we did not test how the R2 reacts to repeated commands during a test. Share the frame splitter and checksum, but keep commands per device.

## 2. 기기 고르기 · Picking the device

- 이름 앞부분 `DiFluid R2` 로 고르세요. 「이름에 r2 포함」은 너무 넓고, 광고 UUID `00FF` 는 다른 기기도 흔히 씁니다.<br>
  Match the name prefix `DiFluid R2`. "Name contains r2" is too broad, and the advertised UUID `00FF` is common on other devices.
- 매장에는 R2 가 여러 대 있을 수 있습니다. 첫 시험에서 주변 R2 3대가 잡혔고, 처음 찾은 기기에 붙었더니 가장 먼 기기였습니다. **신호 센 순서로 보여 주고 이름 끝 번호로 고르게** 하세요.<br>
  A shop may have several R2s. In our first test three were in range, and connecting to the first one found picked the farthest. **List them by signal strength and let the user pick by the trailing number.**
- 한 번 고른 기기는 주소로 기억해 두고 다음부터 그 주소로만 붙으세요.<br>
  Remember the chosen unit by address and reconnect only to that address.

## 3. 프레임 분리 · Frame splitting

- 한 notify 에 프레임이 여러 개 올 수 있습니다([프로토콜 §2](protocol.md)). 버퍼에 이어 붙이고 `DF DF` 를 찾아 길이만큼 잘라 내세요.<br>
  Several frames can share one notification. Append to a buffer, find `DF DF`, and cut by the length byte.
- 체크섬이 틀리거나 길이 바이트가 상한(20)을 넘으면 **1바이트 밀어** 다음 `DF DF` 를 찾으세요. 다만 길이 바이트가 상한 안의 값으로 깨지면, 그 길이만큼 바이트가 모일 때까지(다음 notify 까지) 뒤의 정상 프레임이 늦게 나옵니다. 체크섬이 우연히 맞으면(약 1/256) 정상 프레임이 가짜 프레임에 묻혀 사라질 수도 있습니다. 실제 캡처 로그 9개에는 이런 바이트가 한 번도 없었습니다.<br>
  On a bad checksum or a length byte above the limit (20), **skip one byte** and look for the next `DF DF`. A length byte corrupted to a value within the limit can still hold back the good frame behind it until enough bytes arrive (the next notification), and if the checksum happens to match (about 1 in 256) the good frame is lost inside a bogus one. None of our nine capture logs contained such bytes.

## 4. 결과 채택 규칙 · When to accept a result

- **단일**: 상태 0(측정 끝) **뒤에 온** 패키지 2 만 결과로 받으세요.<br>
  **Single**: accept package 2 only when it comes **after** status 0 (test finished).
- **평균**: 상태 6(평균 끝)이 왔을 때, 직전 회차의 패키지 4 가 **현재 = 전체** 이면 그 회차 패키지 3 의 2 B 평균을 받으세요. 회차가 모자라거나 끝 없이 끊기면 버리세요. 패키지 3 의 4 B 칸은 쓰지 마세요.<br>
  **Average**: when status 6 arrives and the previous round's package 4 shows **current = total**, take that round's 2-byte average from package 3. Drop it if rounds are missing or the link drops before the end. Ignore the 4-byte field in package 3.
- **시작을 놓쳐도** 처리하세요. 측정 도중에 붙으면 단일은 「측정 시작」 없이 「측정 끝」부터, 평균은 「평균 시작」 없이 그 뒤 회차부터 옵니다(평균은 실측 3회 모두 1회차부터). 패키지 3 은 R2 가 계산한 누적 평균이므로, 회차를 놓쳐도 마지막 회차의 평균이 전체 평균일 것입니다(회차를 놓친 경우는 아직 보지 못함).<br>
  **Handle a missed start.** If you connect mid-test, a single test arrives from "finished" without "start", and an average without "average start" (observed three times, each from round 1). Package 3 is the R2's running average, so the last round should still carry the full average even if rounds were missed (not yet observed).
- 진행 중이 아닐 때 온 패키지 1~4 는 버리세요. 순서가 어긋나면 그 측정을 버리세요.<br>
  Drop packages 1–4 that arrive with no test in progress, and drop the test if the order is broken.

## 5. 값 해석 · Interpreting values

- **농도는 부호 있는 16비트**입니다. 부호 없이 읽으면 물에서 654.25 % 같은 값이 나옵니다.<br>
  **Concentration is signed 16-bit.** Read unsigned, water gives values like 654.25 %.
- 온도 단위는 패키지 1 의 data5 로 함께 옵니다. 기기의 단위 설정을 ℃ 로 **바꾸지 말고** 받아서 변환하세요. 평균의 패키지 4 에는 단위 바이트가 없으니 같은 회차 패키지 1 의 단위를 쓰세요.<br>
  The temperature unit comes in package 1, data5. **Do not change** the device's unit setting — convert on your side. Package 4 of an average has no unit byte; use the unit from the same round's package 1.
- 물이 0 보다 뚜렷이 낮게(음수로) 읽히면 영점이 어긋난 것입니다. 한 기기는 물을 −1.11 ~ −1.15 %(굴절률 1.3310)로 읽었습니다. 20 ℃ 물의 굴절률은 약 1.3330 입니다. 이런 기기는 커피도 비슷한 만큼 낮게 읽을 것으로 보이지만, 그 기기로 커피를 재 보지는 않았습니다.<br>
  A water reading clearly below zero means the zero is off. One unit read water as −1.11 to −1.15 % (RI 1.3310); water at 20 °C is about 1.3330. Such a unit probably reads coffee low by a similar amount, but we did not measure coffee on it.

## 6. 기기 설정을 몰래 바꾸지 마세요 · Never change device settings silently

- 바리스타가 본체에서 맞춘 설정(온도 단위·측정 횟수·밝기·자동 측정)을 앱이 알리지 않고 바꾸면 안 됩니다. 설정 쓰기는 사용자가 화면에서 직접 바꿀 때만 보내세요.<br>
  The barista set the unit, number of tests, brightness and auto test on the device; an app must not change them without telling them. Send Set only when the user changes a value on screen.
- 쓴 뒤에는 돌아온 값이 보낸 값과 같을 때만 「적용됨」으로 표시하세요.<br>
  After a Set, show "applied" only if the echoed value matches what you sent.
- **평균 명령은 「측정 횟수」를 바꿉니다(벤더).** 사용자 설정을 지키려면 방금 읽은 값과 같은 N 으로만 보내야 하지만, 그때 설정이 그대로인지는 아직 확인하지 않았습니다. 확인 전에는 단일 명령만 쓰는 것이 안전합니다. 본체 버튼 평균은 명령 없이도 받을 수 있습니다.<br>
  **The average command changes "Number of tests" (vendor).** Sending the same N you just read should preserve it, but we have not verified that. Until verified, the single command is the safe choice; button-started averages arrive without any command.

## 7. 영점 교정 · Calibration

- 교정은 R2 의 기준을 바꿉니다. 화면에서 단계를 밟게 하세요: 프리즘을 닦고 **증류수**를 올리기 → 확인 측정 → 값이 물로 보일 때만 교정 버튼 켜기 → 교정 → 다시 측정.<br>
  Calibration changes the R2's reference. Walk the user through steps: clean the prism, add **distilled water** → check measurement → enable the button only if it reads like water → calibrate → measure again.
- 우리는 확인 측정이 **|TDS| ≤ 1.5 %** 일 때만 교정을 허용합니다. 영점이 어긋난 기기의 물(−1.1 %)은 받고 에스프레소(5 % 이상)는 막는 값입니다.<br>
  We allow calibration only when the check reads **|TDS| ≤ 1.5 %** — this accepts water on an offset unit (−1.1 %) and rejects espresso (5 % and up).
- 교정 중 다른 명령을 보내지 마세요. 교정이 끝날 때까지 연결을 유지하세요.<br>
  Do not send other commands during calibration, and keep the link until it finishes.

## 8. 연결 정책 · Connection policy

- **R2 는 연결돼 있는 동안 광고하지 않았습니다.** 그래서 앱이 늘 붙어 있으면 휴대폰 앱(DiFluid Café)이나 다른 기기가 R2 를 찾지 못할 것입니다(다른 central 로 직접 시험하지는 않음). 필요할 때만 붙고(측정 화면이 열린 동안 등), 「자동 연결」을 끌 수 있게 하세요.<br>
  **The R2 did not advertise while connected.** So if your app stays connected, the phone app (DiFluid Café) or another machine presumably cannot find it (not tested directly with another central). Connect only when needed (e.g. while a measurement screen is open), and let users turn auto-connect off.
- R2 는 배터리 기기라 대부분 꺼져 있습니다. 늘 스캔하면 다른 BLE 기기(저울 등)와 라디오를 다툽니다. 스캔도 필요할 때만 하세요.<br>
  The R2 runs on batteries and is usually off. Scanning all the time competes for the radio with other BLE devices such as scales. Scan only when needed.
- 이미 받은 결과는 다시 연결해도 다시 오지 않았습니다(2회). 연결이 없는 동안 끝난 측정이 연결할 때 오는지는 확인하지 않았습니다. 그런 결과가 온다면 「측정 시작」 없이 온 「측정 끝」과 구별되지 않으니, 연결 직후에 받은 결과를 쓸지 정해 두세요. 놓쳤으면 다시 재게 안내하세요.<br>
  Results already received were not re-sent on reconnect (twice). Whether a test that finished while disconnected arrives on connect was not checked; if it does, it looks the same as a "finished" frame without "start", so decide whether to trust a result that arrives right after connecting. If a result was missed, ask the user to measure again.
- 측정·교정 중에는 끊지 말고 결과까지 기다리세요. 결과 대기 상한은 마지막 프레임 뒤 10 s 를 권합니다.<br>
  Do not disconnect during a test or calibration; wait for the result. We suggest a timeout of 10 s after the last frame.
- **앱이 스스로 끊는 중에 들어온 프레임으로 측정을 시작하지 마세요.** 끊기를 기다리는 1 s 사이에 평균 회차가 들어와 「측정 중」이 됐다가 10 s 뒤 「응답 없음」을 낸 일이 있습니다. 끊기로 정한 연결의 프레임은 버리세요.<br>
  **Do not start tracking a test from frames that arrive while your app is disconnecting.** An average round once arrived during the ~1 s disconnect wait, flipped the state to "measuring", and produced a false "no response" 10 s later. Drop frames from a link you have decided to close.

## 9. Linux(BlueZ)·bleak 에서 · On Linux (BlueZ) with bleak

- 끊을 때 `EOFError`(dbus_fast)나 BlueZ 의 `No matching connection for device` 가 가끔 납니다. 캡처는 끝까지 됐습니다. 끊기 예외는 잡아서 무시하세요.<br>
  Disconnecting sometimes raises `EOFError` (dbus_fast) or BlueZ logs `No matching connection for device`; the capture was complete anyway. Catch and ignore disconnect exceptions.
- 주소로 바로 붙으려면 BlueZ 캐시에 기기가 있어야 합니다. 먼저 `BleakScanner.find_device_by_address()` 로 찾으세요.<br>
  To connect by address, BlueZ needs the device in its cache. Look it up with `BleakScanner.find_device_by_address()` first.
- 캡처·진단 도구는 **한 번에 하나만** 돌리세요. 앞 도구가 붙어 있는 동안 띄운 도구는 R2 를 찾지 못합니다(연결 중엔 광고하지 않음).<br>
  Run **one** capture/diagnostic tool at a time. A second tool started while the first is connected cannot find the R2 (no advertising while connected).
