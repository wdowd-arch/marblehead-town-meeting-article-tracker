import argparse
import re
from pathlib import Path

import fitz  # type: ignore


MONEY_RE = re.compile(r"\$[\d,]+(?:\.\d{2})?")
PERCENT_RE = re.compile(r"\b\d+(?:\.\d+)?%\b")
VOTE_RE = re.compile(
    r"\b(two[- ]thirds|two thirds|majority|unanimous|by ballot|roll call|4/5|three[- ]fourths)\b",
    re.IGNORECASE,
)
SPONSORED_RE = re.compile(r"\bSponsored by the ([^.]+)\.", re.IGNORECASE)


def pdf_text(pdf_path: Path) -> str:
    doc = fitz.open(str(pdf_path))
    try:
        parts = []
        for i in range(doc.page_count):
            parts.append(doc.load_page(i).get_text("text"))
        return "\n".join(parts)
    finally:
        doc.close()


def normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def first_nonempty_lines(text: str, n: int = 6) -> list[str]:
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return lines[:n]


def extract_article_header_facts(text: str) -> dict:
    facts: dict = {}

    # Try to capture "ARTICLE X: Title"
    m = re.search(r"(?i)\bARTICLE\s+(\d{1,3})\s*:\s*(.+)", text)
    if m:
        facts["article_number"] = int(m.group(1))
        facts["title_line"] = m.group(2).strip()

    sponsor = SPONSORED_RE.search(text)
    if sponsor:
        facts["sponsor"] = sponsor.group(1).strip()

    votes = sorted({v.lower() for v in VOTE_RE.findall(text)})
    if votes:
        facts["vote_threshold_mentions"] = votes

    money = sorted({m.group(0) for m in MONEY_RE.finditer(text)})
    if money:
        facts["money_mentions"] = money

    perc = sorted({p.group(0) for p in PERCENT_RE.finditer(text)})
    if perc:
        facts["percent_mentions"] = perc

    return facts


def find_report_snippets(report_text: str, article_number: int, max_snips: int = 6) -> list[str]:
    # Capture short windows around mentions like "Article 12" / "ARTICLE 12"
    patt = re.compile(rf"(?i)\bArticle\s+{article_number}\b|\bARTICLE\s+{article_number}\b")
    snippets: list[str] = []

    for m in patt.finditer(report_text):
        start = max(0, m.start() - 350)
        end = min(len(report_text), m.end() + 650)
        chunk = normalize(report_text[start:end])
        # Keep it short and readable
        chunk = re.sub(r"\n{2,}", "\n", chunk)
        if chunk and chunk not in snippets:
            snippets.append(chunk)
        if len(snippets) >= max_snips:
            break
    return snippets


def write_info_txt(
    out_path: Path,
    article_number: int,
    warrant_text: str,
    fincom_text: str | None,
    override_text: str | None,
) -> None:
    warrant_text_n = normalize(warrant_text)
    facts = extract_article_header_facts(warrant_text_n)

    lines: list[str] = []
    lines.append(f"ARTICLE {article_number}")
    if facts.get("title_line"):
        lines.append(f"Title: {facts['title_line']}")
    if facts.get("sponsor"):
        lines.append(f"Sponsor: {facts['sponsor']}")
    if facts.get("vote_threshold_mentions"):
        lines.append("Vote threshold mentions: " + ", ".join(facts["vote_threshold_mentions"]))
    if facts.get("money_mentions"):
        lines.append("Money mentions: " + ", ".join(facts["money_mentions"]))
    if facts.get("percent_mentions"):
        lines.append("Percent mentions: " + ", ".join(facts["percent_mentions"]))

    lines.append("")
    lines.append("Warrant (first lines):")
    for ln in first_nonempty_lines(warrant_text_n, n=10):
        lines.append(f"- {ln}")

    lines.append("")
    lines.append("Warrant (full text):")
    lines.append(warrant_text_n)

    if fincom_text:
        snips = find_report_snippets(fincom_text, article_number)
        if snips:
            lines.append("")
            lines.append("FinCom report snippets mentioning this article:")
            for s in snips:
                lines.append("---")
                lines.append(s)

    if override_text:
        snips = find_report_snippets(override_text, article_number)
        if snips:
            lines.append("")
            lines.append("Override presentation snippets mentioning this article:")
            for s in snips:
                lines.append("---")
                lines.append(s)

    out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate per-article info.txt files from the extracted warrant articles and other reports."
    )
    parser.add_argument("--articles-dir", default="warrant-articles-2026", help="Folder containing article-XX dirs")
    parser.add_argument("--fincom-pdf", default="2026-Marblehead-FinCom-Report-FINAL-05.01.26-003.pdf")
    parser.add_argument("--override-pdf", default="2026-04-15-Override-Presentation-FINAL.pdf")
    args = parser.parse_args()

    root = Path.cwd()
    articles_dir = (root / args.articles_dir).resolve()
    if not articles_dir.exists():
        raise SystemExit(f"Missing articles dir: {articles_dir}")

    fincom_path = (root / args.fincom_pdf).resolve()
    override_path = (root / args.override_pdf).resolve()

    fincom_text = pdf_text(fincom_path) if fincom_path.exists() else None
    override_text = pdf_text(override_path) if override_path.exists() else None

    for article_dir in sorted(articles_dir.glob("article-*")):
        if not article_dir.is_dir():
            continue
        m = re.match(r"article-(\d+)", article_dir.name)
        if not m:
            continue
        article_number = int(m.group(1))
        article_pdf = article_dir / f"{article_dir.name}.pdf"
        if not article_pdf.exists():
            continue

        warrant_text = pdf_text(article_pdf)
        out_path = article_dir / "info.txt"
        write_info_txt(out_path, article_number, warrant_text, fincom_text, override_text)

    print(f"Wrote info.txt files under: {articles_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

