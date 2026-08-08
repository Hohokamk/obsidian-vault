#!/usr/bin/env python3
"""Generate mapping artifacts from array_config.yaml."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "host"))

from patterns import load_config  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("config", type=Path)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    config = load_config(args.config)
    args.out.mkdir(parents=True, exist_ok=True)
    source_hash = hashlib.sha256(args.config.read_bytes()).hexdigest()

    with (args.out / "logical_to_physical.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["logical_index", "row", "col", "physical_index"])
        for logical, physical in enumerate(config.mapping.tolist()):
            writer.writerow([logical, logical // config.cols, logical % config.cols, physical])

    values = ", ".join(str(int(v)) for v in config.mapping)
    header = f"""/* AUTO-GENERATED. DO NOT EDIT.\n * source_sha256: {source_hash}\n */
#ifndef ARRAY_MAPPING_GENERATED_H
#define ARRAY_MAPPING_GENERATED_H
#include <stdint.h>
#define ARRAY_ROWS {config.rows}u
#define ARRAY_COLS {config.cols}u
#define ARRAY_CHANNELS {config.channels}u
#define ARRAY_FRAME_BYTES {config.byte_count}u
static const uint16_t logical_to_physical[ARRAY_CHANNELS] = {{ {values} }};
#endif
"""
    (args.out / "array_mapping_generated.h").write_text(header, encoding="utf-8")
    (args.out / "source_sha256.txt").write_text(source_hash + "\n", encoding="utf-8")
    print(f"generated mapping for {config.channels} channels in {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
