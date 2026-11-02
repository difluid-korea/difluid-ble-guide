#!/usr/bin/env python3
"""DiFluid Omix Plus — minimal BLE example, receive only / 최소 BLE 예제(받기 전용).

Subscribes to the measurement characteristic FF02 and prints what the user
measures on the device. It never writes to the device: no Omix Plus command
has been confirmed.
측정 특성 FF02 를 구독해 본체에서 잰 결과를 출력한다. 기기에 아무것도 쓰지 않는다
(Omix Plus 의 명령은 확인된 것이 없다).

Not run against an Omix Plus by DiFluid Korea. The decoder is tested with frames
captured by 이승진(180커피로스터스).
DiFluid Korea 는 이 예제를 Omix Plus 로 실행하지 않았다. 해석부는 이승진(180커피로스터스)의
캡처로 시험했다.

    pip install bleak
    python omixplus_minimal.py scan
    python omixplus_minimal.py listen --address <ADDRESS> --seconds 120

The decoding part (parse_notification … MeasurementCollector) has no dependencies.
Protocol notes: ../../omixplus/protocol.md
"""
from __future__ import annotations

import argparse
import asyncio
import math
import struct
import sys

SERVICE_UUID = "000000e2-0000-1000-8000-00805f9b34fb"
CHAR_UUID = "0000ff02-0000-1000-8000-00805f9b34fb"   # notify; all results arrive here
NAME_PREFIX = "omix"                                  # seen: "Omix Plus <unit number>"
MIN_MTU = 129                                         # 126-byte frame + 3; the maker's minimum is unknown
MODES = {1025: "whole", 1281: "ground"}               # 01 04 00 00 / 01 05 00 00


# ── Frames / 프레임 ────────────────────────────────────────────────────────

def parse_notification(data: bytes) -> list[dict]:
    """One notification -> decoded frames. Little-endian payload.
    A frame shorter than its length byte says is reported as "truncated": at MTU 23
    the frames arrived cut to 20 bytes and the rest never came.
    MTU 23 에서는 프레임이 20 B 로 잘려 왔고 나머지는 오지 않았다.
    """
    out, i = [], 0
    while True:
        j = data.find(b"\xdf\xdf", i)
        if j < 0:
            return out
        if len(data) - j < 5:
            out.append({"kind": "truncated", "have": len(data) - j, "need": None})
            return out
        need = data[j + 4] + 6
        frame = data[j:j + need]
        if len(frame) < need:
            out.append({"kind": "truncated", "func": frame[2], "cmd": frame[3],
                        "have": len(frame), "need": need})
            return out
        if sum(frame[:-1]) & 0xFF != frame[-1]:
            out.append({"kind": "bad_checksum", "frame": frame.hex(" ")})
            i = j + 1
            continue
        out.append(decode(frame))
        i = j + need


# ── Decoding / 해석 ────────────────────────────────────────────────────────

def _f32(d: bytes, offset: int) -> float:
    return struct.unpack_from("<f", d, offset)[0]


def decode(frame: bytes) -> dict:
    """Offsets are data offsets (the byte after the length byte is data0)."""
    func, cmd, d = frame[2], frame[3], frame[5:-1]
    if func != 0x03 or (cmd, len(d)) not in ((0x03, 44), (0x05, 120), (0x06, 28)):
        return {"kind": "other", "func": func, "cmd": cmd, "len": len(d)}   # e.g. 03/02, meaning unknown
    p = {"id": struct.unpack_from("<QI", d, 0)}   # data0-7 (Unix time?) + data8-11 (counter)
    if cmd == 0x03:
        mode = struct.unpack_from("<I", d, 12)[0]
        moisture, density = _f32(d, 24), _f32(d, 36)
        whole = mode == 1025   # ground-mode moisture/density were never established
        p.update(kind="quality", mode=MODES.get(mode, f"unknown {mode}"),
                 # negative moisture and zero density mean "no value"
                 moisture=round(moisture, 1) if whole and math.isfinite(moisture) and moisture >= 0 else None,
                 density=round(density, 1) if whole and math.isfinite(density) and density > 0 else None)
    elif cmd == 0x05:
        color_type = struct.unpack_from("<I", d, 12)[0]   # always 2 in the captures
        color = _f32(d, 16)
        p.update(kind="color", color_type=color_type,
                 color=round(color, 1) if color_type == 2 and math.isfinite(color) else None)
    else:
        temp = _f32(d, 12)
        p.update(kind="ambient", temp_c=round(temp, 1) if math.isfinite(temp) else None,
                 rh_pct=struct.unpack_from("<i", d, 16)[0])
    return p


class MeasurementCollector:
    """Groups the quality (03/03), color (03/05) and ambient (03/06) parts of one
    measurement by ID. Order is not assumed. Repeats, and parts older than the
    newest measurement, are dropped. feed() returns the result once all three are in.
    측정 식별자로 세 응답을 묶는다. 순서는 가정하지 않는다.
    """

    def __init__(self) -> None:
        self.parts: dict[tuple, dict] = {}
        self.newest: tuple | None = None

    def feed(self, p: dict) -> dict | None:
        if p.get("kind") not in ("quality", "color", "ambient"):
            return None
        key = p["id"]
        if self.newest is not None and key < self.newest:
            return None
        self.newest = key
        parts = self.parts.setdefault(key, {})
        if parts.get(p["kind"]) == p:
            return None
        parts[p["kind"]] = p
        while len(self.parts) > 8:
            del self.parts[next(iter(self.parts))]
        if len(parts) < 3:
            return None
        q, c, a = parts["quality"], parts["color"], parts["ambient"]
        result = {"kind": "result", "id": key, "mode": q["mode"],
                  "moisture": q["moisture"], "density": q["density"],
                  "temp_c": a["temp_c"], "rh_pct": a["rh_pct"]}
        # keep a ground-mode color apart from the whole-bean color
        result["ground_color" if q["mode"] == "ground" else "color"] = c["color"]
        return result


# ── BLE (needs bleak) ──────────────────────────────────────────────────────

async def scan(seconds: float) -> None:
    from bleak import BleakScanner
    found = await BleakScanner.discover(timeout=seconds, return_adv=True)
    rows = []
    for dev, adv in found.values():
        name = adv.local_name or dev.name or ""
        uuids = [u.lower() for u in adv.service_uuids or []]
        if name.lower().startswith(NAME_PREFIX) or SERVICE_UUID in uuids:
            rows.append((adv.rssi, dev.address, name))
    for rssi, address, name in sorted(rows, reverse=True):
        print(f"{rssi:>4} dBm  {address}  {name}")
    if not rows:
        print("No Omix found. Check power and range, and disconnect it from other apps.")


async def listen(address: str, seconds: float) -> None:
    from bleak import BleakClient, BleakScanner
    device = await BleakScanner.find_device_by_address(address, timeout=10)
    if device is None:
        print("Device not found (off, out of range, or connected elsewhere).")
        return
    collector = MeasurementCollector()

    def on_notify(_char, data: bytearray) -> None:
        for p in parse_notification(bytes(data)):
            if p["kind"] == "truncated":
                print(f"  frame cut to {p['have']} of {p['need']} bytes (MTU too small?). "
                      "Reconnect, wait a few seconds, then measure again.")
                continue
            print(f"  {p}")
            result = collector.feed(p)
            if result:
                print(f"** {result}")

    client = BleakClient(device)
    await client.connect()
    try:
        if not any(s.uuid.lower() == SERVICE_UUID for s in client.services):
            print("No 00E2 measurement service on this device. Stopping.")
            return
        if sys.platform == "win32":   # WinRT may raise the MTU a moment after connecting
            for _ in range(100):
                if client.mtu_size >= MIN_MTU:
                    break
                await asyncio.sleep(0.1)
            note = "" if client.mtu_size >= MIN_MTU else f" (below {MIN_MTU}: a 126-byte frame does not fit in one notification)"
            print(f"MTU {client.mtu_size}{note}")
        await client.start_notify(CHAR_UUID, on_notify)   # subscribe only; nothing is written
        print(f"Listening for {seconds:.0f} s. Measure on the device.")
        await asyncio.sleep(seconds)
    finally:
        try:
            await client.disconnect()
        except Exception as exc:                   # BlueZ may raise here; harmless
            print(f"(disconnect: {exc!r} — ignored)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="command", required=True)
    s = sub.add_parser("scan", help="list nearby Omix devices, strongest first")
    s.add_argument("--seconds", type=float, default=6)
    li = sub.add_parser("listen", help="connect, subscribe to FF02, print results")
    li.add_argument("--address", required=True)
    li.add_argument("--seconds", type=float, default=120)
    args = ap.parse_args()
    if args.command == "scan":
        asyncio.run(scan(args.seconds))
    else:
        asyncio.run(listen(args.address, args.seconds))


if __name__ == "__main__":
    main()
