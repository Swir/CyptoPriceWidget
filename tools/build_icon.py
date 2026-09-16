from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
PNG = ASSETS / "crypto-price-widget.png"
ICO = ASSETS / "crypto-price-widget.ico"


def build() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    size = 512
    image = Image.new("RGBA", (size, size), (7, 17, 31, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((18, 18, 494, 494), radius=105, fill=(9, 29, 49, 255), outline=(85, 183, 255, 255), width=12)
    points = [(86, 350), (174, 276), (240, 306), (318, 194), (424, 120)]
    draw.line(points, fill=(85, 183, 255, 255), width=28, joint="curve")
    for x, y in points:
        draw.ellipse((x - 14, y - 14, x + 14, y + 14), fill=(220, 247, 255, 255))
    draw.line((112, 398, 410, 398), fill=(39, 77, 109, 255), width=12)
    image.save(PNG)
    image.save(ICO, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Generated {PNG.name} and {ICO.name}")


if __name__ == "__main__":
    build()
