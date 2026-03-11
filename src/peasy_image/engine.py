"""peasy-image — Python image processing engine.

20 image operations: resize, crop, rotate, flip, compress, convert,
grayscale, blur, sharpen, brightness, contrast, invert, watermark,
thumbnail, strip metadata (EXIF), info, border, round corners, pad,
and overlay.

Single dependency: Pillow. All functions accept bytes | Path | str
and return bytes.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

# ── Types ────────────────────────────────────────────────────────────

ImageInput = bytes | Path | str
"""Accepted input types: raw bytes, pathlib.Path, or string file path."""

ImageFormat = Literal["png", "jpeg", "webp", "gif", "bmp", "tiff", "ico"]
"""Supported output image formats."""

FlipMode = Literal["horizontal", "vertical", "both"]
"""Flip direction."""

AnchorPosition = Literal[
    "top-left",
    "top-right",
    "bottom-left",
    "bottom-right",
    "center",
]
"""Position anchor for watermarks and overlays."""


@dataclass(frozen=True)
class ImageInfo:
    """Basic image metadata."""

    width: int
    height: int
    format: str
    mode: str
    file_size: int
    has_exif: bool
    has_alpha: bool


@dataclass(frozen=True)
class ExifData:
    """Extracted EXIF metadata."""

    camera_make: str
    camera_model: str
    datetime: str
    exposure_time: str
    f_number: str
    iso: str
    focal_length: str
    gps_latitude: str
    gps_longitude: str
    software: str
    raw: dict[str, str]


# ── Internal helpers ─────────────────────────────────────────────────


def _read(source: ImageInput) -> bytes:
    """Read image data from bytes, Path, or str path."""
    if isinstance(source, bytes):
        return source
    path = Path(source)
    return path.read_bytes()


def _open(source: ImageInput) -> Image.Image:
    """Open an image from any supported input type."""
    data = _read(source)
    return Image.open(io.BytesIO(data))


def _write(img: Image.Image, fmt: str = "png", quality: int = 85) -> bytes:
    """Write an image to bytes in the given format."""
    buf = io.BytesIO()
    save_kwargs: dict[str, object] = {}

    fmt_lower = fmt.lower()
    if fmt_lower == "jpeg":
        # JPEG doesn't support alpha — convert RGBA to RGB
        if img.mode in ("RGBA", "LA", "PA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")
        save_kwargs["quality"] = quality
        save_kwargs["optimize"] = True
    elif fmt_lower == "webp":
        save_kwargs["quality"] = quality
        save_kwargs["method"] = 4
    elif fmt_lower == "png":
        save_kwargs["optimize"] = True

    pil_format = "JPEG" if fmt_lower == "jpeg" else fmt_lower.upper()
    img.save(buf, format=pil_format, **save_kwargs)
    return buf.getvalue()


def _source_size(source: ImageInput) -> int:
    """Get the byte size of the input."""
    if isinstance(source, bytes):
        return len(source)
    return Path(source).stat().st_size


# ── Image operations ─────────────────────────────────────────────────


def resize(
    source: ImageInput,
    width: int | None = None,
    height: int | None = None,
    *,
    maintain_aspect: bool = True,
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Resize an image to the given dimensions.

    If only width or height is given and maintain_aspect is True,
    the other dimension is computed to preserve the aspect ratio.
    """
    img = _open(source)

    if width is None and height is None:
        raise ValueError("At least one of width or height must be specified")

    if maintain_aspect:
        if width and height:
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
        elif width:
            ratio = width / img.width
            img = img.resize((width, round(img.height * ratio)), Image.Resampling.LANCZOS)
        else:
            assert height is not None
            ratio = height / img.height
            img = img.resize((round(img.width * ratio), height), Image.Resampling.LANCZOS)
    else:
        w = width or img.width
        h = height or img.height
        img = img.resize((w, h), Image.Resampling.LANCZOS)

    return _write(img, fmt, quality)


def crop(
    source: ImageInput,
    left: int,
    top: int,
    right: int,
    bottom: int,
    *,
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Crop an image to the given bounding box (left, top, right, bottom)."""
    img = _open(source)

    if left < 0 or top < 0:
        raise ValueError("left and top must be non-negative")
    if right <= left or bottom <= top:
        raise ValueError("right must be > left and bottom must be > top")
    if right > img.width or bottom > img.height:
        raise ValueError(
            f"Crop box ({right}x{bottom}) exceeds image size ({img.width}x{img.height})"
        )

    img = img.crop((left, top, right, bottom))
    return _write(img, fmt, quality)


def rotate(
    source: ImageInput,
    angle: float,
    *,
    expand: bool = True,
    fill_color: str = "#ffffff",
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Rotate an image by the given angle (degrees, counter-clockwise).

    If expand is True, the output image is enlarged to contain the
    full rotated image. fill_color fills any empty areas.
    """
    img = _open(source)
    img = img.rotate(angle, expand=expand, fillcolor=fill_color, resample=Image.Resampling.BICUBIC)
    return _write(img, fmt, quality)


def flip(
    source: ImageInput,
    mode: FlipMode = "horizontal",
    *,
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Flip an image horizontally, vertically, or both."""
    img = _open(source)

    if mode == "horizontal":
        img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    elif mode == "vertical":
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    elif mode == "both":
        img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT).transpose(
            Image.Transpose.FLIP_TOP_BOTTOM
        )
    else:
        raise ValueError(f"Invalid flip mode: {mode!r}. Use 'horizontal', 'vertical', or 'both'")

    return _write(img, fmt, quality)


def compress(
    source: ImageInput,
    *,
    quality: int = 60,
    fmt: str = "jpeg",
) -> bytes:
    """Compress an image by reducing quality.

    Returns the compressed bytes. Default output format is JPEG
    for maximum compression.
    """
    img = _open(source)
    return _write(img, fmt, quality)


def convert(
    source: ImageInput,
    fmt: ImageFormat = "png",
    *,
    quality: int = 85,
) -> bytes:
    """Convert an image to a different format."""
    img = _open(source)
    return _write(img, fmt, quality)


def grayscale(
    source: ImageInput,
    *,
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Convert an image to grayscale."""
    img = _open(source)
    img = img.convert("L")
    return _write(img, fmt, quality)


def blur(
    source: ImageInput,
    radius: float = 2.0,
    *,
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Apply Gaussian blur to an image."""
    img = _open(source)
    img = img.filter(ImageFilter.GaussianBlur(radius=radius))
    return _write(img, fmt, quality)


def sharpen(
    source: ImageInput,
    factor: float = 2.0,
    *,
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Sharpen an image.

    factor=1.0 gives the original, >1.0 sharpens, <1.0 blurs.
    """
    img = _open(source)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(factor)
    return _write(img, fmt, quality)


def brightness(
    source: ImageInput,
    factor: float = 1.2,
    *,
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Adjust image brightness.

    factor=1.0 gives the original, >1.0 brightens, <1.0 darkens.
    0.0 gives a black image.
    """
    img = _open(source)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(factor)
    return _write(img, fmt, quality)


def contrast(
    source: ImageInput,
    factor: float = 1.5,
    *,
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Adjust image contrast.

    factor=1.0 gives the original, >1.0 increases contrast,
    <1.0 decreases contrast.
    """
    img = _open(source)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(factor)
    return _write(img, fmt, quality)


def invert(
    source: ImageInput,
    *,
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Invert the colors of an image."""
    from PIL import ImageOps

    img = _open(source)

    # ImageOps.invert only works on RGB/L modes
    if img.mode == "RGBA":
        r, g, b, a = img.split()
        rgb = Image.merge("RGB", (r, g, b))
        rgb = ImageOps.invert(rgb)
        img = Image.merge("RGBA", (*rgb.split(), a))
    elif img.mode in ("RGB", "L"):
        img = ImageOps.invert(img)
    else:
        img = ImageOps.invert(img.convert("RGB"))

    return _write(img, fmt, quality)


def watermark(
    source: ImageInput,
    text: str,
    *,
    position: AnchorPosition = "bottom-right",
    opacity: int = 128,
    font_size: int = 24,
    color: str = "#ffffff",
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Add a text watermark to an image.

    Uses Pillow's default font. opacity is 0 (invisible) to 255 (opaque).
    """
    img = _open(source).convert("RGBA")

    # Create transparent overlay for the text
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Parse hex color
    r_c = int(color[1:3], 16)
    g_c = int(color[3:5], 16)
    b_c = int(color[5:7], 16)

    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font_size=font_size)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Calculate position
    padding = 20
    x, y = _anchor_xy(img.width, img.height, text_w, text_h, position, padding)

    draw.text((x, y), text, fill=(r_c, g_c, b_c, opacity), font_size=font_size)
    img = Image.alpha_composite(img, overlay)

    return _write(img, fmt, quality)


def thumbnail(
    source: ImageInput,
    size: int = 256,
    *,
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Create a square thumbnail of the given size.

    Crops to center square first, then resizes.
    """
    img = _open(source)

    # Center crop to square
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))

    # Resize to target
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return _write(img, fmt, quality)


def strip_metadata(
    source: ImageInput,
    *,
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Remove all EXIF and metadata from an image.

    Creates a new image with pixel data only — no EXIF, IPTC, or XMP.
    """
    img = _open(source)
    # Create a fresh image without metadata
    clean = Image.new(img.mode, img.size)
    if hasattr(img, "get_flattened_data"):
        clean.putdata(list(img.get_flattened_data()))
    else:
        clean.putdata(list(img.getdata()))
    return _write(clean, fmt, quality)


def info(source: ImageInput) -> ImageInfo:
    """Get basic image information (dimensions, format, mode, EXIF presence)."""
    data = _read(source)
    img = Image.open(io.BytesIO(data))

    has_exif = bool(img.info.get("exif"))
    has_alpha = img.mode in ("RGBA", "LA", "PA")

    return ImageInfo(
        width=img.width,
        height=img.height,
        format=(img.format or "unknown").lower(),
        mode=img.mode,
        file_size=len(data),
        has_exif=has_exif,
        has_alpha=has_alpha,
    )


def get_exif(source: ImageInput) -> ExifData:
    """Extract EXIF metadata from an image.

    Returns an ExifData object with common fields and a raw dict
    of all available tags.
    """
    img = _open(source)
    exif_data = img.getexif()

    raw: dict[str, str] = {}
    for tag_id, value in exif_data.items():
        from PIL.ExifTags import TAGS

        tag_name = TAGS.get(tag_id, str(tag_id))
        raw[tag_name] = str(value)

    return ExifData(
        camera_make=raw.get("Make", ""),
        camera_model=raw.get("Model", ""),
        datetime=raw.get("DateTime", ""),
        exposure_time=raw.get("ExposureTime", ""),
        f_number=raw.get("FNumber", ""),
        iso=raw.get("ISOSpeedRatings", ""),
        focal_length=raw.get("FocalLength", ""),
        gps_latitude=raw.get("GPSLatitude", ""),
        gps_longitude=raw.get("GPSLongitude", ""),
        software=raw.get("Software", ""),
        raw=raw,
    )


def border(
    source: ImageInput,
    width: int = 10,
    color: str = "#000000",
    *,
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Add a solid color border around an image."""
    from PIL import ImageOps

    img = _open(source)

    # Parse hex color to tuple
    r_c = int(color[1:3], 16)
    g_c = int(color[3:5], 16)
    b_c = int(color[5:7], 16)

    img = ImageOps.expand(img, border=width, fill=(r_c, g_c, b_c))
    return _write(img, fmt, quality)


def round_corners(
    source: ImageInput,
    radius: int = 20,
    *,
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Apply rounded corners to an image.

    The output is always PNG (or a format that supports alpha)
    since rounded corners require transparency.
    """
    img = _open(source).convert("RGBA")

    # Create a mask with rounded rectangle
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)

    img.putalpha(mask)
    return _write(img, fmt, quality)


def pad(
    source: ImageInput,
    target_width: int,
    target_height: int,
    *,
    color: str = "#ffffff",
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Pad an image to the target dimensions, centering the original.

    If the image is larger than the target, it is first resized
    to fit within the target (maintaining aspect ratio).
    """
    img = _open(source)

    # Resize if larger than target
    if img.width > target_width or img.height > target_height:
        img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)

    # Parse color
    r_c = int(color[1:3], 16)
    g_c = int(color[3:5], 16)
    b_c = int(color[5:7], 16)

    # Create padded canvas
    if img.mode == "RGBA":
        canvas = Image.new("RGBA", (target_width, target_height), (r_c, g_c, b_c, 255))
    else:
        canvas = Image.new("RGB", (target_width, target_height), (r_c, g_c, b_c))

    # Center the image
    x = (target_width - img.width) // 2
    y = (target_height - img.height) // 2
    canvas.paste(img, (x, y))

    return _write(canvas, fmt, quality)


def overlay(
    source: ImageInput,
    overlay_source: ImageInput,
    *,
    position: AnchorPosition = "center",
    opacity: int = 255,
    fmt: str = "png",
    quality: int = 85,
) -> bytes:
    """Overlay one image on top of another.

    The overlay image is placed at the given position.
    opacity is 0 (invisible) to 255 (fully opaque).
    """
    base = _open(source).convert("RGBA")
    over = _open(overlay_source).convert("RGBA")

    # Apply opacity
    if opacity < 255:
        r, g, b, a = over.split()
        a = a.point(lambda p: int(p * opacity / 255))
        over = Image.merge("RGBA", (r, g, b, a))

    # Calculate position
    x, y = _anchor_xy(base.width, base.height, over.width, over.height, position, 0)

    base.paste(over, (x, y), over)
    return _write(base, fmt, quality)


# ── Internal position helper ─────────────────────────────────────────


def _anchor_xy(
    canvas_w: int | float,
    canvas_h: int | float,
    item_w: int | float,
    item_h: int | float,
    position: AnchorPosition,
    padding: int,
) -> tuple[int, int]:
    """Calculate (x, y) for placing an item on a canvas at the given anchor."""
    if position == "top-left":
        return padding, padding
    if position == "top-right":
        return int(canvas_w - item_w - padding), padding
    if position == "bottom-left":
        return padding, int(canvas_h - item_h - padding)
    if position == "bottom-right":
        return int(canvas_w - item_w - padding), int(canvas_h - item_h - padding)
    # center
    return int((canvas_w - item_w) // 2), int((canvas_h - item_h) // 2)
