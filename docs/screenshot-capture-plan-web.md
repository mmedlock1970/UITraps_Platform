# Task-Based Screenshot Capture — Web App Plan

**Last Updated:** 2026-02-16
**Status:** Ready for Implementation
**Approach:** Web app with manual paste/drop (zero installation)

---

## Executive Summary

Add task-based screenshot capture to the existing UITraps web app. Users manually take screenshots with their OS tools and paste them into a timeline. Zero installation required.

**Key Decision:** Prioritize **zero installation friction** over **automated capture**. Users can try this immediately without downloading anything.

---

## User Flow

```
1. User clicks "New Task Analysis" (or similar) in existing app
   ↓
2. Enters task name: "Sign up for an account"
   ↓
3. Clicks "Start Capturing"
   ↓
4. CAPTURE SCREEN appears with instructions:
   "Take screenshots using your OS tool, then paste them here"

   Shows hotkeys for each OS:
   • Windows: Win+Shift+S
   • macOS: Cmd+Shift+4 or Cmd+Shift+5
   • Linux: PrtScn or Shift+PrtScn
   ↓
5. User takes screenshot with OS tool
   ↓
6. User clicks in paste zone and presses Ctrl+V
   (or drags screenshot file into drop zone)
   ↓
7. Screenshot appears as "Step 1" in timeline
   ↓
8. Repeat steps 5-7 for each screen in the task
   ↓
9. User clicks "Finish Task"
   ↓
10. ESTIMATE screen (existing flow)
    Shows: "5 screenshots, ~2 min, $0.15"
    [Keep Editing] [Analyze Task]
   ↓
11. If Analyze → existing analysis flow
    If Keep Editing → back to capture screen
```

---

## UI Components

### 1. Task Setup Screen

```
┌─────────────────────────────────────────┐
│  Analyze a Task                         │
├─────────────────────────────────────────┤
│                                         │
│  What task are you capturing?          │
│  ┌────────────────────────────────┐    │
│  │ e.g., Sign up for an account   │    │
│  └────────────────────────────────┘    │
│                                         │
│           [Start Capturing]             │
│                                         │
└─────────────────────────────────────────┘
```

**Implementation:**
- Simple input field + button
- Validates task name is not empty
- Transitions to Capture Screen on submit

---

### 2. Capture Screen (Empty State)

```
┌─────────────────────────────────────────────────┐
│  Task: Sign up for an account          [Cancel] │
├─────────────────────────────────────────────────┤
│                                                 │
│  Take screenshots and paste them here           │
│                                                 │
│  Use your OS screenshot tool:                   │
│  • Windows: Win+Shift+S                         │
│  • macOS: Cmd+Shift+4                           │
│  • Linux: PrtScn                                │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │                                           │ │
│  │        Press Ctrl+V to paste             │ │
│  │        or drag files here                │ │
│  │                                           │ │
│  │        [or click to select files]        │ │
│  │                                           │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Implementation:**
- Large drop zone (whole screen is drop target for better UX)
- Listens for `paste` events (Ctrl+V)
- Listens for `drop` events (drag files)
- Click opens file picker as fallback
- Accepts: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`

---

### 3. Capture Screen (With Steps)

```
┌─────────────────────────────────────────────────┐
│  Task: Sign up for an account          [Cancel] │
├─────────────────────────────────────────────────┤
│                                                 │
│  Step 1                                    ⋮    │
│  ┌─────────────────────┐                       │
│  │   [thumbnail]       │                       │
│  │    ~200px wide      │                       │
│  └─────────────────────┘                       │
│                                                 │
│  Step 2                                    ⋮    │
│  ┌─────────────────────┐                       │
│  │   [thumbnail]       │                       │
│  └─────────────────────┘                       │
│                                                 │
│  Step 3                                    ⋮    │
│  ┌─────────────────────┐                       │
│  │   [thumbnail]       │                       │
│  └─────────────────────┘                       │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │  Paste or drop next screenshot (Ctrl+V)  │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│              [Finish Task]                      │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Design notes:**
- Steps displayed as vertical timeline (chronological)
- Thumbnails large enough to recognize (~200px wide, auto height)
- ⋮ menu per step: "Delete" | "View Full Size"
- Drop zone always visible at bottom
- "Finish Task" button appears after first screenshot added

---

### 4. Step Menu (⋮)

Click ⋮ next to any step:
```
┌─────────────────┐
│ View Full Size  │
│ Delete Step     │
└─────────────────┘
```

**View Full Size:**
- Opens modal/lightbox with full resolution image
- [Close] button to return

**Delete Step:**
- Confirmation: "Delete Step 2?" [Cancel] [Delete]
- After delete, remaining steps renumber automatically
- If deleting only step, return to empty state

---

### 5. Estimate Screen (Existing, Minor Tweaks)

```
┌─────────────────────────────────────────┐
│ Task: Sign up for an account            │
│                                         │
│ 3 screenshots captured                  │
│                                         │
│ ┌─────────────────────────────┐        │
│ │ Estimated analysis cost     │        │
│ │ Time: ~1.5 minutes          │        │
│ │ Cost: $0.12                 │        │
│ └─────────────────────────────┘        │
│                                         │
│ [← Keep Editing]  [Analyze Task →]     │
└─────────────────────────────────────────┘
```

**Changes from existing estimate flow:**
- Add "Keep Editing" button (returns to Capture Screen)
- Show count of screenshots instead of just task name

---

## Technical Implementation

### Frontend (React Component Structure)

```
TaskCapture/
├── TaskSetup.tsx          // Task name input
├── CaptureScreen.tsx      // Main capture interface
├── StepTimeline.tsx       // List of captured steps
├── StepCard.tsx           // Individual step with thumbnail
├── DropZone.tsx           // Paste/drop handler
└── useTaskCapture.ts      // State management hook
```

### Key Logic: Paste & Drop Handlers

```typescript
// useTaskCapture.ts
const [steps, setSteps] = useState<Screenshot[]>([]);
const [taskName, setTaskName] = useState('');

const addScreenshot = (file: File) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    const newStep: Screenshot = {
      id: crypto.randomUUID(),
      stepNumber: steps.length + 1,
      imageData: e.target?.result as string,
      fileName: file.name,
      timestamp: Date.now()
    };
    setSteps([...steps, newStep]);
  };
  reader.readAsDataURL(file);
};

const handlePaste = (e: ClipboardEvent) => {
  const items = e.clipboardData?.items;
  if (!items) return;

  for (let item of items) {
    if (item.type.startsWith('image/')) {
      const file = item.getAsFile();
      if (file) addScreenshot(file);
    }
  }
};

const handleDrop = (e: DragEvent) => {
  e.preventDefault();
  const files = Array.from(e.dataTransfer?.files || []);

  files.forEach(file => {
    if (file.type.startsWith('image/')) {
      addScreenshot(file);
    }
  });
};

const deleteStep = (id: string) => {
  setSteps(prev => {
    const filtered = prev.filter(s => s.id !== id);
    // Renumber steps
    return filtered.map((step, idx) => ({
      ...step,
      stepNumber: idx + 1
    }));
  });
};
```

### Integration with Existing Backend

**Existing estimate endpoints:**
- `/estimate` (for file uploads)
- `/estimate-figma` (for Figma URLs)
- `/estimate-url` (for website URLs)

**New endpoint needed:**
```python
@app.post("/estimate-task")
async def estimate_task(
    task_name: str = Form(...),
    screenshots: List[UploadFile] = File(...)
):
    """
    Estimate cost for task-based screenshot analysis.
    Similar to /estimate but accepts task name + multiple screenshots.
    """
    # Reuse existing estimation logic
    # Return same format: { time_estimate, cost_estimate, screenshot_count }
```

**On "Analyze Task":**
- POST to `/analyze-task` with task name + screenshots
- Backend creates analysis report
- Frontend displays in existing ReportViewer component
- Save to localStorage (existing `analysisHistory` service)

---

## Data Flow

```
User pastes screenshot
  ↓
ClipboardEvent fired
  ↓
Extract image from clipboard
  ↓
Convert to File/Blob
  ↓
Read as base64 DataURL
  ↓
Add to steps array (React state)
  ↓
Display thumbnail in timeline
  ↓
On "Finish Task":
  ↓
Convert base64 back to Blobs
  ↓
POST to /estimate-task with FormData
  ↓
Display estimate
  ↓
On "Analyze":
  ↓
POST to /analyze-task
  ↓
Display report (existing ReportViewer)
```

---

## Implementation Phases

### Phase 1: Core Capture Flow (MVP)

**Goal:** User can capture task screenshots and see them in timeline

**Tasks:**
- [ ] Create `TaskSetup` component (task name input)
- [ ] Create `CaptureScreen` component
- [ ] Implement paste handler (`Ctrl+V`)
- [ ] Implement drag-and-drop handler
- [ ] Display screenshots as numbered steps
- [ ] Basic thumbnail display (200px wide)
- [ ] "Finish Task" button (navigates to estimate)

**Success criteria:**
- User can paste 5 screenshots and see timeline
- Screenshots appear immediately after paste
- Clear visual feedback

**Time estimate:** 1-2 days

---

### Phase 2: Editing & Polish

**Goal:** User can fix mistakes and refine capture

**Tasks:**
- [ ] Implement delete step (⋮ menu)
- [ ] Step renumbering after deletion
- [ ] "View Full Size" modal
- [ ] Empty state messaging
- [ ] Loading states (while processing large images)
- [ ] File size validation (warn if >10MB per screenshot)
- [ ] File type validation (reject non-images)

**Success criteria:**
- User can delete and reorder without confusion
- No crashes on large files
- Clear error messages

**Time estimate:** 1 day

---

### Phase 3: Backend Integration

**Goal:** Connect to analysis pipeline

**Tasks:**
- [ ] Create `/estimate-task` endpoint
- [ ] Create `/analyze-task` endpoint
- [ ] Format screenshots for backend (multipart/form-data)
- [ ] Handle estimate response
- [ ] Integrate with existing ReportViewer
- [ ] Save to `analysisHistory` (existing service)
- [ ] Handle errors (upload failed, analysis failed)

**Success criteria:**
- User can complete full flow: capture → estimate → analyze → view report
- Reports appear in "Past Analyses"
- Error handling works

**Time estimate:** 2 days

---

### Phase 4: UX Improvements

**Goal:** Make capture feel smooth and professional

**Tasks:**
- [ ] Keyboard shortcuts (Delete key to remove selected step)
- [ ] Thumbnail click to select + view full size
- [ ] Drag-to-reorder steps (optional)
- [ ] Toast notifications ("Screenshot added", "Step deleted")
- [ ] Better OS-specific instructions (detect platform, show relevant hotkey)
- [ ] Paste zone visual feedback (highlight on hover)
- [ ] Progress indicator during upload

**Success criteria:**
- Feels polished and responsive
- User doesn't need instructions after first use

**Time estimate:** 1-2 days

---

## User Instructions (On-Screen)

### Platform Detection

Detect user's OS and show relevant screenshot instructions:

```typescript
const getOSInstructions = () => {
  const platform = navigator.platform.toLowerCase();

  if (platform.includes('win')) {
    return 'Press Win+Shift+S, then Ctrl+V to paste';
  } else if (platform.includes('mac')) {
    return 'Press Cmd+Shift+4, then Cmd+V to paste';
  } else {
    return 'Press PrtScn, then Ctrl+V to paste';
  }
};
```

Display this dynamically in the capture screen.

---

## Edge Cases & Error Handling

### User pastes non-image content
**Behavior:** Show toast: "Please paste an image file"

### User pastes very large image (>10MB)
**Behavior:** Show warning: "Image is very large (15MB). This may slow analysis. Continue?" [Yes] [No]

### User tries to finish task with 0 screenshots
**Behavior:** Disable "Finish Task" button until at least 1 screenshot added

### User accidentally closes browser during capture
**Options:**
- **A) Don't save** — lose progress (simple, clean)
- **B) Auto-save to localStorage** — restore on return (better UX, more complex)

**Recommendation:** Start with A, add B if users complain

### User drags 10 files at once
**Behavior:** Accept all, add as Step 1, 2, 3... 10 in order

### User pastes same screenshot twice
**Behavior:** Allow it (might be intentional — screen didn't change)

---

## What This Approach Avoids

❌ No installation required
❌ No OS permissions
❌ No browser extensions
❌ No desktop app maintenance
❌ No platform-specific code
❌ No screenshot capture APIs
❌ No global hotkey registration
❌ No auto-update mechanism

---

## Comparison to Other Approaches

| Feature | Web App (Manual Paste) | Browser Extension | Desktop App |
|---------|----------------------|-------------------|-------------|
| **Installation** | None | 15 seconds | 2-5 minutes |
| **Works for web UIs** | ✅ | ✅ | ✅ |
| **Works for desktop apps** | ✅ | ❌ | ✅ |
| **Automatic capture** | ❌ (manual paste) | ✅ | ✅ |
| **Extra steps per screenshot** | +1 (Ctrl+V) | 0 | 0 |
| **Time to ship** | Days | 1-2 weeks | 2-4 weeks |
| **Maintenance burden** | Low | Medium | High |

**For MVP:** Web app wins on speed-to-market and user friction.

---

## Success Metrics

**Adoption:**
- % of users who start a task capture
- % of users who complete (finish task → analyze)

**Engagement:**
- Average screenshots per task
- Time from start to finish per task

**Friction points:**
- Drop-off rate at capture screen (did instructions confuse them?)
- Number of deleted steps (indicator of mistakes)

**Quality:**
- % of analyses that produce useful reports
- User feedback on capture flow

---

## Next Steps

1. **Create React components** (TaskSetup, CaptureScreen, DropZone)
2. **Implement paste/drop handlers** (test with various image types)
3. **Build timeline visualization** (step cards with thumbnails)
4. **Connect to backend** (new `/estimate-task` and `/analyze-task` endpoints)
5. **Test with real users** (5 people, watch them use it, identify friction)
6. **Iterate based on feedback**

---

## Open Questions

### 1. Where does this fit in existing app navigation?

**Options:**
- New button on home screen: "Analyze a Task"
- Part of existing analysis flow (alongside Figma/URL/file upload)
- Separate section in nav menu

**Recommendation:** Add to existing analysis flow, same level as "Upload Files" / "Paste Figma URL" / "Paste Website URL"

### 2. Can users reorder steps after adding them?

**Current plan:** No reordering (keep it simple)

**Alternative:** Add drag-to-reorder in Phase 4

**Trade-off:** Reordering adds complexity. If user adds steps in wrong order, they can delete and re-paste. Fast enough?

### 3. Should we allow editing task name after starting capture?

**Current plan:** No — task name is locked after "Start Capturing"

**Alternative:** Show task name as editable field at top of capture screen

**Recommendation:** Start locked, add editing if users request it

---

**End of Plan**
