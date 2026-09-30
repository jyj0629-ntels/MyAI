"""Generate flow + network diagrams for the 2-round Travel Compare feature.

Run: python scripts/gen_travel_images.py
Outputs: app/static/images/flow_travel.png, net_travel.png
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.join("app", "static", "images")
os.makedirs(OUT_DIR, exist_ok=True)

BG = (13, 29, 45)
NODE = (19, 35, 60)
TEXT = (237, 246, 255)
MUTED = (155, 177, 199)
PRIMARY = (110, 231, 249)
PURPLE = (154, 123, 255)
GREEN = (110, 231, 183)
AMBER = (251, 191, 36)
BORDER_SOFT = (70, 100, 132)


def _font(size, bold=False):
    for p in ([r"C:\Windows\Fonts\malgunbd.ttf"] if bold else [r"C:\Windows\Fonts\malgun.ttf"]) + [r"C:\Windows\Fonts\malgun.ttf"]:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _wrap(d, text, font, max_w):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------- flow (vertical steps) ----------
def render_flow():
    W, H = 720, 980
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 34), "여행 2라운드 비교", font=_font(38, bold=True), fill=TEXT)
    d.text((40, 84), "개인 성향 반영 · 2회 질의 후 로컬 LLM 수렴", font=_font(20), fill=MUTED)
    d.line((40, 122, W - 40, 122), fill=BORDER_SOFT, width=2)

    steps = [
        ("질문 입력 + 성향 로딩", "여행 질문 입력, DB의 개인 선호(가성비/후기 등)를 자동 반영."),
        ("Round1 프롬프트 생성", "성향 포함 프롬프트를 각 Public AI에 전송."),
        ("Round1 응답 수집", "Gemini/Groq/Mistral의 1차 답변을 병렬 수집."),
        ("Ollama가 Round2 질문 생성", "1차 답변의 차이를 좁히는 개선 질문을 로컬 LLM이 작성(성향 포함)."),
        ("Round2 응답 수집", "개선 질문으로 각 Public AI에 재질의, 2차 답변 수집."),
        ("Ollama 최종 취합·안내", "2차 답변을 교차검증해 최종 여행 안내 생성, DB 저장."),
    ]
    box_x0, box_x1 = 60, W - 60
    y, box_h, gap = 150, 112, 26
    for i, (label, body) in enumerate(steps):
        box = (box_x0, y, box_x1, y + box_h)
        color = PRIMARY if i in (0, len(steps) - 1) else BORDER_SOFT
        d.rounded_rectangle(box, radius=16, fill=NODE, outline=color, width=2)
        cx, cy = box_x0 + 34, y + box_h // 2
        d.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), fill=(9, 17, 31), outline=PURPLE, width=2)
        nf = _font(20, bold=True)
        nw = d.textlength(str(i + 1), font=nf)
        d.text((cx - nw / 2, cy - 12), str(i + 1), font=nf, fill=GREEN)
        tx = box_x0 + 72
        d.text((tx, y + 14), label, font=_font(23, bold=True), fill=TEXT)
        ly = y + 50
        for ln in _wrap(d, body, _font(17), box_x1 - tx - 18)[:2]:
            d.text((tx, ly), ln, font=_font(17), fill=MUTED)
            ly += 24
        if i < len(steps) - 1:
            ax = (box_x0 + box_x1) // 2
            d.line((ax, y + box_h + 3, ax, y + box_h + gap - 3), fill=PURPLE, width=3)
            d.polygon([(ax - 8, y + box_h + gap - 11), (ax + 8, y + box_h + gap - 11), (ax, y + box_h + gap - 1)], fill=PURPLE)
        y += box_h + gap
    img.save(os.path.join(OUT_DIR, "flow_travel.png"))
    print("saved flow_travel.png")


# ---------- network diagram ----------
def _node(d, box, title, subtitle, color):
    d.rounded_rectangle(box, radius=16, fill=NODE, outline=color, width=3)
    x0, y0, x1, y1 = box
    tf, sf = _font(22, bold=True), _font(15)
    d.text(((x0 + x1) / 2 - d.textlength(title, font=tf) / 2, y0 + 16), title, font=tf, fill=TEXT)
    if subtitle:
        d.text(((x0 + x1) / 2 - d.textlength(subtitle, font=sf) / 2, y0 + 46), subtitle, font=sf, fill=MUTED)


def _arrow(d, p0, p1, color, label=None):
    d.line((*p0, *p1), fill=color, width=3)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    L = 12
    d.polygon([p1,
               (p1[0] - L * math.cos(ang - 0.4), p1[1] - L * math.sin(ang - 0.4)),
               (p1[0] - L * math.cos(ang + 0.4), p1[1] - L * math.sin(ang + 0.4))], fill=color)
    if label:
        lf = _font(14)
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        lw = d.textlength(label, font=lf)
        d.rectangle((mx - lw / 2 - 4, my - 12, mx + lw / 2 + 4, my + 8), fill=BG)
        d.text((mx - lw / 2, my - 10), label, font=lf, fill=MUTED)


def render_network():
    W, H = 1000, 620
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 30), "여행 2라운드 · 연동망 구성도", font=_font(34, bold=True), fill=TEXT)
    d.text((40, 76), "브라우저 → FastAPI → (성향+2라운드) Public AI ↔ Ollama 취합", font=_font(18), fill=MUTED)
    d.line((40, 112, W - 40, 112), fill=BORDER_SOFT, width=2)

    _node(d, (40, 250, 240, 340), "사용자 브라우저", "/demo_travel", PRIMARY)
    _node(d, (400, 250, 620, 340), "myai-api", "FastAPI (Docker)", PRIMARY)
    _node(d, (760, 120, 960, 200), "Public AI", "Gemini/Groq/Mistral", PURPLE)
    _node(d, (760, 250, 960, 330), "Ollama", "Round2질문·최종취합", GREEN)
    _node(d, (760, 380, 960, 460), "PostgreSQL", "성향·라운드응답·이력", AMBER)

    _arrow(d, (240, 295), (400, 295), PRIMARY, "HTTP :8000")
    _arrow(d, (620, 285), (760, 165), PURPLE, "R1/R2 질의")
    _arrow(d, (620, 295), (760, 290), GREEN, "취합/재질문 생성")
    _arrow(d, (620, 305), (760, 415), AMBER, "저장")
    d.text((40, 500), "· Round1: 성향 반영 질의 → Ollama가 답변 종합해 Round2 질문 생성 → Round2 재질의.", font=_font(16), fill=MUTED)
    d.text((40, 528), "· Ollama가 2차 답변을 교차검증해 최종 안내 생성. 모든 라운드 응답을 DB에 저장.", font=_font(16), fill=MUTED)
    img.save(os.path.join(OUT_DIR, "net_travel.png"))
    print("saved net_travel.png")


render_flow()
render_network()
print("done")
