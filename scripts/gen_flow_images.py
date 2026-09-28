"""Generate flowchart PNGs for the /home landing page (MyAI / DPI / Compare).

Run once locally:  python scripts/gen_flow_images.py
Outputs into app/static/images/.
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.join("app", "static", "images")
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 720, 900
BG = (13, 29, 45)          # panel-strong-ish
CARD = (19, 35, 60)        # panel-soft
BORDER = (110, 231, 249)   # primary
BORDER_SOFT = (60, 90, 120)
TEXT = (237, 246, 255)
MUTED = (155, 177, 199)
ARROW = (154, 123, 255)    # primary-2
ACCENT = (110, 231, 183)   # green


def _font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
        r"C:\Windows\Fonts\malgun.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _wrap(draw, text, font, max_w):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _rounded(draw, box, radius, fill, outline, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def render(title, subtitle, steps, filename):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    title_f = _font(38, bold=True)
    sub_f = _font(20)
    step_title_f = _font(24, bold=True)
    step_body_f = _font(18)

    # Title
    d.text((40, 34), title, font=title_f, fill=TEXT)
    d.text((40, 84), subtitle, font=sub_f, fill=MUTED)
    d.line((40, 122, W - 40, 122), fill=BORDER_SOFT, width=2)

    # Steps as vertical flow
    box_x0, box_x1 = 60, W - 60
    y = 150
    box_h = 108
    gap = 34
    for i, (label, body) in enumerate(steps):
        box = (box_x0, y, box_x1, y + box_h)
        _rounded(d, box, 18, CARD, BORDER if i == 0 or i == len(steps) - 1 else BORDER_SOFT, width=2)

        # step number circle
        cx, cy = box_x0 + 34, y + box_h // 2
        d.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), fill=(9, 17, 31), outline=ARROW, width=2)
        num_f = _font(20, bold=True)
        nw = d.textlength(str(i + 1), font=num_f)
        d.text((cx - nw / 2, cy - 12), str(i + 1), font=num_f, fill=ACCENT)

        tx = box_x0 + 72
        d.text((tx, y + 16), label, font=step_title_f, fill=TEXT)
        lines = _wrap(d, body, step_body_f, box_x1 - tx - 20)
        ly = y + 52
        for ln in lines[:2]:
            d.text((tx, ly), ln, font=step_body_f, fill=MUTED)
            ly += 24

        # arrow to next
        if i < len(steps) - 1:
            ax = (box_x0 + box_x1) // 2
            ay0 = y + box_h + 4
            ay1 = y + box_h + gap - 4
            d.line((ax, ay0, ax, ay1), fill=ARROW, width=3)
            d.polygon(
                [(ax - 8, ay1 - 8), (ax + 8, ay1 - 8), (ax, ay1 + 2)],
                fill=ARROW,
            )
        y += box_h + gap

    path = os.path.join(OUT_DIR, filename)
    img.save(path)
    print("saved", path)


render(
    "MyAI",
    "로컬 LLM 기반 개인화 멀티 AI 비서",
    [
        ("질문 입력", "사용자가 GUI에서 질문을 입력합니다."),
        ("로컬 브레인 분석", "Ollama가 선호도/맥락을 반영해 프롬프트를 생성합니다."),
        ("다중 Public AI 호출", "Gemini/Groq/Mistral 등에 병렬로 질의합니다."),
        ("로컬 LLM 요약·합의", "응답을 교차검증하고 핵심으로 요약·합의합니다."),
        ("최종 답변 + 이력 저장", "최종 결과를 GUI에 표시하고 DB에 저장합니다."),
    ],
    "flow_myai.png",
)

render(
    "DPI 기능",
    "로컬 LLM 프롬프트 재작성(Deep Prompt Injection)",
    [
        ("질문 입력", "사용자가 원본 질문을 입력합니다."),
        ("로컬 LLM 재작성", "Ollama가 질문을 더 정교한 프롬프트로 재구성합니다."),
        ("Public AI 전송", "재작성된 프롬프트를 Public AI에 전송합니다."),
        ("응답 정리·표시", "응답을 정리해 GUI에 표시하고 이력에 저장합니다."),
    ],
    "flow_dpi.png",
)

render(
    "Compare 기능",
    "Public AI 웹 응답 수집 + 교차검증 요약",
    [
        ("질문 입력 / AI 선택", "질문과 수집 대상(ChatGPT/Claude/Gemini)을 고릅니다."),
        ("웹 자동화 수집", "각 Public AI의 웹 응답을 수집합니다."),
        ("원본 응답 DB 저장", "수집된 원본 응답을 DB에 저장합니다."),
        ("로컬 LLM 교차검증 요약", "공통점·차이점을 비교하고 종합 결론을 만듭니다."),
        ("결과 표시 + 이력", "요약과 원본을 함께 보여주고 이력을 관리합니다."),
    ],
    "flow_compare.png",
)

print("done")
