"""Tests for peasy_image.engine — 20 image operations."""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image

from peasy_image import engine

# ── Fixtures ──────────────────────────────────────────────────────


def _make_image(
    width: int = 200, height: int = 100, color: str = "red", mode: str = "RGB"
) -> bytes:
    """Create a test image as PNG bytes."""
    img = Image.new(mode, (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _dimensions(data: bytes) -> tuple[int, int]:
    """Get (width, height) from image bytes."""
    img = Image.open(io.BytesIO(data))
    return img.size


@pytest.fixture()
def red_image() -> bytes:
    """200x100 red RGB image."""
    return _make_image(200, 100, "red")


@pytest.fixture()
def rgba_image() -> bytes:
    """200x100 RGBA image with alpha."""
    return _make_image(200, 100, "blue", "RGBA")


@pytest.fixture()
def square_image() -> bytes:
    """300x300 green square."""
    return _make_image(300, 300, "green")


@pytest.fixture()
def tmp_image(red_image: bytes, tmp_path: Path) -> Path:
    """Write red image to a temp file."""
    p = tmp_path / "test.png"
    p.write_bytes(red_image)
    return p


# ── Resize ────────────────────────────────────────────────────────


class TestResize:
    def test_resize_width_only(self, red_image: bytes) -> None:
        result = engine.resize(red_image, width=100)
        w, h = _dimensions(result)
        assert w == 100
        assert h == 50  # 100/200 * 100

    def test_resize_height_only(self, red_image: bytes) -> None:
        result = engine.resize(red_image, height=50)
        w, h = _dimensions(result)
        assert w == 100  # 50/100 * 200
        assert h == 50

    def test_resize_both_maintain_aspect(self, red_image: bytes) -> None:
        result = engine.resize(red_image, width=80, height=80)
        w, h = _dimensions(result)
        # thumbnail preserves aspect, fits within bounding box
        assert w <= 80
        assert h <= 80

    def test_resize_no_aspect(self, red_image: bytes) -> None:
        result = engine.resize(red_image, width=50, height=50, maintain_aspect=False)
        assert _dimensions(result) == (50, 50)

    def test_resize_requires_dimension(self, red_image: bytes) -> None:
        with pytest.raises(ValueError, match="At least one"):
            engine.resize(red_image)


# ── Crop ──────────────────────────────────────────────────────────


class TestCrop:
    def test_crop_basic(self, red_image: bytes) -> None:
        result = engine.crop(red_image, 10, 10, 110, 60)
        assert _dimensions(result) == (100, 50)

    def test_crop_invalid_box(self, red_image: bytes) -> None:
        with pytest.raises(ValueError, match="right must be > left"):
            engine.crop(red_image, 100, 10, 50, 60)

    def test_crop_exceeds_bounds(self, red_image: bytes) -> None:
        with pytest.raises(ValueError, match="exceeds image size"):
            engine.crop(red_image, 0, 0, 300, 50)


# ── Rotate ────────────────────────────────────────────────────────


class TestRotate:
    def test_rotate_90(self, red_image: bytes) -> None:
        result = engine.rotate(red_image, 90)
        _w, h = _dimensions(result)
        # 90 degree rotation swaps width/height (approximately)
        assert h >= 190  # allow margin for anti-aliasing

    def test_rotate_no_expand(self, red_image: bytes) -> None:
        result = engine.rotate(red_image, 45, expand=False)
        assert _dimensions(result) == (200, 100)


# ── Flip ──────────────────────────────────────────────────────────


class TestFlip:
    def test_flip_horizontal(self, red_image: bytes) -> None:
        result = engine.flip(red_image, mode="horizontal")
        assert _dimensions(result) == (200, 100)

    def test_flip_vertical(self, red_image: bytes) -> None:
        result = engine.flip(red_image, mode="vertical")
        assert _dimensions(result) == (200, 100)

    def test_flip_both(self, red_image: bytes) -> None:
        result = engine.flip(red_image, mode="both")
        assert _dimensions(result) == (200, 100)

    def test_flip_invalid(self, red_image: bytes) -> None:
        with pytest.raises(ValueError, match="Invalid flip mode"):
            engine.flip(red_image, mode="diagonal")  # type: ignore[arg-type]


# ── Compress ──────────────────────────────────────────────────────


class TestCompress:
    def test_compress_reduces_quality(self, red_image: bytes) -> None:
        high = engine.compress(red_image, quality=95, fmt="jpeg")
        low = engine.compress(red_image, quality=10, fmt="jpeg")
        # Lower quality JPEG should be smaller than higher quality
        assert len(low) <= len(high)

    def test_compress_produces_valid_image(self, red_image: bytes) -> None:
        result = engine.compress(red_image, quality=50, fmt="jpeg")
        img = Image.open(io.BytesIO(result))
        assert img.format == "JPEG"


# ── Convert ───────────────────────────────────────────────────────


class TestConvert:
    def test_convert_to_webp(self, red_image: bytes) -> None:
        result = engine.convert(red_image, fmt="webp")
        img = Image.open(io.BytesIO(result))
        assert img.format == "WEBP"

    def test_convert_to_jpeg(self, red_image: bytes) -> None:
        result = engine.convert(red_image, fmt="jpeg")
        img = Image.open(io.BytesIO(result))
        assert img.format == "JPEG"

    def test_convert_rgba_to_jpeg(self, rgba_image: bytes) -> None:
        # RGBA to JPEG should not raise (alpha is handled)
        result = engine.convert(rgba_image, fmt="jpeg")
        img = Image.open(io.BytesIO(result))
        assert img.format == "JPEG"
        assert img.mode == "RGB"


# ── Grayscale ─────────────────────────────────────────────────────


class TestGrayscale:
    def test_grayscale(self, red_image: bytes) -> None:
        result = engine.grayscale(red_image)
        img = Image.open(io.BytesIO(result))
        assert img.mode == "L"


# ── Blur ──────────────────────────────────────────────────────────


class TestBlur:
    def test_blur(self, red_image: bytes) -> None:
        result = engine.blur(red_image, radius=5.0)
        assert _dimensions(result) == (200, 100)


# ── Sharpen ───────────────────────────────────────────────────────


class TestSharpen:
    def test_sharpen(self, red_image: bytes) -> None:
        result = engine.sharpen(red_image, factor=3.0)
        assert _dimensions(result) == (200, 100)


# ── Brightness ────────────────────────────────────────────────────


class TestBrightness:
    def test_brighten(self, red_image: bytes) -> None:
        result = engine.brightness(red_image, factor=1.5)
        assert _dimensions(result) == (200, 100)

    def test_darken(self, red_image: bytes) -> None:
        result = engine.brightness(red_image, factor=0.5)
        assert len(result) > 0


# ── Contrast ──────────────────────────────────────────────────────


class TestContrast:
    def test_increase_contrast(self, red_image: bytes) -> None:
        result = engine.contrast(red_image, factor=2.0)
        assert _dimensions(result) == (200, 100)


# ── Invert ────────────────────────────────────────────────────────


class TestInvert:
    def test_invert_rgb(self, red_image: bytes) -> None:
        result = engine.invert(red_image)
        img = Image.open(io.BytesIO(result))
        # Red inverted should be cyan-ish (0, 255, 255)
        pixel: tuple[int, ...] = img.getpixel((0, 0))  # type: ignore[assignment]
        assert pixel[0] == 0  # R inverted
        assert pixel[1] == 255  # G inverted
        assert pixel[2] == 255  # B inverted

    def test_invert_rgba(self, rgba_image: bytes) -> None:
        result = engine.invert(rgba_image)
        img = Image.open(io.BytesIO(result))
        assert img.mode == "RGBA"


# ── Watermark ─────────────────────────────────────────────────────


class TestWatermark:
    def test_watermark(self, red_image: bytes) -> None:
        result = engine.watermark(red_image, "Test Watermark")
        assert _dimensions(result) == (200, 100)

    def test_watermark_positions(self, red_image: bytes) -> None:
        for pos in ["top-left", "top-right", "bottom-left", "bottom-right", "center"]:
            result = engine.watermark(red_image, "X", position=pos)  # type: ignore[arg-type]
            assert len(result) > 0


# ── Thumbnail ─────────────────────────────────────────────────────


class TestThumbnail:
    def test_thumbnail_square(self, red_image: bytes) -> None:
        result = engine.thumbnail(red_image, size=64)
        assert _dimensions(result) == (64, 64)

    def test_thumbnail_from_square(self, square_image: bytes) -> None:
        result = engine.thumbnail(square_image, size=100)
        assert _dimensions(result) == (100, 100)


# ── Strip Metadata ────────────────────────────────────────────────


class TestStripMetadata:
    def test_strip_metadata(self, red_image: bytes) -> None:
        result = engine.strip_metadata(red_image)
        result_info = engine.info(result)
        assert not result_info.has_exif


# ── Info ──────────────────────────────────────────────────────────


class TestInfo:
    def test_info(self, red_image: bytes) -> None:
        result = engine.info(red_image)
        assert result.width == 200
        assert result.height == 100
        assert result.format == "png"
        assert result.mode == "RGB"
        assert result.file_size > 0
        assert not result.has_alpha

    def test_info_rgba(self, rgba_image: bytes) -> None:
        result = engine.info(rgba_image)
        assert result.has_alpha

    def test_info_path(self, tmp_image: Path) -> None:
        result = engine.info(tmp_image)
        assert result.width == 200


# ── Border ────────────────────────────────────────────────────────


class TestBorder:
    def test_border(self, red_image: bytes) -> None:
        result = engine.border(red_image, width=10, color="#0000ff")
        w, h = _dimensions(result)
        assert w == 220  # 200 + 10*2
        assert h == 120  # 100 + 10*2


# ── Round Corners ─────────────────────────────────────────────────


class TestRoundCorners:
    def test_round_corners(self, red_image: bytes) -> None:
        result = engine.round_corners(red_image, radius=20)
        img = Image.open(io.BytesIO(result))
        assert img.mode == "RGBA"
        # Corner pixel should be transparent
        corner: tuple[int, ...] = img.getpixel((0, 0))  # type: ignore[assignment]
        assert corner[3] == 0


# ── Pad ───────────────────────────────────────────────────────────


class TestPad:
    def test_pad_larger(self, red_image: bytes) -> None:
        result = engine.pad(red_image, 400, 300)
        assert _dimensions(result) == (400, 300)

    def test_pad_shrinks_if_needed(self, red_image: bytes) -> None:
        # Image is 200x100, target is 100x100 -- should resize then center
        result = engine.pad(red_image, 100, 100)
        assert _dimensions(result) == (100, 100)


# ── Overlay ───────────────────────────────────────────────────────


class TestOverlay:
    def test_overlay(self, red_image: bytes) -> None:
        small = _make_image(50, 50, "blue", "RGBA")
        result = engine.overlay(red_image, small, position="center")
        assert _dimensions(result) == (200, 100)

    def test_overlay_with_opacity(self, red_image: bytes) -> None:
        small = _make_image(50, 50, "green", "RGBA")
        result = engine.overlay(red_image, small, opacity=128, position="top-left")
        assert len(result) > 0


# ── Input Types ───────────────────────────────────────────────────


class TestInputTypes:
    def test_bytes_input(self, red_image: bytes) -> None:
        result = engine.info(red_image)
        assert result.width == 200

    def test_path_input(self, tmp_image: Path) -> None:
        result = engine.info(tmp_image)
        assert result.width == 200

    def test_str_input(self, tmp_image: Path) -> None:
        result = engine.info(str(tmp_image))
        assert result.width == 200
