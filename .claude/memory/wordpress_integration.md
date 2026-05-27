---
name: wordpress-integration-requirements
description: Deferred requirements for embedding the tool into the UI Traps WordPress site
metadata:
  type: project
---

Three integration requirements to implement when building the WordPress plugin layer:

**1. Theme following**
Tool reads `data-theme="light|dark"` from `<html>` on mount and watches for changes via MutationObserver. Already implemented in `frontend/src/App.tsx`. WordPress dev just needs to ensure the site sets this attribute. Internal theme toggle hides automatically when the attribute is present.

**2. Mode-driven navigation**
Tool reads `data-uitraps-mode="analyze|chat"` from `#root` on mount. Already implemented in `frontend/src/App.tsx`. Tab row hides automatically — WordPress site navigation drives which interface loads. Tabs remain visible in standalone dev mode.

**3. Floating chat panel**
The "Ask a question" interface should be globally accessible as a floating panel (bottom-right button → slide-in overlay) injected by the WordPress plugin across all pages. The chat component is self-contained — WordPress dev builds the floating shell; tool's chat view just needs to be exported as a named standalone component. NOT YET IMPLEMENTED.

**Why:** Items 1 and 2 are complete. Item 3 is deferred until the WordPress plugin layer is being built.
