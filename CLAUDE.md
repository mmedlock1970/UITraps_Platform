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

## Shared memory
Project memory that persists across Claude sessions is in `.claude/memory/`. Read `MEMORY.md` there for the index.
