import argparse
import json
import re
from pathlib import Path

import fitz  # type: ignore


def normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def pdf_text(pdf_path: Path) -> str:
    doc = fitz.open(str(pdf_path))
    try:
        parts = []
        for i in range(doc.page_count):
            parts.append(doc.load_page(i).get_text("text"))
        return "\n".join(parts)
    finally:
        doc.close()


def extract_articles_array(index_html: str) -> list[dict]:
    # Find: const articles = [ ... ];
    m = re.search(r"const\s+articles\s*=\s*\[\s*(.*?)\s*\];", index_html, flags=re.S)
    if not m:
        raise RuntimeError("Could not find `const articles = [` block in index.html")
    block = m.group(0)
    # Re-extract just the array contents for cleaner transforms.
    m2 = re.search(r"const\s+articles\s*=\s*(\[\s*.*?\s*\])\s*;", block, flags=re.S)
    if not m2:
        raise RuntimeError("Could not parse articles array in index.html")
    arr = m2.group(1)

    # Minimal JS->JSON transform:
    # - Quote unquoted keys: { num: 1, title: "..." } => { "num": 1, "title": "..." }
    # - Remove trailing commas before } or ]
    # Assumes values are already JSON-compatible (strings use double quotes, \n escapes).
    def quote_keys(s: str) -> str:
        out = []
        in_str = False
        esc = False
        for i, ch in enumerate(s):
            if in_str:
                out.append(ch)
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
                out.append(ch)
                continue
            out.append(ch)
        s2 = "".join(out)
        s2 = re.sub(r'([{\[,]\s*)([A-Za-z_]\w*)\s*:', r'\1"\2":', s2)
        s2 = re.sub(r",\s*([}\]])", r"\1", s2)
        return s2

    jsonish = quote_keys(arr)
    return json.loads(jsonish)


def find_report_snippets(report_text: str, article_number: int, max_snips: int = 4) -> list[str]:
    patt = re.compile(rf"(?i)\bArticle\s+{article_number}\b|\bARTICLE\s+{article_number}\b")
    snippets: list[str] = []
    for m in patt.finditer(report_text):
        start = max(0, m.start() - 300)
        end = min(len(report_text), m.end() + 550)
        chunk = normalize(report_text[start:end])
        chunk = re.sub(r"\n{2,}", "\n", chunk)
        if chunk and chunk not in snippets:
            snippets.append(chunk)
        if len(snippets) >= max_snips:
            break
    return snippets


def write_facts_txt(
    out_path: Path,
    a: dict,
    warrant_text: str,
    fincom_text: str | None,
    override_text: str | None,
) -> None:
    num = int(a["num"])
    slug = f"article-{num:02d}"

    lines: list[str] = []
    lines.append(f"ARTICLE {num}: {a.get('title','').strip()}")
    lines.append("")
    lines.append("Quick facts")
    lines.append(f"- Category: {a.get('cat','')}".rstrip())
    lines.append(f"- Sponsor: {a.get('sponsor','')}".rstrip())
    lines.append(f"- Vote threshold: {a.get('vote','')}".rstrip())
    if a.get("key"):
        lines.append(f"- Key: {a.get('key')}".rstrip())
    if a.get("stakes"):
        lines.append(f"- Stakes: {a.get('stakes')}".rstrip())
    if a.get("rec"):
        lines.append(f"- Recommendation: {a.get('rec')} ({a.get('recBy','')})".rstrip())
    if a.get("result"):
        lines.append(f"- Result: {a.get('result')}".rstrip())
    if a.get("resultDetail"):
        if str(a.get("resultDetail")).strip():
            lines.append(f"- Result detail: {a.get('resultDetail')}".rstrip())

    lines.append("")
    lines.append("Journalist notes (tracker)")
    note = normalize(str(a.get("note", "")).replace("\\n", "\n"))
    if note:
        # Force bullets for readability
        for ln in note.splitlines():
            if ln.strip().startswith("—") or ln.strip().startswith("-"):
                lines.append(ln.strip().replace("—", "- ", 1))
            else:
                lines.append(f"- {ln.strip()}")
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("Primary source (warrant text)")
    lines.append(normalize(warrant_text))

    if fincom_text:
        snips = find_report_snippets(fincom_text, num)
        if snips:
            lines.append("")
            lines.append("FinCom report snippets mentioning this article")
            for s in snips:
                lines.append("---")
                lines.append(s)

    if override_text:
        snips = find_report_snippets(override_text, num)
        if snips:
            lines.append("")
            lines.append("Override presentation snippets mentioning this article")
            for s in snips:
                lines.append("---")
                lines.append(s)

    lines.append("")
    lines.append("Assets")
    lines.append(f"- PDF: ./{slug}.pdf")
    lines.append(f"- Images: ./{slug}-p01.png (and more if multi-page)")

    out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate per-article facts.txt from index.html + PDFs.")
    parser.add_argument("--articles-dir", default="warrant-articles-2026")
    parser.add_argument("--index-html", default="index.html")
    parser.add_argument("--fincom-pdf", default="2026-Marblehead-FinCom-Report-FINAL-05.01.26-003.pdf")
    parser.add_argument("--override-pdf", default="2026-04-15-Override-Presentation-FINAL.pdf")
    args = parser.parse_args()

    root = Path.cwd()
    articles_dir = (root / args.articles_dir).resolve()
    index_path = (root / args.index_html).resolve()
    if not index_path.exists():
        raise SystemExit(f"Missing index.html: {index_path}")

    index_html = index_path.read_text(encoding="utf-8", errors="replace")
    articles = extract_articles_array(index_html)

    fincom_path = (root / args.fincom_pdf).resolve()
    override_path = (root / args.override_pdf).resolve()
    fincom_text = pdf_text(fincom_path) if fincom_path.exists() else None
    override_text = pdf_text(override_path) if override_path.exists() else None

    by_num = {int(a["num"]): a for a in articles if "num" in a}

    for num in range(1, 41):
        article_dir = articles_dir / f"article-{num:02d}"
        if not article_dir.exists():
            continue
        article_pdf = article_dir / f"article-{num:02d}.pdf"
        if not article_pdf.exists():
            continue

        warrant_text = pdf_text(article_pdf)
        a = by_num.get(num, {"num": num, "title": "", "cat": "", "sponsor": "", "vote": ""})
        out_path = article_dir / "facts.txt"
        write_facts_txt(out_path, a, warrant_text, fincom_text, override_text)

    print(f"Wrote facts.txt files under: {articles_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

