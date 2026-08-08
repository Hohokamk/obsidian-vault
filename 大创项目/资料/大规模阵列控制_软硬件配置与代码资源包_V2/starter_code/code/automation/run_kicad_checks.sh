#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: $0 board.kicad_sch board.kicad_pcb output_dir" >&2
  exit 2
fi

SCH=$1
PCB=$2
OUT=$3

rm -rf "$OUT"
mkdir -p "$OUT/gerbers" "$OUT/drill"

echo "KiCad version:"
kicad-cli version

# KiCad 10 syntax. Verify optional arguments with --help for the installed minor version.
kicad-cli sch erc --exit-code-violations -o "$OUT/erc.rpt" "$SCH"
kicad-cli pcb drc --exit-code-violations --schematic-parity -o "$OUT/drc.rpt" "$PCB"
kicad-cli sch export pdf -o "$OUT/schematic.pdf" "$SCH"
kicad-cli pcb export gerbers \
  -o "$OUT/gerbers" \
  -l "F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts" \
  "$PCB"
kicad-cli pcb export drill \
  -o "$OUT/drill" \
  --generate-map \
  --generate-report \
  "$PCB"
kicad-cli pcb export step -o "$OUT/board.step" "$PCB"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git rev-parse HEAD > "$OUT/git_commit.txt"
fi

find "$OUT" -type f \
  ! -name "SHA256SUMS" \
  ! -name "fabrication_package.tar.gz" \
  -print0 | sort -z | xargs -0 sha256sum > "$OUT/SHA256SUMS"

tar -czf "$OUT/fabrication_package.tar.gz" -C "$OUT" \
  erc.rpt drc.rpt schematic.pdf gerbers drill board.step SHA256SUMS \
  git_commit.txt 2>/dev/null || \
tar -czf "$OUT/fabrication_package.tar.gz" -C "$OUT" \
  erc.rpt drc.rpt schematic.pdf gerbers drill board.step SHA256SUMS

echo "outputs written to $OUT"
