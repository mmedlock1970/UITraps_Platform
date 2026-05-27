# UI Traps Analyzer — WordPress Embedding Contract

This document defines the interface between the UI Traps Analyzer tool and the WordPress site that embeds it via `<iframe>`. Both sides must honour this contract for the integration to work correctly.

---

## Hosting

The tool is built and deployed via Railway. The WordPress plugin embeds it in an `<iframe>`.

- **Backend URL:** https://uitrapsplatform-production.up.railway.app
- **Frontend URL:** TBD (Netlify/Vercel — Michael to confirm)
- **Deploy trigger:** Push to `master` branch → Railway/Netlify/Vercel rebuilds automatically

---

## Embedding (WordPress side)

```html
<!-- Analyze page -->
<iframe src="https://<frontend-url>/?mode=analyze&theme=light" ...></iframe>

<!-- Chat page -->
<iframe src="https://<frontend-url>/?mode=chat&theme=light" ...></iframe>
```

**Height:** The iframe must have an explicit height. The tool fills `100%` of its container.

```css
iframe {
  width: 100%;
  height: calc(100vh - 80px); /* adjust for WordPress nav height */
  border: none;
}
```

---

## Configuration — URL parameters

Both parameters are optional. The tool falls back to standalone behavior (tabs visible, internal theme toggle visible) if neither is provided.

### `mode`

Controls which interface loads. When set, the tab row is hidden.

| Value | Effect |
|-------|--------|
| `analyze` | Loads the Trap analysis form |
| `chat` | Loads the Ask a question interface |
| *(absent)* | Both tabs visible, user can switch |

### `theme`

Sets the initial color theme. When set, the internal theme toggle is hidden.

| Value | Effect |
|-------|--------|
| `light` | Light mode |
| `dark` | Dark mode |
| *(absent)* | Light mode, internal toggle visible |

---

## Theme — live updates via postMessage

When the user toggles the WordPress site's theme, the parent page notifies the iframe:

```javascript
// WordPress parent page — send when theme changes
document.querySelector('iframe').contentWindow.postMessage(
  { type: 'uitraps-theme', theme: 'dark' }, // or 'light'
  '*'
);
```

The tool listens for this message and updates its theme immediately. The internal toggle stays hidden once any external theme signal has been received.

---

## Auth — JWT via postMessage

The WordPress plugin issues a JWT token and passes it to the iframe on load:

```javascript
// WordPress plugin — send after iframe loads
iframeEl.addEventListener('load', () => {
  iframeEl.contentWindow.postMessage(
    { type: 'uitraps-token', token: '<jwt>' },
    '*'
  );
});
```

The `userId` embedded in the JWT is the permanent WordPress user ID used as the key for subscriptions and reports.

---

## Floating chat panel (deferred)

The "Ask a question" interface will eventually be available as a globally accessible floating panel injected by the WordPress plugin. Not yet implemented.

---

## Change process

Any change to this contract should be:
1. Updated in this document
2. Communicated to both sides before deploying
