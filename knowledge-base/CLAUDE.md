# Knowledge Base Schema

This file defines the structure, naming conventions, and maintenance rules for the Claudistotle knowledge base. It serves as the "schema layer" (inspired by Karpathy's LLM knowledge base architecture).

## Architecture

```
knowledge-base/
├── CLAUDE.md          ← You are here (schema layer)
├── index.md           ← Navigational index (auto-updated by ingest)
├── log.md             ← Operation log (ingest/query history)
├── raw/               ← Read-only project snapshots
│   └── [project]/     ← literature-all.bib + literature-review-final.md
├── wiki/              ← LLM-maintained structured knowledge
│   ├── philosophers/  ← One page per significant philosopher
│   ├── concepts/      ← One page per significant concept
│   └── debates/       ← One page per significant debate/tension
└── notes/             ← Human-curated informal notes
    ├── reading-notes/
    └── ideas/
```

## Naming Conventions

- Philosopher files: `wiki/philosophers/{lowercase-hyphenated-name}.md` (e.g., `immanuel-kant.md`)
- Concept files: `wiki/concepts/{lowercase-hyphenated-concept}.md` (e.g., `categorical-imperative.md`)
- Debate files: `wiki/debates/{lowercase-hyphenated-topic}.md` (e.g., `deontology-vs-consequentialism.md`)
- Raw snapshots: `raw/{project-short-name}/` matching `reviews/{project-short-name}/`

## Cross-References

Use Obsidian-compatible wikilinks: `[[wiki/philosophers/{slug}|{Display Name}]]`

Examples:
- `[[wiki/philosophers/immanuel-kant|Immanuel Kant]]`
- `[[wiki/concepts/categorical-imperative|Categorical Imperative]]`
- `[[wiki/debates/deontology-vs-consequentialism|Deontology vs. Consequentialism]]`

## Page Templates

### Philosopher Page

```markdown
---
name: "{Full Name}"
type: philosopher
era: "{era, e.g., Modern Philosophy (18th century)}"
traditions: [{tradition1}, {tradition2}]
sources: [{project-name-1}]
last_updated: {YYYY-MM-DD}
---

# {Full Name}

## Core Claims
- {claim}, as argued in {Work Title} ({Year})

## Key Works
- *{Title}* ({Year}) — {one-line summary}

## Related Papers
- {Author} ({Year}). "{Title}." {Journal}. DOI: {doi}. — CORE ARGUMENT: {summary}

## Relationships
- Influenced by: [[wiki/philosophers/{slug}|{Name}]]
- Influenced: [[wiki/philosophers/{slug}|{Name}]]
- Debated with: [[wiki/philosophers/{slug}|{Name}]] on [[wiki/concepts/{slug}|{concept}]]

## Cross-Project Notes
### {project-name} ({date})
{Summary of findings from this project}
```

### Concept Page

```markdown
---
name: "{Concept Name}"
type: concept
domains: [{domain1}, {domain2}]
sources: [{project-name-1}]
last_updated: {YYYY-MM-DD}
---

# {Concept Name}

## Definition
{Clear definition with citations}

## Key Perspectives
### {Philosopher/School 1}
{Position and argument}, as argued by [[wiki/philosophers/{slug}|{Name}]]

## Related Philosophers
- [[wiki/philosophers/{slug}|{Name}]] — {their stance on this concept}

## Cross-Project Notes
### {project-name} ({date})
{Summary of how this concept was explored}
```

### Debate Page

```markdown
---
name: "{Debate Topic}"
type: debate
participants: [{philosopher1}, {philosopher2}]
sources: [{project-name-1}]
last_updated: {YYYY-MM-DD}
---

# {Debate Topic}

## Overview
{Brief description of the debate and its significance}

## Positions
### [[wiki/philosophers/{slug}|{Name}]]
{Their position and key arguments}

### [[wiki/philosophers/{slug}|{Name}]]
{Their position and key arguments}

## Key Texts
- {Author} ({Year}). "{Title}." — {how it contributes to this debate}

## Cross-Project Notes
### {project-name} ({date})
{Summary of how this debate appeared in the project}
```

## Ingest Rules

1. **Citation integrity**: All academic claims in wiki pages MUST trace to a verified BibTeX entry. Never generate unsourced claims.
2. **Additive updates**: When updating existing pages, ONLY append to `## Cross-Project Notes` and `## Related Papers`. Never modify prior content in `## Core Claims` or `## Relationships` — only ADD new entries.
3. **Entity threshold**: Create pages only for entities appearing in 2+ BibTeX entries OR flagged as High importance.
4. **Frontmatter maintenance**: Always update `sources` array and `last_updated` when modifying a page.
5. **Index sync**: After creating or updating any wiki page, update the corresponding table in `index.md`.
6. **Log append**: Record every ingest operation in `log.md`.

## Query Rules

1. Read `index.md` first to identify relevant pages.
2. Load at most 5 wiki pages per query for context efficiency.
3. When compiling a Prior Knowledge Brief, include: Known Philosophers, Known Concepts, Known Papers, Research Gaps.

## Maintenance (Future)

- Lint: Detect contradictions between pages, find orphan pages, suggest missing cross-references
- Search: Add local search engine (qmd) when wiki exceeds 100 pages
- Obsidian: Add Dataview queries and Graph View optimization
