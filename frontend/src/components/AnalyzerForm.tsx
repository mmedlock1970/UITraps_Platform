import React, { useState, useCallback, useRef, useEffect } from 'react';
import { ContentType, KbVersion, UserContext } from '../api/types';
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
  platform: string; productDomain: string; screenName: string;
  expLevel: string; techSavvy: string; frequency: string; userGoal: string;
  priorProducts: string; userDesc: string; extraContext: string; kbVersion: KbVersion;
}): UserContext {
  const { platform, productDomain, screenName, expLevel, techSavvy,
          frequency, userGoal, priorProducts, userDesc, extraContext, kbVersion } = fields;

  const formatParts = [
    platform && productDomain ? `${platform} — ${productDomain}` : platform || productDomain,
    screenName ? `Screen: ${screenName}` : '',
  ].filter(Boolean);

  const userParts = [
    userDesc ? `Target users: ${userDesc}` : '',
    expLevel ? `Experience with product: ${expLevel}` : '',
    techSavvy ? `Tech savviness: ${techSavvy}` : '',
    frequency ? `Frequency of use: ${frequency}` : '',
    userGoal ? `Outcome: ${userGoal}` : '',
    priorProducts ? `Products they use regularly: ${priorProducts}` : '',
  ].filter(Boolean);

  const designName = screenName.trim() || undefined;

  return {
    users: userParts.join('. '),
    expertise: `${expLevel}${techSavvy ? ` / ${techSavvy}` : ''}`,
    tasks: userGoal,
    format: formatParts.join('. '),
    design_name: designName || undefined,
    contentType: platformToContentType(platform, productDomain),
    extra_context: extraContext || undefined,
    kb_version: kbVersion,
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
  const [url, setUrl] = useState('');
  const [screenName, setScreenName] = useState('');
  const [platform, setPlatform] = useState('');
  const [productDomain, setProductDomain] = useState('');
  const [isDragover, setIsDragover] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Card 2 — User
  const [expLevel, setExpLevel] = useState('');
  const [techSavvy, setTechSavvy] = useState('');
  const [frequency, setFrequency] = useState('');
  const [userGoal, setUserGoal] = useState('');
  const [userDesc, setUserDesc] = useState('');
  const [priorProducts, setPriorProducts] = useState('');

  // Card 4 — Analysis Scope
  const [extraContext, setExtraContext] = useState('');
  const [kbVersion, setKbVersion] = useState<KbVersion>('v2');

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Create and revoke object URLs for image thumbnails
  useEffect(() => {
    const urls = files.map(f => isImageFile(f) ? URL.createObjectURL(f) : '');
    setThumbnailUrls(urls);
    return () => { urls.forEach(u => { if (u) URL.revokeObjectURL(u); }); };
  }, [files]);

  const validate = useCallback((): boolean => {
    const e: Record<string, string> = {};
    if (files.length === 0 && !url.trim()) e.upload = 'Please upload a screenshot or enter a URL';
    if (!screenName.trim()) e.screenName = 'Required';
    if (!platform) e.platform = 'Required';
    if (!productDomain) e.productDomain = 'Required';
    if (!expLevel) e.expLevel = 'Required';
    if (!techSavvy) e.techSavvy = 'Required';
    if (!frequency) e.frequency = 'Required';
    if (!userGoal.trim()) e.userGoal = 'Required';
    setErrors(e);
    return Object.keys(e).length === 0;
  }, [files, url, screenName, platform, productDomain, expLevel, techSavvy, frequency, userGoal]);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (disabled) return;
    if (!validate()) return;
    const context = assembleContext({ platform, productDomain, screenName,
      expLevel, techSavvy, frequency, userGoal, priorProducts, userDesc, extraContext, kbVersion });
    onSubmit({ files, url, context });
  }, [disabled, validate, files, url, platform, productDomain, screenName,
      expLevel, techSavvy, frequency, userGoal, priorProducts, userDesc, extraContext, kbVersion, onSubmit]);

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
              Provide a name for what is being analyzed
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
              Upload screenshots
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
                  <p className={styles.uploadPrimary}><span>Click to upload</span> or drag and drop</p>
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
            Many Traps are only detectable when we understand what users already know,
            what conventions they have learned from other products, and what they are
            trying to accomplish. The more precisely you describe the user, the more
            accurate the analysis.
          </div>

          <div className={`${styles.fieldGrid} ${styles.twoCol}`}>

            <div className={`${styles.field} ${styles.span2}`}>
              <label className={styles.fieldLabel} htmlFor="userDesc">
                Describe the target users
                <span className={styles.opt}>optional</span>
              </label>
              <textarea
                id="userDesc"
                className={styles.textarea}
                rows={2}
                placeholder="e.g., Adults 55+, low tech confidence, first smartphone users. Or: Healthcare professionals, clinical setting, time-pressured."
                value={userDesc}
                onChange={e => setUserDesc(e.target.value)}
                disabled={disabled}
              />
              <p className={styles.fieldHint}>Age, occupation, cognitive load, accessibility needs, domain expertise — anything relevant to how they'll interact with this UI.</p>
            </div>

            <div className={`${styles.field} ${styles.span2}`}>
              <label className={styles.fieldLabel} htmlFor="userGoal">
                <span className={styles.req} />
                Outcome the user is trying to achieve
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
              <p className={styles.fieldHint}>The specific outcome most users are trying to achieve when they reach this screen or flow.</p>
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

          {/* Knowledge base version selector */}
          <div className={styles.field}>
            <label className={styles.fieldLabel}>
              Knowledge base version
            </label>
            <div className={styles.kbVersionGroup}>
              {(['v2', 'v1', 'both'] as KbVersion[]).map(v => (
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
              {kbVersion === 'v1' && 'Previous knowledge engine.'}
              {kbVersion === 'both' && 'Runs two parallel analyses — one with each engine. Results are shown side-by-side with a toggle. Takes roughly twice as long.'}
            </p>
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
