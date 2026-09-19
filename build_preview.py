"""打印包预览拼图生成器：打印包/*.pdf -> 打印包/预览_contact-sheet.png

用法：python build_preview.py
打印包 PDF 更新后重跑一次即可刷新预览。Windows 控制台勿 print 中文。
"""
import sys
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image

ROOT = Path(__file__).parent
PRINT_DIR = ROOT / "打印包"


def main():
    pdfs = sorted(PRINT_DIR.glob("*.pdf"))
    if not pdfs:
        print("WARN: no pdf in", PRINT_DIR)
        return
    pdf_path = pdfs[0]
    pdf = pdfium.PdfDocument(str(pdf_path))
    n = len(pdf)
    cols = 5 if n > 9 else 4
    rows = (n + cols - 1) // cols
    thumb_w = 520
    imgs = []
    for i in range(n):
        bmp = pdf[i].render(scale=thumb_w / 595)
        imgs.append(bmp.to_pil())
    th = imgs[0].height
    sheet = Image.new("RGB", (cols * thumb_w, rows * th), "white")
    for i, im in enumerate(imgs):
        sheet.paste(im, ((i % cols) * thumb_w, (i // cols) * th))
    out = PRINT_DIR / "预览_contact-sheet.png"
    sheet.save(str(out))
    print("OK:", n, "pages ->", out.name, sheet.size)


if __name__ == "__main__":
    sys.exit(main())
