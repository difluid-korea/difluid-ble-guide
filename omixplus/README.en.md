# Omix Plus — BLE integration

[한국어](README.md) · **English** · [← Guide home](../README.en.md)

How to receive DiFluid **Omix Plus** bean analyzer results (roast color, moisture, density, ambient temperature and humidity) over BLE. Based on material from 이승진(180커피로스터스), who built a receiver for the roastery.

- Contributed by: 이승진(180커피로스터스)
- Product: [difluid.kr/OmixPlus](https://www.difluid.kr/OmixPlus)
- Vendor document: none. The [difluid-sdk-demo](https://github.com/DiFluid/difluid-sdk-demo) README lists Omix as "WIP" (checked 2026-11-02).

> [!IMPORTANT]
> Receive only. The app does not start a measurement; the user measures on the device and the result arrives as notifications. No start, settings or calibration command has been confirmed, so do not write to the Omix Plus.

## Summary

| Item | Value | Status |
|---|---|---|
| Advertised name | `Omix Plus` + unit number (redacted). Seen on one unit | ✅ |
| Measurement service | `0x00E2` (`000000e2-0000-1000-8000-00805f9b34fb`) | ✅ recomputed |
| Measurement characteristic | `0xFF02` (`0000ff02-0000-1000-8000-00805f9b34fb`), notify | ✅ recomputed |
| Other GATT | `0x00E1` / `0xFF01` (notify, write), purpose unknown. The discovery record has no `AA01` as on the R2 and scales | recomputed · ❓ |
| Pairing | The receiver never calls pair. Not tested on a fresh PC | ✅ · ❓ |
| MTU | The contributor's receiver waits for an MTU of 129 or more (126-byte frame + 3). Seen: MTU 23 (cut to 20 B) and 517 (complete). The maker's minimum is unknown | ✅ recomputed · ❓ |
| Frame | `DF DF func cmd len data… sum`, same as the R2 and scales | recomputed |
| Byte order | Little-endian. The R2 and scales are big-endian | recomputed |
| Result responses | `03/03` moisture and density (50 B), `03/05` color (126 B), `03/06` ambient temperature and humidity (34 B) | ✅ recomputed |
| Measurement ID | data0–11 is the same in all three. Looks like Unix time (s) + a counter | recomputed · ❓ |
| Sample mode | `01 04` whole bean, `01 05` ground | ✅ |
| No value | Negative moisture, zero density | ✅ |
| Commands, error codes, settings | None confirmed | ❓ |

✅ checked by the contributor on one unit · recomputed: DiFluid Korea recomputed it from the published capture bytes · 📄 vendor document only · ❓ unknown

DiFluid Korea has not reproduced any of this on an Omix Plus.

## Documents

| Document | Contents |
|---|---|
| [Protocol](protocol.md) | GATT, frame, byte layout of the three responses, arrival order, differences from vendor documents |
| [Verification](verification.md) | Contributor's setup, what was checked, decoded capture values, timing, open questions |
| [Implementation tips](implementation-tips.md) | MTU, grouping a measurement, missing values, ground mode |
| [Capture logs](captures/README.md) | Five sets of raw notification frames, GATT discovery |
| [Minimal Python example](../examples/python/README.md) | Find, subscribe to FF02, print results. No writes |

The reference documents carry Korean and English side by side.

## Quick start

From the repository root:

```bash
pip install bleak          # Python 3.9+
python examples/python/omixplus_minimal.py scan
python examples/python/omixplus_minimal.py listen --address <DEVICE ADDRESS> --seconds 120
```

Measure on the device after it connects; the result is printed. The BLE part of the example has not been run against an Omix Plus. Only the decoder was tested, with the contributor's captures.

## Contributor's setup

- Device: one Omix Plus. Model string and firmware version not obtained (the discovery record has no standard Device Information service `0x180A`; any maker-specific query is unknown)
- Host: Windows (WinRT BLE), Python [bleak](https://github.com/hbldh/bleak) 3.0.2
- Captures: 2026-10-21 to 11-02 (KST)

Other units, firmware or operating systems may differ.

## Source

Protocol notes, captures and device checks: 이승진(180커피로스터스). DiFluid Korea recomputed the captures and wrote them up in Korean and English. The example code was written by DiFluid Korea.
