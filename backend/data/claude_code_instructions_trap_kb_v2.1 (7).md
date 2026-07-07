# Instructions: Integrate trap\_kb\_v2.1 into the UI Traps Analyzer

You are working on an existing tool that analyzes UI artifacts (screenshots, flows) against a "UI Tenets \& Traps" knowledge base (KB). The tool currently: loads one KB file the user selects, injects it into a single Claude API call with the artifact, and returns a structured report. It runs locally and as a web-hosted version (Railway, synced via GitHub).

A new KB generation has been added to the repo. Your job is four tasks: (1) clean the system prompt of rules that conflict with the new KB, (2) add a two-pass analysis mode, (3) add prompt caching, (4) add run logging. Do them in that order. Task 1 must be finished before anything is run or tested.

\---

## Context: the new KB files

The repo now contains (do not edit any of these files — they are generated/authored elsewhere):

**Out of scope:** `UI\_Tenets\_Traps` in the same data folder drives a separate chatbot feature. Do not modify, rename, or delete it, and do not include it as a selectable KB in the analyzer's KB picker if it isn't already excluded.

* `trap\_kb\_v1.0.md` — legacy thin KB (trap names, definitions, one example each)
* `trap\_kb\_v2.0.md` — the previously deployed KB (may still be named `trap\_knowledge\_base\_v2.md`; if so, rename it to `trap\_kb\_v2.0.md` and update any references)
* `trap\_kb\_v2.1.md` — the new master KB. Single file. Contains global rules (G1–G8), a severity/confidence system, a context intake schema (C1–C4), a taxonomy index, 27 trap chunks, and authoring standards. It is self-instructing: all evaluative logic lives in this file.
* `trap\_kb\_v2.1\_twopass/` — the same v2.1 content pre-split for a two-pass process:

  * `pass1\_detection\_pack.md` (\~9K tokens) — detection procedures for all 27 traps + the subset of global rules and the context schema that pass one needs
  * `pass2\_core\_pack.md` (\~3.5K tokens) — full global rules, severity/confidence system, taxonomy index
  * `chunks/\*.md` — one file per trap (\~1.2K tokens each), full adjudication detail
  * `manifest.json` — maps trap names → chunk files; also records the source master file

Design intent you must preserve: **the KB carries all evaluation rules; the system prompt carries only mechanics** (how to load files, what output envelope to emit). When the KB and the prompt disagree about how to evaluate, that is a bug in the prompt.

\---

## Task 1 — Verify prompts.py is mechanics-only, and remap output vocabulary (lightweight; do first)

The repo was built under the rule "all evaluation content lives in the KBs, prompts.py carries only procedural rules" — and `trap\_kb\_v2.0.md`'s own Architecture Notes confirm this division. So expect this task to be a verification pass plus a vocabulary remap, not surgery. Verify that none of the following appears in the system prompt or any prompt template, and remove it only where drift has occurred:

1. **The priority ordering that puts "minimize false alarms" first.** The new KB's global rules define the analysis discipline; the prompt must not impose any detection-priority ordering at all.
2. **Any instruction to apply disconfirmation before detection** (e.g., "Apply disconfirmation criteria FIRST"). The new KB uses the opposite order (detect permissively, then adjudicate) and states this itself in rule G2.
3. **The Tier 1 / Tier 2 / Tier 3 vocabulary and the `testable: false` mechanism.** The new KB replaces these with: confidence labels `Confirmed / Probable / Flagged`, and two distinct not-assessable labels: `"Not assessable from this artifact — \[what would settle it]"` and `"Not assessable without user context — \[what field would settle it]"`, plus `"Not present"`. If the web UI renders tier or testable fields, map/rename them to the new labels rather than deleting the UI feature.
4. **Any per-trap evaluative content that migrated into the prompt over time** (severity rules, trap disambiguation, "do not under-flag" warnings). All of that now lives in the KB.

Keep in the system prompt: output envelope/JSON schema the front end depends on, file-handling mechanics, formatting/few-shot examples of the *output structure* only (strip any evaluative reasoning from the examples), and safety/robustness boilerplate.

The one place old evaluation semantics legitimately leak into mechanics — and where the real work of this task is expected — is the output contract: v2.0's rules route findings into fields using Tier and `testable` vocabulary, so the prompt's few-shot format examples and the web UI's display labels almost certainly use them. Remap those per item 3 above. Field names in the JSON can stay if the front end depends on them; the *labels shown to users* and the *vocabulary in format examples* must switch to the new terms.

The new KB's report structure (its rule G8) has three sections: **Issues** (each with plain-language description, severity Critical/High/Medium/Low, confidence, fix, and a closing trap line), **Worth a closer look**, and **Coverage notes**. If the existing output JSON has fields like `confirmed\_findings` / `potential\_issues` / `flagged\_for\_human\_review` / `traps\_checked\_not\_found`, map them: Issues → the confirmed/primary findings field; Worth a closer look → the review/potential field; Coverage notes → the checked-not-found field. Preserve the front-end contract; change the semantics and labels, not the plumbing, unless the plumbing prevents faithful mapping — in that case extend the schema additively.

Also remove any auto-append behavior tied to the old KB (e.g., automatically adding certain traps to `traps\_checked\_not\_found`). The new KB handles coverage in its Coverage notes rules.

## Task 2 — Add a two-pass analysis mode

**KB picker registry and deprecation (do first within this task).** The picker currently offers: v1, v2, "both v1 and v2", and an old KB also called "v2.1" (predating this work — NOT the new `trap\_kb\_v2.1.md`). Changes:

* Registry becomes: `trap\_kb\_v1.0.md` (label "v1.0 — card deck"), `trap\_kb\_v2.0.md` (label "v2.0 — legacy"), `trap\_kb\_v1.1.md` (label "v1.1"), `trap\_kb\_v2.1.md` (label "v2.1").
* **Deprecate the old v2.1: rename its file to `trap\_kb\_v2.1\_legacy\_DEPRECATED.md`, move it to an `archive/` folder, and remove its picker entry.** This name-collision fix is mandatory before anything else in this task — otherwise "v2.1" is ambiguous in the picker and in all logs. Add a note to the run log documentation: log rows before this change's deploy date that say "v2.1" refer to the legacy file.
* Keep the existing "both v1 and v2" merged mode functioning if it exists (regression), but label it "legacy — merged" and exclude it from the comparison feature below; merged KBs are not a valid experimental condition.

**Comparison runs (new feature).** The user must be able to select TWO KBs (typically v1.1 and v2.1) plus a mode for each (single or twopass) and run them against the same artifact. Requirements:

* The two analyses run as **fully independent API contexts** — same artifact, same user-context block, no shared state, neither output visible to the other.
* After both complete, a third call generates a comparison report that sees ONLY the two final reports (not the artifact, not the KBs). Its required sections: traps reported (side-by-side with severity and confidence per condition); severity differences; confidence differences; reported-not-present per condition; reported-not-assessable per condition with stated reasons; findings unique to one condition.
* Persist all three outputs together; log the two analysis calls per Task 4 with a shared `comparison\_id` field so paired runs are recoverable from the log.

Add a mode switch so an analysis can run as `single` (current behavior: one call, whole KB file) or `twopass`. Expose it wherever the KB is currently selected (CLI flag and web UI control). Both modes must remain available permanently — they are experimental conditions, not a migration.

Two-pass recipe:

**Call 1 (detection).**

* System prompt: mechanics only (per Task 1).
* Content: `pass1\_detection\_pack.md`, then the artifact(s), then the user-supplied context (goals, user population, context of use — whatever the tool collects today).
* Instruction to the model (the pack's header already says this; reinforce in the user turn): run every detection procedure; emit one line per candidate in the format `TRAP | screen | element(s) | triggering condition(s)`; no prose, no filtering, no severity.
* Parse the output: extract trap names, match case-insensitively against the `trap` names in `manifest.json` (exact names — e.g., `Unnecessary Step(s)` includes the `(s)`), dedupe. **Parse tolerantly:** models may render candidate lines as a markdown table (leading `|`), with bullets, numbering, or bold — strip such decoration and compare on letters only (e.g., normalize both sides by removing non-alphabetic characters) rather than raw string equality. Log and surface any line whose trap name still fails to match rather than silently dropping it — a zero-chunks-loaded pass two is a broken run and must be treated as an error, not proceeded with.

**Call 2 (adjudication).**

* Content, in this order: `pass2\_core\_pack.md`, then the chunk file for every trap flagged in call 1 (from `chunks/` per the manifest), then the artifact(s), then the user context, then the full raw candidate list from call 1.
* Instruction: adjudicate per the pack's header (it specifies the order of operations) and emit the final report in the output envelope.
* The pass-2 pack contains a taxonomy index of all 27 traps, so the model can re-route a finding to a trap whose chunk wasn't loaded; this is acceptable — the index one-liners are sufficient for routing, and the report will say so. Do not build a third call for this now.

Edge cases: if call 1 returns zero candidates, still run call 2 with just the core pack (it must produce the Coverage notes section and any "worth a closer look" entries); if call 1 flags more than \~12 traps, load all flagged chunks anyway (worst case is still smaller than the old monolith).

**Pack generation is the tool's job — for ANY KB master, not just v2.1:** the `trap\_kb\_v2.1\_twopass/` and `trap\_kb\_v1.1\_twopass/` folders in the repo are first, externally generated copies — treat them as caches, not sources. Implement one regeneration function that rebuilds a `<master\_basename>\_twopass/` folder from any KB master file whenever that master's content has changed (compare a stored hash; regenerate on mismatch at startup or before a twopass run). Key the splitter off structural headings, not hard-coded trap counts or names — masters differ (v2.1 has 27 traps; v1.1 has 26 and a slightly different chunk layout). Splitting spec, all boundaries are literal headings in the master:

* `pass1\_detection\_pack.md` = the G1, G2, G6, and G7 rules (from `## GLOBAL RULES`) + the entire `## CONTEXT INTAKE SCHEMA` section + for each `### TRAP:` chunk: the trap's name, its one-liner from `## TAXONOMY INDEX`, and its pass-one detection content — everything from the first of `\*\*Definitional conditions` or `\*\*Detection procedure` (whichever the chunk has) up to `\*\*Disconfirmation`. Prepend the pass-one role header found in the existing generated files.
* `pass2\_core\_pack.md` = the full `## GLOBAL RULES` section + `## SEVERITY \& CONFIDENCE` + `## TAXONOMY INDEX`, with the pass-two role header from the existing generated file.
* `chunks/<slug>.md` = each full `### TRAP:` chunk, slug = lowercased trap name, non-alphanumerics → underscores.
* `manifest.json` = trap name → chunk file mapping plus the master's hash.
Every generated file starts with a `GENERATED — do not edit` comment naming its master. The user edits only masters; packs must never be hand-edited, and regeneration must be deterministic (same master in, same packs out). Verify your generator reproduces BOTH shipped folders (`trap\_kb\_v2.1\_twopass/` and `trap\_kb\_v1.1\_twopass/`) from their masters before wiring it in.

## Task 3 — Prompt caching

For both modes, structure API requests so all static content precedes all per-analysis content, and mark the static prefix cacheable using Anthropic prompt caching (`cache\_control: {"type": "ephemeral"}` on the last static content block). Static = system prompt + KB file(s)/pack(s). Variable = artifact images + user context + candidate list. In twopass mode, cache call 1's pack and call 2's core pack; the candidate chunk set varies per analysis, so place chunks after the cached core pack and don't mark them cacheable. Consult the current Anthropic API docs for minimum cacheable token counts and header requirements rather than assuming.

## Task 4 — Run logging

Append one JSONL record per API call to a local log file (and stdout in verbose mode): `run\_id, timestamp, kb\_path, mode, pass (1|2|single), artifact\_id, model, input\_tokens, output\_tokens, cache\_read\_tokens, latency\_ms, num\_candidates (pass 1) / num\_issues (final)`. Token counts come from the API response usage block. This log is the data source for an upcoming evaluation, so field names should be stable once chosen.

\---

## Acceptance checks (run all before declaring done)

1. Single mode with `trap\_kb\_v2.0.md` still runs (regression check — old KB, cleaned prompt).
2. Single mode with `trap\_kb\_v2.1.md` runs and the report contains the three G8 sections mapped into the output envelope, with severity as Critical/High/Medium/Low and confidence as Confirmed/Probable/Flagged. No Tier or `testable` vocabulary anywhere in the output.
3. Twopass mode on a sample screenshot: call 1 emits parseable candidate lines; call 2 loads only the flagged chunks (log the loaded file list); final report renders in the web UI.
4. Twopass with zero candidates (use a deliberately blank/trivial image) still produces a report with Coverage notes.
5. Comparison run (v1.1 twopass vs. v2.1 twopass, same artifact): produces two independent reports plus a comparison document; the log shows both analyses with a shared `comparison\_id`; the picker no longer offers the legacy v2.1, and `archive/trap\_kb\_v2.1\_legacy\_DEPRECATED.md` exists.
6. Grep the codebase for leftover evaluative strings: "false alarm", "Tier 1", "Tier 2", "Tier 3", "testable", "disconfirmation" — none should remain outside the KB files themselves.
7. Log file contains records for every call in checks 1–4 with nonzero token counts, and cache\_read\_tokens is nonzero on the second consecutive run with the same KB.

Do not "improve" the KB files' content while working — if you believe a KB file contains an error, report it; the KB is maintained in a separate authoring process with its own review discipline.

