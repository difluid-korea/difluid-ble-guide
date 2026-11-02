"""Checks r2_minimal's decoding against frames captured from real R2 units.
실제 R2 캡처 프레임으로 r2_minimal 의 해석을 확인합니다.

    python -m pytest test_r2_minimal.py      # or: python test_r2_minimal.py

No bleak needed. Frames come from ../../r2/captures/ (log number in comments).
"""
import r2_minimal as r2


def hx(s: str) -> bytes:
    return bytes.fromhex(s)


def run(frames: list[str]) -> list[dict]:
    """Feed frames through decode + ResultCollector; return emitted events."""
    collector = r2.ResultCollector()
    events = []
    for f in frames:
        event = collector.feed(r2.decode(hx(f)))
        if event:
            events.append(event)
    return events


def test_commands():
    assert r2.GET_SERIAL == hx("df df 00 00 00 be")
    assert r2.GET_MODEL == hx("df df 00 01 00 bf")
    assert r2.GET_FIRMWARE == hx("df df 00 02 00 c0")
    assert r2.GET_SETTINGS == [hx("df df 01 00 00 bf"), hx("df df 01 01 00 c0"),
                               hx("df df 01 02 00 c1"), hx("df df 01 03 00 c2")]
    assert r2.SINGLE_TEST == hx("df df 03 00 00 c1")
    assert r2.build_frame(0x03, 0x02) == hx("df df 03 02 00 c3")   # calibrate


def test_two_frames_in_one_notification():
    # log 1: "test start" and a hardware error arrived as one 18-byte notify
    buf = r2.FrameBuffer()
    out = buf.push(hx("df df 03 00 03 00 0b 00 cf df df 03 fe 03 00 03 03 c8"))
    assert out == [hx("df df 03 00 03 00 0b 00 cf"), hx("df df 03 fe 03 00 03 03 c8")]
    assert r2.decode(out[1]) == {"kind": "error", "error": "hardware 3"}


def test_frame_split_across_notifications_and_resync():
    buf = r2.FrameBuffer()
    assert buf.push(hx("00 df df 03 00")) == []
    assert buf.push(hx("03 00 0b 00 cf")) == [hx("df df 03 00 03 00 0b 00 cf")]
    # a bad checksum is skipped and the next good frame still comes out
    assert buf.push(hx("df df 03 00 03 00 00 00 c5 df df 03 00 03 00 00 00 c4")) == \
        [hx("df df 03 00 03 00 00 00 c4")]


def test_info_and_settings():
    assert r2.decode(hx("df df 00 01 08 44 46 54 2d 52 31 30 32 b7"))["text"] == "DFT-R102"
    assert r2.decode(hx("df df 00 02 04 56 32 33 30 af"))["text"] == "V230"
    assert r2.decode(hx("df df 01 02 01 64 26")) == \
        {"kind": "setting", "name": "brightness", "value": 100}
    assert r2.decode(hx("df df 01 03 01 03 c6"))["value"] == 3


def test_single_coffee():   # log 5
    events = run(["df df 03 00 03 00 0b 00 cf",
                  "df df 03 00 03 00 00 00 c4",
                  "df df 03 00 06 01 00 bb 00 b3 00 36",
                  "df df 03 00 07 02 03 2b 00 02 0e 55 5d"])
    assert events == [{"kind": "result", "mode": "single", "tds": 8.11,
                       "ri": 1.34741, "prism_c": 18.7, "sample_c": 17.9}]


def test_single_water_is_negative_and_start_may_be_missed():   # log 2, first result
    events = run(["df df 03 00 03 00 00 00 c4",          # no "test start"
                  "df df 03 00 06 01 00 d1 00 d2 00 6b",
                  "df df 03 00 07 02 ff 91 00 02 07 ef 52"])
    assert events[0]["tds"] == -1.11 and events[0]["ri"] == 1.33103


def test_no_liquid():   # log 2
    events = run(["df df 03 00 03 00 0b 00 cf", "df df 03 fe 03 00 02 03 c7"])
    assert events == [{"kind": "error", "error": "no liquid"}]


AVG_A = [   # log 6, first average (3 rounds)
    "df df 03 01 03 00 04 00 c9",
    "df df 03 01 03 00 05 00 ca", "df df 03 01 06 01 00 af 00 a9 00 21",
    "df df 03 01 07 02 03 2e 00 02 0e 59 65", "df df 03 01 07 03 03 2e 00 0c 6c 14 89",
    "df df 03 01 07 04 00 af 00 a9 01 03 29",
    "df df 03 01 03 00 05 00 ca", "df df 03 01 06 01 00 af 00 a9 00 21",
    "df df 03 01 07 02 03 2f 00 02 0e 5c 69", "df df 03 01 07 03 03 2f 00 0c 6f fc 75",
    "df df 03 01 07 04 00 af 00 a9 02 03 2a",
    "df df 03 01 03 00 05 00 ca", "df df 03 01 06 01 00 af 00 a9 00 21",
    "df df 03 01 07 02 03 2f 00 02 0e 5b 68", "df df 03 01 07 03 03 2f 00 0c 6f fc 75",
    "df df 03 01 07 04 00 af 00 a9 03 03 2b",
    "df df 03 01 03 00 06 00 cb",
]


def test_average_rounds_and_result():
    events = run(AVG_A)
    progress = [(e["n"], e["this"], e["avg"]) for e in events if e["kind"] == "progress"]
    assert progress == [(1, 8.14, 8.14), (2, 8.15, 8.15), (3, 8.15, 8.15)]
    assert events[-1] == {"kind": "result", "mode": "average", "tds": 8.15,
                          "rounds": 3, "prism_c": 17.5, "sample_c": 16.9}


def test_average_cut_short_is_rejected():
    # round 1 of 3 from log 5, then an end marker (synthetic): must be rejected
    events = run(["df df 03 01 03 00 04 00 c9",
                  "df df 03 01 03 00 05 00 ca", "df df 03 01 06 01 00 ba 00 b2 00 35",
                  "df df 03 01 07 02 03 2b 00 02 0e 55 5e",
                  "df df 03 01 07 03 03 2b 00 0c 60 5c c2",
                  "df df 03 01 07 04 00 ba 00 b2 01 03 3d",
                  "df df 03 01 03 00 06 00 cb"])
    assert events[-1] == {"kind": "error", "error": "incomplete average"}


def test_calibration_success():   # log 8
    events = run(["df df 03 02 03 00 0c 00 d2", "df df 03 02 03 00 01 00 c7",
                  "df df 03 02 06 01 00 db 00 d7 00 7c",
                  "df df 03 02 07 02 00 00 00 02 08 b3 89"])
    assert events == [{"kind": "result", "mode": "calibration", "tds": 0.0,
                       "ri": 1.33299, "prism_c": 21.9, "sample_c": 21.5}]


def test_fahrenheit_is_converted():
    body = hx("df df 03 00 06 01 02 a8 02 a8 01")   # synthetic: 68.0 °F, unit 1
    frame = body + bytes([sum(body) & 0xFF])
    events = run(["df df 03 00 03 00 00 00 c4", frame.hex(),
                  "df df 03 00 07 02 03 2b 00 02 0e 55 5d"])
    assert events[0]["prism_c"] == 20.0


if __name__ == "__main__":
    import sys
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    print(f"{len(tests)} tests passed")
    sys.exit(0)
