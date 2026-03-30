---
name: feedback
description: "Integrate external feedback (e.g., from advisor meetings) into the research workflow. Use when the user has feedback from their advisor, committee members, or peers and wants to systematically process it back into the pipeline."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# External Feedback Integration

Process feedback from advisors, committee members, or external reviewers, classify it by type, and route it to the appropriate workflow stage for iteration.

## Language Rule

Match the user's language. If the user writes in Chinese, respond in Chinese. If in English, respond in English.

## Entry Point Routing

- **User has new feedback to record** -> Start at Step 1 (Record Feedback).
- **User wants to act on previously recorded feedback** -> Start at Step 3 (Route & Execute).
- **User wants to review feedback history** -> Read `advisor-feedback.md` and summarize.

---

## Step 1 — Record Feedback

### 1.1 Gather Feedback

Ask the user:

1. **Source**: Who gave the feedback? (e.g., advisor, committee member, peer)
2. **Date**: When was the meeting/conversation?
3. **Content**: What did they say? (User can describe freely — bullet points, notes, or narrative)

### 1.2 Classify Feedback Items

Parse the user's input and classify each distinct piece of feedback into one or more categories:

| Category | Description | Target Stage |
|----------|-------------|--------------|
| **Direction** | Research question too broad/narrow, need direction change, methodology mismatch | → `/claudistotle:refine` |
| **Literature** | Missing papers, need supplementary areas, missing scholar perspective | → `/claudistotle:literature-review` (supplementary) |
| **Argument** | Logical gaps, problematic premises, rebuttals too weak | → `/claudistotle:draft` Step 1 (revise skeleton) |
| **Evidence** | Insufficient citations, need more primary text analysis, unsupported claims | → `/claudistotle:draft` Step 2 + possibly `/claudistotle:text-commentary` |
| **Writing** | Prose needs refinement, unclear structure, citation format issues | → `/claudistotle:peer-review` (new round) |
| **General** | Encouragement, direction confirmation, no concrete action needed | → Record only |

Present the classified results to the user for confirmation:

```
📋 Feedback Classification Results:

Feedback Source: [Professor Name] — [Date]

1. [Direction] "Research scope too broad; suggest focusing on X rather than whole Y"
   → Suggested Route: /claudistotle:refine

2. [Literature] "You should read Frankfurt (1971) on Freedom of the Will"
   → Suggested Route: /claudistotle:literature-review (supplementary search)

3. [Argument] "Chapter 3 has a logical gap from A to B"
   → Suggested Route: /claudistotle:draft Step 1 (revise skeleton)

4. [General] "Overall direction is good, continue"
   → Record only

Please confirm the classification is correct, or adjust any items as needed.
```

### 1.3 User Confirmation Gate

**STOP and WAIT** for user to confirm the classification. Adjust if needed.

---

## Step 2 — Save Feedback Record

After user confirms, append to `reviews/[project-name]/advisor-feedback.md`:

```markdown
---

## Feedback #[N] — [YYYY-MM-DD]

**Source**: [source]
**Date**: [date]

### Feedback Items

#### F[N].1 [Category Tag]
**Content**: [feedback content]
**Route**: [target skill]
**Status**: 🔲 Pending

#### F[N].2 [Category Tag]
**Content**: [feedback content]
**Route**: [target skill]
**Status**: 🔲 Pending

### Action Plan
1. [First action — corresponding to F[N].X]
2. [Second action — corresponding to F[N].X]
```

If `advisor-feedback.md` doesn't exist yet, create it with a header:

```markdown
# Advisor Feedback Record

This file records all external feedback (advisor, committee members, peers, etc.),
tracks the processing status of each item, and drives research iteration.

Statistics:
- Total feedback sessions: [N]
- Pending items: [M]
- Completed items: [K]
```

---

## Step 3 — Route & Execute

### 3.0 Read INDEX.md

Before routing, read `reviews/[project-name]/INDEX.md` (if exists) to understand the current state of literature, sources, commentaries, and reports. This helps contextualize the feedback and determine if the recommended skill has sufficient data to act on.

### 3.1 Prioritize

If multiple feedback items exist, present a prioritized execution order:

```
Suggested Processing Order (by impact scope, largest first):

1. 🔴 [Direction] F2.1 — Research scope needs narrowing → /claudistotle:refine
   (Affects all subsequent stages; should be addressed first)

2. 🟡 [Literature] F2.2 — Add Frankfurt 1971 → /claudistotle:literature-review
   (Affects argument foundation)

3. 🟢 [Argument] F2.3 — Chapter 3 reasoning gap → /claudistotle:draft Step 1
   (Localized change; can handle after previous two)

Which item would you like to start with?
```

Priority logic:
- **Direction** > **Literature** > **Argument** > **Evidence** > **Writing**
- (Direction changes cascade to everything downstream; writing fixes are local)

### 3.2 Execute with Context

When routing to a target skill, **pass the advisor feedback as additional context**:

**Routing to `/claudistotle:refine`:**
- Read the feedback item(s) classified as "directional"
- Include them in the gap analysis as an additional input dimension: "Advisor feedback"
- The refine analysis should consider the advisor's perspective alongside the literature landscape

**Routing to `/claudistotle:literature-review`:**
- Extract specific authors, papers, or topics mentioned in the feedback
- Use these as targeted supplementary search terms
- Run a focused supplementary search (not a full 6-phase review)

**Routing to `/claudistotle:draft` Step 1:**
- Read the feedback item(s) classified as "argumentation"
- When revising the argument skeleton, specifically address the logical gaps or structural issues identified by the advisor
- Note in the skeleton: `ADVISOR NOTE: [feedback content]`

**Routing to `/claudistotle:draft` Step 2 or `/claudistotle:text-commentary`:**
- Read the feedback item(s) classified as "evidence"
- If the advisor requested more primary text analysis, suggest running `/claudistotle:text-commentary` on the specified texts first
- Pass the context to `/claudistotle:draft` during prose revision

**Routing to `/claudistotle:peer-review`:**
- Read the feedback item(s) classified as "writing"
- Start a new peer-review round focused on the specific writing issues identified
- Athena should specifically check for the issues the advisor flagged

### 3.3 Update Status

After each feedback item is processed, update its status in `advisor-feedback.md`:

- `🔲 Pending` → `✅ Addressed (YYYY-MM-DD)` with a brief note on what was done
- If partially addressed: `🔶 Partially Addressed` with explanation of what remains

---

## Step 4 — Save Processing Report

Save a record of the feedback processing session to:

`reviews/[project-name]/reports/feedback-session-YYYY-MM-DD.md`

Include:
- Which feedback items were processed
- What actions were taken (which skills were invoked)
- Key decisions made during processing
- Remaining items to address

---

## Update PROGRESS.md

After processing feedback, update `PROGRESS.md`:
- Note the feedback session in "Completed Milestones"
- Update "Current Status" if the feedback caused a workflow stage change (e.g., went back to /claudistotle:refine)
- Add remaining feedback items to "Pending Items"

---

## Quality Checklist

Before completing a feedback session, verify:

- [ ] All feedback items from the user have been captured
- [ ] Each item is classified with an appropriate category
- [ ] The user confirmed the classification
- [ ] Feedback is saved to `advisor-feedback.md` with status tracking
- [ ] Actions taken are documented
- [ ] `PROGRESS.md` is updated if workflow stage changed

---

**Typical usage:**

```
User meets advisor → records feedback → /claudistotle:feedback → classifies & routes →
    → /claudistotle:refine (if direction change)
    → /claudistotle:literature-review (if gaps)
    → /claudistotle:draft (if argument/evidence issues)
    → /claudistotle:peer-review (if writing issues)
→ continue normal workflow → next advisor meeting → /claudistotle:feedback again
```

---

## Machine-Readable Exit Signal

As the **last line** of output, append:

```
<!-- STAGE_EXIT: PASS -->
```

Note: `/feedback` is inherently interactive (requires user to provide advisor's words) and does not support autonomous mode. The exit signal is provided for consistency so `/autopilot` can detect completion if `/feedback` is invoked mid-pipeline.
