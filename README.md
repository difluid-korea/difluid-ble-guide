<p align="center"><img src="assets/banner.svg" alt="DiFluid Korea — BLE 개발자 가이드" width="100%"></p>

<p align="center"><b>한국어</b> · <a href="README.en.md">English</a></p>

<p align="center">
  <a href="LICENSE-DOCS.md"><img alt="문서 CC BY 4.0" src="https://img.shields.io/badge/%EB%AC%B8%EC%84%9C-CC%20BY%204.0-4FBBAB"></a>
  <a href="LICENSE"><img alt="코드 MIT" src="https://img.shields.io/badge/%EC%BD%94%EB%93%9C-MIT-4FBBAB"></a>
  <a href="https://www.difluid.kr"><img alt="difluid.kr" src="https://img.shields.io/badge/%EA%B3%B5%EC%8B%9D%EB%AA%B0-difluid.kr-0D0F0F"></a>
  <a href="https://180coffee.com"><img alt="Omix Plus 기여: 180커피로스터스" src="https://img.shields.io/badge/Omix%20Plus%20%EA%B8%B0%EC%97%AC-180%EC%BB%A4%ED%94%BC%EB%A1%9C%EC%8A%A4%ED%84%B0%EC%8A%A4-6F4E37"></a>
</p>

# DiFluid BLE 개발자 가이드

DiFluid 기기를 블루투스(BLE)로 내 앱·기기에 붙이는 방법을 **실제 기기로 확인해** 정리했습니다. 바이트 예시, 실측 타이밍, 본사 문서와 다른 점, 바로 돌려 볼 수 있는 Python 예제를 담았습니다.

> [!NOTE]
> DiFluid 한국 공식 수입사이자 DiFluid Korea 공식 운영사인 **비다스테크(Vidastech)** 가 관리합니다. 프로토콜의 정본은 DiFluid 본사의 [difluid-sdk-demo](https://github.com/DiFluid/difluid-sdk-demo) 이며, 이 가이드는 그것을 실제 기기로 확인하고 보완합니다. 본사 문서 목록은 [본사 공식 자료](#본사-공식-자료)에 있습니다.

## 기기

| 기기 | 무엇을 재나 | 가이드 | 예제 | 제품 |
|---|---|---|---|---|
| **R2 Extract** | 굴절계 — 커피 TDS·굴절률 | [시작하기](r2/README.md) · [프로토콜](r2/protocol.md) | [r2_minimal.py](examples/python/r2_minimal.py) | [difluid.kr](https://www.difluid.kr/R2Extract) |
| **Microbalance · Ti** | 저울 — 무게·유량·타이머 | [시작하기](microbalance/README.md) · [프로토콜](microbalance/protocol.md) | [microbalance_minimal.py](examples/python/microbalance_minimal.py) | [difluid.kr](https://www.difluid.kr/Microbalance) |
| **Omix Plus** | 원두 분석기 — 색도·수분·밀도 수신(받기 전용, 기여 자료) | [시작하기](omixplus/README.md) · [프로토콜](omixplus/protocol.md) | [omixplus_minimal.py](examples/python/omixplus_minimal.py) | [difluid.kr](https://www.difluid.kr/OmixPlus) |

세 기기는 같은 DiFluid 프레임 형식(`DF DF func cmd len data sum`)을 쓰지만, 명령과 응답은 기기마다 다릅니다. 바이트 순서도 다릅니다(R2·저울은 빅 엔디언, Omix Plus 는 리틀 엔디언).

## 세 줄로 시작하기

```bash
pip install bleak                                   # Python 3.9 이상
python examples/python/r2_minimal.py scan           # 주변 R2 찾기
python examples/python/r2_minimal.py listen --address <주소> --single
```

> [!TIP]
> R2 는 연결돼 있는 동안 광고하지 않습니다. 휴대폰 앱(DiFluid Café)과의 연결을 먼저 끊으세요.

## 이 가이드가 다른 점

- **모든 사실에 확인 표시** — ✅ 실측 확인 · 📄 벤더 문서에만 있음 · ❓ 미확인. 확인하지 않은 것을 사실처럼 쓰지 않습니다.
- **원시 캡처 공개(R2 · Omix Plus)** — 판단의 근거가 된 바이트 로그를 그대로 공개합니다. 기기 식별 정보만 가렸습니다. 저울(Microbalance·Ti)은 원시 로그를 남기지 않아, 시험 코드에 고정한 실측 프레임만 싣습니다. Omix Plus 의 캡처와 실기 확인은 기여자의 것입니다.
- **문서와 다른 점** — 본사 문서의 오타와 어긋남을 실물 바이트와 프레임 규칙으로 바로잡았습니다(실물로 확인한 항목에는 ✅).
- **제품에 붙여 본 경험** — 실제 제품에 통합하며 만난 함정과 그 뒤 정한 규칙을 함께 적었습니다.

## 본사 공식 자료

DiFluid 본사가 GitHub([DiFluid](https://github.com/DiFluid))에 공개한 자료입니다. 이 가이드는 [difluid-sdk-demo 커밋 `df4e073`](https://github.com/DiFluid/difluid-sdk-demo/tree/df4e0731dc646b9110479cb3b39bb69346e0a640)(2024-12-24, 2026-11-02 현재 최신)을 실기와 대조했습니다. 「확인한 판」은 그 커밋에 고정한 링크이고, 「최신판」은 본사가 문서를 고치면 함께 바뀝니다.

| 본사 문서 | 대상 | 확인한 판 | 최신판 | 이 가이드 |
|---|---|---|---|---|
| difluid-protocol.md | 공통 프레임 형식 | [v1.0.0 · 2023-03-18](https://github.com/DiFluid/difluid-sdk-demo/blob/df4e0731dc646b9110479cb3b39bb69346e0a640/docs/difluid-protocol.md) | [보기](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/difluid-protocol.md) | 프레임: [R2](r2/protocol.md#2-프레임--frame) · [저울](microbalance/protocol.md#2-프레임--frame) · [Omix Plus](omixplus/protocol.md#2-프레임--frame) |
| protocolR2.md | R2 Extract | [v1.0.0 · 2023-03-18](https://github.com/DiFluid/difluid-sdk-demo/blob/df4e0731dc646b9110479cb3b39bb69346e0a640/docs/protocolR2.md) | [보기](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/protocolR2.md) | [문서와 다른 점](r2/protocol.md#6-벤더-문서와-다른-점--differences-from-the-vendor-document) |
| protocolMicrobalance.md | Microbalance · Ti | [v1.0.0 · 2024-12-24](https://github.com/DiFluid/difluid-sdk-demo/blob/df4e0731dc646b9110479cb3b39bb69346e0a640/docs/protocolMicrobalance.md) | [보기](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/protocolMicrobalance.md) | [문서와 다른 점](microbalance/protocol.md#9-벤더-문서와-다른-점--differences-from-the-vendor-document) |
| protocolOmni.md | Omni — Omix Plus 와 다른 기기 | [v1.0.0 · 2024-12-24](https://github.com/DiFluid/difluid-sdk-demo/blob/df4e0731dc646b9110479cb3b39bb69346e0a640/docs/protocolOmni.md) | [보기](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/protocolOmni.md) | [Omix Plus 와 비교](omixplus/protocol.md#6-벤더-문서와-비교--compared-with-the-vendor-documents) |
| README | 연결 절차, 데모 앱(uniapp) 실행법 | [2024-12-24](https://github.com/DiFluid/difluid-sdk-demo/blob/df4e0731dc646b9110479cb3b39bb69346e0a640/README.md) | [보기](https://github.com/DiFluid/difluid-sdk-demo/blob/master/README.md) | — |

함께 볼 것: [General Coffee Concept](https://github.com/DiFluid/General-Coffee-Concept) — 본사의 커피 개념 해설. 브루 컨트롤 차트 글이 있고, TDS·추출 수율 글은 비어 있습니다(2026-11-02 확인).

## 업데이트 이력

| 날짜 | 내용 |
|---|---|
| 2026-11-02 | 운영 주체 표기 정정 — 비다스테크: DiFluid 한국 공식 수입사, DiFluid Korea 공식 운영사 |
| 2026-11-02 | 첫 화면에 [본사 공식 자료](#본사-공식-자료) 표 추가 — 대조한 본사 커밋(`df4e073`)에 고정한 링크와 최신판 링크 |
| 2026-11-02 | **Omix Plus** 수신 가이드·예제 추가([omixplus/](omixplus/README.md)). 소스 제공: [180커피로스터스](https://180coffee.com) 이승진 로스터 |
| 2026-11-02 | 첫 공개 — **R2 Extract**, **Microbalance · Ti** 가이드와 Python 예제(한/영) |

## 피드백

이 가이드로 개발하셨다면 알려 주세요. 링크를 누르면 제목과 양식이 채워진 메일이 열립니다.

| 무엇을 | 메일 | 함께 주시면 좋은 것 |
|---|---|---|
| 사용 사례 공유 | [[사용 사례] 메일 쓰기](mailto:difluid.kr@gmail.com?subject=%5B%EC%82%AC%EC%9A%A9%20%EC%82%AC%EB%A1%80%5D%20&body=%EB%A7%8C%EB%93%A0%20%EA%B2%83%3A%0A%EC%93%B4%20%EA%B8%B0%EA%B8%B0%C2%B7%ED%8E%8C%EC%9B%A8%EC%96%B4%3A%0A%EA%B0%80%EC%9D%B4%EB%93%9C%EC%97%90%20%EC%86%8C%EA%B0%9C%ED%95%B4%EB%8F%84%20%EB%90%98%EB%82%98%EC%9A%94%28%EC%98%88/%EC%95%84%EB%8B%88%EC%98%A4%29%3A%0A%EB%A7%81%ED%81%AC%3A%0A) | 만든 것, 쓴 기기·펌웨어, 가이드에 소개해도 되는지 |
| 오류·버그 신고 | [[버그] 메일 쓰기](mailto:difluid.kr@gmail.com?subject=%5B%EB%B2%84%EA%B7%B8%5D%20&body=%EB%AC%B8%EC%84%9C%C2%B7%EC%BD%94%EB%93%9C%20%EC%9C%84%EC%B9%98%28%EB%A7%81%ED%81%AC%29%3A%0A%EA%B8%B0%EA%B8%B0%20%EB%AA%A8%EB%8D%B8%C2%B7%ED%8E%8C%EC%9B%A8%EC%96%B4%3A%0A%EC%A6%9D%EC%83%81%3A%0A%EA%B8%B0%EB%8C%80%ED%95%9C%20%EB%8F%99%EC%9E%91%3A%0A%EC%9B%90%EC%8B%9C%20%EB%B0%94%EC%9D%B4%ED%8A%B8%20%EB%A1%9C%EA%B7%B8%28%EC%9E%88%EC%9C%BC%EB%A9%B4%20%EC%B2%A8%EB%B6%80%29%3A%0A) | 문서·코드 위치, 기기 모델·펌웨어, 증상, 원시 바이트 로그 |
| 기능 제안 | [[기능 제안] 메일 쓰기](mailto:difluid.kr@gmail.com?subject=%5B%EA%B8%B0%EB%8A%A5%20%EC%A0%9C%EC%95%88%5D%20&body=%ED%95%84%EC%9A%94%ED%95%9C%20%EA%B8%B0%EB%8A%A5%C2%B7%EA%B8%B0%EA%B8%B0%3A%0A%EC%93%B0%EB%A0%A4%EB%8A%94%20%EC%83%81%ED%99%A9%3A%0A) | 필요한 기능·기기, 쓰려는 상황 |
| 자료 기여 | [difluid.kr@gmail.com](mailto:difluid.kr@gmail.com) | 프로토콜 정리·캡처·코드 — 검토해 작업자 이름과 함께 싣습니다 |

[GitHub 이슈](https://github.com/difluid-korea/difluid-ble-guide/issues)로 보내셔도 됩니다. 사용 사례는 동의하신 경우에만 소개합니다.

## 기여자

- Omix Plus 소스 제공: 이승진 로스터 — [180커피로스터스](https://180coffee.com)

## 라이선스

- 문서·캡처 로그: [CC BY 4.0](LICENSE-DOCS.md) — 출처를 밝히면 자유롭게 쓸 수 있습니다.
- 예제 코드: [MIT](LICENSE)

DiFluid 의 프로토콜 문서는 DiFluid 의 저작물입니다(MIT, © Shenzhen Digitizing Fluid Technology Co., Ltd.). 이 저장소는 그것을 옮겨 싣지 않고 링크하며, 바이트 값 같은 사실만 정리합니다. DiFluid, R2 Extract, Microbalance, Omix, DiFluid Café 는 해당 소유자의 상표입니다.

---

<p align="center"><b>DiFluid Korea</b> · <a href="https://www.difluid.kr">difluid.kr</a> · <a href="mailto:difluid.kr@gmail.com">difluid.kr@gmail.com</a></p>
