# Microbalance · Ti — BLE integration

[한국어](README.md) · **English** · [← Guide home](../README.en.md)

How to connect the DiFluid **Microbalance** and **Microbalance Ti** coffee scales to your own app or hardware over Bluetooth LE. We collected what we confirmed on two units while integrating the scale into a product, together with errors and gaps in the vendor document.

Product info and purchase: [difluid.kr/Microbalance](https://www.difluid.kr/Microbalance) · Vendor document: [protocolMicrobalance.md](https://github.com/DiFluid/difluid-sdk-demo/blob/master/docs/protocolMicrobalance.md) (v1.0.0, 2024-12-24)

> [!WARNING]
> The vendor document and the device disagree in places. Most importantly: **talk over `AA01`, not `FF01`**; **the tare command needs the data byte `01`**; and **sending timer stop freezes the weight output.**

## At a glance

| Item | Value | Status |
|---|---|---|
| Service UUID | Microbalance `0x00EE` ✅ M · Ti `0x00DD` 📄 | |
| Advertised name | Ti: `Mb Ti NNNNNN` — does not start with `DiFluid` | ✅ T |
| Characteristic | `0xAA01` — write commands and receive notifications (the vendor's "FF01" is wrong) | ✅ M · cleartext worked on the Ti ✅, the characteristic used was not recorded |
| Write type | Write with response (no write-without-response on M) | ✅ M · ❓ T |
| Pairing, server, SDK key | Not required | ✅ M·T |
| Frame | `DF DF func cmd len data… sum` — same format as the R2 | ✅ M·T |
| Weight | `DF DF 03 00 00 C1` → response len 13, weight = first 4 bytes ÷ 10 g | ✅ M·T |
| Battery | `DF DF 03 05 00 C6` → **data1** (data0 is the status code) | ✅ T |
| Tare | `DF DF 03 02 01 01 C5` — silently ignored without the data byte `01` | ✅ M · ❓ T |
| Timer stop | `DF DF 03 01 01 00 C3` — **freezes the BLE weight output** (unit not recorded) · the vendor table has no reset command | ✅ · 📄 |
| Sample rate | One frame per request; about 5 Hz with deadline-paced polling (the 5 Hz figure: T) | ✅ M·T |
| Error responses | None defined by the vendor — a tare command missing its data byte was ignored with no error; how the scale reacts to undefined commands is unknown | 📄 · ✅ M · ❓ |

✅ measured on a device · 📄 vendor document only · ❓ unknown — M: Microbalance, T: Microbalance Ti (the unit it was checked on)

## Documents

| Document | Contents |
|---|---|
| [Protocol](protocol.md) | Connection, frames, command table, sensor data, status and battery, device info, tare and timer, differences from the vendor document |
| [Verification](verification.md) | Units, what was confirmed, captured frames, timing, open questions |
| [Implementation tips](implementation-tips.md) | Picking the device, frame splitting, the tare trap, battery and units, the timer, sample rate, BlueZ |
| [Minimal Python example](../examples/python/README.md) | Find, connect, read weight and battery, tare |

The reference documents carry Korean and English side by side.

## Quick start

From the repository root:

```bash
pip install bleak          # Python 3.9+
python examples/python/microbalance_minimal.py scan
python examples/python/microbalance_minimal.py listen --address <SCALE ADDRESS> --seconds 30
```

## Test setup

- Devices: one Microbalance (2026-07-05, 07-26), one Microbalance Ti (2026-08-30). The 2026-09-02 timer start/stop tests did not record which unit was used (probably the Ti).
- Host: Linux (BlueZ) + Python [bleak](https://github.com/hbldh/bleak)
- Other firmware versions or models may behave differently. We did not capture a firmware version string.
