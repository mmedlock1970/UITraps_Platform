# UI Traps Helper — Claude Code Setup Instructions

Paste everything below this line into Claude Code to set up the project.

---

Please set up this project on my machine by doing the following steps in order. Ask me for any information you need as you go.

**1. Pull the latest code**

Run `git pull` to make sure everything is up to date.

**2. Set up the environment file**

Check whether `backend/.env` exists. If it does not, create it by copying `backend/.env.example`.

Then check whether each of these required values is present and non-empty in `backend/.env`:
- `ANTHROPIC_API_KEY`
- `DEV_MODE`
- `JWT_SECRET`

For any that are missing or still set to placeholder values:
- `ANTHROPIC_API_KEY` — ask me for my Anthropic API key and write it in
- `DEV_MODE` — set it to `true`
- `JWT_SECRET` — generate a random 64-character hex string and write it in (use Python: `python -c "import secrets; print(secrets.token_hex(32))"`)

Do not set or prompt for `BOOK_SOURCE_PATH` — it is not needed for normal operation. The knowledge base is already built and committed to the repo.

**3. Install backend dependencies**

```
cd backend
pip install -r requirements.txt
```

**4. Install frontend dependencies**

```
cd frontend
npm install
```

**5. Verify the backend starts cleanly**

Start the backend server and confirm it is listening on port 8000. Check the startup logs for any errors. If there are errors, fix them before continuing.

```
cd backend
python app.py
```

**6. Report what to do next**

Once setup is complete, tell me:
- That the backend is ready and how to start it (`cd backend && python app.py`)
- That the frontend is ready and how to start it (`cd frontend && npm run dev`)
- That the app will be accessible at http://localhost:5173

**Important — do not change these files**

The following files must stay exactly as they are in the repo unless Steve explicitly instructs a change. They are synchronized between two developers and any unilateral change will break the other person's setup:

- `backend/src/prompts.py` — all LLM prompts
- `backend/src/formatters.py` — HTML report structure and CSS
- `backend/data/trap_knowledge_base_v2.md` — the active knowledge base
- The model names in `backend/src/analyzer.py` (`claude-sonnet-4-6` and `claude-haiku-4-5-20251001`)
- The `_ANALYSIS_GROUPS` class variable and `_run_tenet_parallel` / `_merge_reports` methods in `backend/src/analyzer.py` — these implement the Thorough analysis mode (12 parallel tenet-focused calls) and the deduplication merge logic

**Key features to know about**

- **Thorough mode**: The form has a Standard | Thorough toggle in Card 5 (Analysis Scope). When Thorough is selected the backend runs 12 parallel Pass 1 API calls (one per tenet / sub-tenet group), merges and deduplicates the results, then runs a single Pass 2 enrichment pass. This eliminates inconsistency between repeated runs. The `thorough_mode` flag flows: form toggle → `client.ts` → `app.py` (`thorough_mode` form field) → `analyzer.py` `analyze_design(thorough_mode=True)`.
- **Report metadata**: Every report shows "Analysis coverage: Standard" or "Analysis coverage: Thorough" in the metrics block, positioned after Knowledge base and before Time to complete.
