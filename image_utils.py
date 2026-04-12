import io
from PIL import Image
from config import settings

def optimize_image(file_content: bytes, max_size: int = settings.IMAGE_MAX_SIZE, quality: int = settings.IMAGE_QUALITY) -> tuple[bytes, str, str]:
    """
    Optimizes an image by resizing and converting to WebP.
    Returns (optimized_content, new_filename_extension, mime_type)
    """
    # Load image from bytes
    img = Image.open(io.BytesIO(file_content))
    
    # Convert to RGB if necessary (e.g. if it has alpha channel and we want to be safe, 
    # though WebP handles alpha fine. But RGB is standard for general photos).
    # If it's RGBA, WebP will preserve it. If it's CMYK, we must convert to RGB.
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGBA")
    elif img.mode != "RGB":
        img = img.convert("RGB")
    
    # Resize keeping aspect ratio
    width, height = img.size
    if width > max_size or height > max_size:
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Save as WebP
    output = io.BytesIO()
    img.save(output, format="WEBP", quality=quality, optimize=True)
    optimized_content = output.getvalue()
    
    return optimized_content, "webp", "image/webp"
