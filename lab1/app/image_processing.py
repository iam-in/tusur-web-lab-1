from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

CHANNEL_INDEX = {"r": 0, "g": 1, "b": 2}
VALID_ORDERS = {"rgb", "rbg", "grb", "gbr", "brg", "bgr"}


@dataclass(frozen=True)
class ProcessingResult:
    original_image: str
    processed_image: str
    histogram: str
    vertical_profile: str
    horizontal_profile: str
    order: str
    timestamp_text: str


def is_allowed_filename(filename: str, allowed_extensions: set[str]) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def reorder_rgb_channels(image: Image.Image, order: str) -> Image.Image:
    normalized_order = order.lower()
    if normalized_order not in VALID_ORDERS:
        raise ValueError("Unsupported RGB channel order")

    rgb_image = image.convert("RGB")
    data = np.asarray(rgb_image)
    indexes = [CHANNEL_INDEX[channel] for channel in normalized_order]
    changed = data[:, :, indexes]
    return Image.fromarray(changed.astype(np.uint8), mode="RGB")


def add_timestamp_overlay(image: Image.Image, timestamp_text: str) -> Image.Image:
    if not timestamp_text:
        return image

    output = image.copy()
    draw = ImageDraw.Draw(output)
    font = ImageFont.load_default()
    padding = max(12, min(output.size) // 35)
    bbox = draw.textbbox((0, 0), timestamp_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = padding
    y = output.height - text_height - padding
    draw.rectangle(
        (x - 8, y - 8, x + text_width + 8, y + text_height + 8),
        fill=(0, 0, 0),
    )
    draw.text((x, y), timestamp_text, fill=(255, 255, 255), font=font)
    return output


def save_color_histogram(image: Image.Image, target: Path) -> None:
    data = np.asarray(image.convert("RGB"))
    colors = {"r": "#d83a34", "g": "#2f9e44", "b": "#2979ff"}
    labels = {"r": "Red", "g": "Green", "b": "Blue"}

    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=130)
    for channel, index in CHANNEL_INDEX.items():
        ax.hist(
            data[:, :, index].ravel(),
            bins=256,
            range=(0, 255),
            color=colors[channel],
            alpha=0.45,
            label=labels[channel],
        )
    ax.set_title("Color distribution of the source image")
    ax.set_xlabel("Intensity")
    ax.set_ylabel("Pixel count")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(target)
    plt.close(fig)


def save_mean_profile(image: Image.Image, target: Path, axis: str) -> None:
    data = np.asarray(image.convert("RGB"), dtype=np.float32)
    if axis == "vertical":
        profile = data.mean(axis=(1, 2))
        xlabel = "Y coordinate"
        title = "Mean color value by vertical axis"
    elif axis == "horizontal":
        profile = data.mean(axis=(0, 2))
        xlabel = "X coordinate"
        title = "Mean color value by horizontal axis"
    else:
        raise ValueError("Axis must be vertical or horizontal")

    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=130)
    ax.plot(profile, color="#2b5c9e", linewidth=2)
    ax.fill_between(range(len(profile)), profile, color="#9fc5e8", alpha=0.35)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Mean RGB intensity")
    ax.set_ylim(0, 255)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(target)
    plt.close(fig)


def process_image(source: Path, result_dir: Path, order: str, timestamp_text: str = "") -> ProcessingResult:
    result_dir.mkdir(parents=True, exist_ok=True)
    run_id = uuid4().hex
    normalized_timestamp = timestamp_text.strip()

    with Image.open(source) as image:
        original = image.convert("RGB")
        processed = reorder_rgb_channels(original, order)
        processed = add_timestamp_overlay(processed, normalized_timestamp)

        original_path = result_dir / f"{run_id}_original.png"
        processed_path = result_dir / f"{run_id}_processed_{order}.png"
        histogram_path = result_dir / f"{run_id}_histogram.png"
        vertical_path = result_dir / f"{run_id}_vertical_profile.png"
        horizontal_path = result_dir / f"{run_id}_horizontal_profile.png"

        original.save(original_path)
        processed.save(processed_path)
        save_color_histogram(original, histogram_path)
        save_mean_profile(original, vertical_path, "vertical")
        save_mean_profile(original, horizontal_path, "horizontal")

    return ProcessingResult(
        original_image=_relative_static_path(original_path),
        processed_image=_relative_static_path(processed_path),
        histogram=_relative_static_path(histogram_path),
        vertical_profile=_relative_static_path(vertical_path),
        horizontal_profile=_relative_static_path(horizontal_path),
        order=order,
        timestamp_text=normalized_timestamp,
    )


def _relative_static_path(path: Path) -> str:
    static_marker = f"{Path('static')}"
    parts = path.as_posix().split(f"/{static_marker}/", maxsplit=1)
    if len(parts) == 2:
        return parts[1]
    return path.name
