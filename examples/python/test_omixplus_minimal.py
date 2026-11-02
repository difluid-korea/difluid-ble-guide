"""Checks omixplus_minimal's decoding against frames captured from a real Omix Plus.
실제 Omix Plus 에서 캡처한 프레임으로 omixplus_minimal 의 해석을 확인한다.

    python -m pytest test_omixplus_minimal.py      # or: python test_omixplus_minimal.py

No bleak needed. Frames come from ../../omixplus/captures/ (file name in comments),
captured by 이승진 (180 Coffee Roasters). Frames marked "synthetic" were made up for the test.
캡처는 이승진(180커피로스터스) 제공. 「synthetic」은 시험용으로 만든 값이다.
"""
import omixplus_minimal as om


def hx(s: str) -> bytes:
    return bytes.fromhex(s)


# whole-normal.jsonl — color 53.4, moisture 1.2 %, density 387.3
WHOLE = [
    "dfdf03032c649eda6a00000000230300000104000013000000ae47f140983e9f3f00c0004400000000d8a3c1433333904209",
    "dfdf030578649eda6a000000002303000002000000f99b5542971f0042000000000000000000000000000000000000000000"
    "0000000000000000000000000000000000000000000000000000000000000000000000010308080605040405050606050505"
    "050403030202020101010100000000000021090b0b0a09060b98",
    "dfdf03061c649eda6a00000000230300007ed3ae4121000000a571cb42ceffffff9e",
]
# environment-reference.jsonl — 24.7 °C, 31 %RH matched against the device screen
ENV = [
    "dfdf03032ca0b6da6a000000002d030000010400001700000085eb11414083ea3fb7ed1944000000003282e7436666ac421d",
    "dfdf030578a0b6da6a000000002d03000002000000f0458542ac5e1642000000000000000000000000000000000000000000"
    "0000000000000000000000000000000000000000000000000000000000000000000000010003060605050403040404040505"
    "05040404040303030202020101010101011a0708090a09081731",
    "dfdf03061ca0b6da6a000000002d030000c4c3c5411f0000007448cb42ceffffffed",
]
# ground.jsonl — ground mode, color only
GROUND = [
    "dfdf03032c0040d86a00000000ce020000010500000000000000000000504a9bbf000000000000000000000000000000003c",
    "dfdf0305780040d86a00000000ce02000002000000fe0e614267ffbf41000000000000000000000000000000000000000000"
    "0000000000000000000000000000000000000000000000000000000000000000000000010101020303040506070708080807"
    "07060504030201010100000000000000000e0c0e100f0c090870",
    "dfdf03061c0040d86a00000000ce0200008b89b9411f0000008d14ca42000000000f",
]
# not-available.jsonl — negative moisture, zero density
NA = [
    "dfdf03032c3ef8d76a00000000ae020000010400000000000000000000d00f85bf000000000000000000000000000000003f",
    "dfdf0305783ef8d76a00000000ae02000002000000d61bc040c01fbb40000000000000000000000000000000000000000000"
    "0000000000000000000000000000000000000000000000000000000000000000000000013d0f0a0704020100000000000000"
    "00000000000000000000000000000000006301000000000000fb",
    "dfdf03061c3ef8d76a00000000ae020000161cae412d0000002c93c9423200000054",
]
# mtu23-truncated.jsonl — each notification cut to 20 bytes at MTU 23
CUT = [
    "dfdf03032cd7f5d76a00000000ad020000010400",
    "dfdf030578d7f5d76a00000000ad020000020000",
    "dfdf03061cd7f5d76a00000000ad020000e72daf",
]


def collect(frames, reverse=False):
    c, result = om.MeasurementCollector(), None
    for f in (frames[::-1] if reverse else frames):
        for p in om.parse_notification(hx(f)):
            r = c.feed(p)
            if r:
                result = r
    return result


def test_lengths_and_checksums():
    for frames in (WHOLE, ENV, GROUND, NA):
        for f in frames:
            b = hx(f)
            assert len(b) == b[4] + 6 and sum(b[:-1]) & 0xFF == b[-1]
            (p,) = om.parse_notification(b)
            assert p["kind"] in ("quality", "color", "ambient")


def test_whole_bean():
    r = collect(WHOLE)
    assert r == {"kind": "result", "id": (1792712292, 803), "mode": "whole", "color": 53.4,
                 "moisture": 1.2, "density": 387.3, "temp_c": 21.9, "rh_pct": 33}


def test_ambient_matches_screen():
    r = collect(ENV)
    assert (r["temp_c"], r["rh_pct"]) == (24.7, 31)
    assert (r["color"], r["moisture"], r["density"]) == (66.6, 1.8, 463.0)


def test_ground_kept_apart():
    r = collect(GROUND)
    assert r["mode"] == "ground" and r["ground_color"] == 56.3 and "color" not in r
    assert r["moisture"] is None and r["density"] is None


def test_no_value_is_none_not_zero():
    r = collect(NA)
    assert r["moisture"] is None and r["density"] is None and r["color"] == 6.0


def test_order_does_not_matter():
    assert collect(WHOLE) == collect(WHOLE, reverse=True)


def test_truncated_frames_are_reported():
    got = [om.parse_notification(hx(f)) for f in CUT]
    assert [g[0]["kind"] for g in got] == ["truncated"] * 3
    assert [(g[0]["have"], g[0]["need"]) for g in got] == [(20, 50), (20, 126), (20, 34)]


def test_repeats_dropped():
    c = om.MeasurementCollector()
    for f in WHOLE:
        (p,) = om.parse_notification(hx(f))
        c.feed(p)
        assert c.feed(p) is None


def test_older_measurement_does_not_replace_newer():
    # ENV (10-23 01:21 UTC, counter 813) is newer than WHOLE (10-22 23:38 UTC, counter 803)
    c = om.MeasurementCollector()
    for f in ENV:
        (p,) = om.parse_notification(hx(f))
        c.feed(p)
    for f in WHOLE:
        (p,) = om.parse_notification(hx(f))
        assert c.feed(p) is None


def test_different_ids_not_merged():
    # synthetic: the quality frame's counter changed and the checksum fixed
    q = bytearray(hx(WHOLE[0]))
    q[13] ^= 0x01
    q[-1] = sum(q[:-1]) & 0xFF
    assert collect([bytes(q).hex(), WHOLE[1], WHOLE[2]]) is None


def test_bad_checksum_skipped():
    # synthetic: broken checksum, then a good frame in the same buffer
    bad = hx(WHOLE[2])[:-1] + b"\x00"
    got = om.parse_notification(bad + hx(ENV[2]))
    assert got[0]["kind"] == "bad_checksum" and got[-1]["kind"] == "ambient"


def test_big_endian_would_be_wrong():
    # the color bytes F9 9B 55 42 read big-endian are nonsense; little-endian gives 53.4
    import struct
    b = hx(WHOLE[1])
    assert round(struct.unpack_from("<f", b, 21)[0], 1) == 53.4
    assert abs(struct.unpack_from(">f", b, 21)[0]) > 1e30


if __name__ == "__main__":
    import sys
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
    print(f"{len(tests)} tests passed")
    sys.exit(0)
