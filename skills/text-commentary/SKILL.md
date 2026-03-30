---
name: text-commentary
description: >
  Philosophical text close reading analysis: mark logical connectors and write complete commentary (introduction, development, conclusion).
  Use when the user wants to "mark logical connectors", "annotate connectors", "write commentary",
  "analyze text structure", "conduct text analysis", or provides a philosophical
  text for close reading analysis.
allowed-tools: Read, Write, Edit
---

# Philosophical Text Commentary (Two-Stage Process)

This skill executes close reading analysis of philosophical texts, divided into two stages:
1. **Marking Stage**: Mark logical connectors and complete preliminary text analysis
2. **Commentary Stage**: Based on confirmed markings, write introduction, development, and conclusion

**Output language is exclusively Traditional Chinese.** Even if the original text is English, both marking and analysis are conducted in Traditional Chinese.

## Reference Standards

Detailed assignment standards are found in [guide.md]($CLAUDE_PLUGIN_ROOT/docs/references/guide.md). Examples are found in [example.md]($CLAUDE_PLUGIN_ROOT/docs/references/example.md).

## Core Principles (Assignment Guidelines §3.3)

- **Do not paraphrase the text on your own**
- **Do not deviate from the subject matter**
- **Absolutely do not begin analysis from a concept; begin from the text itself** (§6.1.3)

---

## Primary Source Integration

This skill works in conjunction with the `sources/primary/` directory. Workflow:

1. **When user provides text**: If the user pastes text directly, use that text as the object of analysis.
2. **Reading from sources/primary/**: If the user specifies a primary source name without providing text, search for the corresponding `.md` or `.pdf` file in `reviews/[project-name]/sources/primary/`.
3. **Storing source copies**: After analysis is complete, if the original text does not yet exist in `sources/primary/`, prompt the user to store it. Recommended: use the same slug for both the source file and the commentary file (e.g., analyzing Descartes' Second Meditation → store source as `descartes-meditations-2.pdf`, commentary as `commentary-descartes-meditations-2.md`).

### Naming Convention

The `[text-identifier]` portion of the commentary filename must match the original source filename in `sources/primary/`:

```
sources/primary/descartes-meditations-2.md    ← original text
commentary-descartes-meditations-2.md         ← corresponding commentary
```

This convention allows `/draft` to automatically trace from the commentary back to `sources/primary/` to find the original and confirm context.

---

## Stage One: Logical Connector Marking and Preliminary Analysis

Corresponds to assignment guidelines §3 (preparatory work) and §4-5 (understanding text, text types).

### Step 1: Close Reading of Text

Carefully read the entire passage and precisely understand the meaning of each sentence. If the user specifies a file from `sources/primary/`, use the Read tool to access that file.

### Step 2: Mark Logical Connectors

Mark all logical connectors in the original text using the Markdown `==highlight==` syntax.

**Mark only these six categories:**

| Category | Example Terms |
|----------|------------|
| Causal | because, therefore, thus, so, hence, due to, resulting in, from this, consequently |
| Turning Point | but, however, yet, still, conversely, rather |
| Concession | despite, although, even if, even though |
| Condition | if, provided that, only if, in case |
| Progression | moreover, furthermore, even, indeed, not only...but also |
| Contrast | former...latter, both...and, not...but, just as...similarly |

**Strictly prohibited:**
- Philosophical concepts or terminology, ordinary verbs, pronouns or demonstratives, temporal or spatial terms, entire clauses or sentences, generic adverbs

**Each ==highlight== limited to 1-4 characters.** Mark paired connectors separately. Target count: 5-15.

### Step 3: Connector Analysis

List each marked connector, explaining its argumentative function and how it reveals the logical progression of the text.

### Step 4: Preliminary Text Analysis

Answer four questions:
1. **Theme**: What is the theme of the text? What does it discuss?
2. **Purpose**: What is the purpose of the text? What is the author trying to do?
3. **Logical Structure**: What is the logical structure of the text?
4. **Text Type**: (a) Correct or abandon an opinion (b) Reject a claim (c) Establish a definition (d) Solve a problem

### Stage One Output Format

```
## Logical Connectors Marked

[Complete original text, with logical connectors marked using ==highlight==]

## Connector Analysis

| Connector | Category | Argumentative Function |
|-----------|----------|------------------------|
| ...       | Causal   | ...                    |

## Preliminary Text Analysis

**Theme:** ...
**Purpose:** ...
**Logical Structure:** ...
**Text Type:** ...
```

### Stage One Quality Checklist

- [ ] Marked only logical connectors (causal/turning point/concession/condition/progression/contrast), no concepts, verbs, or pronouns mixed in
- [ ] Each marking 1-4 characters, no full-sentence markings
- [ ] Total marking count between 5-15
- [ ] Connector analysis explains the argumentative function of each marking
- [ ] All four preliminary analyses completed
- [ ] All output in Traditional Chinese

**Upon completion, ask the user to confirm the marking results; proceed to Stage Two only after confirmation.**

---

## Stage Two: Writing Complete Commentary

Corresponds to assignment guidelines §6 (three parts of commentary). **Prerequisite: User has confirmed Stage One marking results.**

### One. Introduction (§6.1)

A brief paragraph (approximately 3-6 sentences):
1. Present the problem—that is, the problem the text seeks to solve
2. Briefly describe the text's main argument or direction
3. Indicate what the author is claiming or opposing

**Absolutely avoid**: Analyzing the author's biography (§6.1.2), providing an overview of the author's entire thought system, beginning from abstract concepts

### Two. Development (§6.2)

Core analytical work, using **numbered outline format** paired with bold paragraph titles.

**Process:**
1. Begin with universal concepts mentioned within the text's concerns (§6.2.1)
2. Introduce the problem (§6.2.2)
3. Under the form of the problem presented by the text (question), present the commentator's own problem (problem) (§6.2.3)—mark in bold
4. Emphasize the core concern of the problem (§6.2.4)

**Citation Rules**: When quoting the original text, use quotation marks "". Do not use ==highlight== marks.

### Three. Conclusion (§6.3)

1. Draw a conclusion about the results obtained (§6.3.1)—write coherent discussion first, then attach section numbers in parentheses
2. Expand the results or open toward new problems (§6.3.2)

### Stage Two Output Format

```
## One. Introduction

[Brief paragraph presenting the problem and thesis]

## Two. Development

### 1. [Bold Paragraph Title]
1.1 [Sub-point—quote original text using ""]
1.2 [Sub-point]

### 2. [Bold Paragraph Title]
2.1 [Sub-point]

**The Commentator's Own Problem:** [Clearly marked]

## Three. Conclusion

[Coherent conclusion paragraph with section numbers in parentheses]
[Opening toward new problems]
```

### Stage Two Quality Checklist

- [ ] Introduction presents the problem the text seeks to solve, without author biography, beginning from the text itself
- [ ] Development follows the text's own logical structure, using numbered outline format
- [ ] Development begins with universal concepts, introduces the problem, presents the commentator's own problem, emphasizes core concern
- [ ] The commentator's own problem (problem) is distinguished from the text's problem (question) and clearly marked
- [ ] Conclusion first writes coherent discussion, then attaches section numbers in parentheses
- [ ] Conclusion has openness to new problems
- [ ] Original text quotations use "", entire text contains no ==highlight== marks
- [ ] No independent paraphrasing or deviation from subject matter
- [ ] All output in Traditional Chinese

## File Storage

1. Save the completed commentary to `reviews/[project-name]/commentary-[text-identifier].md`.
2. If the original text analyzed does not yet exist in `reviews/[project-name]/sources/primary/`, remind the user:

   ```
   📝 Commentary saved: commentary-[text-identifier].md

   💡 Recommended: Store the original text (PDF or text file) in:
      sources/primary/[text-identifier].pdf
   This way /claudistotle:draft can automatically locate the original to confirm context during writing.
   ```

---

## Update Index

After saving the commentary, regenerate INDEX.md to reflect the new commentary:

```bash
$PYTHON $CLAUDE_PLUGIN_ROOT/skills/literature-review/scripts/generate_index.py \
  "reviews/[project-name]/"
```

---

## Stage Completion Protocol

When `/text-commentary` completes both stages, output:

```
═══════════════════════════════════════════════════
✅ Text Commentary Complete

📄 Output: commentary-[text-identifier].md
📍 This is independent analysis and does not affect main workflow progress.

💡 This commentary can now be integrated with /claudistotle:draft:
   The system automatically scans commentary-*.md and builds an index during writing.

➡️ Optional next steps:
   • Continue analyzing other texts → /claudistotle:text-commentary
   • Return to main workflow → [Show current stage and next steps from PROGRESS.md]
   • Store original text in sources/primary/ for future reference
═══════════════════════════════════════════════════
```

### Update PROGRESS.md

Read the "Current Status" from `reviews/[project-name]/PROGRESS.md` and display the main workflow's current progress in the completion prompt, so the user knows what to do when returning to the main workflow.

---

**Related Skill:** To research the academic context of the text, use `/claudistotle:literature-review` to search for related secondary sources.

---

## Machine-Readable Exit Signal

As the **last line** of output, append:

```
<!-- STAGE_EXIT: PASS -->
```

This signal is used by `/autopilot` when running text-commentary in parallel with the main pipeline.
