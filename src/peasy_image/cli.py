"""peasy-image CLI — Image processing from the terminal.

Usage::

    peasy-image resize photo.jpg --width 800
    peasy-image crop photo.png --left 10 --top 10 --right 200 --bottom 200
    peasy-image compress photo.png --quality 60
    peasy-image convert photo.bmp webp
    peasy-image info photo.jpg
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from peasy_image import engine

app = typer.Typer(
    name="peasy-image",
    help="Image toolkit — 20 tools from peasyimage.com",
    no_args_is_help=True,
)

console = Console()


def _write_output(data: bytes, output: Path) -> None:
    """Write bytes to file and display size info."""
    output.write_bytes(data)
    kb = len(data) / 1024
    console.print(f"[green]Saved[/green] {output} ({kb:.1f} KB)")


@app.command(name="resize")
def resize_cmd(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    width: Annotated[int | None, typer.Option("--width", "-w")] = None,
    height: Annotated[int | None, typer.Option("--height", "-h")] = None,
    no_aspect: Annotated[bool, typer.Option("--no-aspect")] = False,
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
    fmt: Annotated[str, typer.Option("-f", "--format")] = "png",
    quality: Annotated[int, typer.Option("-q", "--quality")] = 85,
) -> None:
    """Resize an image."""
    result = engine.resize(
        input_file,
        width=width,
        height=height,
        maintain_aspect=not no_aspect,
        fmt=fmt,
        quality=quality,
    )
    out = output or Path(f"{input_file.stem}_resized.{fmt}")
    _write_output(result, out)


@app.command(name="crop")
def crop_cmd(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    left: Annotated[int, typer.Option(help="Left edge")],
    top: Annotated[int, typer.Option(help="Top edge")],
    right: Annotated[int, typer.Option(help="Right edge")],
    bottom: Annotated[int, typer.Option(help="Bottom edge")],
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
    fmt: Annotated[str, typer.Option("-f", "--format")] = "png",
    quality: Annotated[int, typer.Option("-q", "--quality")] = 85,
) -> None:
    """Crop an image to a bounding box."""
    result = engine.crop(input_file, left, top, right, bottom, fmt=fmt, quality=quality)
    out = output or Path(f"{input_file.stem}_cropped.{fmt}")
    _write_output(result, out)


@app.command(name="rotate")
def rotate_cmd(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    angle: Annotated[float, typer.Argument(help="Rotation angle in degrees")],
    no_expand: Annotated[bool, typer.Option("--no-expand")] = False,
    fill: Annotated[str, typer.Option("--fill")] = "#ffffff",
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
    fmt: Annotated[str, typer.Option("-f", "--format")] = "png",
    quality: Annotated[int, typer.Option("-q", "--quality")] = 85,
) -> None:
    """Rotate an image by the given angle."""
    result = engine.rotate(
        input_file, angle, expand=not no_expand, fill_color=fill, fmt=fmt, quality=quality
    )
    out = output or Path(f"{input_file.stem}_rotated.{fmt}")
    _write_output(result, out)


@app.command(name="flip")
def flip_cmd(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    mode: Annotated[str, typer.Argument(help="horizontal, vertical, or both")] = "horizontal",
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
    fmt: Annotated[str, typer.Option("-f", "--format")] = "png",
    quality: Annotated[int, typer.Option("-q", "--quality")] = 85,
) -> None:
    """Flip an image."""
    result = engine.flip(input_file, mode=mode, fmt=fmt, quality=quality)  # type: ignore[arg-type]
    out = output or Path(f"{input_file.stem}_flipped.{fmt}")
    _write_output(result, out)


@app.command("compress")
def compress_cmd(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    quality: Annotated[int, typer.Option("-q", "--quality")] = 60,
    fmt: Annotated[str, typer.Option("-f", "--format")] = "jpeg",
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
) -> None:
    """Compress an image."""
    original_size = input_file.stat().st_size
    result = engine.compress(input_file, quality=quality, fmt=fmt)
    out = output or Path(f"{input_file.stem}_compressed.{fmt}")
    _write_output(result, out)
    ratio = (1 - len(result) / original_size) * 100
    console.print(f"  Reduced by {ratio:.1f}%")


@app.command("convert")
def convert_cmd(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    fmt: Annotated[str, typer.Argument(help="Target format: png, jpeg, webp, gif, bmp, tiff")],
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
    quality: Annotated[int, typer.Option("-q", "--quality")] = 85,
) -> None:
    """Convert an image to a different format."""
    result = engine.convert(input_file, fmt=fmt, quality=quality)  # type: ignore[arg-type]
    out = output or Path(f"{input_file.stem}.{fmt}")
    _write_output(result, out)


@app.command(name="grayscale")
def grayscale_cmd(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
    fmt: Annotated[str, typer.Option("-f", "--format")] = "png",
    quality: Annotated[int, typer.Option("-q", "--quality")] = 85,
) -> None:
    """Convert an image to grayscale."""
    result = engine.grayscale(input_file, fmt=fmt, quality=quality)
    out = output or Path(f"{input_file.stem}_grayscale.{fmt}")
    _write_output(result, out)


@app.command(name="blur")
def blur_cmd(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    radius: Annotated[float, typer.Option("-r", "--radius")] = 2.0,
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
    fmt: Annotated[str, typer.Option("-f", "--format")] = "png",
    quality: Annotated[int, typer.Option("-q", "--quality")] = 85,
) -> None:
    """Apply Gaussian blur."""
    result = engine.blur(input_file, radius=radius, fmt=fmt, quality=quality)
    out = output or Path(f"{input_file.stem}_blurred.{fmt}")
    _write_output(result, out)


@app.command(name="sharpen")
def sharpen_cmd(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    factor: Annotated[float, typer.Option("--factor")] = 2.0,
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
    fmt: Annotated[str, typer.Option("-f", "--format")] = "png",
    quality: Annotated[int, typer.Option("-q", "--quality")] = 85,
) -> None:
    """Sharpen an image."""
    result = engine.sharpen(input_file, factor=factor, fmt=fmt, quality=quality)
    out = output or Path(f"{input_file.stem}_sharpened.{fmt}")
    _write_output(result, out)


@app.command("info")
def info_cmd(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
) -> None:
    """Display image information."""
    result = engine.info(input_file)
    console.print(f"[bold]{input_file.name}[/bold]")
    console.print(f"  Size:      {result.width} x {result.height}")
    console.print(f"  Format:    {result.format}")
    console.print(f"  Mode:      {result.mode}")
    console.print(f"  File size: {result.file_size / 1024:.1f} KB")
    console.print(f"  Has EXIF:  {result.has_exif}")
    console.print(f"  Has alpha: {result.has_alpha}")


@app.command(name="watermark")
def watermark_cmd(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    text: Annotated[str, typer.Argument(help="Watermark text")],
    position: Annotated[str, typer.Option("-p", "--position")] = "bottom-right",
    opacity: Annotated[int, typer.Option("--opacity")] = 128,
    font_size: Annotated[int, typer.Option("--font-size")] = 24,
    color: Annotated[str, typer.Option("--color")] = "#ffffff",
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
    fmt: Annotated[str, typer.Option("-f", "--format")] = "png",
    quality: Annotated[int, typer.Option("-q", "--quality")] = 85,
) -> None:
    """Add a text watermark."""
    result = engine.watermark(
        input_file,
        text,
        position=position,  # type: ignore[arg-type]
        opacity=opacity,
        font_size=font_size,
        color=color,
        fmt=fmt,
        quality=quality,
    )
    out = output or Path(f"{input_file.stem}_watermarked.{fmt}")
    _write_output(result, out)


@app.command(name="thumbnail")
def thumbnail_cmd(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    size: Annotated[int, typer.Option("-s", "--size")] = 256,
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
    fmt: Annotated[str, typer.Option("-f", "--format")] = "png",
    quality: Annotated[int, typer.Option("-q", "--quality")] = 85,
) -> None:
    """Create a square thumbnail."""
    result = engine.thumbnail(input_file, size=size, fmt=fmt, quality=quality)
    out = output or Path(f"{input_file.stem}_thumb.{fmt}")
    _write_output(result, out)


@app.command(name="border")
def border_cmd(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    width: Annotated[int, typer.Option("-w", "--width")] = 10,
    color: Annotated[str, typer.Option("-c", "--color")] = "#000000",
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
    fmt: Annotated[str, typer.Option("-f", "--format")] = "png",
    quality: Annotated[int, typer.Option("-q", "--quality")] = 85,
) -> None:
    """Add a border around an image."""
    result = engine.border(input_file, width=width, color=color, fmt=fmt, quality=quality)
    out = output or Path(f"{input_file.stem}_bordered.{fmt}")
    _write_output(result, out)


@app.command(name="strip")
def strip_cmd(
    input_file: Annotated[Path, typer.Argument(help="Input image file")],
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
    fmt: Annotated[str, typer.Option("-f", "--format")] = "png",
    quality: Annotated[int, typer.Option("-q", "--quality")] = 85,
) -> None:
    """Strip all metadata (EXIF) from an image."""
    result = engine.strip_metadata(input_file, fmt=fmt, quality=quality)
    out = output or Path(f"{input_file.stem}_stripped.{fmt}")
    _write_output(result, out)
