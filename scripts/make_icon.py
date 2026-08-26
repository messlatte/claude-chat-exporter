from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "claude-chat-exporter.ico"
PREVIEW = ROOT / "assets" / "claude-chat-exporter.png"


def build_icon() -> None:
    size = 1024
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((32, 32, 992, 992), radius=232, fill="#1B1A18")
    draw.rounded_rectangle((98, 180, 716, 650), radius=142, fill="#F5F0E9")
    draw.polygon([(270, 620), (270, 790), (452, 642)], fill="#F5F0E9")
    draw.ellipse((192, 350, 256, 414), fill="#D99762")
    draw.ellipse((290, 350, 354, 414), fill="#BE7F53")

    draw.rounded_rectangle((426, 496, 922, 830), radius=116, fill="#71C49A")
    draw.polygon([(670, 796), (824, 930), (814, 780)], fill="#71C49A")
    draw.rounded_rectangle((410, 337, 770, 407), radius=35, fill="#D99762")
    draw.polygon([(724, 270), (872, 372), (724, 474)], fill="#71C49A")

    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, format="ICO", sizes=sizes)
    image.resize((256, 256), Image.Resampling.LANCZOS).save(PREVIEW, format="PNG")


if __name__ == "__main__":
    build_icon()
