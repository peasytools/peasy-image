"""peasy-image MCP server — Image tools for AI assistants.

Start the server::

    uvx --from "peasy-image[mcp]" python -m peasy_image
"""

from __future__ import annotations

import base64

from mcp.server.fastmcp import FastMCP

from peasy_image import engine

mcp = FastMCP(
    "peasy-image",
    instructions="Image tools: resize, crop, rotate, compress, convert, blur, sharpen, watermark.",
)


def _b64_to_bytes(data: str) -> bytes:
    """Decode base64-encoded image data."""
    return base64.b64decode(data)


def _bytes_to_b64(data: bytes) -> str:
    """Encode image bytes to base64."""
    return base64.b64encode(data).decode("ascii")


@mcp.tool()
def image_resize(
    image_b64: str,
    width: int | None = None,
    height: int | None = None,
    maintain_aspect: bool = True,
    fmt: str = "png",
    quality: int = 85,
) -> str:
    """Resize an image. Provide at least width or height. Returns base64."""
    result = engine.resize(
        _b64_to_bytes(image_b64),
        width=width,
        height=height,
        maintain_aspect=maintain_aspect,
        fmt=fmt,
        quality=quality,
    )
    return _bytes_to_b64(result)


@mcp.tool()
def image_crop(
    image_b64: str,
    left: int,
    top: int,
    right: int,
    bottom: int,
    fmt: str = "png",
    quality: int = 85,
) -> str:
    """Crop an image to bounding box (left, top, right, bottom). Returns base64."""
    data = _b64_to_bytes(image_b64)
    result = engine.crop(data, left, top, right, bottom, fmt=fmt, quality=quality)
    return _bytes_to_b64(result)


@mcp.tool()
def image_rotate(
    image_b64: str,
    angle: float,
    expand: bool = True,
    fmt: str = "png",
    quality: int = 85,
) -> str:
    """Rotate an image by angle degrees. Returns base64."""
    result = engine.rotate(_b64_to_bytes(image_b64), angle, expand=expand, fmt=fmt, quality=quality)
    return _bytes_to_b64(result)


@mcp.tool()
def image_compress(
    image_b64: str,
    quality: int = 60,
    fmt: str = "jpeg",
) -> str:
    """Compress an image. Default JPEG at quality 60. Returns base64."""
    result = engine.compress(_b64_to_bytes(image_b64), quality=quality, fmt=fmt)
    return _bytes_to_b64(result)


@mcp.tool()
def image_convert(
    image_b64: str,
    fmt: str = "png",
    quality: int = 85,
) -> str:
    """Convert image format (png, jpeg, webp, gif, bmp, tiff). Returns base64."""
    result = engine.convert(_b64_to_bytes(image_b64), fmt=fmt, quality=quality)  # type: ignore[arg-type]
    return _bytes_to_b64(result)


@mcp.tool()
def image_grayscale(
    image_b64: str,
    fmt: str = "png",
    quality: int = 85,
) -> str:
    """Convert image to grayscale. Returns base64."""
    result = engine.grayscale(_b64_to_bytes(image_b64), fmt=fmt, quality=quality)
    return _bytes_to_b64(result)


@mcp.tool()
def image_blur(
    image_b64: str,
    radius: float = 2.0,
    fmt: str = "png",
    quality: int = 85,
) -> str:
    """Apply Gaussian blur. Returns base64."""
    result = engine.blur(_b64_to_bytes(image_b64), radius=radius, fmt=fmt, quality=quality)
    return _bytes_to_b64(result)


@mcp.tool()
def image_info(image_b64: str) -> dict[str, object]:
    """Get image dimensions, format, mode, file size, EXIF presence."""
    result = engine.info(_b64_to_bytes(image_b64))
    return {
        "width": result.width,
        "height": result.height,
        "format": result.format,
        "mode": result.mode,
        "file_size": result.file_size,
        "has_exif": result.has_exif,
        "has_alpha": result.has_alpha,
    }


@mcp.tool()
def image_watermark(
    image_b64: str,
    text: str,
    position: str = "bottom-right",
    opacity: int = 128,
    font_size: int = 24,
    color: str = "#ffffff",
    fmt: str = "png",
    quality: int = 85,
) -> str:
    """Add text watermark at given position. Returns base64."""
    result = engine.watermark(
        _b64_to_bytes(image_b64),
        text,
        position=position,  # type: ignore[arg-type]
        opacity=opacity,
        font_size=font_size,
        color=color,
        fmt=fmt,
        quality=quality,
    )
    return _bytes_to_b64(result)


@mcp.tool()
def image_thumbnail(
    image_b64: str,
    size: int = 256,
    fmt: str = "png",
    quality: int = 85,
) -> str:
    """Create square thumbnail (center-cropped). Returns base64."""
    result = engine.thumbnail(_b64_to_bytes(image_b64), size=size, fmt=fmt, quality=quality)
    return _bytes_to_b64(result)


@mcp.tool()
def image_strip_metadata(
    image_b64: str,
    fmt: str = "png",
    quality: int = 85,
) -> str:
    """Strip all EXIF and metadata from image. Returns base64."""
    result = engine.strip_metadata(_b64_to_bytes(image_b64), fmt=fmt, quality=quality)
    return _bytes_to_b64(result)


@mcp.tool()
def image_border(
    image_b64: str,
    width: int = 10,
    color: str = "#000000",
    fmt: str = "png",
    quality: int = 85,
) -> str:
    """Add solid color border. Returns base64."""
    data = _b64_to_bytes(image_b64)
    result = engine.border(data, width=width, color=color, fmt=fmt, quality=quality)
    return _bytes_to_b64(result)
