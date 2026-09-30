"""Generate NETWORK / integration diagrams (연동망 구성도) for MyAI / DPI / Compare.

Preview only — writes PNGs to scripts/_preview/ (NOT into app/static).
Run: python scripts/gen_network_images.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.join("scripts", "_preview")
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1000, 620
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


def _center_text(d, box, text, font, fill):
    x0, y0, x1, y1 = box
    tw = d.textlength(text, font=font)
    th = font.size
    d.text(((x0 + x1) / 2 - tw / 2, (y0 + y1) / 2 - th / 2), text, font=font, fill=fill)


def _node(d, box, title, subtitle, color):
    d.rounded_rectangle(box, radius=16, fill=NODE, outline=color, width=3)
    x0, y0, x1, y1 = box
    tf = _font(22, bold=True)
    sf = _font(15)
    tw = d.textlength(title, font=tf)
    d.text(((x0 + x1) / 2 - tw / 2, y0 + 16), title, font=tf, fill=TEXT)
    if subtitle:
        sw = d.textlength(subtitle, font=sf)
        d.text(((x0 + x1) / 2 - sw / 2, y0 + 46), subtitle, font=sf, fill=MUTED)


def _arrow(d, p0, p1, color, label=None, dashed=False):
    x0, y0 = p0
    x1, y1 = p1
    if dashed:
        # simple dashed line
        import math
        dist = math.hypot(x1 - x0, y1 - y0)
        steps = int(dist // 12)
        for i in range(steps):
            if i % 2 == 0:
                sx = x0 + (x1 - x0) * (i / steps)
                sy = y0 + (y1 - y0) * (i / steps)
                ex = x0 + (x1 - x0) * ((i + 1) / steps)
                ey = y0 + (y1 - y0) * ((i + 1) / steps)
                d.line((sx, sy, ex, ey), fill=color, width=3)
    else:
        d.line((x0, y0, x1, y1), fill=color, width=3)
    # arrowhead
    import math
    ang = math.atan2(y1 - y0, x1 - x0)
    L = 12
    d.polygon([
        (x1, y1),
        (x1 - L * math.cos(ang - 0.4), y1 - L * math.sin(ang - 0.4)),
        (x1 - L * math.cos(ang + 0.4), y1 - L * math.sin(ang + 0.4)),
    ], fill=color)
    if label:
        lf = _font(14)
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        lw = d.textlength(label, font=lf)
        d.rectangle((mx - lw / 2 - 4, my - 12, mx + lw / 2 + 4, my + 8), fill=BG)
        d.text((mx - lw / 2, my - 10), label, font=lf, fill=MUTED)


def base(title, subtitle):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 30), title, font=_font(34, bold=True), fill=TEXT)
    d.text((40, 76), subtitle, font=_font(18), fill=MUTED)
    d.line((40, 112, W - 40, 112), fill=BORDER_SOFT, width=2)
    return img, d


def render_myai():
    img, d = base("MyAI · 연동망 구성도", "브라우저 → FastAPI(myai-api) → 로컬 LLM / Public AI / DB")
    # Browser
    _node(d, (40, 250, 240, 340), "사용자 브라우저", "/demo", PRIMARY)
    # API
    _node(d, (400, 250, 620, 340), "myai-api", "FastAPI (Docker)", PRIMARY)
    # Ollama
    _node(d, (760, 140, 960, 220), "Ollama", "로컬 LLM (브레인/요약)", GREEN)
    # Public AI
    _node(d, (760, 260, 960, 340), "Public AI", "Gemini/Groq/Mistral", PURPLE)
    # Postgres
    _node(d, (760, 380, 960, 460), "PostgreSQL", "대화/메모리/이력", AMBER)

    _arrow(d, (240, 295), (400, 295), PRIMARY, "HTTP :8000")
    _arrow(d, (620, 285), (760, 190), GREEN, "HTTP :11434")
    _arrow(d, (620, 295), (760, 300), PURPLE, "API 키")
    _arrow(d, (620, 305), (760, 415), AMBER, "SQL :5432")
    d.text((40, 500), "· 로컬 LLM(Ollama)로 프롬프트 생성·요약, 여러 Public AI 병렬 호출 후 교차검증·합의.", font=_font(16), fill=MUTED)
    d.text((40, 528), "· 모든 요청/응답/메모리는 PostgreSQL에 저장(이력 관리).", font=_font(16), fill=MUTED)
    img.save(os.path.join(OUT_DIR, "net_myai.png"))
    print("saved net_myai.png")


def render_dpi():
    img, d = base("DPI · 연동망 구성도", "브라우저 → FastAPI → (금지어 필터+로컬 LLM 재작성) → Public AI")
    _node(d, (40, 250, 240, 340), "사용자 브라우저", "/demo_dpi", PRIMARY)
    _node(d, (400, 250, 620, 340), "myai-api", "FastAPI (Docker)", PRIMARY)
    _node(d, (760, 130, 960, 210), "Ollama", "로컬 LLM 재작성", GREEN)
    _node(d, (760, 250, 960, 330), "PostgreSQL", "금지어/이력", AMBER)
    _node(d, (760, 370, 960, 450), "Public AI", "Gemini/Groq/Mistral", PURPLE)

    _arrow(d, (240, 295), (400, 295), PRIMARY, "HTTP :8000")
    _arrow(d, (620, 285), (760, 180), GREEN, "재작성")
    _arrow(d, (620, 295), (760, 290), AMBER, "금지어 조회")
    _arrow(d, (620, 305), (760, 405), PURPLE, "정제된 프롬프트")
    d.text((40, 500), "· 원본 질문에서 금지어(사내보안 용어)를 걸러내고, 로컬 LLM이 안전한 프롬프트로 재작성.", font=_font(16), fill=MUTED)
    d.text((40, 528), "· 재작성된 프롬프트만 Public AI로 전송하여 민감정보 유출을 차단.", font=_font(16), fill=MUTED)
    img.save(os.path.join(OUT_DIR, "net_dpi.png"))
    print("saved net_dpi.png")


def render_compare():
    img, d = base("Compare · 연동망 구성도", "브라우저 → FastAPI → 웹수집(Public AI) → 로컬 LLM 교차검증")
    _node(d, (40, 250, 240, 340), "사용자 브라우저", "/demo_compare", PRIMARY)
    _node(d, (400, 250, 620, 340), "myai-api", "FastAPI (Docker)", PRIMARY)
    _node(d, (760, 130, 960, 210), "웹 수집기", "ChatGPT/Claude/Gemini", PURPLE)
    _node(d, (760, 250, 960, 330), "Ollama", "로컬 LLM 교차검증 요약", GREEN)
    _node(d, (760, 370, 960, 450), "PostgreSQL", "원본응답/요약 이력", AMBER)

    _arrow(d, (240, 295), (400, 295), PRIMARY, "HTTP :8000")
    _arrow(d, (620, 285), (760, 180), PURPLE, "웹 스크랩")
    _arrow(d, (620, 295), (760, 290), GREEN, "요약 요청")
    _arrow(d, (620, 305), (760, 405), AMBER, "저장")
    d.text((40, 500), "· 여러 Public AI의 웹 응답을 수집·저장한 뒤, 로컬 LLM이 공통점/차이점을 비교·종합.", font=_font(16), fill=MUTED)
    d.text((40, 528), "· (현재 웹 수집기는 목업, Playwright 연결 시 실제 웹 응답으로 대체)", font=_font(16), fill=MUTED)
    img.save(os.path.join(OUT_DIR, "net_compare.png"))
    print("saved net_compare.png")


render_myai()
render_dpi()
render_compare()
print("done ->", OUT_DIR)
