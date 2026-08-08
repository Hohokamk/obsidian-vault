import pytest

from protocol import (
    Command,
    ProtocolError,
    StreamParser,
    crc16_ccitt,
    decode_frame,
    encode_frame,
)


def test_crc_standard_vector():
    assert crc16_ccitt(b"123456789") == 0x29B1


def test_round_trip():
    raw = encode_frame(Command.SET_FRAME, 0x1234, bytes(range(32)))
    frame = decode_frame(raw)
    assert frame.command == Command.SET_FRAME
    assert frame.sequence == 0x1234
    assert frame.payload == bytes(range(32))


def test_crc_rejects_corruption():
    raw = bytearray(encode_frame(Command.PING, 7, b"abc"))
    raw[-3] ^= 0x01
    with pytest.raises(ProtocolError):
        decode_frame(bytes(raw))


def test_stream_parser_fragmented_and_noise():
    first = encode_frame(Command.PING, 1, b"")
    second = encode_frame(Command.GET_STATUS, 2, b"xy")
    parser = StreamParser()
    frames = []
    stream = b"noise" + first + second
    for byte in stream:
        frames.extend(parser.feed(bytes([byte])))
    assert [f.sequence for f in frames] == [1, 2]
    assert frames[1].payload == b"xy"
