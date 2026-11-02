# R2 Extract — BLE 연동

**한국어** · [English](README.en.md) · [← 가이드 처음으로](../README.md)

DiFluid **R2 Extract** 굴절계(커피 TDS 측정기)를 블루투스(BLE)로 내 앱·기기에 붙이는 방법입니다. DiFluid 가 공개한 프로토콜을 실제 기기 3대의 캡처로 확인하고, 문서와 다른 점과 아직 모르는 점을 함께 정리했습니다.

제품 정보·구매: [difluid.kr/R2Extract](https://www.difluid.kr/R2Extract) · 벤더 문서: [protocolR2.md](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/protocolR2.md) (v1.0.0)

## 한눈에

| 항목 | 값 | 확인 |
|---|---|---|
| 광고 이름 | `DiFluid R2 NNNNNN` (뒤 6자리는 기기마다 다름) | ✅ |
| 서비스 | `0x00FF` (`000000ff-0000-1000-8000-00805f9b34fb`) | ✅ |
| 특성 | `0xAA01` (`0000aa01-0000-1000-8000-00805f9b34fb`) — 명령 쓰기와 응답 notify 모두 | ✅ |
| 쓰기 방식 | 응답 있는 쓰기(write-without-response 속성 없음) | ✅ |
| 페어링·본딩 | 필요 없음 | ✅ |
| 프레임 | `DF DF func cmd len data… sum` — `sum` = 앞 바이트 합의 하위 8비트 | ✅ |
| 단일 측정 | `DF DF 03 00 00 C1` | ✅ |
| 결과 | TDS % = **부호 있는** 16비트 ÷ 100, 굴절률 = 32비트 ÷ 100000 | ✅ |
| 본체 버튼 측정 | 연결된 기기로 같은 바이트가 온다 | ✅ |
| 연결 시 지난 결과 | 이미 받은 결과는 재연결 때 다시 오지 않음(2회 관찰) | ✅ |
| 동시 연결 | 연결 중엔 광고하지 않음(관찰) → 한 번에 한 기기로 봄(다른 기기로는 미시험) | ✅ / ❓ |
| 자동 꺼짐 설정 | 공개 프로토콜에 명령 없음 | ❓ |

✅ 실측 확인 · 📄 벤더 문서에만 있음 · ❓ 미확인

## 문서

| 문서 | 내용 |
|---|---|
| [프로토콜](protocol.md) | 연결, 프레임, 명령, 측정 응답(단일·평균·영점), 오류, 설정, 벤더 문서와 다른 점 |
| [실측 확인 기록](verification.md) | 무엇을 어떻게 확인했나, 타이밍, 미확인 목록 |
| [구현 팁](implementation-tips.md) | 실제로 붙이며 만난 함정과 규칙 |
| [캡처 로그](captures/README.md) | 원시 바이트 로그 9개(기기 식별 정보 가림) |
| [Python 최소 예제](../examples/python/README.md) | 스캔·정보 읽기·단일 측정·청취 |

세부 문서는 한 문서에 한국어와 영어를 함께 적었습니다.

## 빠른 시작

저장소 최상위에서:

```bash
pip install bleak          # Python 3.9 이상
python examples/python/r2_minimal.py scan
python examples/python/r2_minimal.py listen --address <R2 주소> --seconds 60 --single
```

> [!TIP]
> R2 는 연결돼 있는 동안 광고하지 않으므로, 휴대폰 앱(DiFluid Café)에 연결돼 있으면 찾을 수 없을 것입니다. 앱 쪽 연결을 먼저 끊으세요.

## 시험 환경

- 기기: R2 Extract 3대 — 모델 문자열 `DFT-R102`, 펌웨어 `V230`
- 호스트: Linux(BlueZ) + Python [bleak](https://github.com/hbldh/bleak)
- 기간: 2026-11-01 ~ 2026-11-02
- 다른 펌웨어·모델에서는 다를 수 있습니다.
