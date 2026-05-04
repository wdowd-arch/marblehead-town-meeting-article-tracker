# Claude Code knowledge pack (Marblehead Town Meeting 2026)

## What this ZIP contains
- `warrant-articles-2026/` — one folder per warrant article (`article-01` … `article-40`)
  - `facts.txt` — journalist-oriented “one stop” summary (tracker facts + warrant text + relevant report snippets)
  - `info.txt` — raw-ish extracted warrant text + report snippets (backup/reference)
  - `independent-reporting.txt` — added context from Marblehead Independent stories (when applicable)
  - `article-XX.pdf` — cropped PDF containing only that article
  - `article-XX-p01.png` … — images of each page for fast embedding
- `charts/chart-code/` — reproducible Chart.js modules (JS) + `README.md` with usage
- Source PDFs:
  - `Marblehead-Warrant-2026.pdf`
  - `2026-Marblehead-FinCom-Report-FINAL-05.01.26-003.pdf`
  - `2026-04-15-Override-Presentation-FINAL.pdf`

## How to use it (Claude Code workflow)
1. When covering a specific warrant article, open:
   - `warrant-articles-2026/article-XX/facts.txt`
   - (Optional) `warrant-articles-2026/article-XX/independent-reporting.txt` if present
2. Use `facts.txt` sections:
   - **Quick facts** for structured fields (category, sponsor, vote threshold, recommendation).
   - **Journalist notes (tracker)** for pre-written explainers, stakes, and key numbers.
   - **Primary source (warrant text)** for precise paraphrase/quotes.
   - **Report snippets** for FinCom/override context (only where that article is mentioned).
3. For embedding in the live blog / GitHub page, use:
   - Article PDF: `warrant-articles-2026/article-XX/article-XX.pdf`
   - Article images: `warrant-articles-2026/article-XX/article-XX-p01.png` (etc)
   - Charts (code): `charts/chart-code/*.js` or the per-article copies + `chart-embed-snippet.html` (when present)

## Prompt to give Claude Code
Copy/paste the block below into Claude Code along with the ZIP attached/unzipped in the workspace:

```text
You are assisting with live coverage of Marblehead’s 2026 Annual Town Meeting.

Knowledge base layout:
- warrant-articles-2026/article-XX/facts.txt is the primary file for each article.
- Each article folder also contains a cropped article PDF and page images for embedding.
- charts/chart-code/ contains reproducible Chart.js modules and a usage README.
- Some article folders include `*Chart.js` modules + `chart-embed-snippet.html` for copy/paste embeds.

When I ask about an article number N:
1) Read warrant-articles-2026/article-NN/facts.txt first.
2) Produce:
   - A 2–4 sentence explainer suitable for a live blog update.
   - A bullet list of the 5–10 most important concrete facts (numbers, vote threshold, sponsor, recommendation, what a YES/NO does).
   - A short “embed assets” block listing the PDF path and first image path, plus any available chart embed snippet/code paths.
3) Use only information found in the knowledge base files unless I explicitly ask you to add outside reporting.
4) If facts conflict between sources inside the knowledge base, flag the conflict and cite both excerpts.

For every response, include a section titled “What to cite / embed” that lists:
- The exact file paths you actually used
- Any additional files in the knowledge base that you think I should use next (and why)
- Any available embed assets (PDF/PNG and chart snippet/code) for that article
- “Missing context” if something you expected isn’t present in the knowledge base

If I say “update the tracker”, modify the GitHub page files as requested, using the article facts as source material.
```
