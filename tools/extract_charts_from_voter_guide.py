import argparse
import re
from pathlib import Path

from playwright.sync_api import sync_playwright


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "chart"


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract Chart.js canvases from a saved voter guide HTML file.")
    parser.add_argument(
        "--html",
        required=True,
        help="Path to the saved voter guide HTML file (local .htm/.html)",
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repo root where charts/ and warrant-articles-2026/ live",
    )
    parser.add_argument(
        "--charts-dir",
        default="charts",
        help="Output folder (relative to repo root)",
    )
    parser.add_argument(
        "--articles-dir",
        default="warrant-articles-2026",
        help="Articles folder (relative to repo root)",
    )
    args = parser.parse_args()

    html_path = Path(args.html).resolve()
    if not html_path.exists():
        raise SystemExit(f"HTML not found: {html_path}")

    repo_root = Path(args.repo).resolve()
    charts_dir = (repo_root / args.charts_dir).resolve()
    charts_dir.mkdir(parents=True, exist_ok=True)

    articles_dir = (repo_root / args.articles_dir).resolve()

    file_url = html_path.as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 2000})
        try:
            page.goto(file_url, wait_until="load")
            # Give Chart.js time to paint
            page.wait_for_timeout(1500)

            canvases = page.query_selector_all("canvas")
            if not canvases:
                raise SystemExit("No <canvas> elements found.")

            meta = []
            for c in canvases:
                cid = c.get_attribute("id") or ""
                # Identify a human-friendly label from nearest preceding heading
                label = page.evaluate(
                    """(el) => {
                      function textOf(node){ return (node && node.textContent ? node.textContent.trim() : ""); }
                      let cur = el;
                      while (cur && cur !== document.body) {
                        let prev = cur.previousElementSibling;
                        while (prev) {
                          if (/^H[1-4]$/.test(prev.tagName)) return textOf(prev);
                          // sometimes canvas is wrapped; search inside previous blocks
                          const h = prev.querySelector && prev.querySelector('h1,h2,h3,h4');
                          if (h) return textOf(h);
                          prev = prev.previousElementSibling;
                        }
                        cur = cur.parentElement;
                      }
                      return "";
                    }""",
                    c,
                )
                label = (label or "").strip()

                # Determine output base name
                base = cid or slugify(label)
                base = slugify(base)

                out_path = charts_dir / f"{base}.png"
                c.screenshot(path=str(out_path))

                # Attempt to map to an article number by scanning nearby text for "Article N"
                nearby = page.evaluate(
                    """(el) => {
                      const box = el.closest('section,article,div') || el.parentElement;
                      const t = (box ? box.innerText : el.innerText) || "";
                      return t.slice(0, 2000);
                    }""",
                    c,
                )
                m = re.search(r"Article\\s+(\\d{1,2})", nearby or "", flags=re.IGNORECASE)
                article_num = int(m.group(1)) if m else None

                # Heuristics for this guide (when the page doesn't mention article numbers near the chart).
                if article_num is None:
                    lbl = (label or "").lower()
                    if "where the" in lbl and "million" in lbl:
                        article_num = 23  # operating budget
                    elif "health insurance" in lbl:
                        article_num = 23  # budget driver within operating budget
                    elif "how marblehead votes" in lbl or "ballot questions" in lbl:
                        article_num = 29  # override context (town-side override article)

                meta.append(
                    {
                        "id": cid,
                        "label": label,
                        "file": str(out_path),
                        "article": article_num,
                    }
                )

                # Also drop a copy into the best-matching article folder (if any)
                if article_num and articles_dir.exists():
                    article_folder = articles_dir / f"article-{article_num:02d}"
                    if article_folder.exists():
                        dest = article_folder / out_path.name
                        dest.write_bytes(out_path.read_bytes())

            # Write an index for embedding
            idx_lines = ["# Extracted charts", ""]
            for m in meta:
                name = Path(m["file"]).name
                idx_lines.append(f"## {name}")
                if m.get("label"):
                    idx_lines.append(f"- Label: {m['label']}")
                if m.get("id"):
                    idx_lines.append(f"- Canvas id: {m['id']}")
                if m.get("article"):
                    idx_lines.append(f"- Suggested article: {m['article']}")
                idx_lines.append("")
                idx_lines.append("```html")
                src = (Path(args.charts_dir) / name).as_posix()
                alt = (m.get("label") or name).replace('"', "'")
                idx_lines.append(f'<img src="./{src}" alt="{alt}" style="max-width:100%; height:auto;" />')
                idx_lines.append("```")
                idx_lines.append("")

            (charts_dir / "README.md").write_text("\n".join(idx_lines).strip() + "\n", encoding="utf-8")
        finally:
            browser.close()

    print(f"Extracted {len(meta)} charts to: {charts_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
