# Python 최소 예제 · Minimal Python examples

[← 처음으로](../../README.md) · [Home](../../README.en.md)

기기마다 파일 하나로 된, 바로 돌려 볼 수 있는 예제입니다. 해석 부분은 의존성이 없어 다른 언어로 옮기기 쉽습니다.<br>
One self-contained file per device, ready to run. The decoding part has no dependencies, so it is easy to port.

| 파일 · File | 기기 · Device | 하는 일 · What it does | 보내지 않는 것 · Never sends |
|---|---|---|---|
| [`r2_minimal.py`](r2_minimal.py) | R2 Extract | 찾기, 정보·설정 읽기, 단일 측정(`--single`), 결과·평균 진행 출력 · scan, read info and settings, single test, print results and average progress | 설정 쓰기·평균·영점 교정 — R2 의 설정·기준이 바뀜 · setting writes, average, calibration — they change the R2's settings and reference |
| [`microbalance_minimal.py`](microbalance_minimal.py) | Microbalance · Ti | 찾기(서비스 UUID — 없으면 이름. 저울 광고에 UUID 가 실리는지는 미확인), 저울 서비스가 없는 기기면 명령 전에 멈춤, SN·배터리 읽기, 무게 약 5 Hz, 영점(`--tare`) · scan by service UUID, falling back to the name (whether the scale advertises the UUID is unverified); stops before any command if the device has no scale service; read SN and battery, weight at ~5 Hz, tare | 타이머·설정 — 타이머 정지는 무게 송출을 멈춤 · timer, settings — timer stop freezes the weight output |

## 실행 · Run

```bash
pip install bleak          # Python 3.9 이상, bleak 0.19 이상 · Python 3.9+, bleak 0.19+

python r2_minimal.py scan
python r2_minimal.py listen --address <ADDRESS> --seconds 60 --single

python microbalance_minimal.py scan
python microbalance_minimal.py listen --address <ADDRESS> --seconds 30 --tare
```

- R2: 듣는 동안 본체 버튼으로 재도 결과가 나옵니다(평균이면 회차마다 `progress`). · Results from the R2's own button show up too (a `progress` event per average round).
- R2 는 연결돼 있는 동안 광고하지 않아, 휴대폰 앱에 연결돼 있으면 찾지 못할 것입니다. 저울은 확인하지 못했습니다. 찾지 못하면 앱 연결부터 끊으세요. · The R2 does not advertise while connected, so one connected to the phone app presumably cannot be found; we have not checked the scale. If a device does not show up, disconnect it from the app first.
- 예제 BLE 부분은 bleak 3.0 의 API 와 맞춰 확인했습니다. 시험은 실제 프레임으로 해석부를 확인합니다. · The BLE part was checked against the bleak 3.0 API; the tests check the decoder with real frames.

R2 출력 예 · R2 sample output (단일 측정 · single test, [캡처 로그 · capture log 5](../../r2/captures/README.md)):

```
-> df df 03 00 00 c1   (single test)
  <- df df 03 00 03 00 0b 00 cf   {'kind': 'status', 'mode': 'single', 'status': 11, 'text': 'test start'}
  <- df df 03 00 03 00 00 00 c4   {'kind': 'status', 'mode': 'single', 'status': 0, 'text': 'test finished'}
  <- df df 03 00 06 01 00 bb 00 b3 00 36   {'kind': 'temperature', 'mode': 'single', 'unit': 0, 'prism_raw': 187, 'sample_raw': 179}
  <- df df 03 00 07 02 03 2b 00 02 0e 55 5d   {'kind': 'reading', 'mode': 'single', 'tds': 8.11, 'ri': 1.34741}
  ** {'kind': 'result', 'mode': 'single', 'tds': 8.11, 'ri': 1.34741, 'prism_c': 18.7, 'sample_c': 17.9}
```

## 시험 · Tests

```bash
python -m pytest test_r2_minimal.py test_microbalance_minimal.py
# 또는 · or: python test_r2_minimal.py && python test_microbalance_minimal.py
```

[`test_r2_minimal.py`](test_r2_minimal.py) · [`test_microbalance_minimal.py`](test_microbalance_minimal.py) — 실제 기기에서 캡처한 프레임으로 해석부를 확인합니다(bleak 불필요). 시험용으로 만든 프레임에는 「synthetic」 표시를 달았습니다.<br>
They check the decoders against frames captured from real devices (no bleak needed). Frames made up for a test are marked "synthetic".

## 구조 · Structure

| 이름 · Name | 하는 일 · Role |
|---|---|
| `build_frame()` | 명령 프레임 만들기(체크섬 포함) · build a command frame with checksum |
| `FrameBuffer` · `split_frames()` | notify 바이트 → 완전한 프레임(한 notify 에 여러 개·쪼개짐·체크섬 오류 재동기) · notification bytes → complete frames |
| `decode()` | 프레임 하나 → dict · one frame → dict |
| `ResultCollector` (R2) | 해석된 프레임 → 최종 결과(단일·평균·교정)와 평균 진행 · decoded frames → final results and average progress |
| `join_serial()` (Microbalance) | SN 조각 3개 합치기 — SN 은 기기를 식별하므로 출력하지 않음 · join the 3 SN chunks; not printed, it identifies the device |
| `scan()` · `listen()` | bleak 로 찾기·연결 · discovery and connection with bleak |
