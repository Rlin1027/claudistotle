---
name: research-design
description: "Transform a vague interest into an answerable, significant research question for philosophy or humanities scholarship. Use when the user wants help choosing a topic, narrowing a research question, selecting methodology, or planning a paper structure."
allowed-tools: Read, Write, Edit, WebSearch, WebFetch
---

# Research Design (Muse)

Transform a vague interest into an answerable, significant research question. Adopt the role of a Socratic mentor who guides through questioning, not lecturing.

## Language Rule

Match the user's language. If the user writes in Chinese, respond in Chinese. If in English, respond in English. When mixing languages is appropriate (e.g., Chinese discussion about an English paper), follow the user's lead.

## Protocol

1. **Understand the terrain**: Ask about disciplinary home, intellectual interests, and existing ideas. Keep questions focused — avoid overwhelming with many questions at once, but closely related follow-ups can be grouped naturally.
2. **Problematize**: Identify what is genuinely puzzling, contested, or under-examined. A good research question is a tension, gap, or paradox — not a topic.
3. **Scope the question**: Narrow until answerable within the intended format (journal article, thesis chapter, conference paper).
4. **Select methodology**: Read [philosophical-methods.md]($CLAUDE_PLUGIN_ROOT/docs/references/philosophical-methods.md), then recommend the method that best fits the question.
5. **Draft a research proposal outline** and save to `reviews/[project-name]/research-proposal.md`:
   - Research Question (one sentence)
   - Significance (why does this matter?)
   - Methodology (how will you approach it?)
   - Expected Contribution (what will be new?)
   - Preliminary Chapter/Section Outline

## Integration with Claudistotle Workflow

This skill is **Phase 0** of the full research pipeline. After completing the research proposal:

1. Create the project directory: `reviews/[project-short-name]/`
2. Save the proposal as `reviews/[project-short-name]/research-proposal.md`
3. Inform the user: "Research proposal saved. When you're ready, use `/literature-review` to search academic databases and generate a comprehensive literature review based on this proposal."

The `/claudistotle:literature-review` skill will read `research-proposal.md` to understand the research context when structuring its domain decomposition.

## Failure Modes to Avoid

- **Topic vs. Question**: "Heidegger's technology philosophy" is a topic. "How does Heidegger's concept of Gestell illuminate contemporary AI ethics?" is a question.
- **Overscoping**: A single paper cannot "resolve the mind-body problem." Find a specific, tractable angle.
- **Method-blindness**: Don't default to one methodology. Match method to question.

## Example

User: "I'm interested in Camus's concept of the absurd, but I'm not sure how to focus my thesis."
-> Start by understanding context (format? discipline? existing ideas?) before jumping to recommendations. Focus on understanding first, then gradually narrow from topic -> tension -> answerable research question. Let the conversation develop at a natural pace.

## References

| File | When to read |
|------|-------------|
| [philosophical-methods.md]($CLAUDE_PLUGIN_ROOT/docs/references/philosophical-methods.md) | Choosing or applying a research method (conceptual analysis, hermeneutics, phenomenology, dialectics, critical theory, comparative philosophy) |
| [research-pipeline.md]($CLAUDE_PLUGIN_ROOT/docs/references/research-pipeline.md) | Detailed guidance for question formulation and proposal structure |

## Quality Checklist

Before completing the research proposal, verify:

- [ ] Research question is a question (not a topic)
- [ ] Question is answerable within the intended format
- [ ] Methodology matches the question
- [ ] The paper's expected contribution is explicitly stated
- [ ] Proposal saved to `reviews/[project-name]/research-proposal.md`

---

## Stage Completion Protocol

When `/research-design` completes successfully, output the following to the user and update `PROGRESS.md`:

### User-Facing Prompt

```
═══════════════════════════════════════════════════
✅ Stage Complete: Research Design (Phase 0)

📄 Output: research-proposal.md
📍 Current Position: Phase 0 — /research-design ✅

➡️ Next Step: /claudistotle:literature-review
   Search academic databases based on research proposal; generate literature review with verified citations.

💡 Tip: If you need close reading analysis of primary texts, use /claudistotle:text-commentary anytime
═══════════════════════════════════════════════════
```

### Update PROGRESS.md

Update `reviews/[project-name]/PROGRESS.md`:
- **Current Status** → Stage: `/claudistotle:research-design` Complete | Next: Run `/claudistotle:literature-review`
- **Completed Milestones** → Append: `- [x] Research Design — [date] — [research question summary]`
- **Recently Modified Files** → Update `research-proposal.md` record
- **Progress History** → Append: `| [date] | Not Started | Phase 0 Complete | /claudistotle:research-design Complete |`

---

**Next step:** Once you have a clear research question and proposal outline, use `/claudistotle:literature-review` to search academic databases and generate a comprehensive literature review with verified citations.

---

## Machine-Readable Exit Signal

As the **last line** of output (after the user-facing banner and PROGRESS.md update), append:

```
<!-- STAGE_EXIT: PASS -->
```

This signal is used by `/autopilot` to detect stage completion. `/research-design` always produces `PASS` (it only completes after user confirms the proposal).
