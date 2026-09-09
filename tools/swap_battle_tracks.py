#!/usr/bin/env python3
"""Create a small V18 overlay that swaps the two approved battle tracks.

The BFSTM files are swapped byte-for-byte so their loop metadata and encoded
audio remain exactly those already shipped in V16.  The two Switch prefetch
tracks in the battle BARS are rebuilt from the swapped BFSTM DATA sections.
The script writes only the changed overlay files and never mutates the base
package.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


QUICK = "BGM_FieldBattle_QuickIntro_key2"
EASY1_KEY1 = "BGM_FieldBattle_Easy1_key1"
TRACK_TO_BARS = {
    EASY1_KEY1: "FieldBattleBgm.bars",
    QUICK: "D_FieldBattleBgm.bars",
}


def u32(data: bytes, offset: int, endian: str = "<") -> int:
    return struct.unpack_from(endian + "I", data, offset)[0]


def put_u32(data: bytearray, offset: int, value: int, endian: str) -> None:
    struct.pack_into(endian + "I", data, offset, value)


def bars_tracks(data: bytes) -> dict[str, tuple[int, str]]:
    """Return {stream name: (BFSTP offset, endian)} for a Switch BARS."""
    if data[:4] != b"BARS":
        raise ValueError("not a BARS file")
    endian = ">" if data[8:10] == b"\xfe\xff" else "<"
    count = u32(data, 12, endian)
    offsets_pos = 16 + count * 4
    result: dict[str, tuple[int, str]] = {}
    for index in range(count):
        amta_offset = u32(data, offsets_pos + index * 8, endian)
        track_offset = u32(data, offsets_pos + index * 8 + 4, endian)
        if amta_offset == 0xFFFFFFFF:
            continue
        amta_endian = ">" if data[amta_offset + 4 : amta_offset + 6] == b"\xfe\xff" else "<"
        q = amta_offset + 28
        if data[q : q + 4] != b"DATA":
            raise ValueError(f"track {index}: missing DATA section")
        q += 8 + u32(data, q + 4, amta_endian)
        if data[q : q + 4] != b"MARK":
            raise ValueError(f"track {index}: missing MARK section")
        q += 8 + u32(data, q + 4, amta_endian)
        if data[q : q + 4] != b"EXT_":
            raise ValueError(f"track {index}: missing EXT_ section")
        q += 8 + u32(data, q + 4, amta_endian)
        if data[q : q + 4] != b"STRG":
            raise ValueError(f"track {index}: missing STRG section")
        name_len = u32(data, q + 4, amta_endian)
        name = data[q + 8 : q + 8 + name_len - 1].split(b"\0", 1)[0].decode("ascii")
        result[name] = (track_offset, endian)
    return result


def replace_prefetch(bars: bytes, track_name: str, source_bfstm: bytes) -> bytes:
    tracks = bars_tracks(bars)
    if track_name not in tracks:
        raise ValueError(f"missing BARS track {track_name!r}")
    track_offset, endian = tracks[track_name]
    if track_offset == 0xFFFFFFFF:
        raise ValueError(f"BARS track {track_name!r} is external")

    track_len = u32(bars, track_offset + 12, endian)
    if track_len != 0xC180 or bars[track_offset : track_offset + 4] != b"FSTP":
        raise ValueError(f"unexpected compact BFSTP shape for {track_name!r}")
    data_offset = source_bfstm.find(b"DATA")
    if data_offset < 0:
        raise ValueError(f"{track_name!r}: BFSTM has no DATA section")
    audio = source_bfstm[data_offset + 0x20 : data_offset + 0x20 + 0xC000]
    if len(audio) != 0xC000:
        raise ValueError(f"{track_name!r}: BFSTM has too little prefetch audio")

    output = bytearray(bars)
    track = bytearray(output[track_offset : track_offset + track_len])
    track[0x40:0x140] = source_bfstm[0x40:0x140]
    # These fields are omitted/zeroed by the compact Switch prefetch shape.
    track[0x94] = 0
    track[0x95] = 0
    track[0x180 : 0x180 + len(audio)] = audio
    output[track_offset : track_offset + track_len] = track
    put_u32(output, 4, len(output), endian)
    return bytes(output)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(base_dir: Path, output_dir: Path) -> dict[str, object]:
    base_stream = base_dir / "Sound/Resource/Stream"
    base_resource = base_dir / "Sound/Resource"
    output_stream = output_dir / "Sound/Resource/Stream"
    output_resource = output_dir / "Sound/Resource"
    output_stream.mkdir(parents=True, exist_ok=True)
    output_resource.mkdir(parents=True, exist_ok=True)

    source = {
        QUICK: (base_stream / f"{QUICK}.bfstm").read_bytes(),
        EASY1_KEY1: (base_stream / f"{EASY1_KEY1}.bfstm").read_bytes(),
    }
    swapped = {QUICK: source[EASY1_KEY1], EASY1_KEY1: source[QUICK]}
    output_files: dict[str, dict[str, str | int]] = {}
    for name, data in swapped.items():
        destination = output_stream / f"{name}.bfstm"
        destination.write_bytes(data)
        output_files[str(destination.relative_to(output_dir))] = {
            "bytes": len(data),
            "before_sha256": sha256_bytes(source[name]),
            "sha256": sha256(destination),
            "source_slot": EASY1_KEY1 if name == QUICK else QUICK,
        }

    bars_data: dict[str, bytes] = {}
    for name, bars_name in TRACK_TO_BARS.items():
        bars_data.setdefault(bars_name, (base_resource / bars_name).read_bytes())
        bars_data[bars_name] = replace_prefetch(bars_data[bars_name], name, swapped[name])
    for bars_name, data in bars_data.items():
        destination = output_resource / bars_name
        destination.write_bytes(data)
        output_files[str(destination.relative_to(output_dir))] = {
            "bytes": len(data),
            "before_sha256": sha256_bytes((base_resource / bars_name).read_bytes()),
            "sha256": sha256(destination),
        }

    return {
        "version": "v18",
        "base": str(base_dir),
        "swaps": [
            {
                "destination_slot": QUICK,
                "before": "ojos tristes",
                "after": "神の怒り",
                "source_slot": EASY1_KEY1,
            },
            {
                "destination_slot": EASY1_KEY1,
                "before": "神の怒り",
                "after": "ojos tristes",
                "source_slot": QUICK,
            },
        ],
        "bars_prefetch_updated": sorted(TRACK_TO_BARS.items()),
        "files": output_files,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    manifest = build(args.base_dir, args.output_dir)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
