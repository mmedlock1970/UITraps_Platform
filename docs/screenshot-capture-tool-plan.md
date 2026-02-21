# Task-Based Screenshot Capture Tool — Design Plan

**Last Updated:** 2026-02-16
**Status:** Design Complete, Ready for Implementation

---

## Executive Summary

A **desktop application** that enables UX researchers, designers, and PMs to capture task-based screenshot sequences for UI analysis. The tool prioritizes speed, simplicity, and staying out of the user's way during capture.

**Key Principle:** This is a **capture instrument**, not a design tool. Screenshots are raw observational data fed into downstream UI analysis.

---

## Product Principles (Non-Negotiable)

1. **Task-first, not screen-first**
   - A task exists before screenshots
   - One task at a time
   - Task language is user-centered ("Buy dog food") not system-centered

2. **Capture must be frictionless**
   - One obvious way to take screenshots (global hotkey)
   - No decision fatigue
   - Immediate visual confirmation after each capture

3. **Orientation over control**
   - Users always know: what task, how many steps captured, where latest screenshot went
   - Editing exists but is secondary

4. **No analysis during capture**
   - AI does not critique, suggest, or interrupt
   - AI behaves like a calm observer

5. **Means, not destination**
   - Screenshots are structured input, not artifacts to perfect
   - No features that imply polish, presentation, or reporting

---

## Mental Model

**Task** = A goal an end user would complete
*Examples: "Sign up for an account," "Find a specific product," "Delete a saved item"*

**Step** = One screen state encountered while completing that task
*Not named by the user. Just numbered: Step 1, Step 2, Step 3*

**Capture** = Taking a screenshot and adding it as the next step
*Via global hotkey — instant, no UI interaction required*

**User thinks:** *"I'm showing you what I see as I complete this task, screen by screen."*

---

## UX Flow

```
1. START
   User opens desktop app from system tray
   ↓
2. TASK SETUP
   Enters task name: "Sign up for an account"
   Clicks "Start Capturing"
   ↓
3. CAPTURE MODE
   App minimizes to tray, global hotkey activates (Ctrl+Shift+S)
   User completes task in target app, pressing hotkey at each step
   Toast confirms each capture: "✓ Step 3 captured"
   ↓
4. REVIEW CAPTURES
   User clicks tray icon to see captured steps (thumbnails)
   Can delete steps (⋮ menu) or add screenshots
   Clicks "Finish Task"
   ↓
5. ESTIMATE GATE
   "Analyzing 5 screenshots will take ~2 min, cost $0.15"
   [Keep Editing] [Analyze Task]
   ↓
6a. If KEEP EDITING: back to step 3
6b. If ANALYZE: analysis runs → report viewer opens
   ↓
7. COMPLETE
   Report displayed, capture cleared
   App returns to idle state
   Ready for next task
```

---

## Design Decisions

### Platform: Desktop Application (Not Browser Extension)

**Why:**
- Analyze any UI: web apps, desktop apps, design tools, mobile (mirrored)
- Not limited to browser tabs
- Global hotkey works system-wide
- Better for offline use

**Trade-offs:**
- Requires installation (not 1-click extension install)
- Need OS-specific permissions
- More complex distribution

### Screenshot Scope: Active Window (Default) + Full Screen (Optional)

**Default: Active Window Only**

**Captures:** The currently focused application window
**Excludes:** Desktop background, taskbar, other monitors, capture tool itself

**Pros:**
- Clean screenshots (no OS chrome)
- Automatically excludes capture tool window
- Focuses on UI being analyzed
- Smaller file sizes
- Works for 95% of use cases

**Full Screen Toggle (Settings Option):**

User can enable: ☐ Capture full screen instead of active window

**When needed:**
- Desktop-level workflows spanning multiple windows
- Analyzing OS-level interactions
- Capturing context across applications

**Implementation note:**
For full-screen capture, app must hide window before screenshot (0.1s delay)

### One Task at a Time (No Queue)

**Implications:**
- No saved tasks list
- No task management UI
- Linear flow: capture → estimate → analyze → done
- After analysis or cancel, return to clean slate

**On cancel at estimate gate:**
"Discard this capture?" → [Keep Editing] [Discard]
If discard: all screenshots deleted, return to idle

### Hotkey-Driven Capture

**Default:** `Ctrl+Shift+S` (customizable in settings)

**Why hotkey over click:**
- Keeps hands on keyboard/mouse for task completion
- Fastest possible interaction
- No UI to hunt for
- Muscle memory builds quickly

**Conflict detection:**
- App checks if hotkey is already in use
- Warns user on startup
- Allows customization

---

## UI Specifications

### 1. Idle State (System Tray)

```
┌─────────────────────────────┐
│ UITraps Capture             │
├─────────────────────────────┤
│ What task are you capturing?│
│ ┌─────────────────────────┐ │
│ │ [task name input]       │ │
│ └─────────────────────────┘ │
│                             │
│      [Start Capturing]      │
│                             │
│ ⌨  Press Ctrl+Shift+S to    │
│    capture screenshots      │
└─────────────────────────────┘
```

### 2. Capture Confirmation (Toast)

Appears top-right, 2 seconds, auto-dismiss:

```
┌──────────────────┐
│ ✓ Step 3 captured│
└──────────────────┘
```

### 3. Review Screen

```
┌─────────────────────────────────┐
│ Task: Sign up for an account    │
├─────────────────────────────────┤
│ Step 1  [thumbnail ~120px]  ⋮  │
│ Step 2  [thumbnail]          ⋮  │
│ Step 3  [thumbnail]          ⋮  │
│ Step 4  [thumbnail]          ⋮  │
│ Step 5  [thumbnail]          ⋮  │
│                                 │
│ [+ Add Screenshot] [Finish]     │
│                                 │
│ ⌨ Ctrl+Shift+S to capture       │
└─────────────────────────────────┘
```

**⋮ menu per step:** Single option: "Delete"

**Thumbnail interaction:**
- Hover: slight enlarge (no modal)
- Click: no action (avoid lightbox friction)

### 4. Estimate Screen

```
┌─────────────────────────────────────┐
│ Task: Sign up for an account        │
│                                     │
│ 5 screenshots captured              │
│                                     │
│ ┌─────────────────────────────┐    │
│ │ Estimated analysis cost     │    │
│ │ Time: ~2 minutes            │    │
│ │ Cost: $0.15                 │    │
│ └─────────────────────────────┘    │
│                                     │
│ [← Keep Editing]  [Analyze Task →] │
└─────────────────────────────────────┘
```

---

## Editing Model

### Before "Finish Task": Lightweight Iteration

**Delete a step:**
1. Click ⋮ next to step
2. Click "Delete"
3. Confirm: "Delete Step 3?" [Cancel] [Delete]
4. Remaining steps renumber automatically

**Add a screenshot:**
1. Navigate to missed screen
2. Press global hotkey OR click "[+ Add Screenshot]" in app
3. New step added at bottom of list

**Why bottom-only insertion:**
- Avoids "insert after Step X" complexity
- Users can delete and re-capture if order wrong
- Hotkey is fast enough for re-capture

**No reordering:** No drag-and-drop (adds complexity, rarely needed)

### After "Finish Task": Finalization Phase

User can still click "Keep Editing" from estimate screen to return to capture mode.

### After "Analyze Task": No Editing

Analysis has run — capture is locked.

---

## Technical Architecture

### Recommended Tech Stack (MVP)

**Platform:** Electron
**Why:** Fastest to build, cross-platform, integrates with existing React frontend

**Components:**
- **Main Process:** Global hotkey listener, screenshot capture, window management
- **Renderer Process:** React UI (task input, step visualization, estimate screen)
- **IPC:** Communication between main and renderer

**Key APIs:**
- `electron.globalShortcut` — system-wide hotkey
- `desktopCapturer` or native module — screenshot capture
- `BrowserWindow` — app window management (hide/show during capture)

### Screenshot Capture Implementation

**Active Window Capture:**
- Windows: Win32 `GetForegroundWindow` + `BitBlt`
- macOS: `CGWindowListCreateImage` with active window ID
- Linux: X11 active window + `scrot` or `maim`

**Full Screen Capture:**
- Electron `desktopCapturer.getSources({ types: ['screen'] })`
- Hide app window 100ms before capture
- Restore after capture complete

### Data Flow

```
User presses hotkey
  ↓
Main process captures active window/screen
  ↓
Screenshot saved to temp storage (base64 or file)
  ↓
IPC message sent to renderer: "screenshot_captured"
  ↓
Renderer adds to step list, shows toast
  ↓
On "Finish Task": screenshots sent to backend API
  ↓
Backend returns estimate
  ↓
On "Analyze": backend processes, returns report
  ↓
Renderer displays report, clears temp storage
```

### Storage Strategy

**During capture:**
- Screenshots stored in temp directory
- Task metadata (name, step count) in memory

**After analysis:**
- Report saved to localStorage (last 10, per existing pattern)
- Screenshots can be discarded (no longer needed)
- Optional: save screenshots alongside report for re-analysis

**On cancel:**
- All temp files deleted
- Memory cleared

---

## Implementation Phases

### Phase 1: Core Capture (MVP)

**Goal:** Capture task screenshots with global hotkey

**Deliverables:**
- [ ] Desktop app shell (Electron)
- [ ] System tray icon + basic UI
- [ ] Task name input + "Start Capturing" flow
- [ ] Global hotkey registration (`Ctrl+Shift+S`)
- [ ] Active window screenshot capture
- [ ] Toast notification on capture
- [ ] Step thumbnail visualization
- [ ] "Finish Task" → hand off to estimate screen

**Success criteria:**
- User can capture 5-step task in under 1 minute
- No crashes, no missed hotkey presses
- Thumbnails display correctly

### Phase 2: Estimate Integration

**Goal:** Connect to existing backend estimate endpoint

**Deliverables:**
- [ ] Send screenshots + task name to `/estimate` endpoint
- [ ] Display estimate (time/cost)
- [ ] "Keep Editing" / "Analyze Task" buttons
- [ ] Handle cancel → discard flow
- [ ] Integration with analysis API

**Success criteria:**
- Estimate appears within 2 seconds
- User can approve and see analysis progress
- Report displays correctly after analysis

### Phase 3: Editing & Polish

**Goal:** Add step deletion, screenshot addition, edge case handling

**Deliverables:**
- [ ] Delete step (⋮ menu)
- [ ] Add screenshot (button + hotkey)
- [ ] Step renumbering on delete
- [ ] Hotkey conflict detection
- [ ] Customizable hotkey in settings
- [ ] Full screen toggle (settings)
- [ ] Error handling (screenshot fails, API errors)

**Success criteria:**
- User can fix mistakes without restarting
- No UX dead ends
- Clear error messages

### Phase 4: Cross-Platform & Distribution

**Goal:** Ship to users

**Deliverables:**
- [ ] Windows build + installer
- [ ] macOS build + .dmg
- [ ] Auto-update mechanism
- [ ] Crash reporting
- [ ] Usage analytics (optional)
- [ ] User documentation

**Success criteria:**
- Installable on Windows/macOS without developer tools
- Updates deploy automatically

---

## Open Questions

### 1. Do users need access to raw screenshots after analysis?

**Current assumption:** No — screenshots are ephemeral, only report is saved

**If yes:** Need to implement screenshot archiving alongside reports

### 2. Should app window auto-minimize on "Start Capturing"?

**Option A:** Auto-minimize (cleaner, less distraction)
**Option B:** Stay open (user can see steps accumulate in real-time)
**Option C:** User preference in settings

### 3. What happens if user captures 0 steps?

**Scenario:** User clicks "Start Capturing" then immediately "Finish Task"

**Options:**
- Block "Finish Task" until at least 1 step captured
- Allow, but show error on estimate screen
- Allow, but warn: "No screenshots captured. Add at least one step."

### 4. Mobile app analysis workflow?

**Scenario:** User wants to analyze mobile app

**Options:**
- Use screen mirroring (iOS: QuickTime, Android: scrcpy) → capture mirrored window
- Future: mobile app companion that sends screenshots to desktop
- Out of scope for MVP

---

## Success Metrics (Post-Launch)

**Adoption:**
- Downloads / installs
- Active users (weekly)

**Engagement:**
- Tasks captured per user
- Average steps per task
- Time from start capture to analysis complete

**Quality:**
- % of tasks that reach analysis (vs. cancelled)
- % of tasks with editing (delete/add steps)
- Crash rate

**Efficiency:**
- Average time to capture 5-step task
- Hotkey response latency

---

## What This Design Explicitly Avoids

❌ Automatic screenshot detection (breaks user control)
❌ AI-suggested step names (adds latency, breaks trust)
❌ Annotation/markup tools (scope creep)
❌ Multi-task capture queue (cognitive overload)
❌ Step reordering/drag-and-drop (unnecessary complexity)
❌ Cloud sync during capture (adds failure modes)
❌ Comparison views (analysis feature, not capture)
❌ Region selection for screenshots (high friction)
❌ Collaboration features (out of scope)

---

## Next Steps

1. **Validate tech stack choice** (Electron vs. Tauri vs. native)
2. **Set up Electron boilerplate** (if Electron chosen)
3. **Implement Phase 1 MVP** (core capture flow)
4. **User test with 3-5 target users** (before Phase 2)
5. **Iterate based on feedback**
6. **Proceed to Phase 2** (estimate integration)

---

## Appendix: User Scenarios

### Scenario 1: Web App Sign-Up Flow

1. User opens capture tool, enters "Sign up for an account"
2. Clicks "Start Capturing", app minimizes
3. User opens Chrome, navigates to example.com/signup
4. Presses `Ctrl+Shift+S` → Step 1 captured (signup page)
5. Fills email field, presses `Ctrl+Shift+S` → Step 2 captured
6. Clicks "Create Account", presses `Ctrl+Shift+S` → Step 3 captured (loading)
7. Sees confirmation, presses `Ctrl+Shift+S` → Step 4 captured
8. Opens capture tool, clicks "Finish Task"
9. Sees estimate: "4 screenshots, ~1.5 min, $0.12"
10. Clicks "Analyze Task"
11. Report opens, shows 3 UI traps found

### Scenario 2: Desktop App Task (Figma)

1. User enters "Create a new frame in Figma"
2. Opens Figma desktop app
3. Captures: File menu → New file dialog → Blank canvas → Frame tool selected → Frame created
4. 5 steps captured, analyzes, sees report

### Scenario 3: Mistake Recovery

1. User capturing e-commerce checkout flow
2. Accidentally presses `Ctrl+Shift+S` during transition (blurry screen)
3. Opens capture tool, clicks ⋮ next to Step 3, deletes it
4. Continues capture, finishes task

### Scenario 4: Cancel Before Analysis

1. User captures 8 steps
2. Sees estimate: "$0.40"
3. Clicks "Keep Editing", realizes they captured wrong task
4. Clicks tray icon → system menu → "Discard capture"
5. Confirms, returns to idle, starts new task

---

**End of Plan**
