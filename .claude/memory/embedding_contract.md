---
name: embedding-contract
description: Technical contract between the tool and the WordPress site for embedding
metadata:
  type: project
---

See `docs/integration/embedding-contract.md` for the full human-readable contract.

**Summary for Claude:**
- Container height: WordPress sets an explicit height on the mount container; tool fills it with `height: 100%`
- Theme: `data-theme="light|dark"` on `<html>` — tool watches for changes via MutationObserver
- Mode: `data-uitraps-mode="analyze|chat"` on `#root` — locks view, hides tabs
- Deployment: Railway (Michael has configured this)
- All attributes are optional — tool falls back to standalone behavior if absent
