---
name: draft
description: "Draft academic prose for philosophy or humanities papers with proper scholarly apparatus. Use when the user wants to write, draft, or outline a paper, thesis chapter, or journal article. Supports analytic, continental, and comparative philosophy structures."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Academic Writing (Calliope)

Draft clear, well-argued academic prose with proper scholarly apparatus. Always build the argument skeleton first, then write prose section by section.

## Language Rule

Match the user's language. If the user writes in Chinese, respond in Chinese. If in English, respond in English. When writing academic prose, use the language the user specifies for their paper. When mixing languages is appropriate, follow the user's lead.

## Entry Point Routing

- **Starting from scratch** (user has a topic/question but no text) -> Begin at Step 1 (Argument Skeleton).
- **Existing draft or outline** (user already has text and wants to improve it) -> Skip to Step 2 (Prose Expansion). Read the existing text, identify structural and argumentative issues, then refine through surgical edits rather than rewriting from zero.
- **Expanding an outline** (user has bullet points or notes) -> Begin at Step 1, using their outline as the starting material for skeleton construction.
- **Skeleton already confirmed** (user previously completed Step 1 and is returning) -> Read `reviews/[project-name]/argument-skeleton.md` and proceed to Step 2.

---

## Step 1 — Argument Skeleton (Build + Logic Pre-Review)

**Goal:** Establish and validate the paper's logical structure BEFORE writing any prose. This step produces a self-contained skeleton that is reviewed for logical soundness. No prose is written during this step.

### 1.1 Gather Inputs

- **Read `reviews/[project-name]/INDEX.md`** (if exists) first — get an overview of all available literature, commentaries, and sources. Use the index to plan which bib entries and files to load, avoiding unnecessary full-file reads.
- Read [writing-standards.md]($CLAUDE_PLUGIN_ROOT/docs/references/writing-standards.md) to select the discipline-specific template (analytic / continental / comparative).
- Read `reviews/[project-name]/research-proposal.md` (if exists) for the research question, methodology, and argument directions.
- Read `reviews/[project-name]/literature-review-final.md` (if exists) for the scholarly landscape.
- **For `literature-all.bib`**: Use Grep to selectively read specific entries based on INDEX.md, rather than loading the entire file. Only load full bib if the project has fewer than ~30 entries.
- Scan for `commentary-*.md` files (see "Integrating Text Commentary Outputs" below) and note available primary-text analyses.

### 1.2 Build the Skeleton

For each section of the paper, produce:

```
## Section [N]: [Title]

CLAIM: [one sentence — what this section argues]
EVIDENCE: [key sources from literature-all.bib that support this claim]
COUNTERARGUMENT: [the strongest objection to this claim]
REBUTTAL: [how the paper responds to the objection]
COMMENTARY: [relevant commentary-*.md file, if any]
FUNCTION: [what role this section plays in the overall argument — e.g., "establishes premise 1", "addresses primary objection", "synthesizes positions"]
```

The skeleton must show how each section connects to the thesis and to adjacent sections. The overall flow should be visible at a glance.

### 1.3 Logic Pre-Review

After constructing the skeleton, perform a self-audit by checking:

1. **Completeness**: Does the skeleton address the full research question? Are there missing dimensions?
2. **Logical flow**: Does each section's CLAIM follow from the previous section? Are there gaps or leaps?
3. **Premise → Conclusion validity**: Do the accumulated claims actually support the thesis?
4. **Counterargument fairness**: Is each COUNTERARGUMENT the strongest version of the objection (Principle of Charity)?
5. **Evidence sufficiency**: Does every CLAIM have at least one source in EVIDENCE? Flag any unsupported claims.
6. **Redundancy**: Are any two sections making the same argument? Can they be merged?

Output the audit as a brief report appended to the skeleton:

```
─── LOGIC PRE-REVIEW ───

✅ Logical flow: Sections connect coherently
⚠️ Gap detected: Section 3 → 4 requires a bridging argument about [X]
❌ Unsupported claim: Section 5 CLAIM has no entry in literature-all.bib
✅ Counterarguments: All apply Principle of Charity
⚠️ Redundancy: Section 2 and Section 6 overlap on [concept] — consider merging

VERDICT: [Ready for prose / Needs revision]
```

### 1.4 User Confirmation Gate

**Present the skeleton + logic pre-review to the user.** Then STOP and WAIT.

The user may:
- **Approve** -> Proceed to Step 2
- **Request changes** -> Revise the skeleton and re-run the logic pre-review
- **Reject and restart** -> Go back to `/research-design` or restructure from scratch

**Do NOT proceed to Step 2 without explicit user confirmation.** This is the most important gate in the entire workflow.

#### Autonomous Mode Override

When running inside `/autopilot` with `AUTONOMOUS MODE: true` and the logic pre-review verdict is "Ready for prose" (zero ❌ items):
- Skip the confirmation gate and proceed directly to Step 2
- Log: "Autopilot: skeleton auto-approved (logic pre-review clean)"

If the logic pre-review has ANY ❌ items, **always pause** regardless of autonomous mode — structural issues require human judgment.

### 1.5 Save and Archive

1. **Save the confirmed skeleton** to `reviews/[project-name]/argument-skeleton.md`.
2. **Archive this version**:
   ```bash
   mkdir -p "reviews/[project-name]/archive"
   cp "reviews/[project-name]/argument-skeleton.md" \
      "reviews/[project-name]/archive/argument-skeleton-v[N]-YYYY-MM-DD.md"
   ```

If this is a revision of an existing skeleton (e.g., after returning from `/peer-review`), increment the version number. This preserves the evolution of the paper's logical structure — each archived version documents how the argument was reorganized and why.

---

## Step 2 — Prose Expansion

**Goal:** Transform the confirmed skeleton into polished academic prose, section by section.

**Prerequisite:** Step 1 is complete and the user has confirmed the skeleton. If `argument-skeleton.md` exists in the workspace, read it and use it as the structure guide.

### 2.1 Section-by-Section Drafting

Work through one section at a time, following the skeleton's structure:

1. **Brainstorm**: Identify the key points for the section based on its CLAIM, EVIDENCE, and FUNCTION
2. **User curates**: Present the points; user decides what to keep/remove/combine
3. **Draft the section**: Write the prose
   - Every paragraph makes ONE clear claim with evidence or reasoning
   - Weave citations naturally — never dump without engagement
   - Integrate `commentary-*.md` analyses where the skeleton marked COMMENTARY (see "Integrating Text Commentary Outputs")
4. **Refine**: Surgical edits, not full rewrites

### 2.2 Writing Standards

- **Citation integration**: Read [citation-guide.md]($CLAUDE_PLUGIN_ROOT/docs/references/citation-guide.md) for the user's preferred format.
- **Academic register**: Precise, discipline-appropriate vocabulary. Define jargon on first use. Prefer active voice. Be concise.
- **Transitions**: Each section must explicitly connect to the previous one, following the FUNCTION defined in the skeleton.

### 2.3 Save Output

Save completed sections to `reviews/[project-name]/paper-draft.md`. For complete papers, offer to export as .docx via pandoc.

## Using Claudistotle Literature Review Output

When a literature review has been generated by `/literature-review`, leverage its outputs:

- **Read `literature-all.bib`** for citation data — use BibTeX entries for (Author Year) in-text citations
- **Read `note` fields** in BibTeX entries for paper summaries (CORE ARGUMENT, RELEVANCE, POSITION)
- **Read `literature-review-final.md`** for the synthesized scholarly landscape
- **Read `research-proposal.md`** (if generated by `/research-design`) for the research question and methodology

**Citation integrity**: Only cite papers present in the `.bib` files. Do not fabricate references. If a citation is needed that isn't in the bibliography, flag it for the user to verify or run a supplementary `/literature-review` search.

## Integrating Text Commentary Outputs

When `commentary-*.md` files exist in the workspace, they contain close readings of primary texts produced by `/text-commentary`. These are valuable raw material for the draft.

### Protocol

1. **Scan on startup**: Use Glob to find all `reviews/[project-name]/commentary-*.md` files.
2. **Build a commentary index**: For each file, extract:
   - The source text being analyzed
   - The key logical structure identified (from the annotation phase)
   - The core argument of the commentary (from the introduction section)
   - Key philosophical concepts discussed
3. **Present the index** to the user during skeleton construction:
   ```
   Available commentaries:
     📝 commentary-mythe-de-sisyphe-ch1.md — Camus's absurd reasoning; concepts: absurd, suicide, philosophical method
     📝 commentary-etranger-opening.md — Meursault's indifference; concepts: alienation, authenticity
   ```
4. **Integrate during prose writing**: When a section's argument touches concepts covered by a commentary:
   - Draw on the commentary's analysis as primary-text evidence
   - Reference the specific textual passages the commentary identified
   - Use the logical structure the commentary uncovered to support your argument
   - Add a footnote: "See close reading of [text], §[section]" to credit the analytical work
5. **Never copy verbatim** from commentary files. Synthesize and adapt the analysis to serve the draft's argument.

### When no commentaries exist

Simply skip this step. The draft workflow works fully without commentaries — they are an optional enrichment layer.

## Failure Modes to Avoid

- **Throat-clearing**: First paragraph should state the problem and thesis, not spend 500 words warming up.
- **Assertion without argument**: Every claim needs supporting reasoning or evidence.
- **Hedge overdose**: "It seems that perhaps one might argue..." — be direct. State your claim, then qualify if needed.
- **Citation dump**: Citing 5 sources in one sentence without engaging with any of them.

## Example

User: "Help me draft a paper comparing Confucian ren and Aristotelian phronesis."

**Step 1 response:** Present a full argument skeleton with CLAIM/EVIDENCE/COUNTERARGUMENT/REBUTTAL/FUNCTION for each section. Run the logic pre-review. Present the skeleton + audit to the user and WAIT for confirmation.

**Step 2 response** (after user confirms): Work through sections one at a time. For each section, brainstorm key points, let user curate, draft prose, then refine through surgical edits.

## References

| File | When to read |
|------|-------------|
| [writing-standards.md]($CLAUDE_PLUGIN_ROOT/docs/references/writing-standards.md) | Structuring a paper, prose style, or navigating Chinese/English writing conventions |
| [citation-guide.md]($CLAUDE_PLUGIN_ROOT/docs/references/citation-guide.md) | Formatting citations (APA, Chicago, MLA) or citing classical texts |
| [philosophical-methods.md]($CLAUDE_PLUGIN_ROOT/docs/references/philosophical-methods.md) | Applying a specific research method |
| [research-pipeline.md]($CLAUDE_PLUGIN_ROOT/docs/references/research-pipeline.md) | Detailed guidance for argument skeleton construction |

## Quality Checklist

### After Step 1 (Skeleton)

- [ ] Every section has CLAIM, EVIDENCE, COUNTERARGUMENT, REBUTTAL, FUNCTION
- [ ] Logic pre-review completed with no unresolved ❌ items
- [ ] User explicitly confirmed the skeleton
- [ ] Skeleton saved to `reviews/[project-name]/argument-skeleton.md`

### After Step 2 (Prose)

- [ ] Every claim has supporting argument or evidence
- [ ] Counterarguments are addressed, not ignored
- [ ] Citations follow the user's preferred format consistently
- [ ] Prose is clear, direct, and free of unnecessary hedging
- [ ] Structure matches the disciplinary convention
- [ ] Only cites papers from verified sources (`.bib` files or user-provided)
- [ ] Commentary integrations marked with footnotes where applicable
- [ ] Draft is saved to `reviews/[project-name]/paper-draft.md`

---

## Stage Completion Protocol

### After Step 1 Completion (Skeleton Confirmed)

```
═══════════════════════════════════════════════════
✅ Stage Complete: Argument Skeleton (/draft Step 1)

📄 Output:
   • argument-skeleton.md ([N] sections)
   • archive/argument-skeleton-v[N]-YYYY-MM-DD.md (archived)

📍 Current Position: /draft Step 1 ✅

➡️ Next Step: /draft Step 2 (Prose Expansion)
   Expand skeleton into formal academic prose section by section.

💡 Tip: Ready to proceed to Step 2? Or need to adjust skeleton first?
═══════════════════════════════════════════════════
```

### After Step 2 Completion (Full Draft)

```
═══════════════════════════════════════════════════
✅ Stage Complete: Paper Draft (/draft Step 2)

📄 Output: paper-draft.md ([wordcount] words)
📍 Current Position: /draft Step 2 ✅

➡️ Next Step: /claudistotle:validate (Mode B — Citation Integrity Check)
   Verify all citations have corresponding BibTeX entries.

═══════════════════════════════════════════════════
```

### Update PROGRESS.md

Update `reviews/[project-name]/PROGRESS.md`:
- After Step 1: Stage → `/draft` Step 1 Complete | Next: Step 2
- After Step 2: Stage → `/draft` Step 2 Complete | Next: `/validate` Mode B
- **Completed Milestones** → Append corresponding record
- **Progress History** → Append status change

---

**Next step:** After Step 2, run `/claudistotle:validate` (Mode B) to check citation integrity, then use `/claudistotle:peer-review` to simulate rigorous review and iteratively strengthen the paper.

---

## Machine-Readable Exit Signal

As the **last line** of output, append the appropriate signal:

**After Step 1:**
```
<!-- STAGE_EXIT: PASS:SKELETON_APPROVED -->       (skeleton confirmed, ready for Step 2)
<!-- STAGE_EXIT: PAUSE:SKELETON_NEEDS_REVIEW -->   (logic pre-review has ❌ items, needs user)
```

**After Step 2:**
```
<!-- STAGE_EXIT: PASS:DRAFT_COMPLETE -->            (full draft written)
```

These signals are used by `/autopilot` for auto-advance decisions.
