import React, { useState, useCallback, useRef, useEffect } from 'react';
import { ContentType, KbVersion, UserContext } from '../api/types';
import styles from './AnalyzerForm.module.css';

export interface FormSubmitPayload {
  files: File[];
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

const ALL_TENETS = [
  'UNDERSTANDABLE', 'COMFORTABLE', 'RESPONSIVE',
  'EFFICIENT',      'ACCURATE',    'PROTECTIVE',
  'HABITUATING',    'BEAUTIFUL',
] as const;

const TENET_COLORS: Record<string, string> = {
  UNDERSTANDABLE: '#2B4C6F',
  COMFORTABLE:    '#D1492E',
  RESPONSIVE:     '#E0AE22',
  EFFICIENT:      '#AF1C66',
  ACCURATE:       '#45A24C',
  PROTECTIVE:     '#642FA1',
  HABITUATING:    '#1F7DA8',
  BEAUTIFUL:      '#E37209',
};

function tenetTextColor(_hex: string): string {
  return '#ffffff';
}

function tenetLightBg(hex: string): string {
  const r = Math.round(parseInt(hex.slice(1, 3), 16) * 0.10 + 255 * 0.90);
  const g = Math.round(parseInt(hex.slice(3, 5), 16) * 0.10 + 255 * 0.90);
  const b = Math.round(parseInt(hex.slice(5, 7), 16) * 0.10 + 255 * 0.90);
  return `rgb(${r}, ${g}, ${b})`;
}

function assembleContext(fields: {
  platform: string; productDomain: string; screenName: string;
  expLevel: string; techSavvy: string; frequency: string; taskList: Array<{ name: string; description: string }>;
  priorProducts: string; userDesc: string; extraContext: string; productContext: string;
  physicalEnv: string; lighting: string; gripPosition: string; attentionalState: string;
  kbVersion: KbVersion; selectedTenets: string[];
  verbosity: 'brief' | 'standard'; pass1Model: 'sonnet' | 'haiku';
  figmaLink: string; thoroughMode: boolean;
  inputType: 'screenshot' | 'video' | 'flow_diagram';
  flowMode: 'screen' | 'flow';
}): UserContext {
  const { platform, productDomain, screenName, expLevel, techSavvy,
          frequency, taskList, priorProducts, userDesc, extraContext, productContext,
          physicalEnv, lighting, gripPosition, attentionalState, kbVersion, selectedTenets,
          verbosity, pass1Model, figmaLink, thoroughMode, inputType, flowMode } = fields;

  const combinedExtra = [
    (figmaLink.trim() && inputType !== 'flow_diagram') ? `Design file: ${figmaLink.trim()}` : '',
    extraContext,
  ].filter(Boolean).join('\n');

  const formatParts = [
    platform && productDomain ? `${platform} — ${productDomain}` : platform || productDomain,
    screenName ? `Screen: ${screenName}` : '',
  ].filter(Boolean);

  const userParts = [
    userDesc ? `Target users: ${userDesc}` : '',
    expLevel ? `Experience with product: ${expLevel}` : '',
    techSavvy ? `Tech savviness: ${techSavvy}` : '',
    frequency ? `Frequency of use: ${frequency}` : '',
    priorProducts ? `Experience with similar interfaces: ${priorProducts}` : '',
  ].filter(Boolean);

  const designName = screenName.trim() || undefined;

  return {
    users: userParts.join('. '),
    expertise: `${expLevel}${techSavvy ? ` / ${techSavvy}` : ''}`,
    tasks: taskList
      .filter(t => t.description.trim())
      .map(t => (t.name.trim() ? `${t.name}: ${t.description}` : t.description))
      .join('. '),
    task_list: taskList.filter(t => t.description.trim()).length > 1
      ? taskList.filter(t => t.description.trim())
      : undefined,
    format: formatParts.join('. '),
    design_name: designName || undefined,
    contentType: platformToContentType(platform, productDomain),
    extra_context: combinedExtra || undefined,
    product_context: productContext || undefined,
    physical_env: physicalEnv || undefined,
    lighting: lighting || undefined,
    grip_position: gripPosition || undefined,
    attentional_state: attentionalState || undefined,
    kb_version: kbVersion,
    tenet_filter: selectedTenets.length > 0 ? selectedTenets : undefined,
    verbosity,
    pass1_model: pass1Model,
    thorough_mode: thoroughMode || undefined,
    input_type: inputType,
    flow_mode: inputType === 'flow_diagram' ? flowMode : undefined,
    figma_url: (figmaLink.trim() && inputType === 'flow_diagram') ? figmaLink.trim() : undefined,
  };
}

function isImageFile(file: File) {
  return file.type.startsWith('image/');
}

function isVideoFile(file: File) {
  return file.type.startsWith('video/');
}

export const AnalyzerForm: React.FC<AnalyzerFormProps> = ({ onSubmit, disabled = false }) => {
  // Card 1 — Interface
  const [files, setFiles] = useState<File[]>([]);
  const [thumbnailUrls, setThumbnailUrls] = useState<string[]>([]);
  const [figmaLink, setFigmaLink] = useState('');
  const [screenName, setScreenName] = useState('');
  const [platform, setPlatform] = useState('');
  const [productDomain, setProductDomain] = useState('');
  const [productContext, setProductContext] = useState('');
  const [isDragover, setIsDragover] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Card 2 — User
  const [expLevel, setExpLevel] = useState('');
  const [techSavvy, setTechSavvy] = useState('');
  const [frequency, setFrequency] = useState('');
  const [tasks, setTasks] = useState<Array<{ name: string; description: string }>>([
    { name: '', description: '' },
  ]);
  const [userDesc, setUserDesc] = useState('');
  const [priorProducts, setPriorProducts] = useState('');

  // Card 3 — Use Environment
  const [physicalEnv, setPhysicalEnv] = useState('');
  const [lighting, setLighting] = useState('');
  const [gripPosition, setGripPosition] = useState('');
  const [attentionalState, setAttentionalState] = useState('');

  // Card 4 — Additional Context
  const [extraContext, setExtraContext] = useState('');

  // Card 5 — Analysis Scope
  const [kbVersion, setKbVersion] = useState<KbVersion>('v2');
  const [selectedTenets, setSelectedTenets] = useState<string[]>([]);
  const [verbosity, setVerbosity] = useState<'brief' | 'standard'>('standard');
  const [pass1Model, setPass1Model] = useState<'sonnet' | 'haiku'>('sonnet');
  const [thoroughMode, setThoroughMode] = useState(false);
  const [inputType, setInputType] = useState<'screenshot' | 'video' | 'flow_diagram'>('screenshot');
  const [flowMode, setFlowMode] = useState<'screen' | 'flow'>('screen');

  const toggleTenet = useCallback((tenet: string) => {
    setSelectedTenets(prev =>
      prev.includes(tenet) ? prev.filter(t => t !== tenet) : [...prev, tenet]
    );
  }, []);

  const addTask = useCallback(() => {
    setTasks(prev => prev.length < 3 ? [...prev, { name: '', description: '' }] : prev);
  }, []);

  const removeTask = useCallback((index: number) => {
    setTasks(prev => prev.length > 1 ? prev.filter((_, i) => i !== index) : prev);
  }, []);

  const updateTask = useCallback((index: number, field: 'name' | 'description', value: string) => {
    setTasks(prev => prev.map((t, i) => i === index ? { ...t, [field]: value } : t));
  }, []);

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Create and revoke object URLs for image thumbnails
  useEffect(() => {
    const urls = files.map(f => isImageFile(f) ? URL.createObjectURL(f) : '');
    setThumbnailUrls(urls);
    return () => { urls.forEach(u => { if (u) URL.revokeObjectURL(u); }); };
  }, [files]);

  const validate = useCallback((): boolean => {
    const e: Record<string, string> = {};
    const figmaFlowProvided = inputType === 'flow_diagram' && figmaLink.trim().length > 0;
    if (files.length === 0 && !figmaFlowProvided) e.upload = 'Please upload a screenshot, video, or PDF';
    if (!screenName.trim()) e.screenName = 'Required';
    if (!platform) e.platform = 'Required';
    if (!productDomain) e.productDomain = 'Required';
    if (!expLevel) e.expLevel = 'Required';
    if (!techSavvy) e.techSavvy = 'Required';
    if (!frequency) e.frequency = 'Required';
    if (!tasks[0]?.description.trim()) e.userGoal = 'Required';
    setErrors(e);
    return Object.keys(e).length === 0;
  }, [files, screenName, platform, productDomain, expLevel, techSavvy, frequency, tasks]);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (disabled) return;
    if (!validate()) return;
    const context = assembleContext({ platform, productDomain, screenName,
      expLevel, techSavvy, frequency, taskList: tasks, priorProducts, userDesc, extraContext, productContext,
      physicalEnv, lighting, gripPosition, attentionalState, kbVersion, selectedTenets,
      verbosity, pass1Model, figmaLink, thoroughMode, inputType, flowMode });
    onSubmit({ files, context });
  }, [disabled, validate, files, figmaLink, platform, productDomain, screenName,
      expLevel, techSavvy, frequency, tasks, priorProducts, userDesc, extraContext, productContext,
      physicalEnv, lighting, gripPosition, attentionalState, kbVersion, selectedTenets,
      verbosity, pass1Model, thoroughMode, inputType, flowMode, onSubmit]);

  const handleFileChange = useCallback((newFiles: FileList | null) => {
    if (!newFiles || newFiles.length === 0) return;
    setFiles(prev => [...prev, ...Array.from(newFiles)]);
  }, []);

  const handleRemoveFile = useCallback((index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragover(false);
    handleFileChange(e.dataTransfer.files);
  }, [handleFileChange]);

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
            <label className={styles.fieldLabel} htmlFor="screenName">
              <span className={styles.req} />
              Name the interface being evaluated
            </label>
            <input
              id="screenName"
              type="text"
              className={`${styles.input} ${errors.screenName ? styles.inputError : ''}`}
              placeholder="e.g., Product X onboarding flow, screen 1"
              value={screenName}
              onChange={e => setScreenName(e.target.value)}
              disabled={disabled}
            />
            {errors.screenName && <p className={styles.fieldError}>{errors.screenName}</p>}
          </div>

          <div className={styles.field}>
            <label className={styles.fieldLabel}>
              <span className={styles.req} />
              Upload screenshots or provide a link
            </label>
            <div
              className={`${styles.uploadZone} ${isDragover ? styles.uploadZoneDragover : ''} ${files.length > 0 ? styles.uploadZoneActive : ''}`}
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
              {files.length === 0 ? (
                <>
                  <div className={styles.uploadIcon}>↑</div>
                  <p className={styles.uploadPrimary}><span>Click to upload screen shot</span> or drag and drop</p>
                  <p className={styles.uploadSecondary}>PNG · JPG · WEBP · PDF · Video</p>
                </>
              ) : (
                <>
                  <div className={styles.thumbnailGrid} onClick={e => e.stopPropagation()}>
                    {files.map((file, i) => (
                      <div key={i} className={styles.thumbnailItem}>
                        {isImageFile(file) && thumbnailUrls[i] ? (
                          <img src={thumbnailUrls[i]} alt={file.name} className={styles.thumbnailImg} />
                        ) : (
                          <div className={styles.thumbnailNonImage}>
                            <span>{isVideoFile(file) ? '▶' : '📄'}</span>
                            <span>{isVideoFile(file) ? 'Video' : 'PDF'}</span>
                          </div>
                        )}
                        <button
                          type="button"
                          className={styles.thumbnailRemove}
                          onClick={() => handleRemoveFile(i)}
                          title="Remove"
                        >×</button>
                      </div>
                    ))}
                  </div>
                  <p className={styles.uploadPrimary} style={{ marginTop: 10 }}>
                    <span>{files.length} file{files.length > 1 ? 's' : ''} selected</span>
                    {' '}— <span>click to add more</span>
                  </p>
                </>
              )}
            </div>
            <div className={styles.uploadDivider}>or include a Figma design link (optional)</div>
            <input
              id="figmaLinkInput"
              type="text"
              className={styles.input}
              placeholder="figma.com/file/…  or  figma.com/design/…"
              value={figmaLink}
              onChange={e => setFigmaLink(e.target.value)}
              disabled={disabled}
            />
            {errors.upload && <p className={styles.fieldError}>{errors.upload}</p>}
          </div>

          {/* Input type selector */}
          <div className={styles.field} style={{ marginTop: 12 }}>
            <label className={styles.fieldLabel}>What are you uploading?</label>
            <div className={styles.kbVersionGroup}>
              {([
                ['screenshot', 'Screenshot(s)'],
                ['video', 'Video / recording'],
                ['flow_diagram', 'Flow diagram'],
              ] as const).map(([v, label]) => (
                <button
                  key={v}
                  type="button"
                  className={`${styles.kbVersionBtn} ${inputType === v ? styles.kbVersionBtnActive : ''}`}
                  onClick={() => setInputType(v)}
                  disabled={disabled}
                >
                  {label}
                </button>
              ))}
            </div>
            {inputType === 'flow_diagram' && (
              <p className={styles.fieldHint}>
                If uploading an image of a flow, include all connected screens and their navigation arrows in a single file. Or enter a Figma link above — prototype connections will be extracted automatically.
              </p>
            )}
          </div>

          {/* Product context */}
          <div className={styles.field}>
            <label className={styles.fieldLabel} htmlFor="productContext">
              Describe the general purpose of this product
              <span className={styles.opt}>optional</span>
            </label>
            <input
              id="productContext"
              type="text"
              className={styles.input}
              placeholder="e.g., Hospital website, retail mobile app, banking dashboard, B2B SaaS tool"
              value={productContext}
              onChange={e => setProductContext(e.target.value)}
              disabled={disabled}
            />
            <p className={styles.fieldHint}>Helps calibrate findings and recommendations to the product's broader purpose — not just the task being evaluated.</p>
          </div>

          <div className={`${styles.fieldGrid} ${styles.twoCol}`}>
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

          </div>

        </div>
      </div>

      {/* ── Card 2: The User and their goals ── */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <div className={styles.cardNum}>2</div>
          <div className={styles.cardHeaderText}>
            <h2>The User and their goals</h2>
            <p>Who will use this interface, and what do they already know?</p>
          </div>
        </div>
        <div className={styles.cardBody}>

          <div className={styles.callout}>
            <strong>Why this matters</strong>
            Many Traps are only visible when we know what users already understand and what they are trying to do.
            The more precisely you describe the user, the more accurate the analysis.
          </div>

          <div className={`${styles.fieldGrid} ${styles.twoCol}`}>

            <div className={`${styles.field} ${styles.span2}`}>
              <label className={styles.fieldLabel} htmlFor="userDesc">
                Describe the intended users of this interface
                <span className={styles.opt}>optional</span>
              </label>
              <input
                id="userDesc"
                type="text"
                className={styles.input}
                placeholder="e.g., Adults 55+, low tech confidence, first smartphone users. Or: Healthcare professionals, clinical setting, time-pressured."
                value={userDesc}
                onChange={e => setUserDesc(e.target.value)}
                disabled={disabled}
              />
              <p className={styles.fieldHint}>Age, occupation, cognitive load, accessibility needs, domain expertise — anything relevant to how they'll interact with this UI.</p>
            </div>

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
                <option>First-time users</option>
                <option>Mostly new users (0–3 sessions)</option>
                <option>Mixed — new and returning</option>
                <option>Mostly returning users</option>
                <option>Long-term regular users</option>
              </select>
              {errors.expLevel && <p className={styles.fieldError}>{errors.expLevel}</p>}
            </div>

            <div className={styles.field}>
              <label className={styles.fieldLabel} htmlFor="techSavvy">
                <span className={styles.req} />
                Tech savviness
              </label>
              <select
                id="techSavvy"
                className={`${styles.select} ${errors.techSavvy ? styles.inputError : ''}`}
                value={techSavvy}
                onChange={e => setTechSavvy(e.target.value)}
                disabled={disabled}
              >
                <option value="" disabled>Select one</option>
                <option>Novice — rarely uses technology</option>
                <option>Casual — uses apps but not tech-forward</option>
                <option>Average — comfortable with everyday apps</option>
                <option>Competent — quick to learn new interfaces</option>
                <option>Advanced — power user, explores features</option>
                <option>Expert professional — specialist tool user</option>
              </select>
              {errors.techSavvy && <p className={styles.fieldError}>{errors.techSavvy}</p>}
            </div>

            <div className={styles.field}>
              <label className={styles.fieldLabel} htmlFor="frequency">
                <span className={styles.req} />
                How often will users interact with this product?
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

            <div className={styles.field}>
              <label className={styles.fieldLabel} htmlFor="priorProducts">
                Experience with similar interfaces
                <span className={styles.opt}>optional</span>
              </label>
              <select
                id="priorProducts"
                className={styles.select}
                value={priorProducts}
                onChange={e => setPriorProducts(e.target.value)}
                disabled={disabled}
              >
                <option value="">— Select one —</option>
                <option value="none">None — this type of product is new to them</option>
                <option value="limited">Limited — used one or two similar products briefly</option>
                <option value="some">Some — regular user of a comparable product</option>
                <option value="extensive">Extensive — power user of similar products</option>
                <option value="professional">Professional — expert-level familiarity with this category</option>
              </select>
            </div>

            <div className={`${styles.field} ${styles.span2}`}>
              <label className={styles.fieldLabel}>
                <span className={styles.req} />
                User task(s) to evaluate
              </label>
              <p className={styles.fieldHint}>
                The specific outcome(s) users are trying to achieve on this screen or flow.
                You can add up to 3 tasks — each additional task increases analysis time but
                produces a report with a General Findings section plus one section per task.
              </p>
              {tasks.map((task, i) => (
                <div key={i} className={styles.taskRow}>
                  {tasks.length > 1 && (
                    <input
                      type="text"
                      className={styles.input}
                      placeholder={`Task ${i + 1} name (optional)`}
                      value={task.name}
                      onChange={e => updateTask(i, 'name', e.target.value)}
                      disabled={disabled}
                    />
                  )}
                  <div className={styles.taskDescRow}>
                    <input
                      id={i === 0 ? 'userGoal' : undefined}
                      type="text"
                      className={`${styles.input} ${i === 0 && errors.userGoal ? styles.inputError : ''}`}
                      placeholder={tasks.length === 1
                        ? 'e.g., Complete a purchase, Find and book a flight'
                        : `Task ${i + 1} description`}
                      value={task.description}
                      onChange={e => updateTask(i, 'description', e.target.value)}
                      disabled={disabled}
                    />
                    {tasks.length > 1 && (
                      <button
                        type="button"
                        className={styles.taskRemoveBtn}
                        onClick={() => removeTask(i)}
                        disabled={disabled}
                        title="Remove task"
                      >×</button>
                    )}
                  </div>
                </div>
              ))}
              {tasks.length < 3 && (
                <button
                  type="button"
                  className={styles.taskAddBtn}
                  onClick={addTask}
                  disabled={disabled}
                >+ Add task</button>
              )}
              {errors.userGoal && <p className={styles.fieldError}>{errors.userGoal}</p>}
            </div>

          </div>
        </div>
      </div>

      {/* ── Card 3: Use Environment ── */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <div className={styles.cardNum}>3</div>
          <div className={styles.cardHeaderText}>
            <h2>Use Environment</h2>
            <p>Where and how will this interface be used?</p>
          </div>
        </div>
        <div className={styles.cardBody}>
          <div className={styles.callout}>
            <strong>Why this matters</strong>
            The context of use — where users are, what else they're doing, and how much attention they can give the interface —
            shapes which risks are real and how severe they are. The more detail you provide, the sharper the analysis.
          </div>
          <div className={`${styles.fieldGrid} ${styles.twoCol}`}>
            <div className={styles.field}>
              <label className={styles.fieldLabel} htmlFor="physicalEnv">
                Physical environment
                <span className={styles.opt}>optional</span>
              </label>
              <select
                id="physicalEnv"
                className={styles.select}
                value={physicalEnv}
                onChange={e => setPhysicalEnv(e.target.value)}
                disabled={disabled}
              >
                <option value="">— Select one —</option>
                <option value="desk">At a desk or workstation</option>
                <option value="stationary">Stationary but away from a desk (couch, café, waiting area)</option>
                <option value="moving">On the go — walking, commuting, or in transit</option>
                <option value="vehicle">In a vehicle (as a passenger)</option>
                <option value="outdoor">Outdoors or in variable conditions</option>
              </select>
            </div>
            <div className={styles.field}>
              <label className={styles.fieldLabel} htmlFor="lighting">
                Lighting conditions
                <span className={styles.opt}>optional</span>
              </label>
              <select
                id="lighting"
                className={styles.select}
                value={lighting}
                onChange={e => setLighting(e.target.value)}
                disabled={disabled}
              >
                <option value="">— Select one —</option>
                <option value="well_lit">Well lit — consistent indoor lighting</option>
                <option value="variable">Variable or mixed lighting</option>
                <option value="bright">Bright sunlight or significant glare</option>
                <option value="low_light">Low light or dim environment</option>
              </select>
            </div>
            <div className={styles.field}>
              <label className={styles.fieldLabel} htmlFor="gripPosition">
                Typical grip / body position
                <span className={styles.opt}>optional</span>
              </label>
              <select
                id="gripPosition"
                className={styles.select}
                value={gripPosition}
                onChange={e => setGripPosition(e.target.value)}
                disabled={disabled}
              >
                <option value="">— Select one —</option>
                <option value="keyboard">Both hands on a keyboard (desktop or laptop)</option>
                <option value="one_hand">One hand holding device, other hand interacting</option>
                <option value="two_hands_thumbs">Two hands holding device, thumbs for input</option>
                <option value="flat">Device resting flat on a surface</option>
                <option value="hands_free">Hands-free — voice, mounted display, or kiosk</option>
              </select>
            </div>
            <div className={styles.field}>
              <label className={styles.fieldLabel} htmlFor="attentionalState">
                Typically, how focused are users on this interface?
                <span className={styles.opt}>optional</span>
              </label>
              <select
                id="attentionalState"
                className={styles.select}
                value={attentionalState}
                onChange={e => setAttentionalState(e.target.value)}
                disabled={disabled}
              >
                <option value="">— Select one —</option>
                <option value="fully_focused">Fully focused — this is their only active task</option>
                <option value="mostly_focused">Mostly focused, but in a distracting setting</option>
                <option value="divided">Divided — managing this alongside something else</option>
                <option value="peripheral">Mostly elsewhere — this interface is a secondary task</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* ── Card 4: Additional Context ── */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <div className={styles.cardNum}>4</div>
          <div className={styles.cardHeaderText}>
            <h2>Additional Context</h2>
            <p>Anything else that would help calibrate the analysis.</p>
          </div>
        </div>
        <div className={styles.cardBody}>
          <div className={styles.field}>
            <label className={styles.fieldLabel} htmlFor="extraContext">
              Add any additional context
              <span className={styles.opt}>optional</span>
            </label>
            <input
              id="extraContext"
              type="text"
              className={styles.input}
              placeholder="Known technical constraints, recent design changes, specific hypotheses to test, competitive context — anything that would help calibrate the analysis."
              value={extraContext}
              onChange={e => setExtraContext(e.target.value)}
              disabled={disabled}
            />
          </div>
        </div>
      </div>

      {/* ── Card 5: Analysis Scope ── */}
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <div className={styles.cardNum}>5</div>
          <div className={styles.cardHeaderText}>
            <h2>Analysis Scope</h2>
            <p>Narrow to specific Tenets for a faster result, or leave all selected for a complete review.</p>
          </div>
        </div>
        <div className={styles.cardBody}>

          {/* Tenet selector */}
          <div className={styles.field}>
            <label className={styles.fieldLabel}>Tenets to analyze</label>
            <p className={styles.fieldHint} style={{ marginBottom: 10 }}>
              {selectedTenets.length === 0
                ? 'All nine Tenets will be evaluated (default).'
                : `Focusing on ${selectedTenets.length} Tenet${selectedTenets.length > 1 ? 's' : ''}: ${selectedTenets.join(', ')}.`}
            </p>
            <div className={styles.tenetGrid}>
              {ALL_TENETS.map(tenet => (
                <button
                  key={tenet}
                  type="button"
                  className={`${styles.tenetBtn} ${selectedTenets.includes(tenet) ? styles.tenetBtnActive : ''}`}
                  style={{
                    '--tenet-color': TENET_COLORS[tenet],
                    '--tenet-text': tenetTextColor(TENET_COLORS[tenet]),
                    '--tenet-bg-light': tenetLightBg(TENET_COLORS[tenet]),
                  } as React.CSSProperties}
                  onClick={() => toggleTenet(tenet)}
                  disabled={disabled}
                >
                  {tenet}
                </button>
              ))}
            </div>
            {selectedTenets.length > 0 && (
              <button
                type="button"
                className={styles.tenetClearBtn}
                onClick={() => setSelectedTenets([])}
                disabled={disabled}
              >
                Clear — analyze all Tenets
              </button>
            )}
          </div>

          <hr className={styles.fieldDivider} />

          {/* Report verbosity */}
          <div className={styles.field}>
            <label className={styles.fieldLabel}>Report detail</label>
            <div className={styles.kbVersionGroup}>
              {(['standard', 'brief'] as const).map(v => (
                <button
                  key={v}
                  type="button"
                  className={`${styles.kbVersionBtn} ${verbosity === v ? styles.kbVersionBtnActive : ''}`}
                  onClick={() => setVerbosity(v)}
                  disabled={disabled}
                >
                  {v === 'standard' ? 'Standard' : 'Brief'}
                </button>
              ))}
            </div>
            <p className={styles.fieldHint}>
              {verbosity === 'standard' && 'Full narratives for summary, findings, and recommendations.'}
              {verbosity === 'brief' && 'Shorter text throughout. Reduces output tokens and speeds up analysis.'}
            </p>
          </div>

          <hr className={styles.fieldDivider} />

          {/* Analysis model */}
          <div className={styles.field}>
            <label className={styles.fieldLabel}>Analysis model</label>
            <div className={styles.kbVersionGroup}>
              {(['sonnet', 'haiku'] as const).map(v => (
                <button
                  key={v}
                  type="button"
                  className={`${styles.kbVersionBtn} ${pass1Model === v ? styles.kbVersionBtnActive : ''}`}
                  onClick={() => setPass1Model(v)}
                  disabled={disabled}
                >
                  {v === 'sonnet' ? 'Sonnet' : 'Haiku'}
                </button>
              ))}
            </div>
            <p className={styles.fieldHint}>
              {pass1Model === 'sonnet' && 'Recommended. Best visual analysis accuracy for production reviews.'}
              {pass1Model === 'haiku' && '~3× faster and cheaper. Lower accuracy — best for quick checks, not final reviews.'}
            </p>
          </div>

          <hr className={styles.fieldDivider} />

          {/* Knowledge base version selector */}
          <div className={styles.field}>
            <label className={styles.fieldLabel}>Knowledge base version</label>
            <div className={styles.kbVersionGroup}>
              {(['v2', 'v2.1', 'v1', 'both'] as KbVersion[]).map(v => (
                <button
                  key={v}
                  type="button"
                  className={`${styles.kbVersionBtn} ${kbVersion === v ? styles.kbVersionBtnActive : ''}`}
                  onClick={() => setKbVersion(v)}
                  disabled={disabled}
                >
                  {v === 'both' ? 'Compare v1 vs v2' : v.toUpperCase()}
                </button>
              ))}
            </div>
            <p className={styles.fieldHint}>
              {kbVersion === 'v2' && 'Current knowledge engine (recommended).'}
              {kbVersion === 'v2.1' && 'Streamlined v2: tenet overviews, why-it-occurs notes, and remediation guidance removed. Faster analysis, same trap detection accuracy.'}
              {kbVersion === 'v1' && 'Previous knowledge engine.'}
              {kbVersion === 'both' && 'Runs two parallel analyses — one with each engine. Results are shown side-by-side with a toggle. Takes roughly twice as long.'}
            </p>
          </div>

          <hr className={styles.fieldDivider} />

          {/* Analysis coverage */}
          <div className={styles.field}>
            <label className={styles.fieldLabel}>Analysis coverage</label>
            <div className={styles.kbVersionGroup}>
              {([false, true] as const).map(v => (
                <button
                  key={String(v)}
                  type="button"
                  className={`${styles.kbVersionBtn} ${thoroughMode === v ? styles.kbVersionBtnActive : ''}`}
                  onClick={() => setThoroughMode(v)}
                  disabled={disabled}
                >
                  {v ? 'Thorough' : 'Standard'}
                </button>
              ))}
            </div>
            <p className={styles.fieldHint}>
              {!thoroughMode && 'Single-pass analysis. Fast, good coverage for most designs.'}
              {thoroughMode && 'Runs one focused pass per Tenet in parallel, then merges findings. More consistent results, similar speed. Recommended for final reviews.'}
            </p>
          </div>

          <hr className={styles.fieldDivider} />

          {/* Flow analysis mode */}
          <div className={styles.field}>
            <label className={styles.fieldLabel}>
              Flow analysis mode
              {inputType !== 'flow_diagram' && (
                <span className={styles.fieldHintInline}> — select Flow diagram above to enable</span>
              )}
            </label>
            <div className={`${styles.kbVersionGroup} ${inputType !== 'flow_diagram' ? styles.kbVersionGroupDisabled : ''}`}>
              {([
                ['screen', 'Screen analysis'],
                ['flow', 'Flow analysis'],
              ] as const).map(([v, label]) => (
                <button
                  key={v}
                  type="button"
                  className={`${styles.kbVersionBtn} ${flowMode === v ? styles.kbVersionBtnActive : ''}`}
                  onClick={() => inputType === 'flow_diagram' && setFlowMode(v)}
                  disabled={disabled || inputType !== 'flow_diagram'}
                >
                  {label}
                </button>
              ))}
            </div>
            <p className={styles.fieldHint}>
              {flowMode === 'screen'
                ? 'One pass per screen. Thorough per-screen findings, informed by the flow. Takes longer with more screens.'
                : 'One pass for the whole journey. Faster. Finds issues that span multiple screens but may miss finer per-screen detail.'}
            </p>
          </div>

        </div>
      </div>

      {/* ── Submit ── */}
      <div className={styles.submitCard}>
        <div className={styles.submitText}>
          <h3>Ready to analyze.</h3>
          <p>High-severity findings only, ranked by likely user impact. Analysis typically takes 2–3 minutes.</p>
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
