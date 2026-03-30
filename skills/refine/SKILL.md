---
name: refine
description: "Refine the research question after literature review by comparing the original proposal against the actual scholarly landscape. Use after /claudistotle:literature-review (and optionally /claudistotle:validate Mode A) to decide whether to proceed, narrow, or pivot before drafting."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Research Question Refinement

After completing a literature review, the original research question often needs adjustment. This skill forces a deliberate pause between literature review and drafting to ask: *Given what we now know about the scholarly landscape, is our question still the right question?*

## Language Rule

Match the user's language. If the user writes in Chinese, respond in Chinese. If in English, respond in English.

## Entry Point Routing

- **After `/claudistotle:literature-review`** (typical) -> Run the full protocol below.
- **After `/claudistotle:validate` Mode A flagged gaps** -> Read the coverage report first, then run the protocol with gap awareness.
- **User wants to revisit their question mid-project** -> Run the protocol using whatever files currently exist.

---

## Protocol

### 1. Gather Inputs

Read the following files from `reviews/[project-name]/`:

| File | What to extract | Required? |
|------|----------------|-----------|
| `INDEX.md` | Overview of available literature, source counts, coverage stats — **read this first** to avoid loading full bib into context | Recommended |
| `research-proposal.md` | Original research question, methodology, expected contribution, section outline | **Yes** — abort if missing |
| `literature-review-final.md` | Themes covered, debates identified, gaps noted, conclusions | **Yes** — abort if missing |
| `literature-all.bib` | Total paper count, date range, key authors, theoretical positions represented — **use Grep to selectively read entries** based on INDEX.md rather than loading the entire file | Yes |
| `/validate` Mode A report (if user ran it) | Coverage gaps, missing perspectives | Optional |

### 2. Gap Analysis

Produce a structured comparison between the **original proposal** and the **literature landscape**:

```
╔═══════════════════════════════════════════════════╗
║          RESEARCH QUESTION REFINEMENT             ║
╠═══════════════════════════════════════════════════╣

ORIGINAL RESEARCH QUESTION:
  "[verbatim from research-proposal.md]"

ORIGINAL EXPECTED CONTRIBUTION:
  "[verbatim from research-proposal.md]"

───── LITERATURE LANDSCAPE FINDINGS ─────

1. COVERAGE ASSESSMENT
   How well does the literature address the original question?
   - [Fully addressed / Partially addressed / Under-explored / Not addressed at all]
   - Evidence: [cite specific sections from literature-review-final.md]

2. NOVELTY CHECK
   Has someone already answered this question?
   - [No prior answer / Partial answers exist / Substantially answered]
   - Key prior work: [list papers from bib that most directly address the question]
   - What remains unanswered: [specific gap]

3. DEBATE MAPPING
   Where does the question sit in the scholarly debate?
   - Main positions: [list 2-4 competing views found in literature]
   - Which position does the original question implicitly favor?
   - Missing voices: [perspectives not represented in collected literature]

4. SCOPE ASSESSMENT
   Is the question the right size?
   - [Too broad / About right / Too narrow]
   - If too broad: [which sub-question is most tractable and interesting?]
   - If too narrow: [is there enough literature to sustain a full paper?]

5. METHODOLOGY FIT
   Does the chosen methodology still make sense given the literature?
   - [Still appropriate / Needs adjustment / Consider alternative]
   - If adjustment needed: [specific recommendation]
```

### 3. Recommendation

Based on the gap analysis, produce ONE of four recommendations:

**A. PROCEED (Research question unchanged)**
- The question is novel, well-scoped, and the methodology fits.
- The literature landscape supports the original plan.
- Action: Move to `/draft`.

**B. NARROW (Narrow research question)**
- The question is valid but too broad given the literature.
- A specific sub-question emerged as more tractable and interesting.
- Action: Present the refined question for user approval, then update `research-proposal.md`.

**C. PIVOT (Pivot to new question)**
- The literature review revealed that the original question has been substantially answered, or that a more interesting question emerged.
- Action: Present the new question and explain why it's better. If user agrees, route to `/claudistotle:research-design` to formally redesign the research proposal with Socratic guidance, then re-run `/claudistotle:literature-review` for the new direction. For minor pivots where the user prefers to skip the full redesign, update `research-proposal.md` directly and proceed.

**D. EXPAND (Expand literature)**
- The question is good but the literature is insufficient to support it.
- Action: Recommend specific supplementary `/claudistotle:literature-review` searches before proceeding.

### 4. User Confirmation Gate

**Present the gap analysis + recommendation to the user.** Then STOP and WAIT.

The user may:
- **Accept the recommendation** -> Execute the recommended action
- **Choose a different option** -> Follow the user's preference
- **Discuss further** -> Engage in dialogue to refine the direction

**Do NOT update any files without explicit user confirmation.**

#### Autonomous Mode Override

When running inside `/autopilot` with `AUTONOMOUS MODE: true`:

- **PROCEED**: Skip the confirmation gate. Log the decision and proceed directly.
- **NARROW**: Skip the confirmation gate. Apply the narrowing, update `research-proposal.md`, and proceed.
- **PIVOT**: **Always pause** — present to user regardless of autonomous mode. This is a fundamental direction change.
- **EXPAND**: **Always pause** — present to user (or let autopilot attempt self-heal via supplementary literature review).

### 5. Save Analysis Report

Regardless of recommendation (A/B/C/D), save the complete gap analysis to:

`reviews/[project-name]/reports/refine-analysis-YYYY-MM-DD.md`

This report is a key part of the intellectual audit trail — it documents *why* the research question was kept, narrowed, pivoted, or expanded at this point. This is valuable for the thesis methodology chapter and for oral defense preparation.

### 6. Update Research Proposal

If the question was refined (options B or C), update `research-proposal.md`:

1. **Archive the current version first**: Create the archive directory and copy:
   ```bash
   mkdir -p "reviews/[project-name]/archive"
   cp "reviews/[project-name]/research-proposal.md" \
      "reviews/[project-name]/archive/research-proposal-v[N]-YYYY-MM-DD.md"
   ```

2. **Preserve the history in the active file**: Add/update a `## Version History` section at the bottom:
   ```
   ## Version History

   ### v1 (Original — [date])
   Research Question: [original question]
   Reason for refinement: [brief explanation]
   See full version: archive/research-proposal-v1-YYYY-MM-DD.md
   ```

3. **Write the new version**: Update the main sections (Research Question, Significance, Methodology, Expected Contribution) with the refined direction.

4. **Update section outline** if the new question requires a different paper structure.

Save the updated file. Inform the user of what changed.

---

## Failure Modes to Avoid

- **Rubber-stamping**: Don't just say "looks good, proceed" without actually comparing the proposal to the literature. The whole point is to force a genuine reassessment.
- **Overcorrection**: A small adjustment to wording is not a "pivot." Reserve PIVOT for genuinely different questions.
- **Losing the original voice**: The refined question should still reflect the user's intellectual interests, not become a generic literature-gap-filling exercise.
- **False novelty claims**: If the literature substantially addresses the question, say so. Don't pretend there's a gap where there isn't one.

## References

| File | When to read |
|------|-------------|
| [philosophical-methods.md]($CLAUDE_PLUGIN_ROOT/docs/references/philosophical-methods.md) | Evaluating whether methodology still fits after literature review |
| [research-pipeline.md]($CLAUDE_PLUGIN_ROOT/docs/references/research-pipeline.md) | Research question formulation criteria, synthesis matrix |

## Quality Checklist

Before completing the refinement, verify:

- [ ] Both `research-proposal.md` and `literature-review-final.md` were read
- [ ] Gap analysis covers all 5 dimensions (coverage, novelty, debate, scope, methodology)
- [ ] Recommendation is one of the four defined options (A/B/C/D)
- [ ] If question changed: original version preserved in Version History
- [ ] User explicitly confirmed the recommendation before any files were modified

---

## Stage Completion Protocol

When `/refine` completes, output the following to the user and update `PROGRESS.md`:

### User-Facing Prompt

```
═══════════════════════════════════════════════════
✅ Stage Complete: Research Question Refinement

📄 Output:
   • research-proposal.md ([PROCEED/NARROW/PIVOT/EXPAND] — [Updated/Unchanged])
   • reports/refine-analysis-YYYY-MM-DD.md

📍 Current Position: /refine ✅

➡️ Next Step: [Depends on recommendation]
   • PROCEED → /claudistotle:draft Step 1 (Build argument skeleton)
   • NARROW → research-proposal.md updated, proceed to /claudistotle:draft Step 1
   • PIVOT → /claudistotle:research-design (Redesign research proposal, then re-run /claudistotle:literature-review)
   • EXPAND → /claudistotle:literature-review (Supplement literature, then re-run /claudistotle:validate + /claudistotle:refine)

💡 Tip: Before writing, you can use /claudistotle:text-commentary for close reading of primary sources
═══════════════════════════════════════════════════
```

### Update PROGRESS.md

Update `reviews/[project-name]/PROGRESS.md`:
- **Current Stage** → Update to the corresponding next step
- **Completed Milestones** → Append: `- [x] Research question refinement — [date] — [recommendation]`
- **Progress History** → Append status change

---

**Next step:** After refinement is confirmed, proceed to `/claudistotle:draft` Step 1 (Argument Skeleton). If recommendation was PIVOT, route to `/claudistotle:research-design` to redesign the research proposal. If recommendation was EXPAND, run `/claudistotle:literature-review` first to fill gaps.

---

## Machine-Readable Exit Signal

As the **last line** of output, append:

```
<!-- STAGE_EXIT: PASS:PROCEED -->    (recommendation A — question unchanged)
<!-- STAGE_EXIT: PASS:NARROW -->     (recommendation B — question narrowed, proposal updated)
<!-- STAGE_EXIT: PAUSE:PIVOT -->     (recommendation C — needs user decision for direction change)
<!-- STAGE_EXIT: PAUSE:EXPAND -->    (recommendation D — literature insufficient)
```

These signals are used by `/autopilot` for auto-advance and self-heal decisions.
