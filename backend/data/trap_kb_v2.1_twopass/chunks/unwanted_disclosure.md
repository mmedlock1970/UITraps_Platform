<!-- GENERATED from trap_kb_v2.1.md — do not edit; regenerate on any master edit -->
### TRAP: UNWANTED DISCLOSURE *(ratified 2026-07-04)*

**Definition.** The system exposes personal data or behavior in a way that is harmful, embarrassing, or unexpected. Two dimensions: *remote/digital* (data shared to third parties, opt-out defaults, location surfacing, history visible to household members) and *physical/real-time* (a notification read aloud in a crowded room, sensitive content on a visible screen, unsilenceable sounds). The governing test is contextual integrity: not "is this data secret?" but "does this flow match what the user would expect given the context in which they shared it?"

**Boundary.** IS: any communication of user data/behavior the user did not intend, by either dimension. NOT present when: explicit, fully-informed consent covers what/when/whom; disclosure is to the user themselves in a private context; data is aggregated and anonymized beyond individual identifiability. Caused by **Bad Prediction** when a context misjudgment surfaces private content (confirm the prediction error). Co-occurs with **Feedback Failure** when sharing happens *undisclosed* (disclosed-but-unwanted lacks that co-Trap). Deliberate business-driven over-sharing (opt-out defaults, opaque collection) flags additionally as potential dark pattern.

**Detection procedure (pass one — flag, do not filter).** *Unit: whole-artifact + settings audit.*
1. Trace every feature that collects, stores, or surfaces user data; for each flow ask: would the user expect this destination, given where they shared it?
2. Audit defaults: flag every opt-out (rather than opt-in) sharing default, with sensitivity class (location, health, finance, behavior = highest).
3. Physical-dimension sweep against C3: flag audio announcements of content, always-visible sensitive surfaces on shared/ambient devices, unsilenceable sounds — any output the user cannot gate in social contexts.
4. Flag exports, saves, and shares that bundle more than users would expect — e.g., a saved meeting chat log that silently includes private messages; the expectation is set by what the user thinks they are sharing, not by what the feature technically captures.
5. Flag consent asked at moments the user can't understand what they're consenting to.

**Disconfirmation (pass two).** Per Boundary (a)–(c).

**Severity.** High baseline for sensitive categories (health, location, finance, sexuality) — inherently high-consequence; High when disclosure is irreversible and harmful (irreversibility is the norm for disclosure — what varies is the harm branch; grade by it); Medium for social embarrassment (spoiled gifts — which still drove users to competitors). Anchor: the partner-site purchase feed (card example): embarrassment-grade harm, Medium by harm branch — yet irreversible, and it drove a class action and feature shutdown; harm-branch grading is not a reason to under-weigh business risk in the description. Escalators: C3 (shared/ambient devices, public contexts).

**Assessability & Confidence.** High confidence for structural findings: opt-out defaults on sensitive data, ungated audio output of content (artifact/settings suffice). Whether a specific flow violates expectations: Medium confidence, gated by C3 social context — promotion path: context-of-use inquiry. Static single screens: the settings/defaults audit is not assessable — declare "Not assessable from this artifact — settings audit or flows would settle"; physical-dimension flags (visible sensitive surfaces, audio indicators) remain assessable. Context axis: C3 is primary (the privacy clause exists for this Trap); C1 norms shape expectation.

**Attribution.** Bad Prediction upstream (confirm). Feedback Failure co-occurrence (undisclosed sharing). System Amnesia tension: its remediation (retain more) raises this Trap's stakes — cross-note both ways.

**Report fragments.** Finding: "[Feature/setting] shares [data] with [audience] on an opt-out basis / in a context where users are unlikely to expect or intend it." Why it matters: "Users cannot prevent disclosures they don't know about — consequences run from embarrassment to legal liability, and disclosure cannot be undone."

**Remediation.** Defaults must match what fully-informed users would choose. Explicit opt-in for sensitive behavioral data; consent at moments of genuine understanding. For ambient/shared devices: granular control over what surfaces, when, and through which channel. Ask of every collection point: where could this surface, and would the user accept that?
