import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

import fitz  # type: ignore


@dataclass(frozen=True)
class ArticleLoc:
    number: int
    page_idx: int  # 0-based
    y0: float  # top coordinate


def _slug(n: int) -> str:
    return f"article-{n:02d}"


def find_article_locations(pdf_path: Path, max_article: int) -> list[ArticleLoc]:
    doc = fitz.open(str(pdf_path))
    try:
        locs: list[ArticleLoc] = []
        for page_idx in range(doc.page_count):
            page = doc.load_page(page_idx)
            for n in range(1, max_article + 1):
                # Match the warrant's formatting: "ARTICLE 12:" (colon included).
                hits = page.search_for(f"ARTICLE {n}:", quads=False)
                for rect in hits:
                    locs.append(ArticleLoc(number=n, page_idx=page_idx, y0=float(rect.y0)))
        # Earliest occurrence wins per article
        earliest: dict[int, ArticleLoc] = {}
        for loc in sorted(locs, key=lambda l: (l.page_idx, l.y0)):
            earliest.setdefault(loc.number, loc)
        result = [earliest[n] for n in sorted(earliest)]
        # Order by document position for segmentation.
        result.sort(key=lambda l: (l.page_idx, l.y0))
        return result
    finally:
        doc.close()


def write_article_pdfs(source_pdf: Path, out_dir: Path, locs: list[ArticleLoc]) -> list[dict]:
    if not locs:
        raise RuntimeError("No article headings detected (searched for 'ARTICLE <n>:').")

    src = fitz.open(str(source_pdf))
    try:
        # Build sequential segments based on the next heading in the document,
        # not based on article numbers (some articles share a page).
        manifest: list[dict] = []
        ordered = sorted(locs, key=lambda l: (l.page_idx, l.y0))

        for i, loc in enumerate(ordered):
            next_loc = ordered[i + 1] if i + 1 < len(ordered) else None
            slug = _slug(loc.number)
            article_dir = out_dir / slug
            article_dir.mkdir(parents=True, exist_ok=True)

            out = fitz.open()

            start_page = loc.page_idx
            end_page = next_loc.page_idx if next_loc else (src.page_count - 1)

            for pno in range(start_page, end_page + 1):
                sp = src.load_page(pno)
                page_rect = sp.rect

                y_top = loc.y0 if pno == start_page else page_rect.y0
                y_bot = (next_loc.y0 if (next_loc and pno == next_loc.page_idx) else page_rect.y1)

                # If next heading is on the same page, don't include it.
                if y_bot <= y_top + 1:
                    continue

                clip = fitz.Rect(page_rect.x0, y_top, page_rect.x1, y_bot)
                new_page = out.new_page(width=clip.width, height=clip.height)
                new_page.show_pdf_page(new_page.rect, src, pno, clip=clip)

            pdf_out = article_dir / f"{slug}.pdf"
            out.save(str(pdf_out))
            out.close()

            manifest.append(
                {
                    "article": loc.number,
                    "slug": slug,
                    "start_page": loc.page_idx + 1,
                    "pdf": str(pdf_out.as_posix()),
                }
            )

        return manifest
    finally:
        src.close()


def export_article_pngs(out_dir: Path, manifest: list[dict], dpi: int) -> None:
    for item in manifest:
        article_dir = out_dir / item["slug"]
        pdf_path = article_dir / f'{item["slug"]}.pdf'
        doc = fitz.open(str(pdf_path))
        try:
            for i in range(doc.page_count):
                page = doc.load_page(i)
                mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                out_path = article_dir / f'{item["slug"]}-p{i+1:02d}.png'
                pix.save(str(out_path))
        finally:
            doc.close()


def write_embed_index(out_dir: Path, manifest: list[dict]) -> None:
    # JSON for programmatic consumption
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Markdown helpers for quick copy/paste embedding
    lines: list[str] = []
    lines.append("# 2026 Warrant Articles (Extracted)\n")
    lines.append("This folder contains per-article PDFs and PNGs extracted from the full warrant.\n")
    lines.append("## Quick embeds\n")
    lines.append("Use the PDF when you want selectable text; use PNGs for fast inline display.\n")

    for item in manifest:
        slug = item["slug"]
        pdf_rel = f"./{slug}/{slug}.pdf"
        lines.append(f"### Article {item['article']}\n")
        lines.append("PDF embed:\n")
        lines.append("```html")
        lines.append(f'<embed src="{pdf_rel}" type="application/pdf" width="100%" height="900px" />')
        lines.append("```\n")
        lines.append("First page image (example):\n")
        lines.append("```html")
        lines.append(f'<img src="./{slug}/{slug}-p01.png" alt="Article {item["article"]} page 1" style="max-width:100%;" />')
        lines.append("```\n")

    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Split a town meeting warrant PDF into per-article PDFs/PNGs.")
    parser.add_argument("--pdf", default="Marblehead-Warrant-2026.pdf", help="Path to the warrant PDF")
    parser.add_argument("--out", default="warrant-articles-2026", help="Output folder at repo root")
    parser.add_argument("--dpi", type=int, default=150, help="PNG export DPI (150-200 recommended)")
    parser.add_argument("--no-png", action="store_true", help="Skip PNG export (PDFs only)")
    parser.add_argument(
        "--max-article",
        type=int,
        default=40,
        help="Ignore detected article numbers above this value (guards against stray 'ARTICLE 200' OCR/text)",
    )
    args = parser.parse_args()

    repo_root = Path.cwd()
    pdf_path = (repo_root / args.pdf).resolve()
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    out_dir = (repo_root / args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    locs = find_article_locations(pdf_path, max_article=args.max_article)
    manifest = write_article_pdfs(pdf_path, out_dir, locs)
    manifest.sort(key=lambda x: x["article"])

    if not args.no_png:
        export_article_pngs(out_dir, manifest, dpi=args.dpi)

    write_embed_index(out_dir, manifest)
    print(f"Wrote {len(manifest)} articles to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
