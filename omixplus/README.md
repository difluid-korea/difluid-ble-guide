# Omix Plus — BLE 연동

**한국어** · [English](README.en.md) · [← 가이드 처음으로](../README.md)

DiFluid **Omix Plus** 원두 분석기의 측정 결과(색도·수분·밀도·주변 온습도)를 BLE 로 받는 방법. 180커피로스터스가 업무용 수신기를 만들며 남긴 자료를 받아 정리했다.

- 자료 제공: 이승진 로스터 — [180커피로스터스](https://180coffee.com)
- 제품: [difluid.kr/OmixPlus](https://www.difluid.kr/OmixPlus)
- 벤더 문서: 없음. [difluid-sdk-demo](https://github.com/DiFluid/difluid-sdk-demo) README 에 Omix 는 「WIP」로만 있다(2026-11-02 확인).

> [!IMPORTANT]
> 받기 전용이다. 앱은 측정을 시작하지 않고, 본체에서 측정하면 결과가 notify 로 온다. 측정 시작·설정·교정 명령은 확인된 것이 없으므로 Omix Plus 에 쓰기(write)를 보내지 않는다.

## 요약

| 항목 | 값 | 확인 |
|---|---|---|
| 광고 이름 | `Omix Plus` + 기기 번호(가림). 1대에서 관찰 | ✅ |
| 측정 서비스 | `0x00E2` (`000000e2-0000-1000-8000-00805f9b34fb`) | ✅ 재계산 |
| 측정 특성 | `0xFF02` (`0000ff02-0000-1000-8000-00805f9b34fb`), notify | ✅ 재계산 |
| 그 밖의 GATT | `0x00E1` / `0xFF01`(notify·write), 용도 모름. 탐색 기록에 R2·저울의 `AA01` 은 없음 | 재계산 · ❓ |
| 페어링 | 수신 코드는 페어링을 호출하지 않음. 새 PC 에서 필요 없는지는 미확인 | ✅ · ❓ |
| MTU | 기여자 수신기는 MTU 129 이상을 준비 조건으로 씀(126 B 프레임 + 3). 관찰은 MTU 23(20 B 로 잘림)과 517(완전) 두 경우. 제조사 최소 요구는 미확인 | ✅ 재계산 · ❓ |
| 프레임 | `DF DF func cmd len data… sum`. R2·저울과 같음 | 재계산 |
| 바이트 순서 | 리틀 엔디언. R2·저울은 빅 엔디언 | 재계산 |
| 결과 응답 | `03/03` 수분·밀도(50 B), `03/05` 색도(126 B), `03/06` 주변 온습도(34 B) | ✅ 재계산 |
| 측정 식별자 | 세 응답의 data0–11 이 같음. Unix 시각(초) + 카운터로 보임 | 재계산 · ❓ |
| 시료 모드 | `01 04` 홀빈, `01 05` 분쇄 | ✅ |
| 값 없음 | 수분 음수, 밀도 0 | ✅ |
| 명령·오류 코드·설정 | 확인된 것 없음 | ❓ |

✅ 기여자가 실기(1대)로 확인 · 재계산: 공개 캡처 바이트로 DiFluid Korea 가 다시 계산해 맞춤 · 📄 벤더 문서에만 있음 · ❓ 미확인

DiFluid Korea 는 Omix Plus 실기로 재현하지 않았다.

## 문서

| 문서 | 내용 |
|---|---|
| [프로토콜](protocol.md) | GATT, 프레임, 응답 3종의 바이트 배치, 수신 순서, 벤더 문서와 다른 점 |
| [확인 기록](verification.md) | 기여자 시험 환경, 확인 항목, 캡처 해석 값, 타이밍, 미확인 목록 |
| [구현 팁](implementation-tips.md) | MTU, 측정 묶기, 값 없음, 분쇄 모드 |
| [캡처 로그](captures/README.md) | notify 원시 프레임 5묶음, GATT 탐색 결과 |
| [Python 최소 예제](../examples/python/README.md) | 찾기, FF02 구독, 결과 출력. 쓰기 없음 |

세부 문서는 한국어와 영어를 한 문서에 함께 적었다.

## 빠른 시작

저장소 최상위에서:

```bash
pip install bleak          # Python 3.9 이상
python examples/python/omixplus_minimal.py scan
python examples/python/omixplus_minimal.py listen --address <기기 주소> --seconds 120
```

연결 후 본체에서 측정하면 결과가 출력된다. 예제의 BLE 부분은 Omix Plus 로 실행해 보지 않았다. 해석부만 기여자의 캡처로 시험했다.

## 시험 환경(기여자)

- 기기: Omix Plus 1대. 모델 문자열·펌웨어 버전은 확보하지 못함(탐색 기록에 표준 기기 정보 서비스 `0x180A` 가 없음. 제조사 전용 조회 방법은 미확인)
- 호스트: Windows(WinRT BLE), Python [bleak](https://github.com/hbldh/bleak) 3.0.2
- 캡처 기간: 2026-10-21 ~ 11-02(KST)

다른 기기·펌웨어·OS 에서는 다를 수 있다.

## 출처

프로토콜 정리·캡처·실기 확인은 이승진(180커피로스터스)의 자료다. DiFluid Korea 는 캡처를 다시 계산해 확인하고 한영으로 정리했다. 예제 코드는 DiFluid Korea 가 새로 작성했다.
