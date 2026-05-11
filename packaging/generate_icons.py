#!/usr/bin/env python3
"""Gera todos os ícones e imagens do projeto JARVIS."""
import os, math
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_ICONS  = os.path.join(ROOT, "assets", "icons")
OUT_IMAGES = os.path.join(ROOT, "assets", "images")
os.makedirs(OUT_ICONS,  exist_ok=True)
os.makedirs(OUT_IMAGES, exist_ok=True)

BG    = (2, 10, 18, 255)
CYAN  = (0, 212, 255)
BLUE  = (0, 102, 255)
GREEN = (0, 255, 136)
WHITE = (200, 240, 255)
DIM   = (42, 74, 94)

def _font(size):
    for path in [
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

def draw_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2

    d.ellipse([1, 1, size-2, size-2], fill=(2, 10, 18, 240), outline=CYAN, width=max(1, size//64))

    lw = max(1, size // 32)
    m  = size // 12
    d.arc([m, m, size-m, size-m], start=-60,  end=60,  fill=CYAN, width=lw)
    d.arc([m, m, size-m, size-m], start=120,  end=240, fill=BLUE, width=lw)

    m2  = size // 5
    lw2 = max(1, size // 48)
    d.arc([m2, m2, size-m2, size-m2], start=30,  end=150, fill=(*CYAN[:3], 160), width=lw2)
    d.arc([m2, m2, size-m2, size-m2], start=210, end=330, fill=(*BLUE[:3], 160), width=lw2)

    font     = _font(max(8, size // 2))
    text     = "J"
    bbox     = d.textbbox((0, 0), text, font=font)
    tw, th   = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx       = cx - tw // 2 - bbox[0]
    ty       = cy - th // 2 - bbox[1] - size // 16

    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx == 0 and dy == 0:
                continue
            d.text((tx+dx, ty+dy), text, font=font, fill=(*CYAN[:3], 55))
    d.text((tx, ty), text, font=font, fill=WHITE)

    dot_r = max(2, size // 20)
    dot_y = cy + size // 4
    d.ellipse([cx-dot_r, dot_y-dot_r, cx+dot_r, dot_y+dot_r], fill=GREEN)

    return img

def make_icons():
    sizes = [16, 24, 32, 48, 64, 128, 256, 512]
    imgs  = {}
    for sz in sizes:
        ic = draw_icon(sz)
        ic.save(os.path.join(OUT_ICONS, f"jarvis_{sz}.png"))
        imgs[sz] = ic

    imgs[256].save(os.path.join(OUT_ICONS, "jarvis.png"))

    ico_sizes = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
    ico_imgs  = [imgs[s[0]].convert("RGBA") for s in ico_sizes]
    ico_imgs[0].save(
        os.path.join(OUT_ICONS, "jarvis.ico"),
        format="ICO", sizes=ico_sizes, append_images=ico_imgs[1:]
    )

def make_banner():
    w, h   = 800, 200
    banner = Image.new("RGBA", (w, h), BG)
    db     = ImageDraw.Draw(banner)

    for y in range(0, h, 4):
        db.line([(0, y), (w, y)], fill=(0, 212, 255, 8), width=1)

    db.rectangle([0, 0, w-1, h-1], outline=(*CYAN[:3], 180), width=2)
    db.rectangle([4, 4, w-5, h-5], outline=(*CYAN[:3], 60),  width=1)

    f_big  = _font(48)
    f_sub  = _font(14)
    f_tiny = _font(11)

    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx == 0 and dy == 0:
                continue
            db.text((70+dx, 60+dy), "J.A.R.V.I.S", font=f_big, fill=(*CYAN[:3], 22))
    db.text((70, 60),  "J.A.R.V.I.S",                           font=f_big,  fill=WHITE)
    db.text((70, 118), "JUST A RATHER VERY INTELLIGENT SYSTEM",  font=f_sub,  fill=(*CYAN[:3], 200))
    db.text((70, 140), "Linux Personal Assistant  ·  v3.0  ·  PyQt6", font=f_tiny, fill=(*DIM[:3], 255))

    mini = draw_icon(120)
    banner.paste(mini, (650, 40), mini)
    banner.save(os.path.join(OUT_IMAGES, "preview.png"))

if __name__ == "__main__":
    make_icons()
    make_banner()
    print("Ícones gerados em assets/icons/ e assets/images/")
