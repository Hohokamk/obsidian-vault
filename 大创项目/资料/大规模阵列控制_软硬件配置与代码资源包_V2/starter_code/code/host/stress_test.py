#!/usr/bin/env python3
"""Repeatable random-frame stress test."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import time

from device import ArrayDevice, DeviceError
from patterns import load_config, pack_pattern, random_pattern, save_pattern
from protocol import Command, crc16_ccitt

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config" / "array_config.yaml"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--port", required=True)
    p.add_argument("--baud", type=int, default=921600)
    p.add_argument("--frames", type=int, default=100000)
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--density", type=float, default=0.5)
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    p.add_argument("--out", type=Path, default=Path("stress_results"))
    p.add_argument("--progress", type=int, default=1000)
    args = p.parse_args()

    config = load_config(args.config)
    args.out.mkdir(parents=True, exist_ok=True)
    csv_path = args.out / "summary.csv"
    failures = args.out / "failures"
    failures.mkdir(exist_ok=True)

    ok = errors = 0
    started = time.perf_counter()
    try:
        with ArrayDevice(args.port, args.baud, timeout=1.0) as device, csv_path.open(
            "w", newline="", encoding="utf-8"
        ) as fh:
            writer = csv.writer(fh)
            writer.writerow(
                ["frame", "seed", "payload_crc", "ack", "round_trip_ms", "error"]
            )
            for frame_index in range(args.frames):
                frame_seed = args.seed + frame_index
                matrix = random_pattern(config, frame_seed, args.density)
                payload = pack_pattern(matrix, config)
                payload_crc = crc16_ccitt(payload)
                try:
                    reply = device.transact(Command.SET_FRAME, payload, retries=1)
                    ok += 1
                    writer.writerow(
                        [frame_index, frame_seed, f"0x{payload_crc:04X}", 1, f"{reply.round_trip_ms:.3f}", ""]
                    )
                except DeviceError as exc:
                    errors += 1
                    save_pattern(failures / f"frame_{frame_index:08d}.npy", matrix)
                    (failures / f"frame_{frame_index:08d}.txt").write_text(
                        f"seed={frame_seed}\npayload={payload.hex()}\nerror={exc}\n",
                        encoding="utf-8",
                    )
                    writer.writerow(
                        [frame_index, frame_seed, f"0x{payload_crc:04X}", 0, "", str(exc)]
                    )
                if (frame_index + 1) % args.progress == 0:
                    elapsed = time.perf_counter() - started
                    print(
                        f"{frame_index + 1}/{args.frames} ok={ok} errors={errors} "
                        f"rate={(frame_index + 1)/elapsed:.1f} frame/s"
                    )
    except KeyboardInterrupt:
        print("Interrupted; attempt ALL_OFF")
        try:
            with ArrayDevice(args.port, args.baud, timeout=0.5) as device:
                device.transact(Command.ALL_OFF, b"", retries=0)
        except Exception:
            pass
        return 130

    elapsed = time.perf_counter() - started
    print(f"done: ok={ok}, errors={errors}, elapsed={elapsed:.2f}s")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
