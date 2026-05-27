# UI Traps Analyzer — WordPress Embedding Contract

This document defines the interface between the UI Traps Analyzer tool and the WordPress site that embeds it. Both sides must honour this contract for the integration to work correctly.

---

## Hosting

The tool is built and deployed via Railway. The WordPress site loads it from the Railway URL.

- **Railway project:** TBD (Michael to confirm URL)
- **Deploy trigger:** Push to `master` branch → Railway rebuilds and redeploys automatically

---

## Container requirements (WordPress side)

WordPress must provide a container element for the tool to mount into:

```html
<div id="root" data-uitraps-mode="analyze"></div>
```

**Height:** The container must have an explicit height set. The tool fills `100%` of its container — it does not impose its own height.

```css
/* Example — adjust to account for your nav bar height */
#root {
  height: calc(100vh - 80px);
}
```

---

## Configuration attributes

Both attributes are optional. The tool falls back to standalone behavior (tabs visible, internal theme toggle visible) if neither is set.

### `data-uitraps-mode` (on `#root`)

Controls which interface loads. When set, the tab row is hidden — the parent site's navigation drives mode selection.

| Value | Effect |
|-------|--------|
| `analyze` | Loads the Trap analysis form |
| `chat` | Loads the Ask a question interface |
| *(absent)* | Both tabs visible, user can switch |

```html
<!-- Analyze page -->
<div id="root" data-uitraps-mode="analyze"></div>

<!-- Chat page -->
<div id="root" data-uitraps-mode="chat"></div>
```

### `data-theme` (on `<html>`)

Controls the tool's color theme. The tool watches this attribute for changes via MutationObserver, so it responds immediately when the user toggles the site's theme. When set, the tool's internal theme toggle is hidden.

```html
<html data-theme="dark">   <!-- dark mode -->
<html data-theme="light">  <!-- light mode -->
```

Most WordPress themes (GeneratePress, Kadence, etc.) already set this attribute — confirm the attribute name your theme uses.

---

## Floating chat panel (deferred)

The "Ask a question" interface will eventually be available as a globally accessible floating panel injected by the WordPress plugin. This is not yet implemented. When ready, the tool will export the chat view as a standalone component for the WordPress dev to wrap in a floating panel shell.

---

## Change process

Any change to this contract (new attributes, changed behavior, new deployment URL) should be:
1. Updated in this document
2. Communicated to both sides before deploying
