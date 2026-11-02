# 캡처 로그 · Capture logs

[← Omix Plus](../README.md) · [English](../README.en.md)

이승진(180커피로스터스)의 수신기 로그에서 뽑은 Omix Plus notify 프레임이다(Windows, WinRT BLE, bleak). 프레임 바이트는 수정하지 않았다.<br>
Omix Plus notification frames taken from the receiver logs of 이승진(180커피로스터스) (Windows, WinRT BLE, bleak). Frame bytes are unchanged.

## 목록 · Files

| 파일 · File | 내용 · What it shows | MTU |
|---|---|---|
| [whole-normal.jsonl](whole-normal.jsonl) | 홀빈 정상 측정. 색도 53.4 · 수분 1.2 % · 밀도 387.3 · whole bean, normal | 517 |
| [environment-reference.jsonl](environment-reference.jsonl) | 홀빈. 주변 24.7 °C · 31 %RH — 기여자 기록상 본체 화면과 일치 · whole bean; ambient matches the screen per the contributor's records | 517 |
| [ground.jsonl](ground.jsonl) | 분쇄 모드. 색도만 유효 · ground mode; only color valid | 517 |
| [not-available.jsonl](not-available.jsonl) | 홀빈, 수분 음수·밀도 0(값 없음) · whole bean, negative moisture and zero density (no value) | 517 |
| [mtu23-truncated.jsonl](mtu23-truncated.jsonl) | MTU 23 에서 20 B 로 잘린 notify 3개 · three notifications cut to 20 B | 23 |
| [gatt-discovery.json](gatt-discovery.json) | 서비스·특성·속성 탐색 결과 · service, characteristic and property discovery | — |

해석 값은 [확인 기록 §3](../verification.md#3-캡처-해석-값--decoded-capture-values)에 있다. · Decoded values: [verification §3](../verification.md#3-캡처-해석-값--decoded-capture-values).

## 읽는 법 · How to read

한 줄이 notify 하나다. · One line per notification.

| 필드 · Field | 뜻 · Meaning |
|---|---|
| `hex` | 받은 바이트 그대로 · the bytes as received |
| `at` | PC 수신 시각(UTC) · PC receive time (UTC) |
| `characteristic` | 받은 특성. 모두 `FF02` · characteristic; always `FF02` |
| `bytes` | 받은 길이 · received length |
| `count` | 수신기가 그 연결에서 센 notify 순번 · notification number counted by the receiver for that connection |
| `mtu` | 그때 MTU · MTU at the time |
| `type` · `direction` | 모두 `notification` · `RX` · always `notification`, `RX` |
| `t_rel_rx_s` | 파일 첫 줄 기준 초. 송신 기준이 아니다(송신이 없었다) · seconds from the first line of the file; not from a write (nothing was sent) |

`direction`·`t_rel_rx_s` 두 필드만 기여자가 추가했다. · Only `direction` and `t_rel_rx_s` were added by the contributor.

## 뺀 것 · What was left out

기여자가 공개 전에 뺐다. · Removed by the contributor before sharing.

- 기기 BLE 주소, 광고 이름 뒤 기기 번호, PC 경로, 배치 이름, 계정·키 · device BLE address, unit number after the name, PC paths, batch names, accounts and keys
- `03/02` 응답 전부(뜻을 모르고 식별 정보 여부를 확인하지 못함) · every `03/02` response (meaning unknown, identifying data not ruled out)
- 측정 결과가 아닌 이벤트 줄 · event lines that are not measurement results

프레임 안의 측정 시각·카운터(data0–11)는 해석 확인을 위해 남겼다. 시험용으로 바꾼 프레임은 이 폴더에 없다.<br>
The measurement time and counter inside the frames (data0–11) were kept so the decoding can be checked. No altered test frames are in this folder.
