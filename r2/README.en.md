# R2 Extract — BLE integration

[한국어](README.md) · **English** · [← Guide home](../README.en.md)

How to connect the DiFluid **R2 Extract** refractometer (coffee TDS meter) to your own app or hardware over Bluetooth LE. We checked DiFluid's published protocol against captures from three real units, and we list where the document differs from the device and what is still unknown.

Product info and purchase: [difluid.kr/R2Extract](https://www.difluid.kr/R2Extract) · Vendor document: [protocolR2.md](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/protocolR2.md) (v1.0.0)

## At a glance

| Item | Value | Status |
|---|---|---|
| Advertised name | `DiFluid R2 NNNNNN` (6 digits; they differed on each of our three units) | ✅ |
| Service | `0x00FF` (`000000ff-0000-1000-8000-00805f9b34fb`) | ✅ |
| Characteristic | `0xAA01` (`0000aa01-0000-1000-8000-00805f9b34fb`) — write commands and receive notifications | ✅ |
| Write type | Write **with** response (write-without-response is not offered) | ✅ |
| Pairing / bonding | Not required | ✅ |
| Frame | `DF DF func cmd len data… sum` — `sum` = low 8 bits of the sum of all preceding bytes | ✅ |
| Single test | `DF DF 03 00 00 C1` | ✅ |
| Result | TDS % = **signed** 16-bit ÷ 100, refractive index = 32-bit ÷ 100000 | ✅ |
| Button-started tests | Arrive at the connected central with the same bytes | ✅ |
| Past results on connect | Already-delivered results are not re-sent on reconnect (seen twice) | ✅ |
| Concurrent centrals | No advertising while connected (observed) → presumably one central at a time (not tested with another central) | ✅ / ❓ |
| Auto power-off setting | No command in the public protocol | ❓ |

✅ measured on a device · 📄 vendor document only · ❓ unknown

## Documents

| Document | Contents |
|---|---|
| [Protocol](protocol.md) | Connection, frames, commands, measurement responses (single, average, calibration), errors, settings, differences from the vendor document |
| [Verification](verification.md) | What was checked and how, timing, open questions |
| [Implementation tips](implementation-tips.md) | Pitfalls we hit while integrating, and our rules |
| [Capture logs](captures/README.md) | Nine raw byte logs (unit identifiers redacted) |
| [Minimal Python example](../examples/python/README.md) | Scan, read info, single test, listen |

The reference documents carry Korean and English side by side.

## Quick start

From the repository root:

```bash
pip install bleak          # Python 3.9+
python examples/python/r2_minimal.py scan
python examples/python/r2_minimal.py listen --address <R2 ADDRESS> --seconds 60 --single
```

> [!TIP]
> The R2 does not advertise while connected, so if it is connected to the phone app (DiFluid Café) it presumably cannot be found. Disconnect it from the app first.

## Test setup

- Devices: three R2 Extract units — model string `DFT-R102`, firmware `V230`
- Host: Linux (BlueZ) + Python [bleak](https://github.com/hbldh/bleak)
- Dates: 2026-11-01 – 2026-11-02
- Other firmware versions or models may behave differently.
