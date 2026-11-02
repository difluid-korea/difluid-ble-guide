<p align="center"><img src="assets/banner.svg" alt="DiFluid Korea — BLE Developer Guide" width="100%"></p>

<p align="center"><a href="README.md">한국어</a> · <b>English</b></p>

<p align="center">
  <a href="LICENSE-DOCS.md"><img alt="Docs CC BY 4.0" src="https://img.shields.io/badge/docs-CC%20BY%204.0-4FBBAB"></a>
  <a href="LICENSE"><img alt="Code MIT" src="https://img.shields.io/badge/code-MIT-4FBBAB"></a>
  <a href="https://www.difluid.kr"><img alt="difluid.kr" src="https://img.shields.io/badge/store-difluid.kr-0D0F0F"></a>
</p>

# DiFluid BLE Developer Guide

How to connect DiFluid devices to your own app or hardware over Bluetooth LE — **checked on real devices**. Byte-level examples, measured timings, where the vendor docs differ, and a Python example you can run today.

> [!NOTE]
> Maintained by **Vidastech**, the official DiFluid distributor in Korea. DiFluid's own [difluid-sdk-demo](https://github.com/DiFluid/difluid-sdk-demo) is the authoritative protocol; this guide checks and supplements it on real devices.

## Devices

| Device | Measures | Guide | Example | Product |
|---|---|---|---|---|
| **R2 Extract** | Refractometer — coffee TDS and refractive index | [Get started](r2/README.en.md) · [Protocol](r2/protocol.md) | [r2_minimal.py](examples/python/r2_minimal.py) | [difluid.kr](https://www.difluid.kr/R2Extract) |
| **Microbalance · Ti** | Scale — weight, flow, timer | [Get started](microbalance/README.en.md) · [Protocol](microbalance/protocol.md) | [microbalance_minimal.py](examples/python/microbalance_minimal.py) | [difluid.kr](https://www.difluid.kr/Microbalance) |

Both use DiFluid's frame format (`DF DF func cmd len data sum`), but commands and responses differ per device.

## Three commands to a first reading

```bash
pip install bleak                                   # Python 3.9+
python examples/python/r2_minimal.py scan           # find nearby R2 units
python examples/python/r2_minimal.py listen --address <ADDRESS> --single
```

> [!TIP]
> The R2 does not advertise while it is connected. Disconnect it from the phone app (DiFluid Café) first.

## What makes this guide different

- **A status on every fact** — ✅ measured · 📄 vendor document only · ❓ unknown. Nothing unverified is stated as fact.
- **Raw captures (R2)** — the byte logs behind each R2 conclusion, with only unit identifiers redacted. We kept no raw logs for the scales (Microbalance, Ti); only the measured frames pinned in our tests are published.
- **Where the docs differ** — typos and mismatches in the vendor docs, corrected against real bytes or the frame rules (items checked on a device are marked ✅).
- **Product experience** — pitfalls we hit integrating into a real product, and the rules we adopted.

## Feedback

If you built something with this guide, tell us. Each link opens an email with the subject and a short form filled in.

| What | Email | Please include |
|---|---|---|
| Share a use case | [Email [Use case]](mailto:difluid.kr@gmail.com?subject=%5BUse%20case%5D%20&body=What%20you%20built%3A%0ADevice%20and%20firmware%3A%0AMay%20we%20feature%20it%20in%20the%20guide%20%28yes/no%29%3A%0ALink%3A%0A) | What you built, device and firmware, whether we may feature it |
| Report an error or bug | [Email [Bug]](mailto:difluid.kr@gmail.com?subject=%5BBug%5D%20&body=Page%20or%20code%20%28link%29%3A%0ADevice%20model%20and%20firmware%3A%0AWhat%20happened%3A%0AWhat%20you%20expected%3A%0ARaw%20byte%20log%20%28attach%20if%20any%29%3A%0A) | Page or code, device model and firmware, what happened, raw byte log |
| Request a feature | [Email [Feature request]](mailto:difluid.kr@gmail.com?subject=%5BFeature%20request%5D%20&body=Feature%20or%20device%20you%20need%3A%0AYour%20use%20case%3A%0A) | The feature or device, your use case |
| Contribute material | [difluid.kr@gmail.com](mailto:difluid.kr@gmail.com) | Protocol notes, captures, code — published with your name after review |

[GitHub issues](https://github.com/difluid-korea/difluid-ble-guide/issues) work too. Use cases are featured only with your consent.

## License

- Documentation and capture logs: [CC BY 4.0](LICENSE-DOCS.md) — free to use with attribution.
- Example code: [MIT](LICENSE)

DiFluid's protocol documents are DiFluid's own work (MIT, © Shenzhen Digitizing Fluid Technology Co., Ltd.). This repository links to them rather than copying them, and restates only facts such as byte values. DiFluid, R2 Extract, Microbalance and DiFluid Café are trademarks of their respective owner.

---

<p align="center"><b>DiFluid Korea</b> · <a href="https://www.difluid.kr">difluid.kr</a> · <a href="mailto:difluid.kr@gmail.com">difluid.kr@gmail.com</a></p>
