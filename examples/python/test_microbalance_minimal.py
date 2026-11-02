"""Checks microbalance_minimal's decoding against frames captured from real scales.
실제 저울에서 캡처한 프레임으로 microbalance_minimal 의 해석을 확인합니다.

    python -m pytest test_microbalance_minimal.py      # or: python test_microbalance_minimal.py

No bleak needed. Frames marked "synthetic" were made up for the test, the one marked
"vendor" is the vendor document's example, and the rest were captured on real scales
(see ../../microbalance/verification.md §3).
「synthetic」은 시험용으로 만든 값, 「vendor」는 벤더 문서 예시이고, 나머지는 실제 저울에서 캡처했습니다.
"""
import microbalance_minimal as mb


def hx(s: str) -> bytes:
    return bytes.fromhex(s)


# Captured on a Microbalance while removing a 394.0 g weight.
W394 = "df df 03 00 0d 00 00 0f 64 00 00 00 00 00 07 57 88 00 27"
W305 = "df df 03 00 0d 00 00 0b f3 00 00 00 00 00 07 5e e0 00 11"
W000 = "df df 03 00 0d 00 00 00 00 00 00 00 00 00 07 60 e8 00 1d"
# Captured on a Microbalance Ti: Idle, battery 63 %, not charging.
STATUS = "df df 03 05 08 05 3f 00 00 00 00 00 00 12"


def test_commands():
    assert mb.GET_SERIAL == hx("df df 00 00 00 be")
    assert mb.GET_FIRMWARE == hx("df df 00 02 00 c0")
    assert mb.GET_SENSOR_DATA == hx("df df 03 00 00 c1")
    assert mb.GET_STATUS == hx("df df 03 05 00 c6")
    # Every byte matters: without the trailing data byte 01 the scale ignores tare.
    assert mb.TARE == hx("df df 03 02 01 01 c5")
    assert mb.TARE != hx("df df 03 02 00 c3")


def test_weight_frames():
    got = [mb.decode(hx(f)) for f in (W394, W305, W000)]
    assert [g["weight"] for g in got] == [394.0, 305.9, 0.0]
    assert all(g["unit"] == "g" and g["flow_raw"] == 0 and g["time_raw"] == 0 for g in got)
    assert [g["tick"] for g in got] == [481160, 483040, 483560]


def test_status_battery_is_data1():
    s = mb.decode(hx(STATUS))
    assert s == {"kind": "status", "status": 5, "status_text": "idle",
                 "battery_pct": 63, "charging": False}


def test_two_frames_in_one_notification():
    # synthetic SN text; layout as seen on the Ti: chunks 0 and 1 in one 24-byte notification
    c0 = mb.build_frame(0x00, 0x00, b"\x00ABCDE")
    c1 = mb.build_frame(0x00, 0x00, b"\x01FGHIJ")
    c2 = mb.build_frame(0x00, 0x00, b"\x02KL000")
    buf = bytearray(c0 + c1)
    frames = mb.split_frames(buf)
    assert frames == [c0, c1] and not buf
    chunks = {}
    for f in frames + [c2]:
        p = mb.decode(f)
        chunks[p["index"]] = p["text"]
    assert mb.join_serial(chunks) == "ABCDEFGHIJKL000"


def test_split_across_notifications_and_bad_checksum():
    buf = bytearray(hx(W394)[:7])
    assert mb.split_frames(buf) == []
    buf.extend(hx(W394)[7:])
    assert mb.split_frames(buf) == [hx(W394)]
    bad = bytearray(hx(STATUS)[:-1] + b"\x00" + hx(W000))   # broken checksum, then a good frame
    assert mb.split_frames(bad) == [hx(W000)]


def test_vendor_example_still_decodes():
    # vendor document example (not captured): 76 g — same len-13 layout as the captured frames
    assert mb.decode(hx("df df 03 00 0d 00 00 02 f8 00 00 00 00 00 0a 27 b0 00 a9"))["weight"] == 76.0


def test_device_trigger_flag():
    # synthetic: user pressed the power button on the scale (vendor value 3)
    p = mb.decode(mb.build_frame(0x03, 0x02, b"\x03"))
    assert p["kind"] == "button" and p["from_device"]
    assert not mb.decode(mb.build_frame(0x03, 0x02, b"\x01"))["from_device"]


if __name__ == "__main__":
    import sys
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    print(f"{len(tests)} tests passed")
    sys.exit(0)
