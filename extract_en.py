import sys
sys.stdout.reconfigure(encoding="utf-8")
import pdfplumber
from pathlib import Path

src = Path("知识库/英语/素材与拓展/真题试卷")
out = src / "提取文本"
out.mkdir(exist_ok=True)
for pdf_path in sorted(src.glob("*.pdf")):
    txt_path = out / (pdf_path.stem + ".txt")
    if txt_path.exists():
        print("skip:", pdf_path.name); continue
    with pdfplumber.open(pdf_path) as pdf:
        texts = []
        for i, page in enumerate(pdf.pages):
            t = page.extract_text() or ""
            texts.append(f"--- page {i+1} ---\n{t}")
    txt_path.write_text("\n".join(texts), encoding="utf-8")
    print("OK:", pdf_path.name, "pages:", len(texts), "chars:", sum(len(t) for t in texts))
