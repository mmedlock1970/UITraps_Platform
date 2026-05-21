# Claude Setup Briefing — UI Traps Helper

Paste this entire document into Claude at the start of a session to brief it on the project.

---

## What this project is

UI Traps Helper is a two-pass AI analysis tool that identifies "UI Tenets & Traps" usability problems in interface screenshots. It produces a structured HTML report with severity-ranked findings, positive observations, and a trap coverage matrix.

The repo is at: https://github.com/mmedlock1970/UITraps_Platform

## Architecture

```
frontend/ (React + TypeScript, port 5173)
    └── AnalyzerForm   →  user fills in context + uploads screenshots
    └── ReportViewer   →  renders the HTML report in a sandboxed iframe

backend/ (FastAPI + Python, port 8000)
    └── /api/ask       →  main endpoint (handles all analysis)
    └── src/analyzer.py   →  UITrapsAnalyzer class
    └── src/prompts.py    →  ALL LLM prompts (critical file)
    └── src/formatters.py →  HTML report renderer
    └── src/knowledge_base.py / knowledge_extractor.py  →  trap reference data
```

## Two-pass analysis pipeline

**Pass 1** — `claude-sonnet-4-6`  
Visual analysis of the uploaded screenshot. Produces a structured JSON report: confirmed findings (critical/moderate/minor), potential issues, positive observations, traps checked but not found.

**Pass 2** — `claude-haiku-4-5-20251001`  
Text-only enrichment pass. Takes the Pass 1 JSON + knowledge base chunks for each detected trap. Enriches findings with explanation, recommendations, and a summary narrative. Does NOT re-examine the screenshot.

These model names must not be changed.

## Knowledge base

Two versioned knowledge bases are pre-built and committed to the repo:
- `backend/data/trap_knowledge_base_v2.md` — current (27 traps, includes INCORRECT INFORMATION and POOR AESTHETIC)
- `backend/data/trap_knowledge_base_v1.md` — previous (26 traps, uses UNATTRACTIVE APPEARANCE instead)

Trap card example images are in `backend/data/book_images/v1/` and `backend/data/book_images/v2/`.

These files do not need to be regenerated. `BOOK_SOURCE_PATH` is only needed if the book source changes and the knowledge base needs to be rebuilt.

## Environment setup

1. Copy `backend/.env.example` to `backend/.env`
2. Set these values in `backend/.env`:

```
ANTHROPIC_API_KEY=sk-ant-...    ← your own Anthropic API key
DEV_MODE=true                   ← bypasses JWT auth for local dev
JWT_SECRET=<32+ char string>    ← any long random string works locally
```

`BOOK_SOURCE_PATH` is NOT required for normal operation — the knowledge base is already built.

## Starting the servers

Two terminals required:

```bash
# Terminal 1 — backend
cd backend
python app.py
# → runs on http://localhost:8000

# Terminal 2 — frontend
cd frontend
npm run dev
# → opens at http://localhost:5173
```

## Verifying the setup works

1. Open http://localhost:5173 — you should see the analysis form
2. Upload a screenshot, fill in users and goal, click Analyze
3. Backend logs should show:
   - `[UITraps] Pass 1 complete`
   - `[UITraps] Pass 2: using KB text chunks`
   - `[UITraps] Pass 2 complete`
4. A report should appear in the browser

If you see "Failed to fetch": confirm `DEV_MODE=true` is set in `backend/.env` and the backend is running.

## What must NOT be changed without syncing with Steve

These things are tightly coupled across both instances and must stay identical:

| File | Why it matters |
|---|---|
| `backend/src/prompts.py` | Defines how analysis works — any change affects output quality |
| `backend/src/formatters.py` | Defines the report HTML structure — frontend dark mode CSS depends on exact class names |
| `backend/data/trap_knowledge_base_v2.md` | The reference text for all 27 traps |
| Model names in `analyzer.py` lines 75-76 | Must stay `claude-sonnet-4-6` (Pass 1) and `claude-haiku-4-5-20251001` (Pass 2) |

Changes to any of these should be made in one place, committed, and pulled by the other person before continuing.

## Staying in sync

```bash
git pull   # always do this before starting work
git push   # always do this when done
```

If you modify `prompts.py` or `formatters.py`, tell Steve immediately — those changes affect his instance too.

## Key files at a glance

```
backend/
  app.py                    FastAPI app and all endpoints
  src/
    analyzer.py             UITrapsAnalyzer — orchestrates both passes
    prompts.py              ALL prompts (system, user, enrichment)
    formatters.py           HTML report generation + all CSS
    knowledge_base.py       Loads trap_knowledge_base_v*.md
    knowledge_extractor.py  Extracts trap text/images from book source
  data/
    trap_knowledge_base_v2.md   Current KB (27 traps)
    trap_knowledge_base_v1.md   Previous KB (26 traps)
    book_images/v1/ v2/         Trap card example images (in repo)

frontend/src/
  App.tsx                   Main app, routing between views
  components/
    AnalyzerForm.tsx        The analysis input form
    ReportViewer.tsx        Iframe-based report viewer + dark mode CSS
    ChatPanel.tsx           "Discuss Results" side panel
  api/
    client.ts               All fetch calls to the backend
    types.ts                Shared TypeScript types
```
