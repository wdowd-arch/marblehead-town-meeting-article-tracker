# Tonight's coverage — handoff brief

Paste this whole file into a fresh Claude session if this context fills up.

## Project

- **Working folder:** `C:\Users\dowdw\Desktop\GitHub Page MHD TM 2026`
- **Repo:** `wdowd-arch/marblehead-town-meeting-article-tracker` (branch `main`)
- **Live URL:** https://wdowd-arch.github.io/marblehead-town-meeting-article-tracker/
- **Local preview server:** python http.server on port 8080, configured in `.claude/launch.json`. Start with the `mcp__Claude_Preview__preview_start` tool, name "Static site (python http.server)".

## What this is

A static one-page site (`index.html` + `assets/nameplate-horizontal.png`) covering the **2026 Marblehead Annual Town Meeting**, Mon. May 4, 7 p.m., Marblehead High School Field House. 40 warrant articles. Built for The Marblehead Independent. Author: Will Dowd, dowdwill@icloud.com.

## Brand (must follow)

- **Independent Red** `#C2261D` — accent, headlines.
- **Harbor Black** `#1E1F21` — body text.
- **Shell White** `#FDF9F4` — background.
- **Slate Blue** `#375E97` — hyperlinks, light accents (countdown), use sparingly.
- **Typeface:** Georgia for editorial. Inter only for UI elements where sans helps.
- **Logo:** `assets/nameplate-horizontal.png` already wired in masthead, links to marbleheadindependent.com. Do not stretch, recolor or place on dark/photographic backgrounds.
- Full brand spec: `C:\Users\dowdw\Desktop\Wesbsite Redesign\02-WORKING\Brand Guidelines\Brand Guidelines.md`

## Page structure (top → bottom)

1. Donate strip (CTA)
2. "Read the full Town Meeting Guide" link (`.guide-return`)
3. Masthead: kicker "Town of Marblehead" → nameplate logo → title "2026 Town Meeting / convenes tonight" → slate-blue countdown box (id `countdown`) → date line → "BY WILL DOWD" byline.
4. `.header` block with kicker "Tonight · Live coverage" + italic deck. (Black 2px bottom rule.)
5. `.live-block` — red pulse-dot heading "Live updates · Annual Town Meeting opens Monday, May 4" + "Jump to article tracker ↓" button. The empty container is `<div id="liveFeed">`.
6. Anchor `<div id="articleTracker"></div>`.
7. Stats grid, badge key, filters, legend.
8. The 40-article tracker (`.table-wrap` → `#articleList`). Articles defined in the `articles` array in the inline `<script>`. Each has: `num, title, cat, sponsor, vote, key, stakes, note, rec, recBy, result, resultDetail`.
9. Override callout, source line, footer nameplate.

## Posting a live update

Newest entries go at the **top** of `#liveFeed`. Drop in:

```html
<div class="live-entry">
  <div class="live-time">7:08 p.m.</div>
  <div class="live-headline">Headline goes here</div>
  <div class="live-body">Body copy. Use &lt;br&gt;&lt;br&gt; for paragraph breaks.</div>
</div>
```

If the feed still has the placeholder `<div class="live-empty">…</div>`, replace it with the first entry.

## Updating an article result

In the `articles` array, find the right `num`, change `result` from `"tbd"` to one of: `"passed"`, `"failed"`, `"amended"`, `"withdrawn"`, and add a short `resultDetail` (e.g. `"Voice vote, unanimous"` or `"Counted vote 412-188"`). The render code does the rest.

## Workflow each update

1. Edit `index.html` (live entry and/or article result).
2. Refresh the preview pane to verify.
3. `git add -A && git commit -m "<message>" && git push`. GitHub Pages publishes within a minute.

## Repos to ignore

The folder also contains seven reference PDFs and one xlsx (warrant, FinCom report, override deck, FY27 budget, Moderator letter, Town Meeting Guide 2022, May 2026 presentation). They're tracked in the repo. Leave them.

## Open follow-ups (none blocking)

- None right now. Tracker is in pre-meeting "ready" state.
