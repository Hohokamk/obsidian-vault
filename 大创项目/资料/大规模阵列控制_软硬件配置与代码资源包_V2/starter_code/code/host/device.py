"""Serial transport for the array controller."""

from __future__ import annotations

from dataclasses import dataclass
import time

import serial

from protocol import Command, Frame, Status, StreamParser, encode_frame


class DeviceError(RuntimeError):
    pass


@dataclass(slots=True)
class Reply:
    frame: Frame
    round_trip_ms: float


class ArrayDevice:
    def __init__(self, port: str, baudrate: int = 921600, timeout: float = 0.5) -> None:
        self.serial = serial.Serial(port, baudrate=baudrate, timeout=0.05, write_timeout=timeout)
        self.timeout = timeout
        self.sequence = 0
        self.parser = StreamParser()

    def close(self) -> None:
        self.serial.close()

    def __enter__(self) -> "ArrayDevice":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def next_sequence(self) -> int:
        value = self.sequence
        self.sequence = (self.sequence + 1) & 0xFFFF
        return value

    def transact(self, command: Command, payload: bytes = b"", retries: int = 2) -> Reply:
        sequence = self.next_sequence()
        raw = encode_frame(command, sequence, payload)
        last_error: Exception | None = None
        for _ in range(retries + 1):
            self.serial.reset_input_buffer()
            start = time.perf_counter()
            self.serial.write(raw)
            self.serial.flush()
            deadline = start + self.timeout
            while time.perf_counter() < deadline:
                chunk = self.serial.read(self.serial.in_waiting or 1)
                for frame in self.parser.feed(chunk):
                    if frame.command != Command.ACK or frame.sequence != sequence:
                        continue
                    if not frame.payload:
                        raise DeviceError("ACK has no status byte")
                    status = Status(frame.payload[0])
                    if status is not Status.OK:
                        raise DeviceError(f"device returned {status.name}")
                    return Reply(frame, (time.perf_counter() - start) * 1000.0)
            last_error = TimeoutError(f"timeout waiting for sequence {sequence}")
        raise DeviceError(str(last_error))
