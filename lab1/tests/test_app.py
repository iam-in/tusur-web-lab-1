from pathlib import Path

import numpy as np
from PIL import Image

from app.image_processing import process_image, reorder_rgb_channels
from app.web import create_app


def test_reorder_rgb_channels_changes_to_bgr():
    image = Image.new("RGB", (1, 1), (10, 20, 30))

    result = reorder_rgb_channels(image, "bgr")

    assert result.getpixel((0, 0)) == (30, 20, 10)


def test_process_image_creates_all_expected_files(tmp_path: Path):
    source = tmp_path / "source.png"
    data = np.zeros((8, 10, 3), dtype=np.uint8)
    data[:, :, 0] = 220
    data[:, :, 1] = 120
    data[:, :, 2] = 40
    Image.fromarray(data, mode="RGB").save(source)

    result = process_image(source, tmp_path / "results", "grb")

    generated = [
        result.original_image,
        result.processed_image,
        result.histogram,
        result.vertical_profile,
        result.horizontal_profile,
    ]
    assert result.order == "grb"
    assert all((tmp_path / "results" / Path(name).name).exists() for name in generated)


def test_health_endpoint_returns_ok():
    app = create_app()
    app.config.update(TESTING=True)

    with app.test_client() as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
