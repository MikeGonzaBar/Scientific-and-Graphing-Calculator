"""Generate PNG and ICO app icon assets."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"
PNG_PATH = ASSET_DIR / "app_icon.png"
ICO_PATH = ASSET_DIR / "app_icon.ico"


def draw_icon(size: int = 256) -> Image.Image:
    """Draw the calculator icon at the requested square size."""

    image = Image.new("RGBA", (size, size), "#171717")
    draw = ImageDraw.Draw(image)
    scale = size / 256

    def box(coords: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(round(value * scale) for value in coords)

    draw.rounded_rectangle(box((38, 34, 218, 222)), radius=round(24 * scale), fill="#f4f4f4")
    draw.rounded_rectangle(box((58, 54, 198, 100)), radius=round(10 * scale), fill="#1f6f5b")

    wave = [
        box((70, 78))[0:2],
        box((118, 78))[0:2],
        box((134, 62))[0:2],
        box((158, 66))[0:2],
        box((176, 78))[0:2],
        box((192, 78))[0:2],
    ]
    draw.line(wave, fill="#d6ffe8", width=round(8 * scale), joint="curve")

    for x in (58, 102, 146):
        for y in (122, 160):
            draw.rounded_rectangle(
                box((x, y, x + 30, y + 24)),
                radius=round(6 * scale),
                fill="#303030",
            )

    draw.rounded_rectangle(box((184, 122, 198, 184)), radius=round(7 * scale), fill="#d95f3d")
    draw.rounded_rectangle(box((160, 192, 198, 206)), radius=round(7 * scale), fill="#d95f3d")
    return image


def main() -> None:
    """Write the PNG and ICO files used by Tkinter and PyInstaller."""

    ASSET_DIR.mkdir(exist_ok=True)
    icon = draw_icon()
    icon.save(PNG_PATH)
    icon.save(ICO_PATH, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Wrote {PNG_PATH}")
    print(f"Wrote {ICO_PATH}")


if __name__ == "__main__":
    main()
