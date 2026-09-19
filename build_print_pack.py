# -*- coding: utf-8 -*-
"""中秋打印包 PDF 生成器（英语版）：语法与词汇过关 30 问 + 高频易混词 30 组 + 作文句型速查 + 家长提问卡 30 问。
内容直接解析自知识库 Markdown 卡片，避免转抄错误。"""
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parent
KB = ROOT / "知识库" / "英语"
OUT_DIR = ROOT / "打印包"
OUT_DIR.mkdir(exist_ok=True)
OUT_PDF = OUT_DIR / "中秋打印包_英语.pdf"

# ---------- 字体（优先环境变量 DAIMON_CJK_FONT_*，缺失时回退项目内 NotoSansSC） ----------
regular_font = os.environ.get("DAIMON_CJK_FONT_REGULAR")
bold_font = os.environ.get("DAIMON_CJK_FONT_BOLD")
if not regular_font or not bold_font:
    _local_reg = ROOT / "assets" / "fonts" / "NotoSansSC-Regular.ttf"
    _local_bold = ROOT / "assets" / "fonts" / "NotoSansSC-Bold.ttf"
    if _local_reg.exists() and _local_bold.exists():
        regular_font, bold_font = str(_local_reg), str(_local_bold)
if not regular_font or not bold_font:
    raise RuntimeError("CJK fonts unavailable (set DAIMON_CJK_FONT_* or provide assets/fonts/NotoSansSC)")
pdfmetrics.registerFont(TTFont("DaimonCJK", regular_font))
pdfmetrics.registerFont(TTFont("DaimonCJK-Bold", bold_font))
pdfmetrics.registerFontFamily("DaimonCJK", normal="DaimonCJK",
                              bold="DaimonCJK-Bold", italic="DaimonCJK",
                              boldItalic="DaimonCJK-Bold")


def conv(s):
    """markdown 片段 -> reportlab 段落文本：转义 + **粗体** + 状态emoji"""
    s = (s.replace("✅", "已掌握").replace("⚠️", "待强化")
          .replace("⚠", "待强化").replace("❌", "未理解"))
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = s.replace("**", "")
    s = s.replace("`", "")
    return s


# ---------- Markdown 解析 ----------
def read_md(path):
    return path.read_text(encoding="utf-8")


def parse_numbered_lines(block):
    items = []
    for line in block.splitlines():
        m = re.match(r"^(\d+)\.\s+(.*)", line.strip())
        if m:
            items.append((int(m.group(1)), m.group(2).strip()))
    return items


def parse_md_tables(block):
    """返回 block 中所有 markdown 表格（list of list of rows）"""
    tables, cur = [], []
    for line in block.splitlines():
        ls = line.strip()
        if ls.startswith("|") and ls.endswith("|"):
            cells = [c.strip() for c in ls.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue
            cur.append(cells)
        else:
            if cur:
                tables.append(cur)
                cur = []
    if cur:
        tables.append(cur)
    return tables


def section(text, start_marker, end_markers):
    i = text.find(start_marker)
    if i < 0:
        return ""
    j = len(text)
    for m in end_markers:
        k = text.find(m, i + len(start_marker))
        if 0 <= k < j:
            j = k
    return text[i:j]


def parse_check_card(path):
    """解析概念检验 30 问卡"""
    text = read_md(path)
    part1 = section(text, "## 第一部分", ["## 第二部分"])
    part2 = section(text, "## 第二部分", ["## ✅"])
    blk_a = section(part1, "### A.", ["### B."])
    blk_b = section(part1, "### B.", ["\n---", "## "])
    qa = parse_numbered_lines(blk_a)
    qb = parse_numbered_lines(blk_b)
    blk_a2 = section(part2, "### A.", ["### B."])
    blk_b2 = section(part2, "### B.", ["\n---", "## "])
    ta = parse_md_tables(blk_a2)[0]
    tb = parse_md_tables(blk_b2)[0]
    std = section(text, "## ✅ 过关标准", ["## 错题对应", "## 备注"])
    std_items = [re.sub(r"^- \[ \]\s*", "", l.strip()) for l in std.splitlines()
                 if l.strip().startswith("- [ ]")]
    return qa, qb, ta[1:], tb[1:], std_items


def parse_word_blocks(path):
    """解析易混词卡 -> [(组块标题, 表格rows)]"""
    text = read_md(path)
    core = section(text, "## 核心内容", ["## 🗣️", "## 关联卡片"])
    blocks = []
    for m in re.finditer(r"### (第[一二三四五]组块[^\n]+)\n(.*?)(?=\n### |\n---|\Z)", core, re.S):
        title = m.group(1).strip()
        tables = parse_md_tables(m.group(2))
        if tables:
            blocks.append((title, tables[0]))
    return blocks


def parse_bullet_lines(path, sec_start, sec_end):
    text = read_md(path)
    sec = section(text, sec_start, sec_end)
    return [re.sub(r"^-\s*", "", l.strip()) for l in sec.splitlines()
            if l.strip().startswith("- ")]


# ---------- 样式 ----------
INK = HexColor("#1f2430")
MUTED = HexColor("#666666")
ACCENT = HexColor("#274690")

S = {
    "title": ParagraphStyle("t", fontName="DaimonCJK-Bold", fontSize=24,
                            leading=32, textColor=INK, alignment=1),
    "subtitle": ParagraphStyle("st", fontName="DaimonCJK", fontSize=13,
                               leading=20, textColor=MUTED, alignment=1),
    "h1": ParagraphStyle("h1", fontName="DaimonCJK-Bold", fontSize=16,
                         leading=22, textColor=ACCENT, spaceBefore=6,
                         spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="DaimonCJK-Bold", fontSize=12.5,
                         leading=17, textColor=INK, spaceBefore=10,
                         spaceAfter=5),
    "body": ParagraphStyle("b", fontName="DaimonCJK", fontSize=10.5,
                           leading=16, textColor=INK),
    "q": ParagraphStyle("q", fontName="DaimonCJK", fontSize=10.5,
                        leading=16.5, textColor=INK, spaceBefore=1.5,
                        spaceAfter=1.5),
    "small": ParagraphStyle("s", fontName="DaimonCJK", fontSize=9,
                            leading=13.5, textColor=MUTED),
    "cell": ParagraphStyle("c", fontName="DaimonCJK", fontSize=9.5,
                           leading=13.5, textColor=INK),
    "cellb": ParagraphStyle("cb", fontName="DaimonCJK-Bold", fontSize=9.5,
                            leading=13.5, textColor=INK),
    "note": ParagraphStyle("n", fontName="DaimonCJK", fontSize=10,
                           leading=15, textColor=HexColor("#5b3a12"),
                           backColor=HexColor("#fdf0e2"), borderPadding=6,
                           spaceBefore=6, spaceAfter=6),
}


def P(text, style="body"):
    return Paragraph(conv(text), S[style])


def three_line_table(rows, widths, header=True):
    data = []
    for i, row in enumerate(rows):
        st = "cellb" if (header and i == 0) else "cell"
        data.append([Paragraph(conv(str(c)), S[st]) for c in row])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("LINEABOVE", (0, 0), (-1, 0), 1.2, INK),
        ("LINEBELOW", (0, -1), (-1, -1), 1.2, INK),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    if header:
        style.append(("LINEBELOW", (0, 0), (-1, 0), 0.6, INK))
    t.setStyle(TableStyle(style))
    return t


# ---------- 页眉页脚 ----------
def later_pages(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFont("DaimonCJK", 8.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(2.2 * cm, h - 1.3 * cm, "中秋打印包 · 英语（语法词汇过关 + 易混词表 + 作文句型速查 + 家长提问卡）")
    canvas.drawRightString(w - 2.2 * cm, h - 1.3 * cm, "申悦学习 2026.9")
    canvas.setStrokeColor(HexColor("#dddddd"))
    canvas.line(2.2 * cm, h - 1.5 * cm, w - 2.2 * cm, h - 1.5 * cm)
    canvas.drawCentredString(w / 2, 1.1 * cm, f"第 {doc.page} 页")
    canvas.restoreState()


def first_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFont("DaimonCJK", 8.5)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(w / 2, 1.1 * cm, f"第 {doc.page} 页")
    canvas.restoreState()


# ---------- 内容组装 ----------
story = []

# 封面
story.append(Spacer(1, 3.2 * cm))
story.append(Paragraph("中秋打印包 · 英语", S["title"]))
story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph("语法词汇过关 30 问 + 高频易混词 30 组 + 作文句型速查 + 家长提问卡", S["subtitle"]))
story.append(Paragraph("中秋假期 2026.9.25–9.27 · 备战高二第一次月考（主线：阅读理解）", S["subtitle"]))
story.append(Spacer(1, 1.2 * cm))
cover_items = [
    "第一部分　语法与词汇过关 30 问（判断 20 + 填空 10，含答案与一句话解析）",
    "第二部分　高频易混词 30 组：五大组块（动词短语 / 情绪形容词 / 拼写词族 / 形近陷阱 / 完形实词）",
    "第三部分　作文句型速查：应用文三段骨架 + 高级句型 + 加分替换表 + 续写升华金句",
    "第四部分　家长提问卡 30 问：照原话问、看关键词打钩（每天睡前 15 分钟）",
]
for it in cover_items:
    story.append(Paragraph(conv(it), ParagraphStyle(
        "ci", parent=S["body"], fontSize=11.5, leading=20, alignment=1)))
story.append(Spacer(1, 1.0 * cm))
story.append(Paragraph(conv("用法：检验卷先做题后对答案（答案区在第一部分后半），错题回知识库对应卡片补课；"
                            "易混词表与句型速查贴在书桌前，碎片时间扫一眼。"), S["note"]))
story.append(PageBreak())

# 第一部分：语法与词汇过关 30 问
story.append(Paragraph("第一部分　语法与词汇过关 30 问", S["h1"]))
story.append(P("共 30 题（判断 20 + 填空 10），建议用时 20 分钟。判断题在题后（　）内打 √ 或 ×；"
               "填空题把关键词写在横线上。全部做完再翻后面的答案区。过关标准：判断错 ≤ 2、填空对 ≥ 8。"))
story.append(Spacer(1, 8))

qa, qb, ta, tb, std = parse_check_card(
    KB / "概念检验" / "高二深化_英语_概念检验_语法与词汇过关30问.md")
story.append(Paragraph("A. 判断题（每题一句话，√ 或 ×）", S["h2"]))
for n, q in qa:
    story.append(Paragraph(conv(f"{n}. {q}（　）"), S["q"]))
story.append(Spacer(1, 6))
story.append(Paragraph("B. 填空题（写关键词 / 词形）", S["h2"]))
for n, q in qb:
    q2 = q.replace("______", "＿" * 10)
    story.append(Paragraph(conv(f"{n}. {q2}"), S["q"]))
story.append(Spacer(1, 8))
story.append(Paragraph("答案与一句话解析（做完再看）", S["h2"]))
story.append(three_line_table([["题", "答案", "一句话解析"]] + ta,
                              [1.2 * cm, 1.6 * cm, 13.4 * cm]))
story.append(Spacer(1, 6))
story.append(three_line_table([["题", "答案"]] + tb, [1.2 * cm, 15.0 * cm]))
story.append(Spacer(1, 6))
story.append(Paragraph("过关标准", S["h2"]))
for it in std:
    story.append(Paragraph(conv("□ " + it), S["q"]))

story.append(PageBreak())

# 第二部分：高频易混词 30 组
story.append(Paragraph("第二部分　高频易混词 30 组（考前 10 分钟扫一遍）", S["h1"]))
story.append(P("辨析词记「事迹」不记词表：每组的第三列就是它干过的事。做完形/拼写题前先扫一遍对应组块。"))
story.append(Spacer(1, 6))

WORD_CARD = KB / "易错警示与辨析" / "高二深化_英语_易错警示与辨析_高频易混词30组.md"
for title, table in parse_word_blocks(WORD_CARD):
    story.append(Paragraph(title, S["h2"]))
    ncols = len(table[0])
    if ncols >= 4:
        widths = [0.9 * cm, 4.2 * cm, 5.4 * cm, 5.7 * cm]
    else:
        widths = [0.9 * cm, 5.4 * cm, 9.9 * cm]
    story.append(three_line_table(table, widths))
    story.append(Spacer(1, 8))

story.append(PageBreak())

# 第三部分：作文句型速查
story.append(Paragraph("第三部分　作文句型速查", S["h1"]))

story.append(Paragraph("万能三段骨架（报道 / 邮件 / 发言稿通用）", S["h2"]))
story.append(P("第一段（1-2 句）：身份/背景 + 目的（I'm writing to... / On behalf of...）"))
story.append(P("第二段（3-5 句）：主体两要点，要点之间用衔接词（First... Besides... / What's more）"))
story.append(P("第三段（1-2 句）：感谢 + 期待/呼吁（I would appreciate it if... / Looking forward to...）"))
story.append(Spacer(1, 6))

story.append(Paragraph("高级句型弹药库（每篇用 2-3 个，不堆砌）", S["h2"]))
TEMPLATE_CARD = KB / "典型题型与方法" / "高二深化_英语_典型题型与方法_应用文写作模板与高级句型.md"
for line in parse_bullet_lines(TEMPLATE_CARD, "### 高级句型弹药库", "### 加分替换表"):
    story.append(Paragraph(conv("・" + line), S["q"]))
story.append(Spacer(1, 6))


def grab_table(path, header_keyword):
    for t in parse_md_tables(read_md(path)):
        if any(header_keyword in c for c in t[0]):
            return t
    return None


t = grab_table(TEMPLATE_CARD, "普通写法")
if t:
    story.append(Paragraph("加分替换表（阅卷老师眼中的「高级感」）", S["h2"]))
    story.append(three_line_table(t, [5.5 * cm, 10.7 * cm]))
    story.append(Spacer(1, 8))

story.append(Paragraph("读后续写升华金句（双线法收尾用）", S["h2"]))
CONTINUATION_LIB = KB / "素材与拓展" / "作文语料库" / "读后续写动作与情绪描写句库.md"
for line in parse_bullet_lines(CONTINUATION_LIB, "## 五、升华点题句库", "## 六、"):
    story.append(Paragraph(conv("・" + line), S["q"]))
story.append(Spacer(1, 6))
story.append(Paragraph(conv("双线法口诀：先划原文锚点，情节线 + 情感线并行；每段五句式 = 情绪 1 + 动作 2 + 对话 1 + 环境呼应 1。"), S["note"]))

story.append(PageBreak())

# 第四部分：家长提问卡（费曼回话题库）
story.append(Paragraph("第四部分　家长提问卡（费曼回话题库 30 问）", S["h1"]))
story.append(P("家长照「您这样问」原话提问，孩子口头回答（中文答即可）；对照「过关信号」里的关键词，意思对就打 √，"
               "磕绊标 ⚠️、答不上标 ❌。答不上就去最后一列指路的卡片复习。每天睡前 5 题，错了别纠正，"
               "说「再讲讲」就好。"))
story.append(Spacer(1, 8))

QUESTIONS_MD = ROOT / "家长支持" / "家长提问卡_费曼回话题库.md"
Q_SECTIONS = ["语法三大件（12 问）", "阅读与完形（11 问）", "作文与词汇（7 问）"]
q_tables = parse_md_tables(read_md(QUESTIONS_MD))[:3]
for si, (sec_name, qt) in enumerate(zip(Q_SECTIONS, q_tables)):
    block = [Paragraph(sec_name, S["h2"]),
             three_line_table(
                 [["#", "您这样问", "过关信号（听到这些意思就 √）", "不会就去看"]] + qt[1:],
                 [0.9 * cm, 5.6 * cm, 6.3 * cm, 3.4 * cm])]
    story.append(KeepTogether(block))
    story.append(Spacer(1, 10))

# ---------- 构建 ----------
doc = SimpleDocTemplate(str(OUT_PDF), pagesize=A4,
                        topMargin=2.0 * cm, bottomMargin=1.8 * cm,
                        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                        title="中秋打印包 · 英语", author="申悦学习")
doc.build(story, onFirstPage=first_page, onLaterPages=later_pages)
print("OK:", OUT_PDF)
