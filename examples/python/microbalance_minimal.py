#!/usr/bin/env python3
"""DiFluid Microbalance / Microbalance Ti — minimal BLE example / 최소 BLE 예제.

Reads SN and battery, then polls weight at ~5 Hz and prints it. Optionally
tares once. It never sends timer or settings commands: timer stop freezes the
scale's weight output, and settings change the user's scale.
SN·배터리를 읽고 무게를 약 5 Hz 로 읽어 출력합니다. 원하면 영점을 한 번 잡습니다.
타이머·설정 명령은 보내지 않습니다(타이머 정지는 무게 송출을 멈추고, 설정은
사용자의 저울을 바꿉니다).

If the connected device has no scale service (00EE / 00DD), it stops before sending
anything: on an R2 the weight request DF DF 03 00 00 C1 starts a test.
연결한 기기에 저울 서비스(00EE·00DD)가 없으면 아무 명령도 보내기 전에 멈춥니다.
R2 에서는 무게 요청 DF DF 03 00 00 C1 이 측정 명령입니다.

    pip install bleak
    python microbalance_minimal.py scan
    python microbalance_minimal.py listen --address <ADDRESS> --seconds 30 [--tare] [--force]

The decoding part (build_frame … decode) has no dependencies.
Protocol notes: ../../microbalance/protocol.md
"""
from __future__ import annotations

import argparse
import asyncio

SERVICE_UUIDS = {
    "000000ee-0000-1000-8000-00805f9b34fb": "Microbalance",
    "000000dd-0000-1000-8000-00805f9b34fb": "Microbalance Ti",   # vendor document
}
CHAR_UUID = "0000aa01-0000-1000-8000-00805f9b34fb"   # cleartext; NOT ff01
NAME_HINTS = ("mb ti", "microbalance")  # fallback: "mb ti" seen on a Ti; "microbalance" is a guess
MAX_DATA_LEN = 20
POLL_S = 0.2


# ── Frames / 프레임 ────────────────────────────────────────────────────────

def build_frame(func: int, cmd: int, data: bytes = b"") -> bytes:
    head = bytes([0xDF, 0xDF, func, cmd, len(data)]) + bytes(data)
    return head + bytes([sum(head) & 0xFF])


GET_SERIAL = build_frame(0x00, 0x00)              # DF DF 00 00 00 BE
GET_FIRMWARE = build_frame(0x00, 0x02)            # DF DF 00 02 00 C0
GET_SENSOR_DATA = build_frame(0x03, 0x00)         # DF DF 03 00 00 C1
GET_STATUS = build_frame(0x03, 0x05)              # DF DF 03 05 00 C6
TARE = build_frame(0x03, 0x02, b"\x01")           # DF DF 03 02 01 01 C5 — the 01 is required


def split_frames(buf: bytearray) -> list[bytes]:
    """Remove and return complete frames from buf; keeps a partial tail.
    One notification can hold several frames (seen with SN chunks).
    notify 하나에 프레임이 여럿 올 수 있습니다(SN 조각에서 확인).
    """
    frames = []
    while True:
        i = buf.find(b"\xdf\xdf")
        if i < 0:
            del buf[:len(buf) - (1 if buf.endswith(b"\xdf") else 0)]
            return frames
        del buf[:i]
        if len(buf) < 5:
            return frames
        n = buf[4]
        if n > MAX_DATA_LEN:
            del buf[:1]
            continue
        if len(buf) < n + 6:
            return frames
        frame = bytes(buf[:n + 6])
        if sum(frame[:-1]) & 0xFF != frame[-1]:
            del buf[:1]
            continue
        frames.append(frame)
        del buf[:n + 6]


# ── Decoding / 해석 ────────────────────────────────────────────────────────

UNITS = {0: ("g", 10), 1: ("oz", 1000), 2: ("gering", 10)}   # oz / gering: vendor only, untested
STATUS = {0: "power down", 1: "charging", 2: "low power 1", 3: "low-battery shutdown",
          4: "startup", 5: "idle", 6: "device info", 7: "tare in progress",
          8: "OTA", 9: "OTA failed", 10: "timing", 11: "timer pause", 13: "low power 2",
          14: "auto stop timing"}


def decode(frame: bytes) -> dict:
    func, cmd, d = frame[2], frame[3], frame[5:-1]
    if func == 0x00 and cmd == 0x00:
        if len(d) == 6:
            return {"kind": "serial_chunk", "index": d[0], "text": d[1:].decode("ascii", "replace")}
        return {"kind": "serial_unexpected", "len": len(d)}      # SN bytes are never printed
    if func == 0x00 and cmd == 0x02:
        return {"kind": "firmware", "text": d.decode("ascii", "replace")}
    if func == 0x03 and cmd == 0x00 and len(d) >= 13:
        unit_name, div = UNITS.get(d[12], (f"unit {d[12]}", 10))
        return {
            "kind": "weight",
            # Sign is an assumption: no negative weight was ever captured.
            "weight": int.from_bytes(d[0:4], "big", signed=True) / div,
            "unit": unit_name,
            "flow_raw": int.from_bytes(d[4:6], "big", signed=True),   # vendor x10; was 0 with the timer off, never seen non-zero
            "time_raw": int.from_bytes(d[6:8], "big"),                # unit unknown
            "tick": int.from_bytes(d[8:12], "big"),                   # device counter (ms?)
        }
    if func == 0x03 and cmd == 0x05 and len(d) >= 3:
        # data0 is the STATUS code; the battery is data1.
        return {"kind": "status", "status": d[0], "status_text": STATUS.get(d[0], "?"),
                "battery_pct": d[1], "charging": d[2] == 1}
    if func == 0x03 and cmd in (1, 2, 3, 4) and d:
        return {"kind": "button", "cmd": cmd, "value": d[0],
                "from_device": d[0] >= 2 or (cmd == 1 and d[0] == 1)}
    return {"kind": "other", "frame": frame.hex(" ")}


def join_serial(chunks: dict) -> str | None:
    """SN = chunks 0, 1, 2 (5 chars each). Treat it as an identifier: on our
    units it was derived from the BLE address. SN 은 기기 주소에서 나온 값이었습니다.
    """
    if all(i in chunks for i in (0, 1, 2)):
        return "".join(chunks[i] for i in (0, 1, 2))
    return None


# ── BLE (needs bleak) ──────────────────────────────────────────────────────

async def scan(seconds: float) -> None:
    from bleak import BleakScanner
    found = await BleakScanner.discover(timeout=seconds, return_adv=True)
    rows = []
    for dev, adv in found.values():
        uuids = [u.lower() for u in adv.service_uuids or []]
        model = next((SERVICE_UUIDS[u] for u in uuids if u in SERVICE_UUIDS), None)
        name = adv.local_name or dev.name or ""
        if model is None and name.lower().startswith(NAME_HINTS):
            model = "name match only"
        if model:
            rows.append((adv.rssi, dev.address, name, model))
    for rssi, address, name, model in sorted(rows, reverse=True):
        print(f"{rssi:>4} dBm  {address}  {name:<20} {model}")
    if not rows:
        print("No scale found. Is it on, and not connected to the phone app?")


async def listen(address: str, seconds: float, tare: bool, force: bool = False) -> None:
    from bleak import BleakClient, BleakScanner
    device = await BleakScanner.find_device_by_address(address, timeout=10)
    if device is None:
        print("Scale not found (off, out of range, or connected elsewhere).")
        return
    buf, serial = bytearray(), {}

    def on_notify(_char, data: bytearray) -> None:
        buf.extend(data)
        for frame in split_frames(buf):
            p = decode(frame)
            if p["kind"] == "weight":
                warn = "" if p["unit"] == "g" else "   (not grams — untested unit)"
                print(f"  weight {p['weight']:8.1f} {p['unit']}  tick {p['tick']}{warn}")
            elif p["kind"] == "serial_chunk":
                serial[p["index"]] = p["text"]
                if join_serial(serial):
                    print("  serial received (not printed — it identifies the device)")
            else:
                print(f"  {p}")

    client = BleakClient(device)
    await client.connect()
    try:
        found = {s.uuid.lower() for s in client.services}
        if not any(u in SERVICE_UUIDS for u in found) and not force:
            print("No Microbalance service (00EE / 00DD) on this device — stopping before any command.")
            print("(On an R2 the weight request starts a test. The Ti's 00DD comes from the vendor document;")
            print(" if this really is a scale, rerun with --force.)")
            return
        await client.start_notify(CHAR_UUID, on_notify)
        for command in (GET_SERIAL, GET_FIRMWARE, GET_STATUS):
            await client.write_gatt_char(CHAR_UUID, command, response=True)
            await asyncio.sleep(0.3)
        if tare:
            print("-> tare")
            await client.write_gatt_char(CHAR_UUID, TARE, response=True)
        loop = asyncio.get_running_loop()
        end = loop.time() + seconds
        next_at = loop.time()
        while loop.time() < end:
            await client.write_gatt_char(CHAR_UUID, GET_SENSOR_DATA, response=True)
            next_at = max(next_at + POLL_S, loop.time())   # deadline pacing (~5 Hz); after a stall, re-anchor instead of bursting
            await asyncio.sleep(max(0.0, next_at - loop.time()))
    finally:
        try:
            await client.disconnect()
        except Exception as exc:                   # BlueZ may raise here; harmless
            print(f"(disconnect: {exc!r} — ignored)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="command", required=True)
    s = sub.add_parser("scan", help="list nearby Microbalance scales, strongest first")
    s.add_argument("--seconds", type=float, default=6)
    li = sub.add_parser("listen", help="connect, read status, poll weight")
    li.add_argument("--address", required=True)
    li.add_argument("--seconds", type=float, default=30)
    li.add_argument("--tare", action="store_true", help="tare once after connecting")
    li.add_argument("--force", action="store_true",
                    help="continue even if no 00EE/00DD service is found (Ti GATT is unverified)")
    args = ap.parse_args()
    if args.command == "scan":
        asyncio.run(scan(args.seconds))
    else:
        asyncio.run(listen(args.address, args.seconds, args.tare, args.force))


if __name__ == "__main__":
    main()
