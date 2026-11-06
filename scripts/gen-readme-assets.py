#!/usr/bin/env python3
"""README visuals for dsh-tender-extract, derived from the shipped check pipeline.

Two figures, both read off `rules/tender-extract.yaml`, `src/model.ts`,
`src/view.ts`, `src/index.ts` and the real quickstart run -- not from a generic
checker template:

  hero 1440x576 (Pillow; zh/en x light/dark -> four WebP files)
      Left column: kicker / wordmark / two value lines / subtitle / meta /
      footer.  Right side: one real first run in three bands --
        ① the extract row exactly as
           samples/quickstart/input/TE-001-unsafe.json carries it, with the
           empty `出处` cell marked;
        ② the seven-rule rail with this run's state: six rules ran, TE-004
           is skipped;
        ③ the located finding (`第 1 行「sourceRef」为空`, warn) plus the
           skipped entry with its verbatim reason, and the report's field
           shape as declared in `src/shared/report.ts`.
      The claims in the art are the claims of the run: 1 warn, 1 skipped.

  flow 1100x660 (hand-written SVG, light/dark)
      Grammar: TWO-CHANNEL CONFLUENCE into a RULE x FIELD MATRIX, then two
      exits.  The material channel (JSON/YAML -> column aliases -> canonical
      fields) and the rule channel (rules/tender-extract.yaml -> load guard on
      document / number / clause / excerpt / kind / source) meet in
      `runCheck(input, ruleset, opts)`.  Its seven rows state, per rule, which
      field it reads, how it decides, which evidence kind caps its severity,
      and what this run showed.  The matrix drains into `issues[]` and
      `skipped[]` -- never a verdict.

Every label is measured before it is drawn; a label that would overflow aborts
the run instead of shipping clipped text.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow, and the Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf.
"""
from __future__ import annotations

import os
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")
NAME = "dsh-tender-extract"

FONT_FILES = {
    "cjk": r"C:\Windows\Fonts\msyh.ttc",
    "cjk_bold": r"C:\Windows\Fonts\msyhbd.ttc",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "mono_bold": r"C:\Windows\Fonts\consolab.ttf",
}
for _kind, _path in FONT_FILES.items():
    if not os.path.exists(_path):
        raise SystemExit(f"FATAL: font missing: {_path}")
os.makedirs(OUT, exist_ok=True)

RADIUS = 20
SHADOW = 24

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", edge="#e6e2ef",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", pill="#ece7f9", band="#f5f2fb",
        grid="#e7e4f0", mark="#b45309", mark_bg="#fdf3e9",
        ok="#15803d", ok_bg="#eaf6ee",
        shadow=(38, 30, 72), glow=34,
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", pill="#242d42", band="#202839",
        grid="#262f42", mark="#d9a441", mark_bg="#2a2216",
        ok="#3fb950", ok_bg="#16281c",
        shadow=(0, 0, 0), glow=48,
    ),
}


def font(size: float, kind: str = "cjk") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], int(round(size)))


def hx(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w: int, h: int, top: str, bottom: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(base)
    a, b = hx(top), hx(bottom)
    for y in range(h):
        t = 0.12 * (y / h) + 0.88 * (y / h) ** 1.3
        draw.line([(0, y), (w, y)],
                  fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base


def glow(img: Image.Image, cx: int, cy: int, r: int, color: str,
         alpha: int) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rgb = hx(color)
    for i in range(10, 0, -1):
        rr = r * i / 10
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=rgb + (int(alpha * (1 - i / 11)),))
    return Image.alpha_composite(img.convert("RGBA"),
                                 layer.filter(ImageFilter.GaussianBlur(26))
                                 ).convert("RGB")


def card(img: Image.Image, box: tuple[int, int, int, int], s: dict,
         radius: int = RADIUS, shadow: int = SHADOW,
         fill: str | None = None, edge: str | None = None) -> Image.Image:
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(shadow, 0, -2):
        sd.rounded_rectangle([x0 - i // 6, y0 + i // 2, x1 + i // 6, y1 + i],
                             radius=radius + i // 6,
                             fill=s["shadow"] + (int(10 * (1 - i / shadow)),))
    base = Image.alpha_composite(img.convert("RGBA"),
                                 sh.filter(ImageFilter.GaussianBlur(11)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill or s["card"]),
                        outline=hx(edge or s["edge"]), width=2)
    return base.convert("RGB")


_MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def measure(text: str, size: float, kind: str) -> float:
    return _MEASURE.textlength(text, font=font(size, kind))


def require_w(text: str, size: float, kind: str, max_w: float, what: str) -> None:
    got = measure(text, size, kind)
    if got > max_w + 0.4:
        raise SystemExit(f"FATAL: {what} overflows: {text!r} needs "
                         f"{got:.1f}px > {max_w:.0f}px")


def fit(text: str, kind: str, max_w: float, start: int, minimum: int) -> int:
    size = start
    while size > minimum:
        if measure(text, size, kind) <= max_w:
            return size
        size -= 1
    raise SystemExit(f"FATAL: text does not fit {max_w}px at >= {minimum}px: "
                     f"{text!r}")


def fit_lines(lines: list[str], kind: str, max_w: float, start: int,
              minimum: int) -> int:
    return min(fit(t, kind, max_w, start, minimum) for t in lines)


def pill(img: Image.Image, xy: tuple[int, int], text: str, s: dict,
         size: int = 16, fg: str | None = None, bg: str | None = None,
         kind: str = "cjk_bold") -> int:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(text, font=f)
    x, y = xy
    h = size + 20
    d.rounded_rectangle([x, y, x + w + 30, y + h], radius=h // 2,
                        fill=hx(bg or s["pill"]))
    d.text((x + 15, y + h / 2), text, font=f, fill=hx(fg or s["accent"]),
           anchor="lm")
    return int(x + w + 30)


def chip_right(img: Image.Image, right: int, y: int, text: str, fg: str,
               bg: str, size: float = 11, height: int = 20,
               kind: str = "cjk_bold") -> int:
    d = ImageDraw.Draw(img)
    w = d.textlength(text, font=font(size, kind)) + 18
    x = right - w
    d.rounded_rectangle([x, y, right, y + height], radius=height / 2,
                        fill=hx(bg))
    d.text((x + 9, y + height / 2), text, font=font(size, kind),
           fill=hx(fg), anchor="lm")
    return int(x)


def badge(img: Image.Image, cx: int, cy: int, text: str, s: dict,
          size: float = 10) -> None:
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=hx(s["pill"]))
    d.text((cx, cy), text, font=font(size, "cjk_bold"), fill=hx(s["accent"]),
           anchor="mm")


def dash_round_rect(d: ImageDraw.ImageDraw, box: tuple[int, int, int, int],
                    color: str, radius: int = 8, width: int = 2) -> None:
    x0, y0, x1, y1 = box
    for xa, xb in ((x0 + radius, x1 - radius),):
        for yy in (y0, y1):
            for x in range(int(xa), int(xb), 10):
                d.line([(x, yy), (min(x + 6, xb), yy)], fill=hx(color),
                       width=width)
    for y in range(int(y0 + radius), int(y1 - radius), 10):
        for xx in (x0, x1):
            d.line([(xx, y), (xx, min(y + 6, y1 - radius))], fill=hx(color),
                   width=width)
    d.arc([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270,
          fill=hx(color), width=width)
    d.arc([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360,
          fill=hx(color), width=width)
    d.arc([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180,
          fill=hx(color), width=width)
    d.arc([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90,
          fill=hx(color), width=width)


# --------------------------------------------------------------------------- hero
# Every string below is either the quickstart sample, the report contract, or
# the rule pack.  The finding is copied from a real run of
# samples/quickstart/input/TE-001-unsafe.json.
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 摘录核对器",
        value=["七条规则，逐行核对摘录表", "每条差异落到行号与字段"],
        sub="只列材料内部的字面差异，不作出定性结论。",
        meta="tender_extract · TE-001…TE-007 · issues + skipped",
        foot="Apache-2.0 · 只读 · 不联网 · 不调用模型",
        doc_title="摘录表 · 只读",
        doc_chip="JSON / YAML",
        doc_meta="某某工程施工招标 · ZB-2026-018 · 招标文件 2026-02-10 版",
        headers=["序号", "出处", "原文"],
        row=["1", "", "投标人应具有建筑工程施工总承包二级及以上资质，并附资质证书复印件。"],
        empty="（空）",
        extra="类别 资格条件 · 要求 需具备建筑工程施工总承包二级及以上资质并提供证书复印件 · 是否实质性 是",
        rules_title="七条规则 · 本次运行",
        rules_chip="6 执行 · 1 未执行",
        states={"diff": "差异", "clean": "无差异", "skip": "未执行"},
        finding_title="定位差异 · TE-001",
        finding_chip="warn",
        locator="第 1 行 · field sourceRef",
        found="第 1 行「sourceRef」为空",
        expected="「sourceRef」应填写",
        fix="补填出处（章节或页码）；本条只核对是否填写，不判断摘录是否完整",
        fix_lines=["补填出处（章节或页码）；本条只核对是否填写，",
                   "不判断摘录是否完整"],
        basis="依据 招标投标法 第十九条 · 原则性条款推论",
        skip_title="未执行 · TE-004",
        skip_chip="skipped",
        skip_reason="规则库未配置 values：「category」的取值口径由本机构规定，本引擎不硬编码",
        skip_reason_lines=["规则库未配置 values：",
                           "「category」的取值口径由本机构规定，本引擎不硬编码"],
        skip_note="空结果 ≠ 没问题",
        skip_shape="{ rule: TE-004, reason: values unset }",
        report_label="报告形状",
        report_shape="{ id · ruleId · severity · locator{row, field} · found · expected · basis · fix }",
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · extract checker",
        value=["Seven rules over one extract table,", "each difference lands on row + field"],
        sub="Literal differences only — no compliance verdict.",
        meta="tender_extract · TE-001…TE-007 · issues + skipped",
        foot="Apache-2.0 · read-only · no network · no model call",
        doc_title="Clause extract · read-only",
        doc_chip="JSON / YAML",
        doc_meta="some works tender · ZB-2026-018 · tender file 2026-02-10",
        headers=["seq", "sourceRef", "rawText"],
        row=["1", "", "Bidder holds a grade-2 construction general-contracting licence, copy attached."],
        empty="(empty)",
        extra="category qualification · requirement grade-2 licence + copy · mandatory yes",
        rules_title="Seven rules · this run",
        rules_chip="6 ran · 1 skipped",
        states={"diff": "diff", "clean": "clean", "skip": "skipped"},
        finding_title="Finding · TE-001",
        finding_chip="warn",
        locator="row 1 · field sourceRef",
        found="row 1: sourceRef is empty",
        expected="sourceRef should be filled in",
        fix="add the clause or page; this check reads presence only, not completeness",
        fix_lines=["add the clause or page; this check reads presence only,",
                   "not completeness"],
        basis="basis Tender Law art. 19 · derived from principle",
        skip_title="Not run · TE-004",
        skip_chip="skipped",
        skip_reason="values unset in the rule pack: the category vocabulary is institutional",
        skip_reason_lines=["values unset in the rule pack:",
                           "the category vocabulary is institutional"],
        skip_note="empty is not 'all clear'",
        skip_shape="{ rule: TE-004, reason: values unset }",
        report_label="report shape",
        report_shape="{ id · ruleId · severity · locator{row, field} · found · expected · basis · fix }",
    ),
}


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    h = HERO[lang]
    W, H = 1440, 576
    img = gradient(W, H, s["bg_from"], s["bg_to"])
    img = glow(img, 1140, 90, 380, s["accent"], s["glow"])
    img = glow(img, 140, 560, 300, s["accent"], max(8, s["glow"] // 3))
    d = ImageDraw.Draw(img)
    m = 56
    col_w = 540

    # ---- left column --------------------------------------------------------
    pill(img, (m, 64), h["kicker"], s, size=16)
    d = ImageDraw.Draw(img)

    title_size = fit(NAME, "mono_bold", col_w, 58, 50)
    d.text((m - 1, 132), NAME, font=font(title_size, "mono_bold"),
           fill=hx(s["text"]))
    require_w(NAME, title_size, "mono_bold", col_w, "hero title")

    value_size = fit_lines(h["value"], "cjk_bold", col_w,
                           38 if lang == "zh" else 33, 28)
    for i, line in enumerate(h["value"]):
        d.text((m, 234 + i * 54), line, font=font(value_size, "cjk_bold"),
               fill=hx(s["text"]))
        require_w(line, value_size, "cjk_bold", col_w, "hero value line")

    require_w(h["sub"], 22, "cjk", col_w, "hero subtitle")
    d.text((m, 352), h["sub"], font=font(22, "cjk"), fill=hx(s["sub"]))

    require_w(h["meta"], 19, "cjk", col_w, "hero meta")
    d.text((m + 1, 406), h["meta"], font=font(19, "cjk"), fill=hx(s["faint"]))

    d.line([m + 1, 458, m + col_w - 4, 458], fill=hx(s["grid"]), width=2)
    require_w(h["foot"], 16, "cjk", col_w, "hero footer")
    d.text((m + 1, 476), h["foot"], font=font(16, "cjk"), fill=hx(s["faint"]))

    # ---- (1) the extract row: a real quickstart material --------------------
    img = card(img, (620, 52, 1384, 214), s, radius=20, shadow=26)
    d = ImageDraw.Draw(img)
    badge(img, 642, 76, "①", s)
    d = ImageDraw.Draw(img)
    d.text((660, 76), h["doc_title"], font=font(15, "cjk_bold"),
           fill=hx(s["text"]), anchor="lm")
    require_w(h["doc_title"], 15, "cjk_bold", 210, "doc title")
    chip_right(img, 1364, 62, h["doc_chip"], s["accent"], s["pill"], size=11)
    d = ImageDraw.Draw(img)
    require_w(h["doc_meta"], 12, "cjk", 690, "doc meta")
    d.text((660, 96), h["doc_meta"], font=font(12, "cjk"), fill=hx(s["sub"]))

    x0, x1 = 640, 1364
    widths = [64, 140, 500]
    xs: list[int] = []
    acc = x0
    for width in widths:
        xs.append(acc)
        acc += width
    d.rounded_rectangle([x0 - 6, 126, x1 + 6, 152], radius=8, fill=hx(s["band"]))
    for i, head in enumerate(h["headers"]):
        require_w(head, 11.5, "cjk_bold", widths[i] - 12, "table header")
        d.text((xs[i] + 8, 139), head, font=font(11.5, "cjk_bold"),
               fill=hx(s["sub"]), anchor="lm")

    # the empty `出处` cell: the one difference in this run
    cell = (xs[1] - 2, 156, xs[1] + widths[1] - 6, 186)
    d.rounded_rectangle(cell, radius=8, fill=hx(s["mark_bg"]))
    dash_round_rect(d, cell, s["mark"], radius=8, width=2)

    require_w(h["row"][0], 12, "mono", widths[0] - 12, "seq cell")
    d.text((xs[0] + 8, 171), h["row"][0], font=font(12, "mono"),
           fill=hx(s["text"]), anchor="lm")
    require_w(h["empty"], 11.5, "cjk", widths[1] - 14, "empty cell")
    d.text((xs[1] + 8, 171), h["empty"], font=font(11.5, "cjk"),
           fill=hx(s["mark"]), anchor="lm")
    require_w(h["row"][2], 12, "cjk", widths[2] - 14, "raw text cell")
    d.text((xs[2] + 8, 171), h["row"][2], font=font(12, "cjk"),
           fill=hx(s["text"]), anchor="lm")
    d.line([x0, 190, x1, 190], fill=hx(s["grid"]), width=1)

    require_w(h["extra"], 11.5, "cjk", 700, "column fields line")
    d.text((660, 196), h["extra"], font=font(11.5, "cjk"), fill=hx(s["faint"]))

    # ---- (2) the seven-rule rail -------------------------------------------
    img = card(img, (620, 230, 1384, 336), s, radius=18, shadow=22)
    d = ImageDraw.Draw(img)
    badge(img, 642, 252, "②", s)
    d = ImageDraw.Draw(img)
    d.text((660, 252), h["rules_title"], font=font(14, "cjk_bold"),
           fill=hx(s["text"]), anchor="lm")
    require_w(h["rules_title"], 14, "cjk_bold", 230, "rules title")
    chip_right(img, 1364, 238, h["rules_chip"], s["accent"], s["pill"], size=11)
    d = ImageDraw.Draw(img)

    rules = ["TE-001", "TE-002", "TE-003", "TE-004", "TE-005", "TE-006", "TE-007"]
    states = ["diff", "clean", "clean", "skip", "clean", "clean", "clean"]
    tw, gap, ty, th = 96, 6, 276, 50
    for i, (rid, state) in enumerate(zip(rules, states)):
        x = 640 + i * (tw + gap)
        fill = s["mark_bg"] if state == "diff" else s["band"]
        d.rounded_rectangle([x, ty, x + tw, ty + th], radius=10, fill=hx(fill))
        if state == "diff":
            d.rounded_rectangle([x, ty, x + tw, ty + th], radius=10,
                                outline=hx(s["mark"]), width=2)
        if state == "skip":
            dash_round_rect(d, (x, ty, x + tw, ty + th), s["faint"],
                            radius=10, width=1)
        d.text((x + tw / 2, ty + 18), rid, font=font(12, "mono_bold"),
               fill=hx(s["text"]), anchor="mm")
        colour = {"diff": s["mark"], "clean": s["ok"], "skip": s["faint"]}[state]
        d.text((x + tw / 2, ty + 37), h["states"][state],
               font=font(11, "cjk_bold"), fill=hx(colour), anchor="mm")

    # ---- (3) the located finding + the skipped entry ------------------------
    img = card(img, (620, 352, 1010, 504), s, radius=18, shadow=20)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([628, 364, 632, 492], radius=2, fill=hx(s["mark"]))
    badge(img, 646, 370, "③", s)
    d = ImageDraw.Draw(img)
    d.text((664, 370), h["finding_title"], font=font(13.5, "cjk_bold"),
           fill=hx(s["text"]), anchor="lm")
    require_w(h["finding_title"], 13.5, "cjk_bold", 165, "finding title")
    chip_right(img, 992, 358, h["finding_chip"], s["mark"], s["mark_bg"],
               size=11)
    d = ImageDraw.Draw(img)

    require_w(h["locator"], 11, "cjk", 300, "locator")
    d.text((664, 388), h["locator"], font=font(11, "cjk"),
           fill=hx(s["faint"]))
    require_w(h["found"], 13, "cjk", 336, "finding found")
    d.text((664, 409), h["found"], font=font(13, "cjk"), fill=hx(s["text"]))
    require_w(h["expected"], 11.5, "cjk", 326, "finding expected")
    d.text((664, 431), h["expected"], font=font(11.5, "cjk"), fill=hx(s["sub"]))

    if "".join(h["fix_lines"]).replace(" ", "") != h["fix"].replace(" ", ""):
        raise SystemExit("FATAL: hero fix lines do not reconstruct the fix")
    for i, line in enumerate(h["fix_lines"]):
        require_w(line, 11.5, "cjk", 336, "finding fix")
        d.text((664, 450 + i * 16), line, font=font(11.5, "cjk"),
               fill=hx(s["sub"]))
    basis_y = 450 + len(h["fix_lines"]) * 16 + 5
    require_w(h["basis"], 11, "cjk", 336, "finding basis")
    d.text((664, basis_y), h["basis"], font=font(11, "cjk"), fill=hx(s["faint"]))

    img = card(img, (1026, 352, 1384, 504), s, radius=18, shadow=20)
    d = ImageDraw.Draw(img)
    badge(img, 1046, 370, "③", s)
    d = ImageDraw.Draw(img)
    d.text((1064, 370), h["skip_title"], font=font(13.5, "cjk_bold"),
           fill=hx(s["text"]), anchor="lm")
    require_w(h["skip_title"], 13.5, "cjk_bold", 180, "skipped title")
    chip_right(img, 1368, 358, h["skip_chip"], s["faint"], s["band"], size=11)
    d = ImageDraw.Draw(img)
    if "".join(h["skip_reason_lines"]).replace(" ", "") != h["skip_reason"].replace(" ", ""):
        raise SystemExit("FATAL: hero skip reason lines do not reconstruct the reason")
    for i, line in enumerate(h["skip_reason_lines"]):
        require_w(line, 11.5, "cjk", 312, "skip reason")
        d.text((1046, 396 + i * 17), line, font=font(11.5, "cjk"),
               fill=hx(s["sub"]))
    note_y = 396 + len(h["skip_reason_lines"]) * 17 + 18
    require_w(h["skip_note"], 11, "cjk_bold", 312, "skip note")
    d.text((1046, note_y), h["skip_note"], font=font(11, "cjk_bold"),
           fill=hx(s["mark"]))
    require_w(h["skip_shape"], 11, "mono", 322, "skip shape")
    d.text((1046, note_y + 26), h["skip_shape"], font=font(11, "mono"),
           fill=hx(s["faint"]))

    # ---- the report's field shape ------------------------------------------
    img = card(img, (620, 518, 1384, 552), s, radius=18, shadow=14)
    d = ImageDraw.Draw(img)
    d.text((640, 535), h["report_label"], font=font(12, "cjk_bold"),
           fill=hx(s["text"]), anchor="lm")
    require_w(h["report_label"], 12, "cjk_bold", 90, "report label")
    label_w = measure(h["report_label"], 12, "cjk_bold")
    shape_x = 640 + label_w + 18
    require_w(h["report_shape"], 11, "mono", 1364 - shape_x, "report shape")
    d.text((shape_x, 535), h["report_shape"], font=font(11, "mono"),
           fill=hx(s["sub"]), anchor="lm")

    out = f"{NAME}-hero-{lang}-{skin}.webp"
    img.save(os.path.join(OUT, out), "WEBP", quality=92, method=6)
    print(f"wrote {out} ({W}x{H})")


# --------------------------------------------------------------------------- flow
FLOW = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        panel="#ffffff", edge="#e6e2ef", band="#f5f2fb", pill="#ece7f9",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", mark="#b45309", mark_bg="#fdf3e9",
        ok="#15803d", ok_bg="#eaf6ee",
        grid="#e7e4f0", dot="#cfc8e2",
        shadow="#2b2440", shadow_op="0.13",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        panel="#1b2231", edge="#2e374b", band="#202839", pill="#242d42",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", mark="#d9a441", mark_bg="#2a2216",
        ok="#3fb950", ok_bg="#16281c",
        grid="#2b3348", dot="#2a3346",
        shadow="#000000", shadow_op="0.50",
    ),
}

FONT_CSS_SANS = ("'Microsoft YaHei','Segoe UI','PingFang SC',"
                 "'Noto Sans CJK SC',sans-serif")
FONT_CSS_MONO = "Consolas,'Microsoft YaHei',ui-monospace,monospace"

# The seven rows of the matrix: id, field the check reads, check kind, the
# evidence kind that caps the severity, and this run's state.  All of it comes
# from rules/tender-extract.yaml plus one run on
# samples/quickstart/input/TE-001-unsafe.json (1 warn: TE-001; TE-004 skipped).
MATRIX_ROWS = [
    ("TE-001", "sourceRef", "presence", "derived-from-principle", "warn", "diff"),
    ("TE-002", "rawText", "presence", "derived-from-principle", "warn", "clean"),
    ("TE-003", "rawText ↔ requirement", "sharedTerms", "direct", "error", "clean"),
    ("TE-004", "category", "enum", "institutional-configuration", "info", "skip"),
    ("TE-005", "seq", "unique", "derived-from-principle", "warn", "clean"),
    ("TE-006", "header: project + source", "headerPresence", "derived-from-principle", "warn", "clean"),
    ("TE-007", "rawText · terms", "containsAny", "derived-from-principle", "warn", "clean"),
]
STATE_WORD = {"diff": "1 diff", "clean": "clean", "skip": "skipped"}


class Svg:
    """Small SVG writer that measures every label before it is emitted."""

    def __init__(self, s: dict) -> None:
        self.s = s
        self.parts: list[str] = []
        self.overflows: list[str] = []

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def width(self, content: str, size: float, mono: bool = False,
              bold: bool = False, spacing: float | None = None) -> float:
        if mono and content.isascii():
            kind = "mono_bold" if bold else "mono"
        elif any(ord(c) > 127 for c in content):
            kind = "cjk_bold" if bold else "cjk"
        elif mono:
            kind = "mono_bold" if bold else "mono"
        else:
            kind = "cjk_bold" if bold else "cjk"
        got = _MEASURE.textlength(content,
                                 font=ImageFont.truetype(FONT_FILES[kind], size))
        if spacing:
            got += spacing * max(len(content) - 1, 0)
        return got

    def text(self, x: float, y: float, content: str, size: float, fill: str, *,
             anchor: str = "start", mono: bool = False, bold: bool = False,
             max_w: float | None = None, opacity: float | None = None,
             spacing: float | None = None) -> None:
        got = self.width(content, size, mono, bold, spacing)
        if max_w is not None and got > max_w:
            self.overflows.append(f"{content!r} needs {got:.1f} > {max_w:.1f}")
        family = FONT_CSS_MONO if mono else FONT_CSS_SANS
        attrs = ""
        if anchor != "start":
            attrs += f' text-anchor="{anchor}"'
        if bold:
            attrs += ' font-weight="700"'
        if opacity is not None:
            attrs += f' opacity="{opacity}"'
        if spacing is not None:
            attrs += f' letter-spacing="{spacing}"'
        self.add(f'<text x="{x}" y="{y}" fill="{fill}" '
                 f'font-family="{family}" font-size="{size}"{attrs}>'
                 f'{escape(content)}</text>')

    def rect(self, x: float, y: float, w: float, h: float, rx: float,
             fill: str, stroke: str | None = None, sw: float = 1.4,
             opacity: float | None = None, shadow: bool = False) -> None:
        attrs = ""
        if stroke:
            attrs += f' stroke="{stroke}" stroke-width="{sw}"'
        if opacity is not None:
            attrs += f' opacity="{opacity}"'
        if shadow:
            attrs += ' filter="url(#soft)"'
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                 f'fill="{fill}"{attrs}/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, stroke: str,
             width: float = 1, opacity: float | None = None,
             dash: str | None = None) -> None:
        attrs = f' stroke-width="{width}"'
        if opacity is not None:
            attrs += f' opacity="{opacity}"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                 f'stroke="{stroke}"{attrs}/>')

    def path(self, d: str, stroke: str, width: float = 2,
             marker: str | None = None, dash: str | None = None) -> None:
        attrs = f' fill="none" stroke="{stroke}" stroke-width="{width}"'
        if marker:
            attrs += f' marker-end="url(#{marker})"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        self.add(f'<path d="{d}"{attrs}/>')

    def pill_right(self, right: float, cy: float, text: str, fg: str, bg: str,
                   size: float = 11, height: float = 20) -> float:
        w = self.width(text, size, mono=True, bold=True) + 18
        x = right - w
        self.rect(x, cy - height / 2, w, height, height / 2, bg)
        self.add(f'<text x="{x + w / 2}" y="{cy + size * 0.35}" fill="{fg}" '
                 f'font-family="{FONT_CSS_MONO}" font-size="{size}" '
                 f'font-weight="700" text-anchor="middle">{escape(text)}</text>')
        return x

    def pill_left(self, x: float, cy: float, text: str, fg: str, bg: str,
                  size: float = 11, height: float = 20) -> float:
        w = self.width(text, size, mono=True, bold=True) + 18
        self.rect(x, cy - height / 2, w, height, height / 2, bg)
        self.add(f'<text x="{x + w / 2}" y="{cy + size * 0.35}" fill="{fg}" '
                 f'font-family="{FONT_CSS_MONO}" font-size="{size}" '
                 f'font-weight="700" text-anchor="middle">{escape(text)}</text>')
        return x + w


def flow_svg(skin: str) -> str:
    s = FLOW[skin]
    svg = Svg(s)

    svg.add('<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="660" '
            'viewBox="0 0 1100 660" role="img" aria-labelledby="figTitle figDesc">')
    svg.add('<title id="figTitle">dsh-tender-extract structure: two intake '
            'channels converge in a rule × field matrix, then issues and '
            'skipped</title>')
    svg.add('<desc id="figDesc">The material channel (JSON or YAML extract '
            'table, column aliases resolved to canonical fields) and the rule '
            'channel (rules/tender-extract.yaml, load guard on document, '
            'number, clause, excerpt, kind and source) meet in runCheck. Its '
            'seven-row matrix states, per rule, the field read, the check kind, '
            'the evidence kind that caps severity, and this run: TE-001 is one '
            'warn difference, TE-002, TE-003, TE-005, TE-006 and TE-007 are '
            'clean, TE-004 is skipped because values[] is empty. Two exits: '
            'issues[] carries row, field, found, expected and fix; skipped[] '
            'carries the rule and its reason. There is no verdict.</desc>')

    # ---- background ---------------------------------------------------------
    svg.add('<defs>')
    svg.add('<linearGradient id="bg" x1="0" y1="0" x2="0.25" y2="1">'
            f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
            f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    svg.add(f'<filter id="soft" x="-30%" y="-30%" width="170%" height="185%">'
            f'<feDropShadow dx="0" dy="7" stdDeviation="10" '
            f'flood-color="{s["shadow"]}" flood-opacity="{s["shadow_op"]}"/>'
            f'</filter>')
    svg.add(f'<pattern id="dots" width="26" height="26" '
            f'patternUnits="userSpaceOnUse"><circle cx="1.2" cy="1.2" '
            f'r="1.2" fill="{s["dot"]}"/></pattern>')
    svg.add(f'<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0 0 L10 5 L0 10 z" fill="{s["accent"]}"/></marker>')
    svg.add(f'<marker id="arrfaint" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0 0 L10 5 L0 10 z" fill="{s["faint"]}"/></marker>')
    svg.add('</defs>')
    svg.add(f'<rect width="1100" height="660" rx="22" fill="url(#bg)"/>')
    svg.add(f'<rect width="1100" height="660" rx="22" fill="url(#dots)" '
            f'opacity="0.5"/>')

    # ---- header -------------------------------------------------------------
    svg.text(44, 58, NAME, 29, s["text"], mono=True, bold=True, max_w=520)
    svg.text(44, 88,
             "One extract table × seven rules → every difference lands on a "
             "row and a field; an empty issue list is never 'all clear'.",
             14.5, s["sub"], max_w=960)
    svg.pill_right(1056, 47, "rules/tender-extract.yaml · v2026.1",
                   s["accent"], s["pill"])
    svg.text(44, 112, "IN · JSON / YAML · header + rows[] · read-only", 11,
             s["faint"], mono=True, max_w=440)
    svg.text(1056, 112, "OUT · issues[] + skipped[] · no verdict", 11,
             s["faint"], anchor="end", mono=True, max_w=340)
    svg.line(44, 126, 1056, 126, s["grid"], 1)

    # ---- channel 1: material ------------------------------------------------
    svg.rect(44, 138, 288, 110, 18, s["panel"], s["edge"], 1.4, shadow=True)
    svg.text(58, 158, "MATERIAL · READ", 11, s["faint"], bold=True,
             spacing=1.2, max_w=252)
    svg.text(58, 184, "extract table · header + rows[]", 15, s["text"],
             bold=True, max_w=252)
    svg.text(58, 204, "column aliases → canonical fields", 11.5, s["sub"],
             max_w=252)
    svg.text(58, 222, "出处 → sourceRef · 原文 → rawText", 11, s["sub"],
             mono=True, max_w=252)
    svg.text(58, 240, "parseTable · canonicaliseRow", 11, s["faint"],
             mono=True, max_w=252)

    # ---- channel 2: rule pack ----------------------------------------------
    svg.rect(768, 138, 288, 110, 18, s["panel"], s["edge"], 1.4, shadow=True)
    svg.text(782, 158, "RULE PACK · LOAD", 11, s["faint"], bold=True,
             spacing=1.2, max_w=252)
    svg.text(782, 184, "rules/tender-extract.yaml", 13, s["text"], mono=True,
             bold=True, max_w=252)
    svg.text(782, 204, "7 rules · version 2026.1", 11.5, s["sub"], max_w=252)
    svg.text(782, 222, "guard: document · number · clause", 11, s["sub"],
             mono=True, max_w=252)
    svg.text(782, 240, "excerpt · kind · source · verbatim", 11, s["faint"],
             mono=True, max_w=252)

    # ---- confluence ---------------------------------------------------------
    svg.path("M188 248 C188 258 230 281 378 281", s["accent"], 2, marker="arr")
    svg.path("M912 248 C912 258 870 281 722 281", s["accent"], 2, marker="arr")
    svg.rect(386, 262, 328, 38, 19, s["panel"], s["accent"], 1.6, shadow=True)
    svg.text(550, 281, "runCheck(input, ruleset, options)", 12, s["text"],
             anchor="middle", mono=True, bold=True, max_w=300)
    svg.text(550, 296, "pure · no I/O · no clock · no model", 11, s["sub"],
             anchor="middle", max_w=300)
    svg.path("M550 300 V314", s["accent"], 2, marker="arr")

    # ---- the rule x field matrix -------------------------------------------
    svg.rect(44, 320, 1012, 220, 18, s["panel"], s["edge"], 1.4, shadow=True)
    svg.text(66, 342, "RULE × FIELD MATRIX · run on samples/quickstart", 14,
             s["text"], bold=True, max_w=560)
    svg.pill_right(1030, 338, "6 ran · 1 skipped", s["accent"], s["pill"])

    svg.rect(56, 350, 988, 22, 8, s["band"], opacity=0.6)
    for x, label, max_w in ((66, "RULE", 80), (158, "FIELD READ", 220),
                            (392, "CHECK KIND", 150),
                            (560, "BASIS KIND → CAP", 300),
                            (880, "THIS RUN", 140)):
        svg.text(x, 365, label, 11, s["faint"], bold=True, spacing=0.8,
                 max_w=max_w)

    cap_style = {"error": (s["text"], s["band"]),
                 "warn": (s["mark"], s["mark_bg"]),
                 "info": (s["accent"], s["pill"])}
    state_style = {"diff": (s["mark"], s["mark_bg"]),
                   "clean": (s["ok"], s["ok_bg"]),
                   "skip": (s["faint"], s["band"])}

    for i, (rid, field, kind, basis, cap, state) in enumerate(MATRIX_ROWS):
        top = 372 + i * 24
        cy = top + 13.5
        if i == 0:
            svg.rect(56, top + 1, 988, 22, 5, s["mark_bg"], opacity=0.55)
        if i == 3:
            svg.rect(56, top + 1, 988, 22, 5, s["band"], opacity=0.75)
        if i > 0:
            svg.line(56, top, 1044, top, s["grid"], 1, opacity=0.8)
        svg.text(66, cy + 4.6, rid, 13, s["text"], mono=True, bold=True,
                 max_w=80)
        svg.text(158, cy + 4.6, field, 13, s["text"], max_w=220)
        svg.text(392, cy + 4.2, kind, 11.5, s["sub"], mono=True, max_w=150)
        svg.text(560, cy + 4.2, basis, 11.5, s["sub"], mono=True, max_w=190)
        fg, bg = cap_style[cap]
        svg.pill_left(762, cy, "≤ " + cap, fg, bg)
        fg, bg = state_style[state]
        svg.pill_right(1030, cy, STATE_WORD[state], fg, bg)

    # ---- exits --------------------------------------------------------------
    svg.path("M282 540 V552", s["accent"], 2, marker="arr")
    svg.path("M818 540 V552", s["accent"], 2, marker="arr")

    svg.rect(44, 556, 476, 84, 18, s["panel"], s["edge"], 1.4, shadow=True)
    svg.text(60, 580, "issues[] · 1", 13, s["text"], bold=True, max_w=240)
    svg.pill_right(500, 570, "warn", s["mark"], s["mark_bg"])
    svg.text(60, 602, "row 1 · field sourceRef · TE-001", 11, s["sub"],
             mono=True, max_w=440)
    svg.text(60, 624, "differences only — no verdict, no score", 11,
             s["faint"], max_w=440)

    svg.rect(580, 556, 476, 84, 18, s["panel"], s["edge"], 1.4, shadow=True)
    svg.text(596, 580, "skipped[] · 1", 13, s["text"], bold=True, max_w=240)
    svg.pill_right(1036, 570, "not run", s["faint"], s["band"])
    svg.text(596, 602, "TE-004 · values[] unset → reason recorded", 11,
             s["sub"], mono=True, max_w=440)
    svg.text(596, 624, "an empty list is never a silent pass", 11, s["faint"],
             max_w=440)

    svg.add('</svg>')
    if svg.overflows:
        raise SystemExit("FATAL: flow labels overflow:\n  "
                         + "\n  ".join(svg.overflows))
    return "\n".join(svg.parts) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for lang in ("zh", "en"):
        for skin in ("light", "dark"):
            hero(lang, skin)
    for skin in ("light", "dark"):
        name = f"{NAME}-flow-v5-{skin}.svg"
        with open(os.path.join(OUT, name), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(flow_svg(skin))
        print(f"wrote {name} (1100x660)")


if __name__ == "__main__":
    main()
