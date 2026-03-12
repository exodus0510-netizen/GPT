from __future__ import annotations

from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen


def generate_image_via_pollinations(prompt: str, output_path: str) -> str:
    """
    Generate an image using Pollinations public endpoint.
    This is keyless and useful for quick prototyping.
    """
    encoded = quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&nologo=true"

    data = urlopen(url, timeout=60).read()
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return str(target)
