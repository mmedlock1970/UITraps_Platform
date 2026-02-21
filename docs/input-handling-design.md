# UITraps — Input Handling Design

**Last Updated:** 2026-02-16
**Status:** Design Complete, Ready for Implementation

---

## Guiding Principle

**When in doubt, fall back to the four-choice Options Widget.**
Ambiguous input should never dead-end the user — always offer a clear path forward.

---

## The Options Widget

Appears whenever the system detects analysis intent but isn't sure which type, or when the user is clearly starting something new.

```
┌─────────────────────────────────────────────────┐
│ How would you like to analyze your UI?          │
├─────────────────────────────────────────────────┤
│ ○ Describe the task here                        │
│ ○ Drop screenshots you have already taken       │
│ ○ Help me capture step by step screenshots      │
│   of the task                                   │
│ ○ Other (just chat)                             │
└─────────────────────────────────────────────────┘
```

---

## Complete Input → Response Map

### 1. Knowledge Question
**Examples:** "What is the Invisible Element trap?" / "What's the difference between trap X and trap Y?"
**Response:** RAG chat response. No analysis flow triggered.

---

### 2. Describes a UI Issue in Writing
**Examples:** "The checkout button is really hard to find" / "Users keep missing the error message"
**Response:** Trap analysis via RAG chat. No analysis pipeline triggered.

---

### 3. Analysis Intent, No Files
**Examples:** "Analyze this signup flow" / "I want to check a user journey" / "I have a design to check"
**Response:** Show Options Widget.

---

### 4. "Start a New Analysis"
**Response:** Show Options Menu:
- Capture a task step by step (screenshots)
- Upload files I already have (screenshots, PDFs)
- Analyze a Figma design
- Ask a question about UI

---

### 5. Website URL Pasted
**Examples:** `https://amazon.com/checkout`
**Response:**
> "I can't automatically crawl websites due to bot protection. Instead, I'll guide you to capture screenshots of the flow step by step."

→ Show Options Widget

**Note:** Web crawler code preserved in backend but disabled from user-facing perspective. Can be reinstated later.

---

### 6. Figma URL
**Response:** Existing Figma analysis flow. Unchanged.

---

### 7. Single Screenshot Dropped
**Response:**
- Accept the screenshot
- Ask context questions (see Context Questions section)
- Ask: "Are there other screenshots that are part of this flow?"

---

### 8. Multiple Screenshots Dropped
**Response:**
- Accept all recognizable files
- Show drag-to-reorder UI: "Are these in order? Drag to rearrange if needed."
  - Conversational ordering available as fallback and additional option
- Ask context questions

---

### 9. PDF Dropped
**Response:** Existing PDF analysis flow. Unchanged.

---

### 10. Video File Dropped (.mp4, .mov, etc.)
**Response:**
> "I can't analyze video directly yet. Please take screenshots of the key steps and drop those in instead."

**Status:** ⏸ PARKED — Video frame extraction (auto-extract frames, let user adjust) is the desired end state but is not being built now. Revisit when core capture flow is stable.

**Desired future behavior (when revisited):**
- Extract key frames automatically from video
- Present frames as steps in the timeline
- Let user delete/reorder frames before analyzing

---

### 11. Unrecognized File Type
**Examples:** .docx, .sketch, .xlsx, .zip
**Response:**
> "I'm not able to analyze [filename.docx]. I can work with screenshots (PNG, JPG), PDFs, and video files. Please drop one of those instead."

---

### 12. Mixed Files (Recognizable + Unrecognizable)
**Examples:** 2 screenshots + 1 .docx file
**Response:**
- Announce which files will be analyzed and which can't be processed:
  > "I can analyze these: screenshot1.png, screenshot2.png. I'm not able to process: notes.docx."
- Proceed with recognizable files
- Ask: Are these in any order? Anything else I should know?

---

### 13. Mixed Files (All Recognizable — Screenshots + PDF)
**Response:**
- Analyze together, no issue
- Ask: Are these in any order? Anything else I should know?

---

### 14. Hosted Image or PDF URL
**Examples:** `https://imgur.com/abc.png` / `https://example.com/design.pdf`
**Response:** Fetch and treat as file upload. Same flow as dropping that file.

---

### 15. Loom / YouTube / Unrecognized URL
**Examples:** `https://loom.com/share/abc` / `https://youtube.com/watch?v=xyz`
**Response:** Treat exactly like a website URL (#5):
> "I can't process that link directly. I'll guide you to capture screenshots of the flow instead."

→ Show Options Widget

---

### 16. "What can you do?" / "How does this work?"
**Response:** Capability summary — clear, not a trap analysis. Includes:
- What UITraps analyzes (UI flows, screenshots, Figma designs)
- How to start (describe a task, upload files, step-by-step capture)
- What kind of questions it can answer
- Link/reference to Options Widget for next step

---

### 17. "Can I see my past analyses?"
**Response:**
> "Your past analyses are saved — click 'Past Analyses' in the menu to view them."

→ Route to Past Analyses view.

---

### 18. Ambiguous Single Word or Unclear Reply
**Examples:** "yes", "ok", "sure", "hmm", "maybe"
**Response:**
- If clearly in response to a question the system just asked → treat as part of that conversation and reply appropriately
- If no clear context → fall back to Options Widget

---

### 19. Off-Topic Query
**Examples:** "What's the weather?" / "Write me a poem"
**Response:**
> "I'm specialized in UI analysis and usability evaluation. Want me to help you analyze an interface instead?"

---

### 20. Pricing / Meta Question
**Examples:** "How much does an analysis cost?" / "What does this service do?" / "How long does analysis take?"
**Response:** Informational RAG response. Treated like any other knowledge question — can answer anything about the service, pricing, website, or capabilities.

---

### 21. Post-Analysis Follow-Up
**Examples:** "What does the Effectively Invisible Element finding mean?" / "Tell me more about finding 3"
**Response:** RAG chat response in the context of the report. No new analysis triggered.

---

### 22. "Analyze This Again"
**Response:** Re-run analysis against the same screenshots/files. Same flow as original analysis.

---

### 23. Revised Design Upload
**Examples:** "I fixed the button — is it better now?" + new screenshot
**Response:** Treat as new analysis. Accept file, ask context questions, proceed to estimate.

---

### 24. Files Dropped Mid-Capture Flow
**Response:**
- If recognizable file type (image, PDF) → add to current capture as next step
- If unrecognized → error message (#11), continue capture

---

### 25. URL Pasted Mid-Capture Flow
**Response:**
> "I can't add a URL to your current capture. To include this screen, take a screenshot of it and paste it here."

---

### 26. Targeted Trap Request
**Examples:** "Can you check this specifically for Hidden Costs?" / "I just want to know about Roach Motel patterns"
**Response:** Support targeted trap analysis. Accept files/screenshots, run analysis focused on specified trap(s). This is a supported feature.

*Note: Implementation detail TBD — does this modify the analysis prompt, or is it a post-analysis filter?*

---

## Context Questions

**Required for ALL analysis types** — task capture, file upload, Figma, targeted trap. No exceptions.
Asked after files/screenshots are collected, before the estimate screen.

*Current context question set applies. No changes to this flow.*

---

## Scale & Limits

### Screenshot Count Per Task

| Count | Behavior |
|-------|----------|
| 1–10 | No friction. Proceed normally. |
| 11–15 | Soft warning: "That's a long flow. Are all these part of the same task? Splitting into smaller tasks gives more focused results." User can still continue. |
| 16+ | Hard limit: "We can analyze up to 15 screenshots per task. Please remove some steps or split this into separate tasks for better results." |

**Hard limit: 15 screenshots per task.**

---

### File Size

- Auto-compress/resize screenshots on the frontend before uploading
- Target: max 1–2MB per image after compression
- User does not see this happening
- No warning unless compression fails

---

### Running Cost Estimate

- Shown in the capture UI as screenshots are added
- Updates live with each screenshot added or removed
- Example: "3 screenshots added — estimated cost: ~$0.09"
- Each analysis is independent (no cumulative session tracking)

---

### Analysis Time Expectations

Shown on estimate screen:

| Screenshots | Expected Time |
|-------------|---------------|
| 1–5 | ~1 minute |
| 6–10 | ~2 minutes |
| 11–15 | ~3–4 minutes |

---

## What's Deprecated (User-Facing)

| Feature | Status |
|---------|--------|
| Web crawler / website URL analysis | Disabled from user perspective. Code preserved in backend. |

---

## What's Unchanged

| Feature | Status |
|---------|--------|
| Figma analysis | Unchanged |
| PDF analysis | Unchanged |
| File upload (screenshots) | Unchanged |
| RAG chat / knowledge questions | Unchanged |
| Context questions before estimate | Unchanged |
| Estimate flow | Unchanged |
| ReportViewer | Unchanged |
| Past Analyses | Unchanged |

---

## Implementation Notes

### Priority Order
1. Options Widget (needed everywhere)
2. Input detection / routing logic (chat, files, URLs)
3. Web crawler deprecation message
4. Task capture flow (see screenshot-capture-plan-web.md)
5. Drag-to-reorder for multiple screenshots
6. Running cost estimate in capture UI
7. Video frame extraction (investigate complexity first)
8. Targeted trap analysis

### Key Files to Modify
- `frontend/src/hooks/useUnifiedInput.ts` — central routing logic
- `frontend/src/hooks/useChat.ts` — message handling
- `backend/src/web_crawler.py` — comment out / disable endpoints
- `backend/app.py` — disable web crawler routes

---

**End of Document**
