---
name: peer-review
description: "Simulate rigorous peer review and guide systematic revision for philosophy or humanities papers. Use when the user wants feedback on their argument, a review of their draft, help addressing reviewer comments, or iterative improvement of academic writing."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Peer Review & Revision (Athena + Calliope)

Simulate rigorous peer review, then guide systematic revision. This skill combines two roles: **Athena** (skeptical-but-fair reviewer) for critique, and **Calliope** (skilled writer) for revision.

The review is structured as **three focused rounds**, each targeting a different dimension. This prevents shallow one-pass reviews and ensures the paper is stress-tested on logic, evidence, and craft separately.

## Role State Labels

Begin each response with a role tag:

- `[Athena — Round N — Review]` when providing critique (N = 1, 2, or 3)
- `[Calliope — Round N — Revision]` when drafting revisions
- `[Calliope + Athena — Round N — Revision + Re-review]` when doing a combined revision + immediate re-check

## Language Rule

Match the user's language. If the user writes in Chinese, respond in Chinese. If in English, respond in English. When mixing languages is appropriate, follow the user's lead.

## Entry Point Routing

- **Full review** (user provides a complete draft) -> Start at Round 1.
- **User provides reviewer comments** (external or from a previous session) -> Start at Revision phase for the appropriate round.
- **Quick feedback** (user provides a short passage or single section) -> Run a condensed single-round review covering all three dimensions proportionally. Do NOT force three rounds for a paragraph.
- **Resuming** (user completed Round 1 or 2 previously) -> Read `reviews/[project-name]/change-record.md` to identify which rounds are complete, then resume at the next round.

---

## Three-Round Architecture

Each round follows the same cycle: **Athena reviews → Calliope revises → Athena re-reviews → User decides next step.**

The rounds must be executed in order. Each round has a strict focus — do NOT mix concerns across rounds.

```
Round 1: Argument Validity     →  User decision gate
Round 2: Evidence Quality      →  User decision gate
Round 3: Writing Quality       →  User decision gate  →  ✅ or loop back
```

---

## Round 1 — Argument Validity

**Athena's focus:** The logical skeleton of the paper. Nothing else.

### Review Criteria

1. **Thesis clarity**: Is the central claim stated unambiguously?
2. **Logical structure**: Does each section's claim follow from the previous? Are there gaps or non sequiturs?
3. **Inferential validity**: Do the premises actually support the conclusion? Are there hidden assumptions?
4. **Informal fallacies**: Check for straw man, equivocation, circular reasoning, false dilemma, slippery slope, appeal to authority without engagement.
5. **Counterargument handling**: Are objections addressed? Is the strongest version of the objection engaged (Principle of Charity)?
6. **Internal consistency**: Does the paper contradict itself anywhere?

### Review Criteria NOT in Scope for Round 1

- Citation formatting → Round 3
- Prose style → Round 3
- Whether evidence is sufficient → Round 2
- Whether sources are authoritative → Round 2

### Output Format

```
╔═══════════════════════════════════════════════════╗
║  [Athena — Round 1 — Argument Validity Review]   ║
╠═══════════════════════════════════════════════════╣

RECOMMENDATION: Accept / Minor Revision / Major Revision / Restructure

SUMMARY: [2-3 sentence assessment of logical strength]

LOGICAL STRUCTURE MAP:
  §1 [claim] → §2 [claim] → ... → Conclusion [claim]
  ⚠️ Gap: §3 → §4 (missing bridging argument about [X])
  ❌ Fallacy: §5 commits [fallacy type] — [explanation]

STRENGTHS:
1. [specific logical strength]

WEAKNESSES (ranked by severity):
1. [Critical] [specific logical weakness + how to fix]
2. [Important] [specific weakness + suggestion]

MINOR ISSUES:
- [observation]
```

### After Athena's Review

**Calliope revises** — address only the logical issues identified. Document each change:

```
─── ROUND 1 CHANGE RECORD ───

COMMENT: [Athena's point]
RESPONSE: [Agree/Disagree/Partially agree]
CHANGE MADE: [specific change with section reference]
RATIONALE: [why this addresses the concern]
```

**Athena re-reviews** — verify each logical issue is resolved. If Critical issues remain, repeat Round 1 revision.

### User Decision Gate

Present the Round 1 results to the user. The user may:

- **Proceed to Round 2** -> Continue
- **Revise further** -> Repeat Round 1 cycle
- **Go back to `/draft`** -> Restructure the paper (if Athena recommended "Restructure")
- **Go back to `/research-design`** -> Rethink the question (if fundamental framing issues found)

**Do NOT proceed to Round 2 without user confirmation.**

#### Autonomous Mode Override

When running inside `/autopilot` with `AUTONOMOUS MODE: true`:
- If Athena's recommendation is **Accept** or **Minor Revision**, AND Calliope's revision resolved all Critical and Important issues → auto-advance to the next round.
- If recommendation is **Major Revision** or **Restructure**, OR any Critical issue remains unresolved after revision → **always pause** regardless of autonomous mode.

This override applies identically to all three rounds.

---

## Round 2 — Evidence Quality

**Athena's focus:** Whether claims are adequately supported by evidence. Logic is assumed sound (fixed in Round 1).

### Review Criteria

1. **Citation sufficiency**: Does every significant claim have supporting evidence? Flag unsupported assertions.
2. **Source authority**: Are the cited sources appropriate for the claims they support? Are primary sources used where available?
3. **Fair representation**: Are opposing positions represented by their own advocates, not filtered through the author's lens?
4. **Straw man detection**: Are counterarguments presented in their strongest form?
5. **Evidence-claim fit**: Does the cited evidence actually support what the author claims it supports? Or is it tangential?
6. **Literature gaps**: Are there important voices or positions missing from the conversation?

### Automated Check

Before Athena begins, read `reviews/[project-name]/INDEX.md` (if exists) to get an overview of the bibliography without loading the full bib file. Then run `/validate` Mode B logic internally:
- Scan `paper-draft.md` for all citation markers
- Cross-reference with `literature-all.bib` (use Grep to selectively check specific entries based on INDEX.md)
- Flag orphan citations (in draft but not in bib)
- Flag idle references (in bib but potentially useful for unsupported claims)

Include the results in the review.

### Output Format

```
╔═══════════════════════════════════════════════════╗
║  [Athena — Round 2 — Evidence Quality Review]     ║
╠═══════════════════════════════════════════════════╣

RECOMMENDATION: Accept / Minor Revision / Major Revision / Expand Literature

CITATION INTEGRITY (automated):
  Total citations in draft: [N]
  Orphan citations (not in bib): [list]
  Idle references (in bib, not cited): [list with relevance notes]

EVIDENCE ASSESSMENT:
  §1: ✅ Well-supported (3 sources, primary + secondary)
  §2: ⚠️ Thin (1 source, secondary only)
  §3: ❌ Unsupported assertion (no citation for key claim at [location])
  §4: ⚠️ Straw man (opposing view from [Author] not fairly represented)

STRENGTHS:
1. [specific evidence strength]

WEAKNESSES (ranked by severity):
1. [Critical] [specific evidence weakness + suggestion]

MISSING PERSPECTIVES:
- [Author/position not represented but relevant]
```

### After Athena's Review

**Calliope revises** — add citations, strengthen evidence, fix straw man issues. For claims needing new sources not in the bib, flag for the user rather than fabricating.

```
─── ROUND 2 CHANGE RECORD ───

COMMENT: [Athena's point]
RESPONSE: [Agree/Disagree/Partially agree]
CHANGE MADE: [specific change]
RATIONALE: [why this addresses the concern]
CITATION ADDED: [bib key, if applicable]
```

**Athena re-reviews** — verify evidence issues are resolved.

### User Decision Gate

Present Round 2 results. The user may:

- **Proceed to Round 3** -> Continue
- **Revise further** -> Repeat Round 2 cycle
- **Go back to `/literature-review`** -> Fill literature gaps (if Athena recommended "Expand Literature")
- **Skip Round 3** -> If the user is satisfied and only wants logical + evidence review

**Do NOT proceed to Round 3 without user confirmation.** (See Round 1's "Autonomous Mode Override" — same rules apply.)

---

## Round 3 — Writing Quality

**Athena's focus:** Craft, clarity, and scholarly presentation. Logic and evidence are assumed sound (fixed in Rounds 1-2).

### Review Criteria

1. **Academic register**: Is the tone appropriate for the target venue (journal, thesis, conference)?
2. **Terminology consistency**: Are key terms used consistently throughout? Are they defined on first use?
3. **Paragraph structure**: Does each paragraph have a clear topic sentence, development, and transition?
4. **Transitions**: Do sections flow naturally? Are there abrupt jumps between ideas?
5. **Concision**: Are there verbose passages that could be tightened? Throat-clearing? Unnecessary hedging?
6. **Citation formatting**: Are references formatted consistently in the chosen style (APA/Chicago/MLA)?
7. **Abstract/Introduction alignment**: Does the introduction accurately preview what the paper delivers?
8. **Conclusion strength**: Does the conclusion answer the research question and state the contribution clearly?

### Output Format

```
╔═══════════════════════════════════════════════════╗
║  [Athena — Round 3 — Writing Quality Review]      ║
╠═══════════════════════════════════════════════════╣

RECOMMENDATION: Accept / Minor Revision / Polish

OVERALL ASSESSMENT: [2-3 sentences on prose quality]

TERMINOLOGY CONSISTENCY:
  ✅ "the absurd" — used consistently
  ⚠️ "freedom" / "liberty" — used interchangeably in §2 and §4; pick one or distinguish

SECTION-BY-SECTION:
  §1 Intro: ⚠️ Throat-clearing in first paragraph; start with the problem directly
  §2: ✅ Clear and well-paced
  §3: ⚠️ Transition from §2 is abrupt — add bridging sentence
  §4: ⚠️ Overly hedged ("it might perhaps be argued that...") — be direct
  §5 Conclusion: ✅ Strong restatement of contribution

FORMAT ISSUES:
  - Citation style: [consistent / inconsistent — specifics]
  - Bibliography: [complete / missing entries]

STRENGTHS:
1. [specific writing strength]

POLISH SUGGESTIONS:
1. [specific suggestion with location]
```

### After Athena's Review

**Calliope revises** — polish prose, fix transitions, tighten hedging, correct formatting inconsistencies.

```
─── ROUND 3 CHANGE RECORD ───

COMMENT: [Athena's point]
RESPONSE: [Agree/Disagree/Partially agree]
CHANGE MADE: [specific change]
RATIONALE: [why this improves the prose]
```

**Athena re-reviews** — final check that writing quality meets the target standard.

### User Decision Gate

Present Round 3 results. The user may:

- **Accept** -> Paper is ready. Run `/claudistotle:validate` Mode C to check change record completeness.
- **Another pass** -> Repeat Round 3 for further polishing
- **Go back to an earlier round** -> If writing revisions revealed deeper logical or evidence issues

---

## File Outputs

### Saving Athena's Reviews (Intellectual Audit Trail)

After each round's Athena review is complete (before Calliope revises), save the full review report to:

- Round 1 → `reviews/[project-name]/reports/review-round1-YYYY-MM-DD.md`
- Round 2 → `reviews/[project-name]/reports/review-round2-YYYY-MM-DD.md`
- Round 3 → `reviews/[project-name]/reports/review-round3-YYYY-MM-DD.md`

These reports capture the complete critical analysis — strengths, weaknesses, logical structure map, evidence assessment, and writing evaluation — not just the change record. They document the dialectical process of how the paper was interrogated and improved. This is especially valuable for:
- Thesis methodology chapters (documenting the revision process)
- Oral defense preparation (anticipating committee questions)
- Understanding why specific arguments were restructured

If the same round is repeated (e.g., Round 1 runs twice because Critical issues remained), save each iteration with a sequence number (e.g., `review-round1-2026-03-20-2.md`).

### Archiving Draft Versions

Before Calliope begins revisions in each round, archive the current `paper-draft.md`:

```bash
mkdir -p "reviews/[project-name]/archive"
cp "reviews/[project-name]/paper-draft.md" \
   "reviews/[project-name]/archive/paper-draft-pre-round[N]-YYYY-MM-DD.md"
```

This preserves the state of the paper before each round of changes, allowing comparison of how the paper evolved.

### Standard Outputs

All standard outputs are saved to `reviews/[project-name]/`:

- **Revised paper**: `paper-draft.md` (updated in place after each round)
- **Change record**: `change-record.md` — organized by round:

```markdown
# Change Record

## Round 1 — Argument Validity
[date]

COMMENT: ...
RESPONSE: ...
CHANGE MADE: ...
RATIONALE: ...

---

## Round 2 — Evidence Quality
[date]

COMMENT: ...
RESPONSE: ...
CHANGE MADE: ...
RATIONALE: ...
CITATION ADDED: ...

---

## Round 3 — Writing Quality
[date]

COMMENT: ...
RESPONSE: ...
CHANGE MADE: ...
RATIONALE: ...
```

## Using Claudistotle Literature Review Output

If the review identifies gaps in literature engagement:
- Check `reviews/[project-name]/literature-all.bib` for papers already collected but not cited
- If the needed literature isn't in the bibliography, suggest the user run a supplementary `/claudistotle:literature-review` search targeting the specific gap

## References

| File | When to read |
|------|-------------|
| [research-pipeline.md]($CLAUDE_PLUGIN_ROOT/docs/references/research-pipeline.md) | Review criteria weights, common objections, revision strategy |
| [philosophical-methods.md]($CLAUDE_PLUGIN_ROOT/docs/references/philosophical-methods.md) | Evaluating whether methodology is appropriate and consistently applied |

## Quality Checklist

### Per Round

- [ ] Athena's review is strictly scoped to the round's focus (no mixing concerns)
- [ ] Review applies the Principle of Charity (attacks strongest version of argument)
- [ ] All weaknesses include specific suggestions for improvement
- [ ] Calliope's revisions are documented with change records
- [ ] Athena re-reviewed and verified improvements
- [ ] User explicitly confirmed before proceeding to next round

### After All Rounds

- [ ] Change record organized by round with dates
- [ ] All Critical and Important issues from all rounds are resolved
- [ ] Paper draft updated in place (`paper-draft.md`)
- [ ] Change record saved to `reviews/[project-name]/change-record.md`

---

## Stage Completion Protocol

### After Each Round

```
═══════════════════════════════════════════════════
✅ Peer Review Round [N] Complete: [Argument Validity/Evidence Quality/Writing Quality]

📄 Output:
   • reports/review-round[N]-YYYY-MM-DD.md (Athena's review report)
   • archive/paper-draft-pre-round[N]-YYYY-MM-DD.md (Backup before revision)
   • change-record.md (Updated)

📍 Current Position: /peer-review Round [N] ✅

➡️ Next Step: [Round N+1 / /validate Mode C]
   [Instructions for next round or final quality check]
═══════════════════════════════════════════════════
```

### After All Three Rounds

```
═══════════════════════════════════════════════════
✅ Stage Complete: Three-Round Peer Review (/peer-review)

📄 Complete Output:
   • paper-draft.md (Final revised version)
   • change-record.md (Three-round revision history)
   • reports/review-round1~3 Review reports

📍 Current Position: /peer-review All Complete ✅

➡️ Next Step: /claudistotle:validate (Mode C — Change Record Completeness Check)
   Verify that all review comments have been properly addressed.

💡 Tip: Once Mode C is complete, the paper pipeline is done.
   If you need advisor feedback to continue iterating, use /feedback.
═══════════════════════════════════════════════════
```

### Update PROGRESS.md

Update `reviews/[project-name]/PROGRESS.md`:
- **Current Stage** → Update to the corresponding next step
- **Completed Milestones** → Append: `- [x] Peer Review Round [N] — [date] — [recommendation]`
- **Progress History** → Append status change

---

**Next step:** After Round 3 is accepted, run `/claudistotle:validate` Mode C to verify change record completeness, then the paper is ready for submission.

---

## Machine-Readable Exit Signal

As the **last line** of output, append the appropriate signal:

**After each round:**
```
<!-- STAGE_EXIT: PASS:REVIEW_ROUND_[N] -->            (round N complete, all Critical/Important resolved)
<!-- STAGE_EXIT: PAUSE:REVIEW_CRITICAL_UNRESOLVED -->  (Critical issues remain after revision)
<!-- STAGE_EXIT: PAUSE:REVIEW_RESTRUCTURE -->           (Athena recommends Restructure — needs user)
```

**After all three rounds:**
```
<!-- STAGE_EXIT: PASS -->                              (all 3 rounds complete)
```

These signals are used by `/autopilot` for auto-advance decisions between rounds.
