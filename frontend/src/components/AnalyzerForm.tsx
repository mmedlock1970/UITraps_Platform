import React, { useState, useCallback, useRef, useEffect } from 'react';
import { ContentType, KbVersion, UserContext } from '../api/types';
import { FormSnapshot } from '../services/analysisHistory';
import styles from './AnalyzerForm.module.css';

export interface FormSubmitPayload {
  files: File[];
  context: UserContext;
  formSnapshot: FormSnapshot;
}

interface AnalyzerFormProps {
  onSubmit: (payload: FormSubmitPayload) => void;
  disabled?: boolean;
  initialValues?: FormSnapshot;
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
  figmaLink: string; thoroughMode: boolean; reportStyle: 'trap' | 'issues';
  inputType: 'screenshot' | 'video' | 'flow_diagram';
}): UserContext {
  const { platform, productDomain, screenName, expLevel, techSavvy,
          frequency, taskList, priorProducts, userDesc, extraContext, productContext,
          physicalEnv, lighting, gripPosition, attentionalState, kbVersion, selectedTenets,
          verbosity, pass1Model, figmaLink, thoroughMode, reportStyle, inputType } = fields;

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
    priorProducts ? `Experience with similar interfaces: ${priorProducts.charAt(0).toUpperCase() + priorProducts.slice(1)}` : '',
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
    tenet_filter: selectedTenets.length > 0 && selectedTenets.length < ALL_TENETS.length ? selectedTenets : undefined,
    verbosity,
    pass1_model: pass1Model,
    thorough_mode: thoroughMode || undefined,
    report_style: reportStyle,
    input_type: inputType,
    figma_url: (figmaLink.trim() && inputType === 'flow_diagram') ? figmaLink.trim() : undefined,
  };
}

function isImageFile(file: File) {
  return file.type.startsWith('image/');
}

function isVideoFile(file: File) {
  return file.type.startsWith('video/');
}

const INPUT_TYPE_LABELS = {
  screenshot: 'a screenshot',
  video: 'a video',
  flow_diagram: 'a flow diagram',
} as const;

const INPUT_TYPE_CHIP_LABELS = {
  screenshot: 'Screenshot(s)',
  video: 'Video / recording',
  flow_diagram: 'Flow diagram',
} as const;

const FLOW_FILENAME_RE = /flow|diagram|journey|wireflow/i;

function inferFileType(files: File[], figmaLink: string): 'screenshot' | 'video' | 'flow_diagram' {
  if (figmaLink.trim() && files.length === 0) return 'flow_diagram';
  if (files.some(f => isVideoFile(f))) return 'video';
  if (files.some(f => FLOW_FILENAME_RE.test(f.name))) return 'flow_diagram';
  return 'screenshot';
}

export const AnalyzerForm: React.FC<AnalyzerFormProps> = ({ onSubmit, disabled = false, initialValues }) => {
  const iv = initialValues;

  // Card 1 — Interface
  const [files, setFiles] = useState<File[]>([]);
  const [thumbnailUrls, setThumbnailUrls] = useState<string[]>([]);
  const [figmaLink, setFigmaLink] = useState(iv?.figmaLink ?? '');
  const [screenName, setScreenName] = useState(iv?.screenName ?? '');
  const [platform, setPlatform] = useState(iv?.platform ?? '');
  const [productDomain, setProductDomain] = useState(iv?.productDomain ?? '');
  const [productContext, setProductContext] = useState(iv?.productContext ?? '');
  const [isDragover, setIsDragover] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Card 2 — User
  const [expLevel, setExpLevel] = useState(iv?.expLevel ?? '');
  const [techSavvy, setTechSavvy] = useState(iv?.techSavvy ?? '');
  const [frequency, setFrequency] = useState(iv?.frequency ?? '');
  const [tasks, setTasks] = useState<Array<{ name: string; description: string }>>(
    iv?.tasks ?? [{ name: '', description: '' }]
  );
  const [userDesc, setUserDesc] = useState(iv?.userDesc ?? '');
  const [priorProducts, setPriorProducts] = useState(iv?.priorProducts ?? '');

  // Card 3 — Use Environment
  const [physicalEnv, setPhysicalEnv] = useState(iv?.physicalEnv ?? '');
  const lighting = iv?.lighting ?? '';
  const [gripPosition, setGripPosition] = useState(iv?.gripPosition ?? '');
  const [attentionalState, setAttentionalState] = useState(iv?.attentionalState ?? '');

  // Card 4 — Additional Context
  const [extraContext, setExtraContext] = useState(iv?.extraContext ?? '');

  // Card 5 — Analysis Scope
  const [kbVersion, setKbVersion] = useState<KbVersion>(iv?.kbVersion ?? 'v2');
  const [selectedTenets, setSelectedTenets] = useState<string[]>(iv?.selectedTenets ?? [...ALL_TENETS]);
  const [verbosity, setVerbosity] = useState<'brief' | 'standard'>(iv?.verbosity ?? 'standard');
  const [pass1Model, setPass1Model] = useState<'sonnet' | 'haiku'>(iv?.pass1Model ?? 'sonnet');
  const [thoroughMode, setThoroughMode] = useState(iv?.thoroughMode ?? false);
  const [reportStyle, setReportStyle] = useState<'trap' | 'issues'>('trap');
  const [lockedInputType, setLockedInputType] = useState<'screenshot' | 'video' | 'flow_diagram' | null>(iv?.lockedInputType ?? null);
  const [autoDetectedType, setAutoDetectedType] = useState<'flow_diagram' | null>(null);
  const inputType = lockedInputType ?? autoDetectedType ?? inferFileType(files, figmaLink);

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

  const moveTask = useCallback((index: number, direction: -1 | 1) => {
    setTasks(prev => {
      const next = [...prev];
      const target = index + direction;
      if (target < 0 || target >= next.length) return prev;
      [next[index], next[target]] = [next[target], next[index]];
      return next;
    });
  }, []);

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState(false);

  // Reset manual override and auto-detection when all files and figma link are cleared
  useEffect(() => {
    if (files.length === 0 && !figmaLink.trim()) {
      setLockedInputType(null);
      setAutoDetectedType(null);
    }
  }, [files, figmaLink]);

  // Detect flow diagrams from image aspect ratio (wide images = likely a flow)
  useEffect(() => {
    const singleImage = files.length === 1 && isImageFile(files[0]) ? files[0] : null;
    if (!singleImage) { setAutoDetectedType(null); return; }
    const url = URL.createObjectURL(singleImage);
    const img = new Image();
    img.onload = () => {
      setAutoDetectedType(img.width > img.height * 1.8 ? 'flow_diagram' : null);
      URL.revokeObjectURL(url);
    };
    img.onerror = () => { setAutoDetectedType(null); URL.revokeObjectURL(url); };
    img.src = url;
    return () => URL.revokeObjectURL(url);
  }, [files]);

  // Create and revoke object URLs for image thumbnails
  useEffect(() => {
    const urls = files.map(f => isImageFile(f) ? URL.createObjectURL(f) : '');
    setThumbnailUrls(urls);
    return () => { urls.forEach(u => { if (u) URL.revokeObjectURL(u); }); };
  }, [files]);

  const validate = useCallback((): Record<string, string> => {
    const e: Record<string, string> = {};
    const figmaFlowProvided = inputType === 'flow_diagram' && figmaLink.trim().length > 0;
    if (files.length === 0 && !figmaFlowProvided) e.upload = 'Please upload a screenshot, video, or PDF';
    if (!screenName.trim()) e.screenName = 'Required';
    if (!platform) e.platform = 'Required';
    if (!productDomain) e.productDomain = 'Required';
    if (!expLevel) e.expLevel = 'Required';
    if (!userDesc.trim()) e.userDesc = 'Required';
    if (!tasks[0]?.description.trim()) e.userGoal = 'Required';
    setErrors(e);
    return e;
  }, [files, figmaLink, lockedInputType, screenName, platform, productDomain, expLevel, userDesc, tasks]);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (disabled) return;
    const errs = validate();
    if (Object.keys(errs).length > 0) {
      setFormError(true);
      const fieldOrder = ['screenName', 'upload', 'platform', 'productDomain', 'userDesc', 'expLevel', 'userGoal'];
      const idMap: Record<string, string> = {
        screenName: 'screenName', upload: 'uploadZone',
        platform: 'platform', productDomain: 'productDomain',
        userDesc: 'userDesc', expLevel: 'expLevel', userGoal: 'userGoal',
      };
      const firstField = fieldOrder.find(f => errs[f]);
      if (firstField) {
        setTimeout(() => {
          const el = document.getElementById(idMap[firstField]);
          if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            if (typeof (el as HTMLInputElement).focus === 'function') (el as HTMLInputElement).focus();
          }
        }, 50);
      }
      return;
    }
    setFormError(false);
    const formSnapshot: FormSnapshot = {
      figmaLink, screenName, platform, productDomain, productContext,
      expLevel, techSavvy, frequency, tasks, userDesc, priorProducts,
      physicalEnv, lighting, gripPosition, attentionalState, extraContext,
      kbVersion, selectedTenets, verbosity, pass1Model, thoroughMode, lockedInputType,
    };
    const context = assembleContext({ platform, productDomain, screenName,
      expLevel, techSavvy, frequency, taskList: tasks, priorProducts, userDesc, extraContext, productContext,
      physicalEnv, lighting, gripPosition, attentionalState, kbVersion, selectedTenets,
      verbosity, pass1Model, figmaLink, thoroughMode, reportStyle, inputType });
    onSubmit({ files, context, formSnapshot });
  }, [disabled, validate, files, figmaLink, screenName, platform, productDomain, productContext,
      expLevel, techSavvy, frequency, tasks, userDesc, priorProducts, extraContext,
      physicalEnv, lighting, gripPosition, attentionalState, kbVersion, selectedTenets,
      verbosity, pass1Model, thoroughMode, reportStyle, lockedInputType, onSubmit]);

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
              Give a name to this analysis
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
              id="uploadZone"
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
                  <p className={styles.uploadPrimary}><span>Click to upload screenshot</span> or drag and drop</p>
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
            <div className={styles.uploadDivider}>or include a Figma design link</div>
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
            {(files.length > 0 || figmaLink.trim()) && (
              <div className={styles.inferredTypeStrip}>
                <span className={styles.inferredTypeLabel}>
                  {figmaLink.trim() && files.length === 0
                    ? 'Figma link detected — will analyze as a flow diagram.'
                    : `Looks like ${INPUT_TYPE_LABELS[inputType]}.`}
                </span>
                {files.length > 0 && (
                  <span className={styles.inferredTypeAlts}>
                    <span className={styles.inferredTypeChangeLabel}>Change to:</span>
                    {(['screenshot', 'video', 'flow_diagram'] as const)
                      .filter(t => t !== inputType)
                      .map(t => (
                        <button
                          key={t}
                          type="button"
                          className={styles.inferredTypeChip}
                          onClick={() => setLockedInputType(t)}
                          disabled={disabled}
                        >
                          {INPUT_TYPE_CHIP_LABELS[t]}
                        </button>
                      ))}
                  </span>
                )}
                {inputType === 'flow_diagram' && files.length === 0 && (
                  <p className={styles.fieldHint} style={{ marginTop: 6 }}>
                    Prototype connections will be extracted automatically. Both per-screen and flow-level analysis will run.
                  </p>
                )}
                {inputType === 'flow_diagram' && files.length > 0 && (
                  <p className={styles.fieldHint} style={{ marginTop: 6 }}>
                    Include all connected screens and their navigation arrows in a single file.
                  </p>
                )}
              </div>
            )}
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
                  <option>Mobile app (iOS / Android)</option>
                  <option>Tablet app</option>
                  <option>Mobile web browser</option>
                </optgroup>
                <optgroup label="Desktop">
                  <option>Desktop web browser</option>
                  <option>Desktop application</option>
                </optgroup>
                <optgroup label="Other devices">
                  <option>Smart TV / streaming device</option>
                  <option>Kiosk / public terminal</option>
                  <option>Wearable or specialty device</option>
                </optgroup>
                <option>Other</option>
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
                <span className={styles.req} />
                Describe the intended users of this interface
              </label>
              <input
                id="userDesc"
                type="text"
                className={`${styles.input} ${errors.userDesc ? styles.inputError : ''}`}
                placeholder="e.g., Adults 55+, low tech confidence, first smartphone users. Or: Healthcare professionals, clinical setting, time-pressured."
                value={userDesc}
                onChange={e => setUserDesc(e.target.value)}
                disabled={disabled}
              />
              <p className={styles.fieldHint}>Age, occupation, accessibility needs, domain expertise — anything relevant to how they'll interact with this UI.</p>
              {errors.userDesc && <p className={styles.fieldError}>{errors.userDesc}</p>}
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
                <option>New users (first time or few sessions)</option>
                <option>Mixed — new and returning</option>
                <option>Mostly returning users</option>
                <option>Long-term regular users</option>
              </select>
              {errors.expLevel && <p className={styles.fieldError}>{errors.expLevel}</p>}
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
                <option value="some">Some — has used a comparable product</option>
                <option value="extensive">Extensive — power user of similar products</option>
              </select>
            </div>

            <div className={styles.field}>
              <label className={styles.fieldLabel} htmlFor="techSavvy">
                Tech savviness
                <span className={styles.opt}>optional</span>
              </label>
              <select
                id="techSavvy"
                className={styles.select}
                value={techSavvy}
                onChange={e => setTechSavvy(e.target.value)}
                disabled={disabled}
              >
                <option value="">— Select one —</option>
                <option>Low — limited tech experience</option>
                <option>Average — comfortable with everyday apps</option>
                <option>High — power user or specialist</option>
              </select>
            </div>

            <div className={styles.field}>
              <label className={styles.fieldLabel} htmlFor="frequency">
                How often will users interact with this product?
                <span className={styles.opt}>optional</span>
              </label>
              <select
                id="frequency"
                className={styles.select}
                value={frequency}
                onChange={e => setFrequency(e.target.value)}
                disabled={disabled}
              >
                <option value="">— Select one —</option>
                <option>One-time or rare</option>
                <option>Occasional — monthly</option>
                <option>Regular — weekly</option>
                <option>Frequent — daily or more</option>
              </select>
            </div>

            <div className={`${styles.field} ${styles.span2}`}>
              <label className={styles.fieldLabel}>
                <span className={styles.req} />
                Describe the user task(s) to evaluate
              </label>
              {tasks.map((task, i) => (
                <div key={i} className={styles.taskRow}>
                  <div className={styles.taskDescRow}>
                    {tasks.length > 1 && (
                      <div className={styles.taskReorderBtns}>
                        <button
                          type="button"
                          className={styles.taskReorderBtn}
                          onClick={() => moveTask(i, -1)}
                          disabled={disabled || i === 0}
                          title="Move up"
                        >▲</button>
                        <button
                          type="button"
                          className={styles.taskReorderBtn}
                          onClick={() => moveTask(i, 1)}
                          disabled={disabled || i === tasks.length - 1}
                          title="Move down"
                        >▼</button>
                      </div>
                    )}
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
              <p className={styles.fieldHint}>
                You can add up to 3 tasks — each additional task increases analysis time.
              </p>
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
                <option value="stationary">Stationary, away from a desk (couch, café, waiting area)</option>
                <option value="moving">On the go — walking, commuting, outdoors, or in a vehicle</option>
                <option value="hands_free">Mounted display, kiosk, or hands-free setting</option>
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
                <option value="handheld">Handheld device — one or two hands, thumbs for input</option>
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
              {selectedTenets.length === ALL_TENETS.length
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
            {selectedTenets.length < ALL_TENETS.length && (
              <button
                type="button"
                className={styles.tenetClearBtn}
                onClick={() => setSelectedTenets([...ALL_TENETS])}
                disabled={disabled}
              >
                Select all Tenets
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

          {/* Report Style */}
          <div className={styles.field}>
            <label className={styles.fieldLabel}>Report style</label>
            <div className={styles.kbVersionGroup}>
              <button
                type="button"
                className={`${styles.kbVersionBtn} ${reportStyle === 'trap' ? styles.kbVersionBtnActive : ''}`}
                onClick={() => setReportStyle('trap')}
                disabled={disabled}
              >
                By Trap
              </button>
              <button
                type="button"
                className={`${styles.kbVersionBtn} ${reportStyle === 'issues' ? styles.kbVersionBtnActive : ''}`}
                onClick={() => setReportStyle('issues')}
                disabled={disabled}
              >
                By Issue
              </button>
            </div>
            <p className={styles.fieldHint}>
              {reportStyle === 'trap' && 'Findings grouped by trap type. Best for understanding which patterns appear in your design.'}
              {reportStyle === 'issues' && 'Findings grouped as individual issues, ranked by severity. Best for a prioritized action list.'}
            </p>
          </div>


        </div>
      </div>

      {/* ── Submit ── */}
      <div className={styles.submitCard}>
        {formError && (
          <p className={styles.formErrorBanner}>
            Please complete all required fields before running the analysis.
          </p>
        )}
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
