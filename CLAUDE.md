# UI Traps Analyzer — Project Context for Claude Code

## What this project is
A web-based UI analysis tool that uses Claude to detect usability problems (UI Traps) in interface designs. Users upload screenshots, Figma URLs, PDFs, or flow diagram images and receive a structured analysis report identifying issues by trap type, severity, and location.

## Team
- **Steve** — builds the analyzer tool (this repo)
- **Michael** — project lead, coordinates integration
- **Ahmed** — WordPress developer handling the site integration

## How to start the dev servers
Two servers required — start both:
```
# Terminal 1 — backend (port 8000)
cd backend
python app.py

# Terminal 2 — frontend (port 5173)
cd frontend
npm run dev
```
Open http://localhost:5173

## Key architecture
- **Backend**: Python/FastAPI (`backend/app.py`) — handles file uploads, calls Claude API, returns HTML reports
- **Frontend**: React/TypeScript (`frontend/src/`) — form-based input, analysis progress, report viewer, chat interface
- **Analysis engine**: `backend/src/analyzer.py` — two-pass analysis (detect → enrich), flow diagram support
- **Prompts**: `backend/src/prompts.py` — all Claude prompt logic lives here
- **Schema**: `backend/src/schema.py` — JSON schema for structured Claude output
- **Formatter**: `backend/src/formatters.py` — converts structured output to HTML report

## WordPress integration (in progress)
The tool is being embedded into the UI Traps WordPress site. See `docs/integration/embedding-contract.md` for the full contract.

Key points:
- Tool is deployed via Railway (Michael has set this up)
- Tool is embedded in an `<iframe>` — parent page cannot touch the iframe's internal DOM
- Initial mode and theme are set via URL params: `?mode=analyze&theme=light`
- Live theme changes are sent via `postMessage({ type: 'uitraps-theme', theme: 'dark' })`
- JWT token is passed via `postMessage({ type: 'uitraps-token', token: '<jwt>' })` after iframe loads
- Tool fills its container height (`height: 100%`) — WordPress dev sets the iframe height

## Where feedback on trap analysis effectiveness goes

When Steve or Michael report that the analysis tool missed a trap, confused two traps, rated severity wrong, or otherwise misbehaved:

**UPDATE THE KNOWLEDGE BASE — NOT the system prompt.**

The file is: `backend/data/trap_knowledge_base_v2.md`
Specifically: the `## AI Detection Rules` section of the relevant trap chunk(s).

### What lives where

| Belongs in `trap_knowledge_base_v2.md` | Belongs in `backend/src/prompts.py` |
|---|---|
| When to flag a specific trap | Output field structure and schema |
| How confident to be (Tier 1/2/3) | `traps_checked_not_found` population rules |
| How to distinguish between similar traps | Whole-interface scan procedure (procedural steps only) |
| Severity calibration per trap | Severity label definitions (Critical/Moderate/Minor) |
| What counts as a confirmed vs. potential finding | Page-role awareness (entry vs. destination pages) |
| Testability conditions from static artifacts | Few-shot output format examples |
| Disambiguation rules (BAD PREDICTION vs INCORRECT INFORMATION, etc.) | Hedged language requirements |
| Per-trap detection criteria | Output requirements (summary_headline, region, etc.) |

### The test

Ask: "Is this about WHAT to conclude about a trap, or HOW to structure the output?"
- **WHAT to conclude** → KB (`## AI Detection Rules` in the relevant chunk)
- **HOW to structure output** → system prompt (`prompts.py`)

If the feedback is "it flagged X when it should have flagged Y" or "it gave high severity when it should be moderate" or "it missed this trap entirely" → that is always a KB edit.

## Shared memory
Project memory that persists across Claude sessions is in `.claude/memory/`. Read `MEMORY.md` there for the index.
