---
name: validate
description: "Quality gate between workflow phases. Checks literature coverage, citation integrity, and change record completeness. Use after /claudistotle:literature-review, after /claudistotle:draft, or after /claudistotle:peer-review to catch errors before they propagate."
allowed-tools: Read, Glob, Grep, Bash
---

# Validate (Quality Gate)

Lightweight quality checks that run between workflow phases. Each mode targets a specific transition point in the research pipeline. The goal is to catch errors early — before they compound into wasted effort.

## Language Rule

Match the user's language. If the user writes in Chinese, respond in Chinese. If in English, respond in English.

## Entry Point Routing

Determine the mode based on context:

- **User says "validate" with no qualifier** -> Auto-detect: check which files exist in the workspace and run the most relevant mode.
- **After `/claudistotle:literature-review`** or user mentions literature/coverage -> Mode A (Literature Coverage).
- **After `/claudistotle:draft`** or user mentions citations/references -> Mode B (Citation Integrity).
- **After `/claudistotle:peer-review`** or user mentions review/changes -> Mode C (Change Record).
- **User says "validate all" or "full check"** -> Run all three modes in sequence.

## Auto-Detection Logic

When mode is not specified, scan `reviews/[project-name]/` for existing files:

1. If `change-record.md` exists and was recently modified -> Mode C
2. If `paper-draft.md` exists and was recently modified -> Mode B
3. If `literature-all.bib` exists and was recently modified -> Mode A
4. If none of the above -> Report: "No outputs found to validate. Run a research workflow first."

---

## Mode A — Literature Coverage Check

**When:** After `/claudistotle:literature-review` completes, before proceeding to `/claudistotle:refine`.

**Purpose:** Verify that the collected literature actually covers the research question's key dimensions.

### Protocol

0. **Read** `reviews/[project-name]/INDEX.md` (if exists) — get an overview of available literature, sources, and reports before loading full files. Use the index to identify which bib entries are relevant, then selectively read only what's needed via Grep.

1. **Read** `reviews/[project-name]/research-proposal.md`
   - Extract: core research question, key concepts, methodology, listed literature directions
   - If file doesn't exist, ask the user for their research question

2. **Read** `reviews/[project-name]/literature-all.bib`
   - Parse all BibTeX entries
   - Extract: author, title, year, keywords, `note` field (contains CORE ARGUMENT, RELEVANCE, POSITION tags)

3. **Read** `reviews/[project-name]/literature-review-final.md` (if exists)
   - Extract: section headings, key themes discussed

4. **Build concept coverage matrix:**

   For each key concept from the research proposal:
   - Search bib entries (title, keywords, note) for relevant matches
   - Count: how many papers cover this concept?
   - Classify coverage: Strong (3+ papers) / Adequate (1-2 papers) / Missing (0 papers)

5. **Check methodological balance:**
   - Are there papers representing different positions on the research question?
   - Is there at least one paper for each major opposing viewpoint?

6. **Output the coverage report:**

```
╔═══════════════════════════════════════════════════╗
║           LITERATURE COVERAGE REPORT              ║
╠═══════════════════════════════════════════════════╣

Research Question: [from research-proposal.md]

CONCEPT COVERAGE:
  ✅ [concept 1] — Strong (5 papers)
  ⚠️ [concept 2] — Adequate (2 papers)
  ❌ [concept 3] — Missing (0 papers)

METHODOLOGICAL BALANCE:
  ✅ Supporting positions: [count] papers
  ⚠️ Opposing positions: [count] papers
  ❌ Missing perspective: [description]

TOTAL: [X]/[Y] concepts covered | [N] papers in bibliography

RECOMMENDATION:
  [ ] Ready to proceed to /claudistotle:refine
  [ ] Suggest supplementary /claudistotle:literature-review for: [specific gaps]
```

### Decision Point

- All concepts Strong or Adequate, balance OK -> "Ready to proceed to `/claudistotle:refine`"
- Any concept Missing -> Recommend supplementary `/claudistotle:literature-review` with specific search terms
- User decides: proceed anyway or fill gaps first

---

## Mode B — Citation Integrity Check

**When:** After `/claudistotle:draft` completes, before proceeding to `/claudistotle:peer-review`.

**Purpose:** Ensure every citation in the draft has a matching bib entry, and flag unused references.

### Protocol

1. **Read** `reviews/[project-name]/paper-draft.md`
   - Extract all citation markers: patterns like `(Author Year)`, `(Author, Year)`, `Author (Year)`, `\cite{key}`, `[@key]`, or any consistent citation format
   - Build a list of all cited keys/names

2. **Read** `reviews/[project-name]/literature-all.bib`
   - Parse all BibTeX entries
   - Build a list of all available keys + author-year pairs

3. **Cross-reference:**

   **Orphan citations** (cited in draft but not in bib):
   - List each with the sentence context where it appears
   - Severity: HIGH — these are potentially fabricated references

   **Idle references** (in bib but not cited in draft):
   - List each with its `note` field summary
   - Severity: LOW — but may indicate missed opportunities to strengthen arguments

   **Duplicate entries** (same paper with different bib keys):
   - Identify by matching author+title+year
   - Severity: MEDIUM — causes confusion in bibliography

4. **BibTeX format validation:**
   - Check required fields per entry type (@article: author, title, journal, year; @book: author, title, publisher, year; etc.)
   - Flag entries missing required fields
   - Check for encoding issues in author names

5. **Output the integrity report:**

```
╔═══════════════════════════════════════════════════╗
║           CITATION INTEGRITY REPORT               ║
╠═══════════════════════════════════════════════════╣

Draft: paper-draft.md ([word count] words, [cite count] citations)
Bibliography: literature-all.bib ([entry count] entries)

ORPHAN CITATIONS (in draft, not in bib): [count]
  ❌ (Smith 2019) — "...as Smith argues, the concept of..." [line ~42]
  ❌ (Chen 2021) — "...following Chen's framework..." [line ~78]

IDLE REFERENCES (in bib, not cited): [count]
  📚 jones2020ethics — "Ethics of AI in Healthcare" (might support §3 argument)
  📚 wang2018comparative — "Comparative Analysis of..." (relevant to §5?)

DUPLICATE ENTRIES: [count]
  ⚠️ camus1942 / camus1942myth — same paper, different keys

FORMAT ISSUES: [count]
  ⚠️ lee2020 — missing 'journal' field (type: @article)

RECOMMENDATION:
  [ ] All clear — ready for /claudistotle:peer-review
  [ ] Fix [N] orphan citations before proceeding
  [ ] Consider citing [N] idle references to strengthen arguments
```

### Decision Point

- Zero orphan citations, no format issues -> "Ready for `/claudistotle:peer-review`"
- Orphan citations found -> Must fix before proceeding (potential fabrication)
- Idle references found -> Optional: user decides whether to incorporate
- User decides: fix now or proceed with known issues

---

## Mode C — Change Record Completeness

**When:** After `/claudistotle:peer-review` completes, before finalizing the paper.

**Purpose:** Ensure every review comment has been addressed with a documented response.

### Protocol

1. **Read** `reviews/[project-name]/change-record.md`
   - Parse all COMMENT → RESPONSE → CHANGE MADE → RATIONALE blocks
   - Identify any incomplete blocks (missing RESPONSE, CHANGE MADE, or RATIONALE)

2. **Check completeness:**

   **Unaddressed comments** (COMMENT without RESPONSE):
   - List each with severity (from original review)
   - Severity: HIGH for Critical/Important, LOW for Minor

   **Response without action** (RESPONSE exists but no CHANGE MADE):
   - Acceptable if RESPONSE is "Disagree" with clear RATIONALE
   - Flag if RESPONSE is "Agree" or "Partially agree" but no CHANGE MADE

   **Missing rationale** (CHANGE MADE exists but no RATIONALE):
   - Important for audit trail — flag all

3. **Cross-check with draft:**
   - For each CHANGE MADE that references a section, verify the section in `paper-draft.md` actually reflects the change
   - Flag discrepancies (claimed change not found in draft)

4. **Output the completeness report:**

```
╔═══════════════════════════════════════════════════╗
║        CHANGE RECORD COMPLETENESS REPORT          ║
╠═══════════════════════════════════════════════════╣

Total review comments: [count]
  ✅ Fully addressed: [count]
  ⚠️ Partially addressed: [count]
  ❌ Unaddressed: [count]

UNADDRESSED COMMENTS:
  ❌ [Critical] "The argument in §2 assumes..."
  ❌ [Important] "Missing engagement with..."

INCOMPLETE RECORDS:
  ⚠️ Comment #4 — has RESPONSE but no CHANGE MADE
  ⚠️ Comment #7 — has CHANGE MADE but no RATIONALE

DRAFT CONSISTENCY:
  ✅ 12/14 changes verified in paper-draft.md
  ❌ Comment #3 — change claimed in §4 but section unchanged

RECOMMENDATION:
  [ ] All comments addressed — ready for submission
  [ ] Address [N] remaining comments before finalizing
```

### Decision Point

- All comments addressed, draft consistent -> "Ready for submission"
- Unaddressed Critical/Important comments -> Must address before proceeding
- Minor gaps only -> User decides: fix or accept

---

## Saving Reports

After generating any validation report, save a timestamped copy to the `reports/` subdirectory:

- Mode A → `reviews/[project-name]/reports/validate-coverage-YYYY-MM-DD.md`
- Mode B → `reviews/[project-name]/reports/validate-citation-YYYY-MM-DD.md`
- Mode C → `reviews/[project-name]/reports/validate-record-YYYY-MM-DD.md`

If a report for the same mode and date already exists, append a sequence number (e.g., `validate-coverage-2026-03-20-2.md`).

These reports form part of the research's intellectual audit trail — they document what was checked, what passed, and what failed at each stage.

## General Rules

1. **Never modify working files.** `/validate` is read-only for the main workspace files. It only writes to `reports/`.
2. **Be specific.** Always quote the problematic text with approximate line numbers.
3. **Prioritize.** Rank issues by severity. Don't bury critical problems in a list of minor ones.
4. **Be actionable.** Every flagged issue should suggest what to do next.
5. **Respect the user's decision.** After presenting the report, let the user decide whether to fix issues or proceed.

## Quality Checklist

Before completing any validation report, verify:

- [ ] All relevant files in the workspace were read
- [ ] Issues are ranked by severity (High → Medium → Low)
- [ ] Each issue includes specific location and suggested action
- [ ] The recommendation clearly states whether to proceed or fix first
- [ ] The report format is consistent and readable

---

## Stage Completion Protocol

When `/validate` completes any mode, output the following to the user and update `PROGRESS.md`:

### User-Facing Prompt (Mode A)

```
═══════════════════════════════════════════════════
✅ Quality Gate Complete: Validate Mode A (Literature Coverage)

📄 Report: reports/validate-coverage-YYYY-MM-DD.md
📍 Current Position: Quality Gate A ✅

➡️ Next Step: /claudistotle:refine
   Compare literature landscape against research question; decide if narrowing or direction adjustment is needed.
═══════════════════════════════════════════════════
```

### User-Facing Prompt (Mode B)

```
═══════════════════════════════════════════════════
✅ Quality Gate Complete: Validate Mode B (Citation Integrity)

📄 Report: reports/validate-citation-YYYY-MM-DD.md
📍 Current Position: Quality Gate B ✅

➡️ Next Step: /claudistotle:peer-review
   Begin three-round peer review: argument validity → evidence quality → writing quality.
═══════════════════════════════════════════════════
```

### User-Facing Prompt (Mode C)

```
═══════════════════════════════════════════════════
✅ Quality Gate Complete: Validate Mode C (Change Record Completeness)

📄 Report: reports/validate-record-YYYY-MM-DD.md
📍 Current Position: Quality Gate C ✅

🎉 Research workflow complete! Paper has passed all quality checks.

💡 Next Options:
   • Export paper to .docx (pandoc)
   • Use /claudistotle:feedback to record advisor feedback and continue iteration
   • Re-run any stage for deepening
═══════════════════════════════════════════════════
```

### Update PROGRESS.md

Update `reviews/[project-name]/PROGRESS.md`:
- **Current Status** → Update to corresponding next step
- **Completed Milestones** → Append: `- [x] Validate Mode [A/B/C] — [date] — [result summary]`
- **Progress History** → Append status change

---

## Machine-Readable Exit Signal

As the **last line** of output, append the appropriate signal:

**Mode A:**
```
<!-- STAGE_EXIT: PASS -->                          (all concepts Strong or Adequate)
<!-- STAGE_EXIT: FAIL:coverage_gap:[N]_missing -->  (N concepts with Missing coverage)
```

**Mode B:**
```
<!-- STAGE_EXIT: PASS -->                           (zero orphan citations, no critical format issues)
<!-- STAGE_EXIT: FAIL:orphan_citations:[N] -->       (N orphan citations found)
<!-- STAGE_EXIT: FAIL:format_issues:[N] -->          (N critical format issues)
```

**Mode C:**
```
<!-- STAGE_EXIT: PASS -->                           (all comments addressed, draft consistent)
<!-- STAGE_EXIT: FAIL:unaddressed:[N] -->            (N unaddressed Critical/Important comments)
<!-- STAGE_EXIT: FAIL:incomplete_records:[N] -->     (N incomplete change record entries)
```

These signals are used by `/autopilot` for auto-advance decisions and self-healing.

---

**Typical usage in the pipeline:**

```
/claudistotle:literature-review  →  /claudistotle:validate(A)  →  /claudistotle:refine  →  /claudistotle:draft  →  /claudistotle:validate(B)  →  /claudistotle:peer-review  →  /claudistotle:validate(C)  →  ✅
```
