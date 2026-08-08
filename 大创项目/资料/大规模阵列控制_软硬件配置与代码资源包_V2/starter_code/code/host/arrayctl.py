#!/usr/bin/env python3
"""Command-line controller for the 256-channel array.

Use --dry-run before hardware is available. It prints the exact protocol frame.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from patterns import (
    border,
    checkerboard,
    empty,
    full,
    load_config,
    load_pattern,
    one,
    pack_pattern,
    random_pattern,
)
from protocol import Command, encode_frame, hex_bytes

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config" / "array_config.yaml"


def list_ports() -> int:
    try:
        import serial.tools.list_ports
    except ImportError as exc:
        raise RuntimeError("pyserial is required for port discovery; install requirements.txt") from exc
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return 1
    for port in ports:
        print(f"{port.device}\t{port.description}\t{port.hwid}")
    return 0


def make_payload(args, config):
    if args.action == "off":
        return Command.ALL_OFF, b""
    if args.action == "on":
        pattern = full(config)
    elif args.action == "one":
        pattern = one(config, args.row, args.col)
    elif args.action == "checker":
        pattern = checkerboard(config, args.invert)
    elif args.action == "border":
        pattern = border(config)
    elif args.action == "random":
        pattern = random_pattern(config, args.seed, args.density)
    elif args.action == "send":
        pattern = load_pattern(args.file)
    elif args.action == "ping":
        return Command.PING, b""
    elif args.action == "status":
        return Command.GET_STATUS, b""
    else:
        raise ValueError(f"unsupported action: {args.action}")
    return Command.SET_FRAME, pack_pattern(pattern, config)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--port")
    p.add_argument("--baud", type=int, default=921600)
    p.add_argument("--timeout", type=float, default=0.5)
    p.add_argument("--dry-run", action="store_true")
    sub = p.add_subparsers(dest="action", required=True)
    sub.add_parser("ports")
    sub.add_parser("ping")
    sub.add_parser("status")
    sub.add_parser("off")
    sub.add_parser("on")
    one_p = sub.add_parser("one")
    one_p.add_argument("--row", type=int, required=True)
    one_p.add_argument("--col", type=int, required=True)
    checker_p = sub.add_parser("checker")
    checker_p.add_argument("--invert", action="store_true")
    sub.add_parser("border")
    random_p = sub.add_parser("random")
    random_p.add_argument("--seed", type=int, default=2026)
    random_p.add_argument("--density", type=float, default=0.5)
    send_p = sub.add_parser("send")
    send_p.add_argument("file", type=Path)
    return p


def main() -> int:
    args = build_parser().parse_args()
    if args.action == "ports":
        return list_ports()
    config = load_config(args.config)
    command, payload = make_payload(args, config)
    if args.dry_run:
        raw = encode_frame(command, 0, payload)
        print(f"command={command.name} payload_bytes={len(payload)}")
        print(hex_bytes(raw))
        return 0
    if not args.port:
        print("error: --port is required unless --dry-run is used", file=sys.stderr)
        return 2
    try:
        from device import ArrayDevice
    except ImportError as exc:
        print("error: pyserial is required for hardware access; install requirements.txt", file=sys.stderr)
        return 2
    with ArrayDevice(args.port, args.baud, args.timeout) as device:
        reply = device.transact(command, payload)
        print(
            f"ACK seq={reply.frame.sequence} status={reply.frame.payload[0]} "
            f"round_trip_ms={reply.round_trip_ms:.3f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
