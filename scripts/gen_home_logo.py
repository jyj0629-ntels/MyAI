"""Generate a small home/brand logo PNG used as the 'go to /home' link in each page header.

Run: python scripts/gen_home_logo.py  -> app/static/images/home_logo.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join("app", "static", "images", "home_logo.png")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

SIZE = 96  # rendered small in HTML; high-res for crispness
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# rounded gradient-ish square (approx gradient with two triangles)
d.rounded_rectangle((4, 4, SIZE - 4, SIZE - 4), radius=22, fill=(110, 231, 249, 255))
d.polygon([(SIZE - 4, 4), (SIZE - 4, SIZE - 4), (4, SIZE - 4)], fill=(154, 123, 255, 255))
d.rounded_rectangle((4, 4, SIZE - 4, SIZE - 4), radius=22, outline=(9, 17, 31, 120), width=2)


def _font(size):
    for p in (r"C:\Windows\Fonts\malgunbd.ttf", r"C:\Windows\Fonts\arialbd.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


f = _font(40)
text = "AI"
tw = d.textlength(text, font=f)
d.text(((SIZE - tw) / 2, 24), text, font=f, fill=(4, 18, 29, 255))

img.save(OUT)
print("saved", OUT)
