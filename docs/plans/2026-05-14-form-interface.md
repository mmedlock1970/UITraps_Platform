# Form Interface Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the chat welcome screen with a structured 4-card form as the default view, keeping the chat interface accessible via a header button.

**Architecture:** The form collects rich context across 4 cards (Interface, User, Use Environment [coming soon], Analysis Scope). Supported fields are assembled into the existing `users`/`tasks`/`format`/`contentType` strings plus a new `extra_context` field. Form submission bypasses `useUnifiedInput` and calls `unifiedAsk` directly from `App.tsx`, reusing the existing report/progress views. Card 3 (Use Environment) and the tenet grid + severity slider in Card 4 are rendered disabled with "Coming soon" badges.

**Tech Stack:** React 18, TypeScript, CSS Modules, FastAPI (Python), existing `unifiedAsk` API function

---

## Task 1: Add `extra_context` to the API type and client

**Files:**
- Modify: `frontend/src/api/types.ts:110-116`
- Modify: `frontend/src/api/client.ts:416-487`

### Step 1: Add `extra_context` to `UserContext`

In `frontend/src/api/types.ts`, update the `UserContext` interface:

```typescript
export interface UserContext {
  users: string;
  expertise: string;
  tasks: string;
  format: string;
  contentType?: ContentType;
  extra_context?: string;   // add this line
}
```

### Step 2: Pass `extra_context` in `unifiedAsk`

In `frontend/src/api/client.ts`, inside `unifiedAsk()`, after the existing `formData.append('content_type', ...)` line (~line 444):

```typescript
if (context) {
  formData.append('users', context.users);
  formData.append('tasks', context.tasks);
  formData.append('format', context.format);
  formData.append('content_type', context.contentType || 'website');
  if (context.extra_context) formData.append('extra_context', context.extra_context);  // add
}
```

### Step 3: Commit

```
git add frontend/src/api/types.ts frontend/src/api/client.ts
git commit -m "feat: add extra_context field to UserContext and unifiedAsk"
```

---

## Task 2: Add `extra_context` to the backend

**Files:**
- Modify: `backend/app.py:1742-1753`
- Modify: `backend/src/prompts.py:1041-1056`

### Step 1: Accept `extra_context` in `/api/ask`

In `backend/app.py`, add the new form field to `unified_ask()` parameters (after `chat_context`):

```python
@app.post("/api/ask", response_model=UnifiedAskResponse)
async def unified_ask(
    user: dict = Depends(get_current_user),
    message: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    users: Optional[str] = Form(None),
    tasks: Optional[str] = Form(None),
    format: Optional[str] = Form(None),
    content_type: str = Form("website"),
    conversation_history: Optional[str] = Form(None),
    chat_context: Optional[str] = Form(None),
    extra_context: Optional[str] = Form(None),   # add this line
):
```

Then find the line where `user_context` is built (~line 1827):

```python
user_context = {"users": users, "tasks": tasks, "format": format, "content_type": content_type}
```

Change it to:

```python
user_context = {
    "users": users,
    "tasks": tasks,
    "format": format,
    "content_type": content_type,
    "extra_context": extra_context or "",
}
```

### Step 2: Use `extra_context` in the prompt

In `backend/src/prompts.py`, find the `context_text` f-string (~line 1041). Add an extra context section after the DESIGN FORMAT block:

```python
extra_ctx = user_context.get('extra_context', '').strip()
extra_context_section = f"""
ADDITIONAL CONTEXT:
{extra_ctx}
""" if extra_ctx else ""
```

Then in the f-string, add `{extra_context_section}` after `{content_type_section}`:

```python
context_text = f"""...
{"4" if has_expertise else "3"}. DESIGN FORMAT:
{user_context['format']}
{content_type_section}
{extra_context_section}
{page_context_section}
...
"""
```

### Step 3: Commit

```
git add backend/app.py backend/src/prompts.py
git commit -m "feat: accept and inject extra_context in analysis prompt"
```

---

## Task 3: Build the new AnalyzerForm CSS

**Files:**
- Overwrite: `frontend/src/components/AnalyzerForm.module.css`

Replace the entire file with CSS Module equivalents of the HTML design's styles. Key classes needed:

```css
/* AnalyzerForm.module.css */

.form {
  max-width: 780px;
  margin: 0 auto;
  padding: 0 24px 100px;
}

.intro {
  margin-bottom: 40px;
}

.introTitle {
  font-size: 36px;
  font-weight: 800;
  letter-spacing: -0.8px;
  line-height: 1.15;
  color: #111111;
  margin-bottom: 14px;
}

.introSubtitle {
  font-size: 16px;
  color: #4a4744;
  max-width: 520px;
  line-height: 1.65;
  margin: 0;
}

.requiredNote {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-top: 12px;
  font-size: 13px;
  color: #8a8680;
}

.requiredDot {
  width: 6px;
  height: 6px;
  background: #e05c1a;
  border-radius: 50%;
  flex-shrink: 0;
}

.card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  border: 1px solid #e8e6e2;
  margin-bottom: 16px;
  overflow: hidden;
}

.cardHeader {
  padding: 20px 24px 16px;
  border-bottom: 1px solid #e8e6e2;
  display: flex;
  align-items: center;
  gap: 14px;
}

.cardNum {
  width: 28px;
  height: 28px;
  background: #111111;
  color: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.cardHeaderText h2 {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.2px;
  color: #111111;
  line-height: 1.3;
  margin: 0;
}

.cardHeaderText p {
  font-size: 13px;
  color: #8a8680;
  margin: 1px 0 0;
}

.cardBody {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Coming soon overlay for disabled cards */
.cardComingSoon {
  position: relative;
}

.cardComingSoon .cardBody {
  opacity: 0.4;
  pointer-events: none;
  user-select: none;
}

.comingSoonBadge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f7f6f4;
  border: 1.5px solid #e8e6e2;
  color: #8a8680;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 4px 10px;
  border-radius: 100px;
  margin-left: auto;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.fieldGrid {
  display: grid;
  gap: 16px;
}

.twoCol {
  grid-template-columns: 1fr 1fr;
}

.span2 {
  grid-column: span 2;
}

@media (max-width: 580px) {
  .twoCol { grid-template-columns: 1fr; }
  .span2 { grid-column: span 1; }
}

.fieldLabel {
  font-size: 13px;
  font-weight: 600;
  color: #111111;
  display: flex;
  align-items: center;
  gap: 6px;
  line-height: 1.3;
}

.req {
  width: 5px;
  height: 5px;
  background: #e05c1a;
  border-radius: 50%;
  flex-shrink: 0;
}

.opt {
  font-size: 11px;
  font-weight: 400;
  color: #8a8680;
}

.fieldHint {
  font-size: 12px;
  color: #8a8680;
  line-height: 1.5;
  margin: 0;
}

.input,
.select,
.textarea {
  background: #f7f6f4;
  border: 1.5px solid #e8e6e2;
  color: #111111;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 14px;
  padding: 10px 14px;
  border-radius: 6px;
  outline: none;
  width: 100%;
  transition: border-color 0.15s, background 0.15s;
  line-height: 1.5;
}

.input::placeholder,
.textarea::placeholder {
  color: #d0cdc8;
}

.input:focus,
.select:focus,
.textarea:focus {
  border-color: #111111;
  background: #ffffff;
}

.select {
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='11' height='7' viewBox='0 0 11 7'%3E%3Cpath d='M1 1l4.5 4.5L10 1' stroke='%238a8680' stroke-width='1.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 13px center;
  background-color: #f7f6f4;
  padding-right: 34px;
}

.textarea {
  resize: vertical;
  min-height: 80px;
}

/* Upload zone */
.uploadZone {
  border: 2px dashed #d0cdc8;
  border-radius: 8px;
  background: #f7f6f4;
  padding: 28px 20px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  position: relative;
}

.uploadZone:hover,
.uploadZoneDragover {
  border-color: #e05c1a;
  background: #fdf1ea;
}

.uploadZoneActive {
  border-color: #e05c1a;
  background: #fdf1ea;
}

.uploadZone input[type="file"] {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
  width: 100%;
  height: 100%;
}

.uploadIcon {
  font-size: 24px;
  margin-bottom: 8px;
  opacity: 0.4;
}

.uploadPrimary {
  font-size: 14px;
  font-weight: 500;
  color: #111111;
  margin-bottom: 3px;
}

.uploadPrimary span {
  text-decoration: underline;
  text-underline-offset: 2px;
}

.uploadSecondary {
  font-size: 12px;
  color: #8a8680;
  margin: 0;
}

.uploadDivider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0 0;
  font-size: 12px;
  color: #8a8680;
}

.uploadDivider::before,
.uploadDivider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #d0cdc8;
}

.fieldError {
  font-size: 12px;
  color: #e05c1a;
  margin: 0;
}

.inputError {
  border-color: #e05c1a !important;
}

.callout {
  background: #fdf1ea;
  border-radius: 8px;
  border: 1px solid rgba(224, 92, 26, 0.18);
  padding: 14px 16px;
  font-size: 13px;
  color: #4a4744;
  line-height: 1.55;
}

.callout strong {
  color: #e05c1a;
  font-weight: 600;
  display: block;
  margin-bottom: 3px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.fieldDivider {
  border: none;
  border-top: 1px solid #e8e6e2;
  margin: 4px 0;
}

/* Submit card */
.submitCard {
  background: #111111;
  border-radius: 12px;
  padding: 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.submitText h3 {
  font-size: 17px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.3px;
  margin: 0 0 4px;
}

.submitText p {
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  line-height: 1.5;
  max-width: 360px;
  margin: 0;
}

.btnSubmit {
  background: #ffffff;
  color: #111111;
  border: none;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 14px;
  font-weight: 700;
  padding: 13px 28px;
  border-radius: 8px;
  cursor: pointer;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: opacity 0.15s, transform 0.1s;
  letter-spacing: -0.1px;
  flex-shrink: 0;
}

.btnSubmit:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btnSubmit:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btnArrow {
  font-size: 16px;
  transition: transform 0.15s;
}

.btnSubmit:hover:not(:disabled) .btnArrow {
  transform: translateX(3px);
}

.errorMessage {
  background: #fdecea;
  border: 1px solid #f5c6c6;
  color: #c0392b;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 13px;
  margin-top: 12px;
}
```

### Step: Commit

```
git add frontend/src/components/AnalyzerForm.module.css
git commit -m "feat: new AnalyzerForm CSS matching design spec"
```

---

## Task 4: Build the new AnalyzerForm component

**Files:**
- Overwrite: `frontend/src/components/AnalyzerForm.tsx`

The component collects all form fields and assembles them into `UserContext` on submit. Card 3 and the tenet/severity section of Card 4 are rendered disabled.

**Platform → ContentType mapping** (used in assembly):
```
'iPhone / iOS app' | 'Android phone app' | 'iPad / tablet app' → 'mobile_app'
'Mobile web browser' | 'Desktop web browser' → 'website'
'Desktop application — Mac' | 'Desktop application — Windows' → 'desktop_app'
(anything with 'game' in productDomain) → 'game'
everything else → 'other'
```

**Context assembly** on submit:
- `tasks` = `userGoal`
- `users` = joined from: `[expLevel, "Frequency: "+frequency, "Goal: "+userGoal, "Familiar products: "+priorProducts, "Pain points: "+painPoints]` — skip empty parts
- `format` = `[platform, productDomain, "Screen: "+screenName, screenDesc]` — joined, skip empty
- `contentType` = derived from platform (see mapping above)
- `extra_context` = `extraContext` field value

```tsx
import React, { useState, useCallback, useRef } from 'react';
import { ContentType, UserContext } from '../api/types';
import styles from './AnalyzerForm.module.css';

export interface FormSubmitPayload {
  files: File[];
  url: string;
  context: UserContext;
}

interface AnalyzerFormProps {
  onSubmit: (payload: FormSubmitPayload) => void;
  disabled?: boolean;
}

function platformToContentType(platform: string, productDomain: string): ContentType {
  const p = platform.toLowerCase();
  const d = productDomain.toLowerCase();
  if (p.includes('iphone') || p.includes('ios') || p.includes('android') || p.includes('ipad') || p.includes('tablet')) return 'mobile_app';
  if (p.includes('desktop application')) return 'desktop_app';
  if (d.includes('gaming') || p.includes('game')) return 'game';
  return 'website';
}

function assembleContext(fields: {
  platform: string; productDomain: string; screenName: string; screenDesc: string;
  expLevel: string; frequency: string; userGoal: string; priorProducts: string;
  painPoints: string; extraContext: string;
}): UserContext {
  const { platform, productDomain, screenName, screenDesc, expLevel, frequency,
          userGoal, priorProducts, painPoints, extraContext } = fields;

  const formatParts = [
    platform && productDomain ? `${platform} — ${productDomain}` : platform || productDomain,
    screenName ? `Screen: ${screenName}` : '',
    screenDesc ? `Description: ${screenDesc}` : '',
  ].filter(Boolean);

  const userParts = [
    expLevel,
    frequency ? `Frequency of use: ${frequency}` : '',
    userGoal ? `Primary goal: ${userGoal}` : '',
    priorProducts ? `Products they use regularly: ${priorProducts}` : '',
    painPoints ? `Known pain points: ${painPoints}` : '',
  ].filter(Boolean);

  return {
    users: userParts.join('. '),
    expertise: expLevel,
    tasks: userGoal,
    format: formatParts.join('. '),
    contentType: platformToContentType(platform, productDomain),
    extra_context: extraContext || undefined,
  };
}

export const AnalyzerForm: React.FC<AnalyzerFormProps> = ({ onSubmit, disabled = false }) => {
  // Card 1 — Interface
  const [files, setFiles] = useState<File[]>([]);
  const [url, setUrl] = useState('');
  const [screenName, setScreenName] = useState('');
  const [platform, setPlatform] = useState('');
  const [productDomain, setProductDomain] = useState('');
  const [screenDesc, setScreenDesc] = useState('');
  const [isDragover, setIsDragover] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Card 2 — User
  const [expLevel, setExpLevel] = useState('');
  const [frequency, setFrequency] = useState('');
  const [userGoal, setUserGoal] = useState('');
  const [priorProducts, setPriorProducts] = useState('');
  const [painPoints, setPainPoints] = useState('');

  // Card 4 — Analysis Scope (only extra context is active)
  const [extraContext, setExtraContext] = useState('');

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = useCallback((): boolean => {
    const e: Record<string, string> = {};
    if (files.length === 0 && !url.trim()) e.upload = 'Please upload a screenshot or enter a URL';
    if (!screenName.trim()) e.screenName = 'Required';
    if (!platform) e.platform = 'Required';
    if (!productDomain) e.productDomain = 'Required';
    if (!screenDesc.trim()) e.screenDesc = 'Required';
    if (!expLevel) e.expLevel = 'Required';
    if (!frequency) e.frequency = 'Required';
    if (!userGoal.trim()) e.userGoal = 'Required';
    setErrors(e);
    return Object.keys(e).length === 0;
  }, [files, url, screenName, platform, productDomain, screenDesc, expLevel, frequency, userGoal]);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (disabled) return;
    if (!validate()) return;
    const context = assembleContext({ platform, productDomain, screenName, screenDesc,
      expLevel, frequency, userGoal, priorProducts, painPoints, extraContext });
    onSubmit({ files, url, context });
  }, [disabled, validate, files, url, platform, productDomain, screenName, screenDesc,
      expLevel, frequency, userGoal, priorProducts, painPoints, extraContext, onSubmit]);

  const handleFileChange = useCallback((newFiles: FileList | null) => {
    if (!newFiles) return;
    setFiles(Array.from(newFiles));
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragover(false);
    handleFileChange(e.dataTransfer.files);
  }, [handleFileChange]);

  const uploadLabel = files.length > 0
    ? files.length === 1 ? files[0].name : `${files.length} files selected`
    : null;

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>

      <div className={styles.intro}>
        <h1 className={styles.introTitle}>Analyze your interface<br />for high-severity Traps.</h1>
        <p className={styles.introSubtitle}>Tell us about your interface and its users. The more context you provide, the more accurate the analysis.</p>
        <div className={styles.requiredNote}>
          <span className={styles.requiredDot} />
          Required fields
        </div>
      </div>

      {/* ── Card 1: The Interface ── */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <div className={styles.cardNum}>1</div>
          <div className={styles.cardHeaderText}>
            <h2>The Interface</h2>
            <p>What are we analyzing?</p>
          </div>
        </div>
        <div className={styles.cardBody}>

          <div className={styles.field}>
            <label className={styles.fieldLabel}>
              <span className={styles.req} />
              Upload a screenshot
            </label>
            <div
              className={`${styles.uploadZone} ${isDragover ? styles.uploadZoneDragover : ''} ${uploadLabel ? styles.uploadZoneActive : ''}`}
              onDragOver={e => { e.preventDefault(); setIsDragover(true); }}
              onDragLeave={() => setIsDragover(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*,video/*,application/pdf"
                multiple
                onChange={e => handleFileChange(e.target.files)}
                style={{ display: 'none' }}
              />
              <div className={styles.uploadIcon}>↑</div>
              {uploadLabel ? (
                <p className={styles.uploadPrimary}><span>{uploadLabel}</span></p>
              ) : (
                <p className={styles.uploadPrimary}><span>Click to upload</span> or drag and drop</p>
              )}
              <p className={styles.uploadSecondary}>{uploadLabel ? 'Ready to analyze' : 'PNG · JPG · WEBP · PDF · Video'}</p>
            </div>
            {errors.upload && <p className={styles.fieldError}>{errors.upload}</p>}
          </div>

          <div className={styles.field}>
            <label className={styles.fieldLabel} htmlFor="urlInput">
              Live URL or Figma link
              <span className={styles.opt}>alternative to upload</span>
            </label>
            <input
              id="urlInput"
              type="url"
              className={styles.input}
              placeholder="https://   or   figma.com/file/…"
              value={url}
              onChange={e => setUrl(e.target.value)}
              disabled={disabled}
            />
          </div>

          <div className={`${styles.fieldGrid} ${styles.twoCol}`}>
            <div className={`${styles.field} ${styles.span2}`}>
              <label className={styles.fieldLabel} htmlFor="screenName">
                <span className={styles.req} />
                Screen or flow name
              </label>
              <input
                id="screenName"
                type="text"
                className={`${styles.input} ${errors.screenName ? styles.inputError : ''}`}
                placeholder="e.g., Checkout — Payment step, Onboarding flow screens 1–4"
                value={screenName}
                onChange={e => setScreenName(e.target.value)}
                disabled={disabled}
              />
              {errors.screenName && <p className={styles.fieldError}>{errors.screenName}</p>}
              <p className={styles.fieldHint}>Name the specific screen or flow so findings can be precisely located in the report.</p>
            </div>

            <div className={styles.field}>
              <label className={styles.fieldLabel} htmlFor="platform">
                <span className={styles.req} />
                Platform
              </label>
              <select
                id="platform"
                className={`${styles.select} ${errors.platform ? styles.inputError : ''}`}
                value={platform}
                onChange={e => setPlatform(e.target.value)}
                disabled={disabled}
              >
                <option value="" disabled>Select one</option>
                <optgroup label="Mobile">
                  <option>iPhone / iOS app</option>
                  <option>Android phone app</option>
                  <option>iPad / tablet app</option>
                  <option>Mobile web browser</option>
                </optgroup>
                <optgroup label="Desktop">
                  <option>Desktop web browser</option>
                  <option>Desktop application — Mac</option>
                  <option>Desktop application — Windows</option>
                </optgroup>
                <optgroup label="Devices">
                  <option>Smart TV / streaming device</option>
                  <option>Smart speaker — voice only</option>
                  <option>Smart display — voice + screen</option>
                  <option>Smartwatch / wearable</option>
                  <option>AR headset</option>
                  <option>VR headset</option>
                  <option>In-vehicle display</option>
                  <option>Kiosk / public terminal</option>
                </optgroup>
                <option>Other / custom hardware</option>
              </select>
              {errors.platform && <p className={styles.fieldError}>{errors.platform}</p>}
            </div>

            <div className={styles.field}>
              <label className={styles.fieldLabel} htmlFor="productDomain">
                <span className={styles.req} />
                Product domain
              </label>
              <select
                id="productDomain"
                className={`${styles.select} ${errors.productDomain ? styles.inputError : ''}`}
                value={productDomain}
                onChange={e => setProductDomain(e.target.value)}
                disabled={disabled}
              >
                <option value="" disabled>Select one</option>
                <option>E-commerce / retail</option>
                <option>Finance / banking</option>
                <option>Health / medical</option>
                <option>Travel / navigation</option>
                <option>Productivity / work tools</option>
                <option>Entertainment / media</option>
                <option>Social / communication</option>
                <option>Education</option>
                <option>Smart home / IoT</option>
                <option>Gaming</option>
                <option>Government / civic</option>
                <option>Other</option>
              </select>
              {errors.productDomain && <p className={styles.fieldError}>{errors.productDomain}</p>}
            </div>

            <div className={`${styles.field} ${styles.span2}`}>
              <label className={styles.fieldLabel} htmlFor="screenDesc">
                <span className={styles.req} />
                What does this screen or flow do?
              </label>
              <textarea
                id="screenDesc"
                className={`${styles.textarea} ${errors.screenDesc ? styles.inputError : ''}`}
                rows={3}
                placeholder="e.g., Final checkout step where users review their order, enter payment details, and confirm purchase."
                value={screenDesc}
                onChange={e => setScreenDesc(e.target.value)}
                disabled={disabled}
              />
              {errors.screenDesc && <p className={styles.fieldError}>{errors.screenDesc}</p>}
            </div>
          </div>

        </div>
      </div>

      {/* ── Card 2: The User ── */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <div className={styles.cardNum}>2</div>
          <div className={styles.cardHeaderText}>
            <h2>The User</h2>
            <p>Who will use this interface, and what do they already know?</p>
          </div>
        </div>
        <div className={styles.cardBody}>

          <div className={styles.callout}>
            <strong>Why this matters</strong>
            Many Traps are only detectable when we understand what users already know,
            what conventions they have learned from other products, and what they are
            trying to accomplish. The more precisely you describe the user, the more
            accurate the analysis.
          </div>

          <div className={`${styles.fieldGrid} ${styles.twoCol}`}>

            <div className={styles.field}>
              <label className={styles.fieldLabel} htmlFor="expLevel">
                <span className={styles.req} />
                Experience with this product
              </label>
              <select
                id="expLevel"
                className={`${styles.select} ${errors.expLevel ? styles.inputError : ''}`}
                value={expLevel}
                onChange={e => setExpLevel(e.target.value)}
                disabled={disabled}
              >
                <option value="" disabled>Select one</option>
                <option>First-time users only</option>
                <option>Primarily new users (0–3 uses)</option>
                <option>Mixed — new and returning</option>
                <option>Primarily returning users</option>
                <option>Expert / power users</option>
                <option>Trained professionals</option>
              </select>
              {errors.expLevel && <p className={styles.fieldError}>{errors.expLevel}</p>}
            </div>

            <div className={styles.field}>
              <label className={styles.fieldLabel} htmlFor="frequency">
                <span className={styles.req} />
                How often do users interact with this?
              </label>
              <select
                id="frequency"
                className={`${styles.select} ${errors.frequency ? styles.inputError : ''}`}
                value={frequency}
                onChange={e => setFrequency(e.target.value)}
                disabled={disabled}
              >
                <option value="" disabled>Select one</option>
                <option>Once (single-use task)</option>
                <option>Rarely — a few times per year</option>
                <option>Occasionally — monthly</option>
                <option>Regularly — weekly</option>
                <option>Frequently — daily</option>
                <option>Continuously — multiple times per day</option>
              </select>
              {errors.frequency && <p className={styles.fieldError}>{errors.frequency}</p>}
            </div>

            <div className={`${styles.field} ${styles.span2}`}>
              <label className={styles.fieldLabel} htmlFor="userGoal">
                <span className={styles.req} />
                Primary user goal on this screen
              </label>
              <input
                id="userGoal"
                type="text"
                className={`${styles.input} ${errors.userGoal ? styles.inputError : ''}`}
                placeholder="e.g., Complete a purchase, Find and book a flight, Set up smart home routines"
                value={userGoal}
                onChange={e => setUserGoal(e.target.value)}
                disabled={disabled}
              />
              {errors.userGoal && <p className={styles.fieldError}>{errors.userGoal}</p>}
              <p className={styles.fieldHint}>The specific goal most users are trying to accomplish when they reach this screen or flow.</p>
            </div>

            <div className={`${styles.field} ${styles.span2}`}>
              <label className={styles.fieldLabel} htmlFor="priorProducts">
                Products this user population uses regularly
                <span className={styles.opt}>optional</span>
              </label>
              <textarea
                id="priorProducts"
                className={styles.textarea}
                rows={2}
                placeholder="e.g., iPhone, Gmail, Amazon, Spotify — or for specialist tools: Salesforce, Epic, AutoCAD"
                value={priorProducts}
                onChange={e => setPriorProducts(e.target.value)}
                disabled={disabled}
              />
              <p className={styles.fieldHint}>This establishes which icons, conventions, and interaction patterns users have already learned.</p>
            </div>

            <div className={`${styles.field} ${styles.span2}`}>
              <label className={styles.fieldLabel} htmlFor="painPoints">
                Known user pain points or complaints
                <span className={styles.opt}>optional</span>
              </label>
              <textarea
                id="painPoints"
                className={styles.textarea}
                rows={2}
                placeholder="e.g., Users frequently abandon at the payment step, Support gets calls about how to cancel"
                value={painPoints}
                onChange={e => setPainPoints(e.target.value)}
                disabled={disabled}
              />
              <p className={styles.fieldHint}>Existing evidence of problems helps focus the analysis on areas most likely to yield high-severity findings.</p>
            </div>

          </div>
        </div>
      </div>

      {/* ── Card 3: Use Environment — COMING SOON ── */}
      <div className={`${styles.card} ${styles.cardComingSoon}`}>
        <div className={styles.cardHeader}>
          <div className={styles.cardNum}>3</div>
          <div className={styles.cardHeaderText}>
            <h2>Use Environment</h2>
            <p>Where and how will this interface be used?</p>
          </div>
          <span className={styles.comingSoonBadge}>Coming soon</span>
        </div>
        <div className={styles.cardBody}>
          <div className={`${styles.fieldGrid} ${styles.twoCol}`}>
            <div className={styles.field}>
              <label className={styles.fieldLabel}>Physical environment</label>
              <select className={styles.select} disabled defaultValue=""><option value="" disabled>Select one</option></select>
            </div>
            <div className={styles.field}>
              <label className={styles.fieldLabel}>Lighting conditions</label>
              <select className={styles.select} disabled defaultValue=""><option value="" disabled>Select one</option></select>
            </div>
            <div className={styles.field}>
              <label className={styles.fieldLabel}>Typical grip / body position</label>
              <select className={styles.select} disabled defaultValue=""><option value="" disabled>Select one</option></select>
            </div>
          </div>
        </div>
      </div>

      {/* ── Card 4: Analysis Scope ── */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <div className={styles.cardNum}>4</div>
          <div className={styles.cardHeaderText}>
            <h2>Analysis Scope</h2>
            <p>Focus the analysis or run it across all Tenets.</p>
          </div>
        </div>
        <div className={styles.cardBody}>

          {/* Tenet grid — coming soon */}
          <div style={{ opacity: 0.4, pointerEvents: 'none', userSelect: 'none' }}>
            <div className={styles.field}>
              <label className={styles.fieldLabel}>
                <span className={styles.req} />
                Tenets to analyze
                <span className={styles.comingSoonBadge}>Coming soon</span>
              </label>
              <p className={styles.fieldHint}>Select specific Tenets to focus the analysis, or keep all selected for a full review.</p>
            </div>
          </div>

          <hr className={styles.fieldDivider} />

          {/* Extra context — ACTIVE */}
          <div className={styles.field}>
            <label className={styles.fieldLabel} htmlFor="extraContext">
              Additional context
              <span className={styles.opt}>optional</span>
            </label>
            <textarea
              id="extraContext"
              className={styles.textarea}
              rows={3}
              placeholder="Known technical constraints, recent design changes, specific hypotheses to test, competitive context — anything that would help calibrate the analysis."
              value={extraContext}
              onChange={e => setExtraContext(e.target.value)}
              disabled={disabled}
            />
          </div>

        </div>
      </div>

      {/* ── Submit ── */}
      <div className={styles.submitCard}>
        <div className={styles.submitText}>
          <h3>Ready to analyze.</h3>
          <p>High-severity findings only, ranked by likely user impact. Analysis typically takes 15–30 seconds.</p>
        </div>
        <button type="submit" className={styles.btnSubmit} disabled={disabled}>
          Run Analysis
          <span className={styles.btnArrow}>→</span>
        </button>
      </div>

    </form>
  );
};

export default AnalyzerForm;
```

### Step: Commit

```
git add frontend/src/components/AnalyzerForm.tsx
git commit -m "feat: rebuild AnalyzerForm with 4-card design, coming-soon fields"
```

---

## Task 5: Wire the form into App.tsx

**Files:**
- Modify: `frontend/src/App.tsx`

### Step 1: Add form view state and analysis handler

The form view needs its own loading/elapsed state separate from `useUnifiedInput` (which manages the chat pipeline). Add these at the top of the `App` component, after existing `useState` declarations:

```tsx
// Form-specific analysis state
const [formAnalysisPhase, setFormAnalysisPhase] = useState<'idle' | 'analyzing'>('idle');
const [formFileCount, setFormFileCount] = useState(0);
const formElapsed = useElapsedTime();
```

Add the form submit handler:

```tsx
const handleFormSubmit = useCallback(async (payload: import('./components/AnalyzerForm').FormSubmitPayload) => {
  const { files, url, context } = payload;

  setFormAnalysisPhase('analyzing');
  setFormFileCount(files.length || 1);
  formElapsed.start();

  try {
    // Determine input: URL takes priority if no files; otherwise use files
    const inputFiles = files.length > 0 ? files : [];
    const inputMessage = url && files.length === 0 ? url : undefined;
    const imageTimeout = Math.min(180000 + (files.length || 1) * 120000, 1800000);

    const result = await unifiedAsk({
      apiEndpoint,
      token: effectiveToken,
      message: inputMessage,
      files: inputFiles,
      context,
      timeout: imageTimeout,
    });

    formElapsed.stop();

    if (result.report_html) {
      handleAnalysisComplete(
        result,
        files.map(f => f.name),
        files,
        { users: context.users, tasks: context.tasks, format: context.format, contentType: context.contentType || 'website' }
      );
    }
  } catch (err) {
    formElapsed.stop();
    console.error('Form analysis failed:', err);
  } finally {
    setFormAnalysisPhase('idle');
    formElapsed.reset();
  }
}, [apiEndpoint, effectiveToken, formElapsed, handleAnalysisComplete, unifiedAsk]);
```

Note: `unifiedAsk` needs to be imported directly. Add it to the existing import:

```tsx
import { unifiedAsk } from './api/client';
```

### Step 2: Update `AppView` type and default view

Change the type (line ~118):
```tsx
type AppView = 'form' | 'chat' | 'report' | 'history' | 'task-capture';
```

Change the default (line ~132):
```tsx
const [view, setView] = useState<AppView>('form');
```

### Step 3: Add "form analysis in progress" view

Insert this block just before the `// ── Estimate preview overlay ──` block (~line 458):

```tsx
// ── Form analysis in progress ──
if (view === 'form' && formAnalysisPhase === 'analyzing') {
  return (
    <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
      <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
        <header className={styles.header}>
          <div className={styles.logo}>UI Traps <span className={styles.logoAccent}>Helper</span></div>
        </header>
        <div className={styles.overlayContainer}>
          <AnalysisProgress
            elapsedTime={formElapsed.elapsedTime}
            onCancel={() => { setFormAnalysisPhase('idle'); formElapsed.reset(); }}
            inputType={formFileCount > 1 ? 'multi_image' : 'single_image'}
            fileCount={formFileCount}
          />
        </div>
      </div>
    </div>
  );
}
```

### Step 4: Add form view render

Insert this block just before the `// ── Estimate preview overlay ──` block, after the form-analysis-in-progress block:

```tsx
// ── Form view (default) ──
if (view === 'form') {
  return (
    <div className={`uitraps-viewport-wrapper ${styles.viewportWrapper}`} data-theme={theme}>
      <div className={`uitraps-platform ${styles.platform}`} data-theme={theme}>
        <header className={styles.header}>
          <div className={styles.logo}>UI Traps <span className={styles.logoAccent}>Helper</span></div>
          <div className={styles.headerActions}>
            <button className={styles.headerButton} onClick={() => setView('chat')}>Chat</button>
            {getAnalysisHistory().length > 0 && (
              <button className={styles.headerButton} onClick={() => setView('history')}>Past Analyses</button>
            )}
            <button className={styles.headerButton} onClick={toggleTheme}>
              {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
            </button>
          </div>
        </header>
        <div style={{ overflowY: 'auto', flex: 1, paddingTop: '40px' }}>
          <AnalyzerForm onSubmit={handleFormSubmit} disabled={false} />
        </div>
      </div>
    </div>
  );
}
```

### Step 5: Add "Analyzer" button in chat view header

In the main chat view header (~line 519), add an "Analyzer" button alongside "New Session":

```tsx
<button className={styles.headerButton} onClick={() => setView('form')}>
  Analyzer
</button>
```

### Step 6: Add `AnalyzerForm` import

At the top of `App.tsx`, add:
```tsx
import { AnalyzerForm, FormSubmitPayload } from './components/AnalyzerForm';
```

### Step 7: Update history/report "Back" button targets

In the history view header (~line 440), change "Back to Chat" to navigate to form:
```tsx
<button className={styles.headerButton} onClick={() => setView('form')}>Back</button>
```

In the report view header (~line 393), update "Back to Chat" label:
```tsx
<button className={styles.headerButton} onClick={() => setView('form')}>New Analysis</button>
```

### Step 8: Commit

```
git add frontend/src/App.tsx
git commit -m "feat: add form view as default, header Chat/Analyzer toggle"
```

---

## Task 6: Smoke test

1. Run backend: `python app.py` in `backend/`
2. Run frontend: `npm run dev` in `frontend/`
3. Open `http://localhost:5173`
4. Verify form loads as default view
5. Click "Chat" — verify chat interface appears
6. Click "Analyzer" — verify form returns
7. Fill out form, upload a screenshot, submit — verify analysis progress appears, then report
8. Verify "Additional context" content appears to influence report (check backend log)
9. Check `backend/uitraps_error.log` for any errors

---

## Task 7: Commit and push

```bash
git push origin master
```
