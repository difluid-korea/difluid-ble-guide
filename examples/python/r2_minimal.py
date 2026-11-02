#!/usr/bin/env python3
"""DiFluid R2 Extract — minimal BLE example / 최소 BLE 예제.

Reads device info and settings, optionally starts one single test, and prints
every frame and every finished result while listening. Settings are never
written.
기기 정보·설정을 읽고, 원하면 단일 측정을 한 번 걸고, 듣는 동안 오는 프레임과
측정 결과를 출력합니다. 설정은 쓰지 않습니다.

    pip install bleak
    python r2_minimal.py scan
    python r2_minimal.py listen --address <ADDRESS> --seconds 60 [--single]

The decoding part (build_frame … ResultCollector) has no dependencies and can be
used on its own. Protocol notes: ../../r2/protocol.md
해석 부분(build_frame … ResultCollector)은 의존성이 없어 따로 쓸 수 있습니다.
"""
from __future__ import annotations

import argparse
import asyncio

SERVICE_UUID = "000000ff-0000-1000-8000-00805f9b34fb"
CHAR_UUID = "0000aa01-0000-1000-8000-00805f9b34fb"   # commands and responses
NAME_PREFIX = "difluid r2"                            # e.g. "DiFluid R2 123456"
MAX_DATA_LEN = 20                                     # vendor: max 20 data bytes


# ── Frames / 프레임 ────────────────────────────────────────────────────────

def build_frame(func: int, cmd: int, data: bytes = b"") -> bytes:
    """DF DF func cmd len data… sum — sum is the low byte of the byte total."""
    head = bytes([0xDF, 0xDF, func, cmd, len(data)]) + bytes(data)
    return head + bytes([sum(head) & 0xFF])


GET_SERIAL = build_frame(0x00, 0x00)        # DF DF 00 00 00 BE
GET_MODEL = build_frame(0x00, 0x01)         # DF DF 00 01 00 BF
GET_FIRMWARE = build_frame(0x00, 0x02)      # DF DF 00 02 00 C0
GET_SETTINGS = [build_frame(0x01, k) for k in range(4)]   # unit, auto, brightness, tests
SINGLE_TEST = build_frame(0x03, 0x00)       # DF DF 03 00 00 C1


class FrameBuffer:
    """Collects notification bytes and returns complete, checksum-valid frames.

    One notification may hold several frames; a frame may (in theory) span two.
    notify 하나에 프레임이 여럿일 수 있고, 한 프레임이 둘로 나뉠 수도 있습니다(이론상 — 실측에서는 보지 못함).
    """

    def __init__(self) -> None:
        self.buf = bytearray()

    def push(self, chunk: bytes) -> list[bytes]:
        self.buf += chunk
        frames = []
        while True:
            start = self.buf.find(b"\xdf\xdf")
            if start < 0:
                # keep a lone trailing 0xDF: it may be the first header byte
                keep = 1 if self.buf.endswith(b"\xdf") else 0
                del self.buf[:len(self.buf) - keep]
                return frames
            del self.buf[:start]
            if len(self.buf) < 5:
                return frames
            length = self.buf[4]
            if length > MAX_DATA_LEN:
                del self.buf[:1]                 # bad length byte: resync
                continue
            size = 6 + length
            if len(self.buf) < size:
                return frames                    # wait for the rest
            frame = bytes(self.buf[:size])
            if sum(frame[:-1]) & 0xFF != frame[-1]:
                del self.buf[:1]                 # bad checksum: resync
                continue
            frames.append(frame)
            del self.buf[:size]


# ── Decoding / 해석 ────────────────────────────────────────────────────────

MODES = {0x00: "single", 0x01: "average", 0x02: "calibration"}
STATUS = {0: "test finished", 1: "calibration finished", 4: "average start",
          5: "average round", 6: "average finished", 7: "loop start",
          8: "loop ongoing", 9: "loop finished", 10: "average keep-alive",
          11: "test start", 12: "calibration start"}
SETTINGS = {0: "unit", 1: "auto_test", 2: "brightness", 3: "tests"}
GENERAL_ERRORS = {1: "test error", 2: "calibration failed", 3: "no liquid",
                  4: "beyond range"}


def _i16(b: bytes) -> int:
    return int.from_bytes(b, "big", signed=True)


def _celsius(raw: int, unit: int) -> float:
    value = raw / 10
    return round((value - 32) * 5 / 9 if unit == 1 else value, 1)


def decode(frame: bytes) -> dict:
    """One frame -> dict with a "kind" key."""
    func, cmd, data = frame[2], frame[3], frame[5:-1]
    if func == 0x00:
        if cmd == 0x00 and data:
            return {"kind": "serial_chunk", "index": data[0],
                    "text": data[1:].decode("ascii", "replace")}
        names = {0x01: "model", 0x02: "firmware"}
        return {"kind": names.get(cmd, f"info_{cmd}"),
                "text": data.decode("ascii", "replace")}
    if func == 0x01:
        return {"kind": "setting", "name": SETTINGS.get(cmd, cmd),
                "value": data[0] if data else None}
    if func != 0x03:
        return {"kind": "unknown", "frame": frame.hex(" ")}
    if cmd == 0xFE:
        # device layout: data0 = package, data1 = class, data2 = code
        # (the vendor table is shifted by one byte)
        cls, code = (data[1], data[2]) if len(data) >= 3 else (None, None)
        if cls == 2:
            what = GENERAL_ERRORS.get(code, f"general {code}")
        elif cls == 3:
            what = f"hardware {code}"            # number shown on the R2 screen
        else:
            what = f"class {cls} code {code}"
        return {"kind": "error", "error": what}
    if cmd == 0xFF:
        return {"kind": "error", "error": "unknown error"}
    mode = MODES.get(cmd, f"cmd_{cmd}")
    pkg = data[0] if data else None
    if pkg == 0 and len(data) >= 2:
        return {"kind": "status", "mode": mode, "status": data[1],
                "text": STATUS.get(data[1], "?")}
    if pkg == 1 and len(data) >= 6:
        return {"kind": "temperature", "mode": mode, "unit": data[5],
                "prism_raw": _i16(data[1:3]), "sample_raw": _i16(data[3:5])}
    if pkg == 2 and len(data) >= 3:
        ri = int.from_bytes(data[3:7], "big") / 100000 if len(data) >= 7 else None
        return {"kind": "reading", "mode": mode,
                "tds": _i16(data[1:3]) / 100, "ri": ri}      # signed!
    if pkg == 3 and len(data) >= 3:
        # data3-6 is NOT an average refractive index; ignored.
        return {"kind": "average", "mode": mode, "tds": _i16(data[1:3]) / 100}
    if pkg == 4 and len(data) >= 7:
        return {"kind": "round", "mode": mode, "n": data[5], "total": data[6],
                "prism_raw": _i16(data[1:3]), "sample_raw": _i16(data[3:5])}
    return {"kind": "unknown", "frame": frame.hex(" ")}


class ResultCollector:
    """Decoded frames -> finished results (single, average, calibration).

    Accepts a single result only after "test finished"; an average only when
    the last round reports current == total. Works even if the start frame was
    missed (connected mid-test).
    「측정 끝」 뒤의 결과만, 평균은 마지막 회차(현재 = 전체)만 받습니다. 시작
    프레임을 놓쳐도 동작합니다.
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.mode = None
        self.finished = False      # single/calibration: end marker seen
        self.unit = 0
        self.temps = None
        self.round = {}

    def feed(self, p: dict):
        kind = p["kind"]
        if kind == "error":
            self.reset()
            return p
        mode = p.get("mode")
        if kind == "status":
            s = p["status"]
            if s in (11, 12, 4):                       # a new test starts
                self.reset()
                self.mode = mode
            elif s in (0, 1):                          # single/calibration end
                if self.mode not in (None, mode):
                    self.reset()
                self.mode, self.finished = mode, True
            elif s == 5:                               # next average round
                self.mode, self.round = "average", {}
            elif s == 6 and self.mode == "average":
                r, self.mode = self.round, None
                if r.get("n") is not None and r.get("n") == r.get("total") \
                        and "avg" in r:
                    result = {"kind": "result", "mode": "average",
                              "tds": r["avg"], "rounds": r["total"],
                              "prism_c": r.get("prism_c"),
                              "sample_c": r.get("sample_c")}
                    self.reset()
                    return result
                self.reset()
                return {"kind": "error", "error": "incomplete average"}
            return None
        if self.mode is None or mode != self.mode:
            return None                                # no context: drop
        if kind == "temperature":
            self.unit = p["unit"]
            self.temps = (_celsius(p["prism_raw"], self.unit),
                          _celsius(p["sample_raw"], self.unit))
        elif self.mode == "average":
            if kind == "reading":
                self.round["this"] = p["tds"]
            elif kind == "average":
                self.round["avg"] = p["tds"]
            elif kind == "round":
                self.round.update(n=p["n"], total=p["total"],
                                  prism_c=_celsius(p["prism_raw"], self.unit),
                                  sample_c=_celsius(p["sample_raw"], self.unit))
                return {"kind": "progress", "n": p["n"], "total": p["total"],
                        "this": self.round.get("this"),
                        "avg": self.round.get("avg")}
        elif kind == "reading" and self.finished:
            prism, sample = self.temps or (None, None)
            result = {"kind": "result", "mode": self.mode, "tds": p["tds"],
                      "ri": p["ri"], "prism_c": prism, "sample_c": sample}
            self.reset()
            return result
        return None


# ── BLE (needs bleak) / BLE (bleak 필요) ──────────────────────────────────

async def scan(seconds: float) -> None:
    from bleak import BleakScanner
    found = await BleakScanner.discover(timeout=seconds, return_adv=True)
    rows = [(adv.rssi, dev.address, adv.local_name or dev.name or "")
            for dev, adv in found.values()]
    rows = [r for r in rows if r[2].lower().startswith(NAME_PREFIX)]
    for rssi, address, name in sorted(rows, reverse=True):   # strongest first
        print(f"{rssi:>4} dBm  {address}  {name}")
    if not rows:
        print("No R2 found. Is it on, and not connected to the phone app?")


async def listen(address: str, seconds: float, single: bool) -> None:
    from bleak import BleakClient, BleakScanner
    device = await BleakScanner.find_device_by_address(address, timeout=10)
    if device is None:
        print("R2 not found (off, out of range, or connected elsewhere).")
        return
    frames, results = FrameBuffer(), ResultCollector()

    def on_notify(_char, data: bytearray) -> None:
        for frame in frames.push(bytes(data)):
            packet = decode(frame)
            print(f"  <- {frame.hex(' ')}   {packet}")
            event = results.feed(packet)
            if event:
                print(f"  ** {event}")

    client = BleakClient(device)
    await client.connect()
    try:
        await client.start_notify(CHAR_UUID, on_notify)
        for command in [GET_SERIAL, GET_MODEL, GET_FIRMWARE, *GET_SETTINGS]:
            print(f"-> {command.hex(' ')}")
            await client.write_gatt_char(CHAR_UUID, command, response=True)
            await asyncio.sleep(0.3)
        if single:
            print(f"-> {SINGLE_TEST.hex(' ')}   (single test)")
            await client.write_gatt_char(CHAR_UUID, SINGLE_TEST, response=True)
        print(f"Listening {seconds:.0f} s — the R2's own button works too.")
        await asyncio.sleep(seconds)
    finally:
        try:
            await client.disconnect()
        except Exception as exc:                 # BlueZ may raise EOFError here
            print(f"(disconnect: {exc!r} — ignored)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="command", required=True)
    s = sub.add_parser("scan", help="list nearby R2 units, strongest first")
    s.add_argument("--seconds", type=float, default=6)
    li = sub.add_parser("listen", help="connect, read info, print frames")
    li.add_argument("--address", required=True)
    li.add_argument("--seconds", type=float, default=60)
    li.add_argument("--single", action="store_true", help="send one single test")
    args = ap.parse_args()
    if args.command == "scan":
        asyncio.run(scan(args.seconds))
    else:
        asyncio.run(listen(args.address, args.seconds, args.single))


if __name__ == "__main__":
    main()
