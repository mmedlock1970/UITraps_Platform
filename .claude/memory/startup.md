---
name: startup
description: How to start the dev servers for local development
metadata:
  type: project
---

Two servers required — start both before opening the app:

```
# Terminal 1 — backend API (port 8000)
cd backend
python app.py

# Terminal 2 — frontend dev server (port 5173)
cd frontend
npm run dev
```

Open http://localhost:5173
