# Microbalance · Ti — BLE 연동

**한국어** · [English](README.en.md) · [← 가이드 처음으로](../README.md)

DiFluid **Microbalance**·**Microbalance Ti** 커피 저울을 블루투스(BLE)로 내 앱·기기에 붙이는 방법입니다. 실제 제품에 저울을 통합하며 두 기기로 확인한 사실과, 본사 문서의 오류·빠진 내용을 함께 정리했습니다.

제품 정보·구매: [difluid.kr/Microbalance](https://www.difluid.kr/Microbalance) · 벤더 문서: [protocolMicrobalance.md](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/protocolMicrobalance.md) (v1.0.0, 2024-12-24)

> [!WARNING]
> 본사 문서와 실물이 다른 곳이 있습니다. 특히 **통신 특성은 `FF01` 이 아니라 `AA01`**, **영점 명령에는 데이터 바이트 `01` 이 꼭 필요**하고, **타이머 정지를 보내면 무게 송출이 멈춥니다.**

## 한눈에

| 항목 | 값 | 확인 |
|---|---|---|
| 서비스 UUID | Microbalance `0x00EE` ✅ M · Ti `0x00DD` 📄 | |
| 광고 이름 | Ti: `Mb Ti NNNNNN` — `DiFluid` 로 시작하지 않음 | ✅ T |
| 특성 | `0xAA01` — 명령 쓰기와 응답 notify 모두(벤더 문서의 「FF01」은 틀림) | ✅ M · Ti 는 평문 동작 ✅, 고른 특성은 기록 없음 |
| 쓰기 방식 | 응답 있는 쓰기(M 은 write-without-response 없음) | ✅ M · ❓ T |
| 페어링·서버·SDK 키 | 필요 없음 | ✅ M·T |
| 프레임 | `DF DF func cmd len data… sum` — R2 와 같은 형식 | ✅ M·T |
| 무게 | `DF DF 03 00 00 C1` → 응답 len 13, 무게 = 앞 4 B ÷ 10 g | ✅ M·T |
| 배터리 | `DF DF 03 05 00 C6` → **data1**(data0 은 상태 코드) | ✅ T |
| 영점 | `DF DF 03 02 01 01 C5` — 데이터 `01` 이 없으면 조용히 무시 | ✅ M · ❓ T |
| 타이머 정지 | `DF DF 03 01 01 00 C3` — **BLE 무게 송출이 멈춤**(기종 기록 없음) · 리셋 명령은 벤더 표에 없음 | ✅ · 📄 |
| 샘플레이트 | 요청 1회 = 응답 1프레임, 마감 기준 폴링으로 약 5 Hz(5 Hz 수치는 T) | ✅ M·T |
| 오류 응답 | 벤더 정의 없음 — 데이터 바이트를 빠뜨린 영점 명령은 오류 없이 무시됨. 정의되지 않은 명령에 대한 반응은 모름 | 📄 · ✅ M · ❓ |

✅ 실측 확인 · 📄 벤더 문서에만 있음 · ❓ 미확인 — M: 일반 Microbalance, T: Microbalance Ti(확인한 기기)

## 문서

| 문서 | 내용 |
|---|---|
| [프로토콜](protocol.md) | 연결, 프레임, 명령 총표, 센서 데이터, 상태·배터리, 기기 정보, 영점·타이머, 벤더 문서와 다른 점 |
| [실측 확인 기록](verification.md) | 기기, 확인한 것, 실측 프레임, 타이밍, 미확인 목록 |
| [구현 팁](implementation-tips.md) | 기기 고르기, 프레임 분리, 영점 함정, 배터리·단위, 타이머, 샘플레이트, BlueZ |
| [Python 최소 예제](../examples/python/README.md) | 찾기·연결·무게 읽기·배터리·영점 |

세부 문서는 한 문서에 한국어와 영어를 함께 적었습니다.

## 빠른 시작

저장소 최상위에서:

```bash
pip install bleak          # Python 3.9 이상
python examples/python/microbalance_minimal.py scan
python examples/python/microbalance_minimal.py listen --address <저울 주소> --seconds 30
```

## 시험 환경

- 기기: Microbalance 1대(2026-07-05·07-26), Microbalance Ti 1대(2026-08-30). 2026-09-02 의 타이머 시작·정지 시험은 기종 기록이 없습니다(정황상 Ti).
- 호스트: Linux(BlueZ) + Python [bleak](https://github.com/hbldh/bleak)
- 다른 펌웨어·모델에서는 다를 수 있습니다. 펌웨어 버전 문자열은 캡처하지 못했습니다.
