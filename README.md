# peasy-image

[![PyPI version](https://agentgif.com/badge/pypi/peasy-image/version.svg)](https://pypi.org/project/peasy-image/)
[![Python](https://img.shields.io/pypi/pyversions/peasy-image)](https://pypi.org/project/peasy-image/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Dependencies: 1](https://img.shields.io/badge/dependencies-1_(Pillow)-blue)](https://pypi.org/project/peasy-image/)

Python image toolkit -- 21 operations for resize, crop, rotate, compress, convert, blur, sharpen, watermark, and more. Powered by [Pillow](https://python-pillow.org/). Every function accepts `bytes | Path | str` and returns `bytes`, so it works equally well with files on disk, HTTP responses, and in-memory buffers. Outputs to 7 image formats: PNG, JPEG, WebP, GIF, BMP, TIFF, and ICO.

Built for [peasyimage.com](https://peasyimage.com), which offers free interactive tools for image resizing, compression, format conversion, metadata stripping, and more. The site serves as the reference implementation and hosts the REST API, glossary, and developer guides that complement this library.

> **Try the interactive tools at [peasyimage.com](https://peasyimage.com)** -- [Image Tools](https://peasyimage.com/), [Image Glossary](https://peasyimage.com/glossary/), [Image Guides](https://peasyimage.com/guides/)

<p align="center">
  <img src="demo.gif" alt="peasy-image demo — resize, compress, convert images in Python" width="800">
</p>

## Table of Contents

- [Install](#install)
- [Quick Start](#quick-start)
- [What You Can Do](#what-you-can-do)
  - [Image Resizing & Cropping](#image-resizing--cropping)
  - [Format Conversion](#format-conversion)
  - [Image Compression](#image-compression)
  - [Image Enhancement](#image-enhancement)
  - [Watermarking & Overlays](#watermarking--overlays)
  - [Thumbnails & Padding](#thumbnails--padding)
  - [Visual Effects](#visual-effects)
  - [Metadata & Privacy](#metadata--privacy)
- [Input Flexibility](#input-flexibility)
- [Command-Line Interface](#command-line-interface)
- [MCP Server (Claude, Cursor, Windsurf)](#mcp-server-claude-cursor-windsurf)
- [REST API Client](#rest-api-client)
- [API Reference](#api-reference)
- [Learn More About Image Processing](#learn-more-about-image-processing)
- [Also Available](#also-available)
- [Peasy Developer Tools](#peasy-developer-tools)
- [License](#license)

## Install

```bash
pip install peasy-image            # Core library (Pillow)
pip install "peasy-image[cli]"     # + CLI (typer, rich)
pip install "peasy-image[mcp]"     # + MCP server for AI assistants
pip install "peasy-image[api]"     # + REST API client (httpx)
pip install "peasy-image[all]"     # Everything
```

## Quick Start

```python
from peasy_image import resize, compress, convert, info, watermark

# Resize an image to 800px wide, maintaining aspect ratio
resized = resize("photo.jpg", width=800)

# Compress a PNG to JPEG at quality 60 for web delivery
compressed = compress("photo.png", quality=60, fmt="jpeg")

# Convert any image to WebP for modern browsers
webp = convert("photo.jpg", fmt="webp")

# Add a semi-transparent copyright watermark
marked = watermark("photo.jpg", "© 2026", position="bottom-right", opacity=128)

# Inspect image dimensions, format, and EXIF presence
meta = info("photo.jpg")
print(f"{meta.width}x{meta.height} {meta.format} ({meta.file_size / 1024:.0f} KB)")
```

Every function returns `bytes`. Write the result to disk, send it over HTTP, or pipe it into the next operation:

```python
from pathlib import Path
from peasy_image import resize, compress

# Chain operations: resize then compress
resized = resize("photo.jpg", width=1200)
optimized = compress(resized, quality=70, fmt="webp")
Path("output.webp").write_bytes(optimized)
```

## What You Can Do

### Image Resizing & Cropping

Resizing images correctly means understanding aspect ratios and resampling algorithms. An image with a 3:2 aspect ratio (e.g., 6000x4000 from a DSLR) should be scaled proportionally to avoid distortion. peasy-image uses Lanczos resampling by default -- the highest quality downsampling algorithm available in Pillow, producing sharp results without aliasing artifacts.

| Operation | Function | Key Parameters |
|-----------|----------|----------------|
| Resize by width | `resize()` | `width`, `maintain_aspect=True` |
| Resize by height | `resize()` | `height`, `maintain_aspect=True` |
| Resize exact | `resize()` | `width`, `height`, `maintain_aspect=False` |
| Crop to box | `crop()` | `left`, `top`, `right`, `bottom` |
| Square thumbnail | `thumbnail()` | `size` (center-crops then resizes) |
| Pad to dimensions | `pad()` | `target_width`, `target_height`, `color` |

```python
from peasy_image import resize, crop, thumbnail, pad

# Resize a 6000x4000 DSLR photo to 1200px wide for blog posts
blog_image = resize("dslr_photo.jpg", width=1200, fmt="jpeg", quality=85)

# Crop a specific region — coordinates are (left, top, right, bottom)
cropped = crop("screenshot.png", left=100, top=50, right=900, bottom=650)

# Create a 256x256 square thumbnail for user avatars
avatar = thumbnail("portrait.jpg", size=256, fmt="webp")

# Pad a 800x600 image to 1200x1200 with white background for social media
padded = pad("product.png", target_width=1200, target_height=1200, color="#ffffff")
```

Learn more: [PeasyImage](https://peasyimage.com/) · [Aspect Ratio Glossary](https://peasyimage.com/glossary/aspect-ratio/)

### Format Conversion

Choosing the right image format depends on the content, target platform, and whether transparency is needed. Each format makes different trade-offs between file size, quality, feature support, and browser compatibility.

| Format | Transparency | Animation | Lossy/Lossless | Best For |
|--------|:------------:|:---------:|:--------------:|----------|
| **PNG** | Yes (alpha) | No | Lossless | Screenshots, logos, graphics with text |
| **JPEG** | No | No | Lossy | Photographs, gradients, natural images |
| **WebP** | Yes (alpha) | Yes | Both | Web delivery (26-34% smaller than JPEG) |
| **GIF** | Yes (1-bit) | Yes | Lossless (palette) | Simple animations, icons (256 color limit) |
| **BMP** | No | No | Uncompressed | Windows bitmaps, legacy compatibility |
| **TIFF** | Yes (alpha) | No | Both | Print, archival, medical imaging |
| **ICO** | Yes (alpha) | No | Lossless | Favicons, Windows icons |

```python
from peasy_image import convert

# Convert a BMP screenshot to PNG for lossless web sharing
png_bytes = convert("screenshot.bmp", fmt="png")

# Convert a JPEG photo to WebP for 30%+ smaller file size on the web
webp_bytes = convert("photo.jpg", fmt="webp", quality=80)

# Convert a PNG logo to ICO for favicon use
ico_bytes = convert("logo.png", fmt="ico")

# Convert a WebP animation frame to TIFF for print production
tiff_bytes = convert("frame.webp", fmt="tiff")
```

Learn more: [PeasyImage](https://peasyimage.com/) · [Image Guides](https://peasyimage.com/guides/) · [WebP Glossary](https://peasyimage.com/glossary/webp/)

### Image Compression

Image compression reduces file size while balancing perceptual quality. For photographs, JPEG compression at quality 60-80 typically achieves 70-90% file size reduction with minimal visible degradation. WebP compression offers even better results -- Google reports 25-34% smaller files compared to JPEG at equivalent perceptual quality.

The `quality` parameter controls the compression level: 100 means maximum quality (largest file), and lower values produce smaller files with increasing artifacts. For JPEG, values below 50 introduce visible blocking artifacts. For WebP, the threshold is around 40.

```python
from peasy_image import compress

# Compress a 5MB JPEG photo to ~500KB for web pages
web_ready = compress("large_photo.jpg", quality=70, fmt="jpeg")

# Aggressive compression for email thumbnails
email_img = compress("photo.png", quality=50, fmt="jpeg")

# WebP compression for modern web delivery — smaller than JPEG
webp_small = compress("photo.jpg", quality=65, fmt="webp")
```

Learn more: [PeasyImage](https://peasyimage.com/) · [Image Guides](https://peasyimage.com/guides/) · [Lossy Compression Glossary](https://peasyimage.com/glossary/lossy-compression/)

### Image Enhancement

Image enhancement operations adjust the visual properties of an image. These are powered by Pillow's `ImageEnhance` and `ImageFilter` modules, which implement standard image processing algorithms.

| Operation | Function | Factor/Radius | Effect |
|-----------|----------|:-------------:|--------|
| Gaussian blur | `blur()` | `radius=2.0` | Softens the image, reduces noise |
| Sharpen | `sharpen()` | `factor=2.0` | Increases edge definition |
| Brightness | `brightness()` | `factor=1.2` | `1.0` = original, `>1.0` = brighter, `0.0` = black |
| Contrast | `contrast()` | `factor=1.5` | `1.0` = original, `>1.0` = more contrast |
| Grayscale | `grayscale()` | -- | Converts to single-channel luminance |
| Invert | `invert()` | -- | Reverses all color values (negative) |

```python
from peasy_image import blur, sharpen, brightness, contrast, grayscale, invert

# Apply Gaussian blur with radius 5 for a background bokeh effect
blurred = blur("photo.jpg", radius=5.0, fmt="jpeg")

# Sharpen a slightly soft scan — factor 2.0 doubles edge contrast
sharp = sharpen("scan.png", factor=2.0)

# Brighten an underexposed photo by 30%
bright = brightness("dark_photo.jpg", factor=1.3, fmt="jpeg")

# Increase contrast for a washed-out image
vivid = contrast("flat_photo.jpg", factor=1.8, fmt="jpeg")

# Convert a portrait to black-and-white for artistic effect
bw = grayscale("portrait.jpg", fmt="jpeg", quality=90)

# Create a color-inverted negative
negative = invert("photo.png")
```

Learn more: [PeasyImage](https://peasyimage.com/) · [Gaussian Blur Glossary](https://peasyimage.com/glossary/gaussian-blur/) · [Image Guides](https://peasyimage.com/guides/)

### Watermarking & Overlays

Watermarks protect image ownership and establish brand attribution. peasy-image supports text watermarks with configurable position, opacity, font size, and color. The overlay function composites one image on top of another, useful for logos, badges, or frame overlays.

Both operations use 5 anchor positions for placement:

| Position | Anchor | Typical Use |
|----------|--------|-------------|
| `top-left` | Upper-left corner | Branding logos |
| `top-right` | Upper-right corner | Date stamps |
| `bottom-left` | Lower-left corner | Credit lines |
| `bottom-right` | Lower-right corner | Copyright text (default) |
| `center` | Centered on canvas | Proof watermarks |

```python
from peasy_image import watermark, overlay

# Add a copyright notice in the bottom-right corner at 50% opacity
marked = watermark(
    "photo.jpg",
    "© 2026 Studio Name",
    position="bottom-right",
    opacity=128,          # 0 = invisible, 255 = fully opaque
    font_size=24,
    color="#ffffff",       # White text
    fmt="jpeg",
)

# Add a centered "DRAFT" watermark for proof images
proof = watermark("design.png", "DRAFT", position="center", opacity=80, font_size=72)

# Composite a logo badge onto a product photo
branded = overlay(
    "product.jpg",
    "logo.png",
    position="top-left",
    opacity=200,           # Slightly transparent
)
```

Learn more: [PeasyImage](https://peasyimage.com/) · [Watermark Glossary](https://peasyimage.com/glossary/watermark/)

### Thumbnails & Padding

Creating consistent thumbnail sizes from images of varying dimensions requires either cropping (losing edges) or padding (adding borders). The `thumbnail()` function center-crops to a square then resizes -- ideal for avatar grids and gallery previews. The `pad()` function fits the image within target dimensions and fills the remaining space with a background color -- ideal for product listings and social media where specific dimensions are required.

```python
from peasy_image import thumbnail, pad

# Create 128x128 square thumbnails for a user avatar grid
avatar = thumbnail("profile.jpg", size=128, fmt="webp")

# Create an Instagram-compatible 1080x1080 image with white letterboxing
square = pad("landscape.jpg", target_width=1080, target_height=1080, color="#ffffff")

# Create a Pinterest-optimized 1000x1500 pin with dark background
pin = pad("photo.jpg", target_width=1000, target_height=1500, color="#1a1a1a")
```

Learn more: [PeasyImage](https://peasyimage.com/) · [Image Glossary](https://peasyimage.com/glossary/)

### Visual Effects

Visual effects transform the structural appearance of an image -- rotating, flipping, adding borders, or rounding corners. These are commonly used in UI design, social media graphics, and batch processing pipelines.

| Operation | Function | Key Parameters |
|-----------|----------|----------------|
| Rotate | `rotate()` | `angle`, `expand=True`, `fill_color` |
| Flip | `flip()` | `mode`: `"horizontal"`, `"vertical"`, `"both"` |
| Border | `border()` | `width`, `color` (hex string) |
| Round corners | `round_corners()` | `radius` (pixels) |

```python
from peasy_image import rotate, flip, border, round_corners

# Rotate a scanned document 90 degrees clockwise (expand canvas to fit)
straightened = rotate("scan.png", angle=-90, expand=True)

# Flip a selfie horizontally to match mirror view
mirrored = flip("selfie.jpg", mode="horizontal", fmt="jpeg")

# Add a 4px black border around a product photo
framed = border("product.png", width=4, color="#000000")

# Apply 20px rounded corners for a card-style UI element
card = round_corners("screenshot.png", radius=20)
```

Learn more: [PeasyImage](https://peasyimage.com/) · [Image Rotation Glossary](https://peasyimage.com/glossary/rotation/)

### Metadata & Privacy

Digital photos from smartphones and cameras embed EXIF (Exchangeable Image File Format) metadata that can include GPS coordinates, camera model, date/time, lens information, and editing software. Publishing images with EXIF data intact can unintentionally expose a photographer's home address, daily routine, or equipment details.

The `strip_metadata()` function creates a clean copy of the image with pixel data only -- no EXIF, IPTC, or XMP metadata survives. The `info()` and `get_exif()` functions let you inspect what metadata exists before deciding what to do with it.

| Function | Purpose | Returns |
|----------|---------|---------|
| `info()` | Dimensions, format, mode, file size, EXIF/alpha flags | `ImageInfo` dataclass |
| `get_exif()` | Camera make/model, GPS, exposure, ISO, focal length | `ExifData` dataclass |
| `strip_metadata()` | Remove all EXIF, IPTC, XMP metadata | Clean image `bytes` |

```python
from peasy_image import info, get_exif, strip_metadata

# Check if an image contains EXIF metadata before publishing
meta = info("photo.jpg")
print(f"Size: {meta.width}x{meta.height}, EXIF: {meta.has_exif}, Alpha: {meta.has_alpha}")

# Inspect EXIF data — camera, GPS, exposure settings
exif = get_exif("photo.jpg")
print(f"Camera: {exif.camera_make} {exif.camera_model}")
print(f"GPS: {exif.gps_latitude}, {exif.gps_longitude}")  # Privacy risk!
print(f"ISO: {exif.iso}, Exposure: {exif.exposure_time}, f/{exif.f_number}")

# Strip all metadata before sharing online — removes GPS, camera info, timestamps
clean = strip_metadata("photo.jpg", fmt="jpeg", quality=90)
```

Learn more: [PeasyImage](https://peasyimage.com/) · [EXIF Glossary](https://peasyimage.com/glossary/exif/) · [Image Guides](https://peasyimage.com/guides/)

## Input Flexibility

Every function in peasy-image accepts 3 input types through the `ImageInput` union type:

| Input Type | Example | Use Case |
|------------|---------|----------|
| `bytes` | `resize(raw_bytes, width=800)` | HTTP responses, in-memory buffers, chained operations |
| `Path` | `resize(Path("photo.jpg"), width=800)` | Explicit pathlib paths |
| `str` | `resize("photo.jpg", width=800)` | String file paths (most common) |

This design means you can chain operations without touching the filesystem:

```python
from peasy_image import resize, compress, watermark

# Pipeline: resize → watermark → compress — all in memory
pipeline = resize("original.jpg", width=1200)
pipeline = watermark(pipeline, "© 2026", opacity=100)
pipeline = compress(pipeline, quality=75, fmt="webp")
# pipeline is bytes — write to disk or send over HTTP
```

## Command-Line Interface

Install with `pip install "peasy-image[cli]"` for terminal access to all 21 operations.

```bash
# Resize an image to 800px wide
peasy-image resize photo.jpg --width 800

# Compress a PNG to JPEG at quality 60 — shows file size reduction percentage
peasy-image compress photo.png --quality 60

# Convert a BMP to WebP
peasy-image convert photo.bmp webp

# Inspect image dimensions, format, mode, EXIF presence
peasy-image info photo.jpg

# Add a watermark at bottom-right with custom font size and opacity
peasy-image watermark photo.jpg "© 2026" --position bottom-right --font-size 32

# Create a 128x128 square thumbnail
peasy-image thumbnail photo.jpg --size 128

# Apply Gaussian blur with radius 5
peasy-image blur photo.jpg --radius 5.0

# Sharpen an image with factor 2.5
peasy-image sharpen photo.jpg --factor 2.5

# Strip all EXIF metadata before sharing
peasy-image strip photo.jpg -o clean_photo.png

# Add a 10px red border
peasy-image border photo.png --width 10 --color "#ff0000"

# Rotate 90 degrees clockwise
peasy-image rotate photo.jpg -90
```

All commands support `-o`/`--output` for custom output path, `-f`/`--format` for output format, and `-q`/`--quality` for compression quality.

## MCP Server (Claude, Cursor, Windsurf)

peasy-image includes a Model Context Protocol server that exposes 12 image tools to AI assistants. Images are passed as base64-encoded strings.

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "peasy-image": {
      "command": "uvx",
      "args": ["--from", "peasy-image[mcp]", "python", "-m", "peasy_image"]
    }
  }
}
```

**Cursor** (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "peasy-image": {
      "command": "uvx",
      "args": ["--from", "peasy-image[mcp]", "python", "-m", "peasy_image"]
    }
  }
}
```

**Windsurf** (`~/.windsurf/mcp.json`):

```json
{
  "mcpServers": {
    "peasy-image": {
      "command": "uvx",
      "args": ["--from", "peasy-image[mcp]", "python", "-m", "peasy_image"]
    }
  }
}
```

Available MCP tools: `image_resize`, `image_crop`, `image_rotate`, `image_compress`, `image_convert`, `image_grayscale`, `image_blur`, `image_info`, `image_watermark`, `image_thumbnail`, `image_strip_metadata`, `image_border`.

## REST API Client

The API client wraps the [peasyimage.com REST API](https://peasyimage.com/developers/) for querying tools, glossary terms, and guides programmatically.

```bash
pip install "peasy-image[api]"
```

```python
from peasy_image.api import PeasyImageAPI

api = PeasyImageAPI()

# List all available image tools
tools = api.list_tools()
for tool in tools:
    print(f"{tool['name']}: {tool['description']}")

# Get details for a specific tool
resize_tool = api.get_tool("resize-image")

# Search across tools, glossary, and guides
results = api.search("webp compression")

# Browse the image processing glossary
terms = api.list_glossary()
exif_term = api.get_glossary_term("exif")

# Read image processing guides
guides = api.list_guides()
compression_guide = api.get_guide("image-compression")

# Get the OpenAPI 3.1.0 specification
spec = api.openapi_spec()
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tools/` | List all image tools |
| GET | `/api/v1/tools/{slug}/` | Tool detail |
| GET | `/api/v1/glossary/` | List glossary terms |
| GET | `/api/v1/glossary/{slug}/` | Glossary term detail |
| GET | `/api/v1/guides/` | List image guides |
| GET | `/api/v1/guides/{slug}/` | Guide detail |
| GET | `/api/v1/search/?q={query}` | Search across all content |
| GET | `/api/openapi.json` | OpenAPI 3.1.0 specification |

Full API documentation at [peasyimage.com/developers/](https://peasyimage.com/developers/).

## API Reference

### Image Operations

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `resize(source, width, height, *, maintain_aspect, fmt, quality)` | `width: int\|None`, `height: int\|None`, `maintain_aspect: bool=True` | `bytes` | Resize with Lanczos resampling, optional aspect ratio preservation |
| `crop(source, left, top, right, bottom, *, fmt, quality)` | `left: int`, `top: int`, `right: int`, `bottom: int` | `bytes` | Crop to bounding box coordinates |
| `rotate(source, angle, *, expand, fill_color, fmt, quality)` | `angle: float`, `expand: bool=True`, `fill_color: str="#ffffff"` | `bytes` | Rotate counter-clockwise with optional canvas expansion |
| `flip(source, mode, *, fmt, quality)` | `mode: "horizontal"\|"vertical"\|"both"` | `bytes` | Mirror image along axis |
| `compress(source, *, quality, fmt)` | `quality: int=60`, `fmt: str="jpeg"` | `bytes` | Reduce file size via quality adjustment |
| `convert(source, fmt, *, quality)` | `fmt: "png"\|"jpeg"\|"webp"\|"gif"\|"bmp"\|"tiff"\|"ico"` | `bytes` | Convert between 7 image formats |
| `grayscale(source, *, fmt, quality)` | -- | `bytes` | Convert to single-channel luminance |
| `blur(source, radius, *, fmt, quality)` | `radius: float=2.0` | `bytes` | Apply Gaussian blur filter |
| `sharpen(source, factor, *, fmt, quality)` | `factor: float=2.0` (1.0=original) | `bytes` | Enhance edge definition |
| `brightness(source, factor, *, fmt, quality)` | `factor: float=1.2` (1.0=original, 0.0=black) | `bytes` | Adjust image brightness |
| `contrast(source, factor, *, fmt, quality)` | `factor: float=1.5` (1.0=original) | `bytes` | Adjust image contrast |
| `invert(source, *, fmt, quality)` | -- | `bytes` | Reverse all color values (negative) |
| `watermark(source, text, *, position, opacity, font_size, color, fmt, quality)` | `text: str`, `position: AnchorPosition`, `opacity: int=128` | `bytes` | Add text watermark at anchor position |
| `thumbnail(source, size, *, fmt, quality)` | `size: int=256` | `bytes` | Center-crop to square then resize |
| `strip_metadata(source, *, fmt, quality)` | -- | `bytes` | Remove all EXIF, IPTC, XMP metadata |
| `border(source, width, color, *, fmt, quality)` | `width: int=10`, `color: str="#000000"` | `bytes` | Add solid color border around image |
| `round_corners(source, radius, *, fmt, quality)` | `radius: int=20` | `bytes` | Apply rounded corners with transparency |
| `pad(source, target_width, target_height, *, color, fmt, quality)` | `target_width: int`, `target_height: int`, `color: str="#ffffff"` | `bytes` | Pad to dimensions with centered image |
| `overlay(source, overlay_source, *, position, opacity, fmt, quality)` | `overlay_source: ImageInput`, `position: AnchorPosition`, `opacity: int=255` | `bytes` | Composite one image on top of another |

### Metadata Operations

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `info(source)` | -- | `ImageInfo` | Width, height, format, mode, file size, EXIF/alpha flags |
| `get_exif(source)` | -- | `ExifData` | Camera make/model, GPS, exposure, ISO, focal length, raw tags |

### Types

| Type | Values | Used By |
|------|--------|---------|
| `ImageInput` | `bytes \| Path \| str` | All functions (first parameter) |
| `ImageFormat` | `"png" \| "jpeg" \| "webp" \| "gif" \| "bmp" \| "tiff" \| "ico"` | `convert()`, `fmt` parameter |
| `FlipMode` | `"horizontal" \| "vertical" \| "both"` | `flip()` |
| `AnchorPosition` | `"top-left" \| "top-right" \| "bottom-left" \| "bottom-right" \| "center"` | `watermark()`, `overlay()` |
| `ImageInfo` | Frozen dataclass: `width`, `height`, `format`, `mode`, `file_size`, `has_exif`, `has_alpha` | `info()` return type |
| `ExifData` | Frozen dataclass: `camera_make`, `camera_model`, `datetime`, `exposure_time`, `f_number`, `iso`, `focal_length`, `gps_latitude`, `gps_longitude`, `software`, `raw` | `get_exif()` return type |

## Learn More About Image Processing

- **Tools**: [PeasyImage Tools](https://peasyimage.com/)
- **Guides**: [Image Processing Guides](https://peasyimage.com/guides/)
- **Glossary**: [EXIF](https://peasyimage.com/glossary/exif/) · [Aspect Ratio](https://peasyimage.com/glossary/aspect-ratio/) · [Gaussian Blur](https://peasyimage.com/glossary/gaussian-blur/) · [WebP](https://peasyimage.com/glossary/webp/) · [Lossy Compression](https://peasyimage.com/glossary/lossy-compression/)
- **API**: [REST API Docs](https://peasyimage.com/developers/) · [OpenAPI Spec](https://peasyimage.com/api/openapi.json)

## Also Available

| Platform | Install | Link |
|----------|---------|------|
| **npm** | `npm install peasy-image` | [npm](https://www.npmjs.com/package/peasy-image) |
| **MCP** | `uvx --from "peasy-image[mcp]" python -m peasy_image` | [Config](#mcp-server-claude-cursor-windsurf) |

## Peasy Developer Tools

Part of the [Peasy Tools](https://peasytools.com) open-source developer tools ecosystem.

| Package | PyPI | npm | Description |
|---------|------|-----|-------------|
| **peasy-image** | [PyPI](https://pypi.org/project/peasy-image/) | [npm](https://www.npmjs.com/package/peasy-image) | 21 image operations: resize, crop, compress, convert, watermark -- [peasyimage.com](https://peasyimage.com) |
| peasy-pdf | [PyPI](https://pypi.org/project/peasy-pdf/) | [npm](https://www.npmjs.com/package/peasy-pdf) | PDF merge, split, rotate, compress, extract, encrypt -- [peasypdf.com](https://peasypdf.com) |
| peasy-css | [PyPI](https://pypi.org/project/peasy-css/) | [npm](https://www.npmjs.com/package/peasy-css) | CSS gradients, shadows, borders, flexbox, grid, animations -- [peasycss.com](https://peasycss.com) |
| peasy-compress | [PyPI](https://pypi.org/project/peasy-compress/) | [npm](https://www.npmjs.com/package/peasy-compress) | ZIP, TAR, gzip, bz2, lzma archive operations -- [peasytools.com](https://peasytools.com) |
| peasy-document | [PyPI](https://pypi.org/project/peasy-document/) | [npm](https://www.npmjs.com/package/peasy-document) | Markdown, HTML, CSV, JSON document conversion -- [peasytools.com](https://peasytools.com) |
| peasy-audio | [PyPI](https://pypi.org/project/peasy-audio/) | -- | Audio convert, trim, merge, normalize, analyze -- [peasyaudio.com](https://peasyaudio.com) |
| peasy-video | [PyPI](https://pypi.org/project/peasy-video/) | -- | Video trim, resize, extract audio, thumbnails, GIF -- [peasyvideo.com](https://peasyvideo.com) |
| peasy-convert | [PyPI](https://pypi.org/project/peasy-convert/) | -- | Unified CLI for all Peasy tools -- [peasytools.com](https://peasytools.com) |
| peasy-mcp | [PyPI](https://pypi.org/project/peasy-mcp/) | -- | Unified MCP server for AI assistants -- [peasytools.com](https://peasytools.com) |

## License

MIT
