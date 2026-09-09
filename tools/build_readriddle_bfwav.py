#!/usr/bin/env python3
"""Encode a fixed-size Nintendo FWAV replacement for BGM_ReadRiddle.

The V16 resource is an embedded FWAV with a fixed 109,501-sample slot.  This
tool keeps that container and its channel layout intact, replaces the DSP
ADPCM payload with PCM from a supplied 48 kHz WAV, and pads any remaining
samples with silence.  It is deliberately limited to the two-channel FWAV
shape used by the V16 ReadRiddle resource.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
import wave
from array import array
from pathlib import Path


SAMPLES_PER_FRAME = 14
DSP_COEFFICIENT_COUNT = 8


def read_u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def read_i16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<h", data, offset)[0]


def trunc_div(numerator: int, denominator: int) -> int:
    """Integer division with the truncation direction used by Rust/C."""

    if numerator < 0:
        return -((-numerator) // denominator)
    return numerator // denominator


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def read_pcm_wav(path: Path) -> list[list[int]]:
    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        sample_rate = wav.getframerate()
        frames = wav.getnframes()
        raw = wav.readframes(frames)

    if channels != 2:
        raise ValueError(f"input WAV must be stereo, got {channels} channels")
    if sample_width != 2:
        raise ValueError(f"input WAV must be 16-bit PCM, got {sample_width * 8}-bit")
    if sample_rate != 48000:
        raise ValueError(f"input WAV must be 48000 Hz, got {sample_rate} Hz")

    samples = array("h")
    samples.frombytes(raw)
    if sys.byteorder != "little":
        samples.byteswap()
    if len(samples) != frames * channels:
        raise ValueError("input WAV frame count does not match its PCM payload")
    return [list(samples[channel::channels]) for channel in range(channels)]


def read_channel_layout(template: bytes) -> dict:
    if template[:4] != b"FWAV":
        raise ValueError("template is not a FWAV")
    if read_u32(template, 0x0C) != len(template):
        raise ValueError("template FWAV size field does not match file size")

    info_offset = read_u32(template, 0x18)
    data_offset = read_u32(template, 0x24)
    if template[info_offset : info_offset + 4] != b"INFO":
        raise ValueError("template INFO block is missing")
    if template[data_offset : data_offset + 4] != b"DATA":
        raise ValueError("template DATA block is missing")
    codec = template[info_offset + 0x08]
    sample_rate = read_u32(template, info_offset + 0x0C)
    sample_count = read_u32(template, info_offset + 0x14)
    channel_table = info_offset + 0x1C
    channels = read_u32(template, channel_table)
    if codec != 0x02 or sample_rate != 48000 or channels != 2:
        raise ValueError(
            "template must be 48 kHz, stereo Nintendo DSP ADPCM "
            f"(codec={codec}, rate={sample_rate}, channels={channels})"
        )

    layout = []
    for channel in range(channels):
        entry = channel_table + 0x04 + channel * 0x08
        channel_info = channel_table + read_u32(template, entry + 0x04)
        data_position = data_offset + 0x08 + read_u32(template, channel_info + 0x04)
        coef_position = channel_info + read_u32(template, channel_info + 0x0C)
        coefficients = tuple(
            read_i16(template, coef_position + coefficient * 2)
            for coefficient in range(DSP_COEFFICIENT_COUNT * 2)
        )
        layout.append(
            {
                "channel": channel,
                "data_position": data_position,
                "coefficients": coefficients,
            }
        )

    layout.sort(key=lambda item: item["data_position"])
    encoded_channel_size = ((sample_count + 13) // 14) * 8
    for index, item in enumerate(layout):
        next_position = (
            layout[index + 1]["data_position"]
            if index + 1 < len(layout)
            else len(template)
        )
        available = next_position - item["data_position"]
        if available < encoded_channel_size:
            raise ValueError(
                f"channel {item['channel']} has {available} bytes, "
                f"needs {encoded_channel_size}"
            )
        item["encoded_size"] = encoded_channel_size

    return {
        "info_offset": info_offset,
        "data_offset": data_offset,
        "sample_rate": sample_rate,
        "sample_count": sample_count,
        "channels": channels,
        "layout": layout,
    }


def encode_frame(
    pcm: list[int],
    history_2: int,
    history_1: int,
    coefficients: tuple[int, ...],
    sample_count: int,
) -> tuple[bytes, int, int]:
    """Encode one 14-sample DSP frame and return its reconstructed history."""

    in_samples = [[0] * 16 for _ in range(DSP_COEFFICIENT_COUNT)]
    out_samples = [[0] * 14 for _ in range(DSP_COEFFICIENT_COUNT)]
    scales = [0] * DSP_COEFFICIENT_COUNT
    distances = [0.0] * DSP_COEFFICIENT_COUNT

    for coefficient_set in range(DSP_COEFFICIENT_COUNT):
        coefficient_0 = coefficients[coefficient_set * 2]
        coefficient_1 = coefficients[coefficient_set * 2 + 1]
        in_samples[coefficient_set][0] = history_2
        in_samples[coefficient_set][1] = history_1

        distance = 0
        for sample in range(sample_count):
            predicted = trunc_div(
                in_samples[coefficient_set][sample] * coefficient_1
                + in_samples[coefficient_set][sample + 1] * coefficient_0,
                2048,
            )
            in_samples[coefficient_set][sample + 2] = predicted
            residual = clamp(pcm[sample] - predicted, -32768, 32767)
            if abs(residual) > abs(distance):
                distance = residual

        temp_scale = 0
        temp_distance = distance
        while temp_scale <= 12 and not -8 <= temp_distance <= 7:
            temp_scale += 1
            temp_distance = trunc_div(temp_distance, 2)
        scale = -1 if temp_scale <= 1 else temp_scale - 2

        while True:
            scale += 1
            distances[coefficient_set] = 0.0
            overflow_index = 0
            for sample in range(sample_count):
                predicted_scaled = (
                    in_samples[coefficient_set][sample] * coefficient_1
                    + in_samples[coefficient_set][sample + 1] * coefficient_0
                )
                residual_scaled = trunc_div(
                    (pcm[sample] << 11) - predicted_scaled,
                    2048,
                )
                quantized_value = residual_scaled / float(1 << scale)
                if residual_scaled > 0:
                    quantized = int(quantized_value + 0.4999999)
                else:
                    quantized = int(quantized_value - 0.4999999)

                if quantized < -8:
                    overflow_index = max(overflow_index, -8 - quantized)
                    quantized = -8
                elif quantized > 7:
                    overflow_index = max(overflow_index, quantized - 7)
                    quantized = 7
                out_samples[coefficient_set][sample] = quantized

                reconstructed = (
                    predicted_scaled
                    + ((quantized * (1 << scale)) << 11)
                    + 1024
                ) >> 11
                reconstructed = clamp(reconstructed, -32768, 32767)
                in_samples[coefficient_set][sample + 2] = reconstructed
                error = pcm[sample] - reconstructed
                distances[coefficient_set] += float(error * error)

            overflow = overflow_index + 8
            while overflow > 256:
                scale += 1
                if scale >= 12:
                    scale = 11
                overflow >>= 1
            if not (scale < 12 and overflow_index > 1):
                break

        if scale > 11:
            raise ValueError(f"invalid DSP scale {scale}")
        scales[coefficient_set] = scale

    best_distance = min(distances)
    best_index = distances.index(best_distance)
    for sample in range(sample_count, 14):
        out_samples[best_index][sample] = 0

    encoded = bytearray(8)
    encoded[0] = (best_index << 4) | (scales[best_index] & 0x0F)
    for byte_index in range(7):
        high = out_samples[best_index][byte_index * 2] & 0x0F
        low = out_samples[best_index][byte_index * 2 + 1] & 0x0F
        encoded[byte_index + 1] = (high << 4) | low

    # The source frame is reconstructed in-place by the reference encoder.
    # Those final two values are the next frame's y[n-2], y[n-1].
    next_history_2 = in_samples[best_index][14]
    next_history_1 = in_samples[best_index][15]
    return bytes(encoded), next_history_2, next_history_1


def encode_channel(samples: list[int], coefficients: tuple[int, ...]) -> bytes:
    encoded = bytearray()
    history_2 = 0
    history_1 = 0
    frame_count = (len(samples) + SAMPLES_PER_FRAME - 1) // SAMPLES_PER_FRAME
    for frame_index in range(frame_count):
        start = frame_index * SAMPLES_PER_FRAME
        frame_samples = samples[start : start + SAMPLES_PER_FRAME]
        sample_count = len(frame_samples)
        if sample_count < SAMPLES_PER_FRAME:
            frame_samples = frame_samples + [0] * (SAMPLES_PER_FRAME - sample_count)
        frame, history_2, history_1 = encode_frame(
            frame_samples,
            history_2,
            history_1,
            coefficients,
            SAMPLES_PER_FRAME,
        )
        encoded.extend(frame)
    return bytes(encoded)


def build(template_path: Path, input_wav: Path, output_path: Path) -> dict:
    template = template_path.read_bytes()
    layout = read_channel_layout(template)
    input_channels = read_pcm_wav(input_wav)
    if len(input_channels[0]) != len(input_channels[1]):
        raise ValueError(
            "left and right input channels must contain the same number of samples"
        )
    target_samples = layout["sample_count"]
    if len(input_channels[0]) > target_samples:
        raise ValueError(
            f"input WAV has {len(input_channels[0])} samples, "
            f"slot only holds {target_samples}"
        )

    padded_channels = []
    for channel in input_channels:
        padded_channels.append(channel + [0] * (target_samples - len(channel)))

    result = bytearray(template)
    for item in layout["layout"]:
        encoded = encode_channel(
            padded_channels[item["channel"]], item["coefficients"]
        )
        if len(encoded) != item["encoded_size"]:
            raise AssertionError(
                f"channel {item['channel']} encoded to {len(encoded)} bytes, "
                f"expected {item['encoded_size']}"
            )
        start = item["data_position"]
        result[start : start + len(encoded)] = encoded

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(result)
    return {
        "output": str(output_path),
        "size": len(result),
        "sample_rate": layout["sample_rate"],
        "channels": layout["channels"],
        "slot_samples": target_samples,
        "input_samples": len(input_channels[0]),
        "audible_seconds": len(input_channels[0]) / layout["sample_rate"],
        "slot_seconds": target_samples / layout["sample_rate"],
        "channel_data_bytes": layout["layout"][0]["encoded_size"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--input-wav", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.template, args.input_wav, args.output), ensure_ascii=False))


if __name__ == "__main__":
    main()
