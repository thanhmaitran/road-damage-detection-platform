"""Upload validation: size, real content (Pillow decode), pixel cap. Filename is never used."""
import io

from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError

ALLOWED_FORMATS = {"JPEG", "PNG"}


async def read_image(file, max_bytes: int, max_pixels: int) -> Image.Image:
    data = await file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(413, f"File too large (max {max_bytes // (1024 * 1024)} MB)")
    if not data:
        raise HTTPException(400, "Empty file")
    try:
        with Image.open(io.BytesIO(data)) as probe:
            fmt = probe.format
            if probe.width * probe.height > max_pixels:
                raise HTTPException(413, "Image dimensions too large")
        if fmt not in ALLOWED_FORMATS:
            raise HTTPException(415, "Only JPEG and PNG images are supported")
        img = Image.open(io.BytesIO(data))
        img.load()
        return img
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(400, "Invalid or corrupted image")
