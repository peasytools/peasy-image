"""peasy-image — Python image toolkit.

20 image operations powered by Pillow:
resize, crop, rotate, flip, compress, convert, grayscale, blur, sharpen,
brightness, contrast, invert, watermark, thumbnail, strip_metadata, info,
get_exif, border, round_corners, pad, overlay.
"""

from __future__ import annotations

from peasy_image.engine import (
    AnchorPosition,
    ExifData,
    FlipMode,
    ImageFormat,
    ImageInfo,
    ImageInput,
    blur,
    border,
    brightness,
    compress,
    contrast,
    convert,
    crop,
    flip,
    get_exif,
    grayscale,
    info,
    invert,
    overlay,
    pad,
    resize,
    rotate,
    round_corners,
    sharpen,
    strip_metadata,
    thumbnail,
    watermark,
)

__version__ = "0.1.0"

__all__ = [
    # Types
    "AnchorPosition",
    "ExifData",
    "FlipMode",
    "ImageFormat",
    "ImageInfo",
    "ImageInput",
    # Operations
    "blur",
    "border",
    "brightness",
    "compress",
    "contrast",
    "convert",
    "crop",
    "flip",
    "get_exif",
    "grayscale",
    "info",
    "invert",
    "overlay",
    "pad",
    "resize",
    "rotate",
    "round_corners",
    "sharpen",
    "strip_metadata",
    "thumbnail",
    "watermark",
]
