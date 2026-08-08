"""Binary protocol shared by the Python host and STM32 firmware.

Frame layout (little-endian):
    A5 5A | version:u8 | command:u8 | sequence:u16 | length:u16 |
    payload[length] | crc16:u16

CRC16-CCITT-FALSE covers version through payload, not SOF or CRC itself.
Polynomial 0x1021, initial value 0xFFFF, no reflection, xorout 0x0000.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
import struct
from typing import Iterable

SOF = b"\xA5\x5A"
VERSION = 1
HEADER_AFTER_SOF = struct.Struct("<BBHH")
CRC_STRUCT = struct.Struct("<H")
MAX_PAYLOAD = 4096


class Command(IntEnum):
    PING = 0x01
    SET_FRAME = 0x02
    SET_ONE = 0x03
    ALL_OFF = 0x04
    GET_STATUS = 0x05
    PLAY = 0x06
    STOP = 0x07
    SET_RATE = 0x08
    ACK = 0x80


class Status(IntEnum):
    OK = 0
    BAD_CRC = 1
    BAD_LENGTH = 2
    BAD_COMMAND = 3
    BUSY = 4
    OUT_OF_RANGE = 5
    DRIVER_ERROR = 6
    TIMEOUT = 7


class ProtocolError(ValueError):
    """Raised when a complete frame is malformed."""


@dataclass(frozen=True, slots=True)
class Frame:
    version: int
    command: int
    sequence: int
    payload: bytes

    def encode(self) -> bytes:
        return encode_frame(self.command, self.sequence, self.payload, self.version)


def crc16_ccitt(data: bytes, initial: int = 0xFFFF) -> int:
    """Return CRC-16/CCITT-FALSE."""
    crc = initial & 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def encode_frame(
    command: int | Command,
    sequence: int,
    payload: bytes | bytearray | memoryview = b"",
    version: int = VERSION,
) -> bytes:
    payload_bytes = bytes(payload)
    if len(payload_bytes) > MAX_PAYLOAD:
        raise ValueError(f"payload too large: {len(payload_bytes)} > {MAX_PAYLOAD}")
    if not 0 <= sequence <= 0xFFFF:
        raise ValueError("sequence must fit uint16")
    body = HEADER_AFTER_SOF.pack(
        version & 0xFF,
        int(command) & 0xFF,
        sequence,
        len(payload_bytes),
    ) + payload_bytes
    return SOF + body + CRC_STRUCT.pack(crc16_ccitt(body))


def decode_frame(raw: bytes) -> Frame:
    minimum = len(SOF) + HEADER_AFTER_SOF.size + CRC_STRUCT.size
    if len(raw) < minimum:
        raise ProtocolError("frame too short")
    if raw[:2] != SOF:
        raise ProtocolError("bad SOF")
    version, command, sequence, length = HEADER_AFTER_SOF.unpack_from(raw, 2)
    if length > MAX_PAYLOAD:
        raise ProtocolError("payload length exceeds limit")
    expected = minimum + length
    if len(raw) != expected:
        raise ProtocolError(f"length mismatch: expected {expected}, got {len(raw)}")
    body_end = 2 + HEADER_AFTER_SOF.size + length
    body = raw[2:body_end]
    received_crc = CRC_STRUCT.unpack_from(raw, body_end)[0]
    calculated_crc = crc16_ccitt(body)
    if received_crc != calculated_crc:
        raise ProtocolError(
            f"bad CRC: received 0x{received_crc:04X}, calculated 0x{calculated_crc:04X}"
        )
    payload = raw[2 + HEADER_AFTER_SOF.size : body_end]
    return Frame(version, command, sequence, payload)


class StreamParser:
    """Incremental parser for a serial byte stream.

    Invalid bytes before SOF are discarded. A CRC failure discards the first
    SOF byte and resumes searching, so the parser can recover from corruption.
    """

    def __init__(self, max_payload: int = MAX_PAYLOAD) -> None:
        self.buffer = bytearray()
        self.max_payload = max_payload
        self.errors = 0

    def feed(self, data: bytes | bytearray | memoryview) -> list[Frame]:
        self.buffer.extend(data)
        frames: list[Frame] = []
        minimum = len(SOF) + HEADER_AFTER_SOF.size + CRC_STRUCT.size

        while True:
            sof_index = self.buffer.find(SOF)
            if sof_index < 0:
                # Keep a trailing 0xA5 because it may be the first SOF byte.
                self.buffer[:] = self.buffer[-1:] if self.buffer[-1:] == SOF[:1] else b""
                break
            if sof_index:
                del self.buffer[:sof_index]
            if len(self.buffer) < minimum:
                break

            _, _, _, length = HEADER_AFTER_SOF.unpack_from(self.buffer, 2)
            if length > self.max_payload:
                self.errors += 1
                del self.buffer[0]
                continue
            total = minimum + length
            if len(self.buffer) < total:
                break
            candidate = bytes(self.buffer[:total])
            try:
                frames.append(decode_frame(candidate))
            except ProtocolError:
                self.errors += 1
                del self.buffer[0]
                continue
            del self.buffer[:total]
        return frames


def hex_bytes(data: Iterable[int]) -> str:
    return " ".join(f"{int(value) & 0xFF:02X}" for value in data)
