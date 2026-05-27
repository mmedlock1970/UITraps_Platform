---
name: architecture
description: Full system architecture and key integration details from Michael's briefing
metadata:
  type: project
---

## System architecture

```
WordPress (uitraps.com)
└── WordPress plugin (issues JWT tokens for logged-in users)
└── <iframe> embeds the React frontend
React Frontend (Vite/TypeScript)
└── deployed separately (Netlify/Vercel — TBD)
└── calls → Railway backend API
Railway Backend (FastAPI/Python)
└── auto-deploys from GitHub master branch, /backend folder
└── URL: https://uitrapsplatform-production.up.railway.app
└── SQLite database (Railway disk)
└── calls → Anthropic Claude API
└── calls → Figma API (optional)
```

## Auth flow
1. WordPress plugin issues a JWT token when user logs in
2. React frontend receives token via `window.postMessage` from WordPress parent page
3. All Railway API calls include `Authorization: Bearer <token>`
4. Railway validates token using `JWT_SECRET` (must match WordPress wp-config.php)
5. `userId` = permanent WordPress user ID — key for subscriptions and reports

## Dev mode
- `DEV_MODE=true` in Railway env bypasses JWT auth
- Frontend auto-enables dev mode on localhost/127.0.0.1

## Key endpoints
- `POST /api/webhook/subscription` — WooCommerce subscription lifecycle (secured with X-Webhook-Secret)
- `POST /api/webhook/tokens` — WooCommerce bonus token purchases (secured with X-Webhook-Secret)
- `GET /api/user/usage` — user's token balance (JWT required)
- `GET /reports` — user's past reports (JWT required, filtered per user)
- `GET /health` — Railway health check on startup

## Ahmed's WooCommerce integration (in progress)
Ahmed is connecting WooCommerce subscription events to Railway webhooks. Currently debugging a secret mismatch. Both webhook endpoints are secured with `X-Webhook-Secret` header.

## Key files
- `backend/app.py` — all API endpoints
- `backend/src/analyzer.py` — core AI analysis. **Lines 75-76 have model names — do NOT change without checking with Michael**
- `backend/src/subscription_service.py` — subscription/token logic
- `backend/src/database.py` — database models (UserSubscription table)
- `backend/src/prompts.py` — analysis prompts
- `frontend/src/hooks/useUnifiedInput.ts` — central frontend orchestrator

## Environment variables (Railway — never commit to repo)
- `ANTHROPIC_API_KEY` — Claude API key
- `JWT_SECRET` — must match WordPress wp-config.php
- `WEBHOOK_SECRET` — shared secret for Ahmed's WooCommerce webhooks
- `FIGMA_TOKEN` — Figma API token
- `MONTHLY_LIMIT` — default analyses per user per month

## ⚠️ Iframe embedding changes the data attribute contract
The React app is embedded in an **iframe**. The parent WordPress page cannot directly set attributes on the iframe's internal `<html>` element. Current implementation reads `data-theme` from `document.documentElement` (wrong for iframe) and `data-uitraps-mode` from `#root` (also inaccessible from parent). 

**Fix needed:**
- Mode → pass as URL parameter: `src="https://app.uitraps.com/?mode=analyze"`
- Theme → pass via `postMessage` from parent to iframe
See [[embedding-contract]] for the corrected contract.
