# Claudistotle — Publishing Plan

This document outlines two publishing routes for the Claudistotle plugin: GitHub self-hosted marketplace (immediate availability) and the official Anthropic marketplace (broader reach after review).

---

## Route 1: GitHub Repository + Self-Hosted Marketplace

**Goal**: Let anyone install Claudistotle directly from a public GitHub repo.

### Step 1 — Create the GitHub Repository

```bash
# Navigate to the plugin directory
cd claudistotle-plugin

# Initialize git
git init
git branch -M main

# Create the remote repo (requires gh CLI)
gh repo create Rlin1027/claudistotle --public \
  --description "Philosophy research assistant plugin for Claude Code"

# Or create manually at https://github.com/new
```

### Step 2 — Push the Code

```bash
git add .
git commit -m "Initial release v1.0.0 — Claudistotle philosophy research plugin"
git remote add origin git@github.com:Rlin1027/claudistotle.git
git push -u origin main
```

### Step 3 — Create a Release Tag

```bash
git tag -a v1.0.0 -m "v1.0.0 — Initial public release"
git push origin v1.0.0
```

Optionally, create a GitHub Release via the web UI or:

```bash
gh release create v1.0.0 --title "v1.0.0" --notes "Initial release of Claudistotle plugin."
```

### Step 4 — How Users Install

Users have two options:

**Option A — Add as marketplace (recommended):**

```
/plugin marketplace add Rlin1027/claudistotle
/plugin install claudistotle@claudistotle
```

This allows auto-update support. When you push a new version, users run `/plugin marketplace update claudistotle` to get the latest.

**Option B — Project-level configuration:**

Add to `.claude/settings.json` in any project repo:

```json
{
  "extraKnownMarketplaces": {
    "claudistotle": {
      "source": {
        "source": "github",
        "repo": "Rlin1027/claudistotle"
      }
    }
  },
  "enabledPlugins": {
    "claudistotle@claudistotle": true
  }
}
```

This auto-prompts collaborators to install the plugin when they trust the project folder.

### Files Created for Route 1

| File | Purpose |
|------|---------|
| `.claude-plugin/marketplace.json` | Marketplace catalog — lists the plugin with metadata |
| `.claude-plugin/plugin.json` | Plugin manifest — name, version, author, keywords |
| `.gitignore` | Excludes .env, .venv, .DS_Store, reviews output |

---

## Route 2: Official Anthropic Marketplace

**Goal**: Get listed in `claude-plugins-official` so all Claude Code users can discover and install Claudistotle from the built-in Discover tab.

### Prerequisites

- The GitHub repo from Route 1 must be public and stable
- Plugin must pass `claude plugin validate .` with no errors
- README.md should be comprehensive (already done)

### Step 1 — Validate the Plugin

```bash
# From the plugin root directory
claude plugin validate .
```

Fix any reported errors before submitting.

### Step 2 — Submit via the Official Form

Choose one:

- **Claude.ai**: https://claude.ai/settings/plugins/submit
- **Console**: https://platform.claude.com/plugins/submit

Fill in:
- **Plugin name**: claudistotle
- **GitHub repo URL**: https://github.com/Rlin1027/claudistotle
- **Description**: Philosophy research assistant — automated literature review with verified citations, primary text analysis, academic writing, and peer review simulation.
- **Category**: Research / Academic
- **License**: Apache-2.0

### Step 3 — Wait for Review

Anthropic reviews plugins for quality and security. The review process may take some time. Keep the GitHub repo maintained during this period.

### Step 4 — After Approval

Once approved, users install with:

```
/plugin install claudistotle@claude-plugins-official
```

The plugin appears in the Discover tab of `/plugin` for all Claude Code users.

---

## Version Update Workflow

When you release a new version:

1. Update `version` in both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
2. Commit and push
3. Tag the release:
   ```bash
   git tag -a v1.1.0 -m "v1.1.0 — description of changes"
   git push origin v1.1.0
   ```
4. Users on Route 1 run `/plugin marketplace update claudistotle` to get the new version
5. Users on Route 2 (official marketplace) get updates automatically if auto-update is enabled

---

## Repository Structure (Ready to Push)

```
claudistotle/                       ← GitHub repo root
├── .claude-plugin/
│   ├── plugin.json                 ← Plugin manifest
│   └── marketplace.json            ← Self-hosted marketplace catalog
├── .gitignore
├── assets/
│   └── Claudistotle.png
├── agents/
│   ├── literature-review-agent.md
│   ├── peer-review-agent.md
│   ├── autopilot-agent.md
│   └── text-commentary-agent.md
├── skills/
│   ├── setup/SKILL.md
│   ├── help/SKILL.md
│   ├── research-design/SKILL.md
│   ├── literature-review/SKILL.md  (+ scripts/)
│   ├── refine/SKILL.md
│   ├── text-commentary/SKILL.md
│   ├── draft/SKILL.md
│   ├── validate/SKILL.md
│   ├── peer-review/SKILL.md
│   ├── feedback/SKILL.md
│   ├── autopilot/SKILL.md
│   └── philosophy-research/SKILL.md (+ scripts/)
├── hooks/
│   ├── hooks.json
│   └── scripts/
├── docs/
│   ├── workflow.mermaid
│   ├── ARCHITECTURE.md
│   ├── conventions.md
│   ├── permissions-guide.md
│   └── PUBLISHING.md              ← This file
├── reviews/                        ← Template directory (gitignored contents)
├── CLAUDE.md
├── README.md
├── CONTRIBUTING.md
├── GETTING_STARTED.md
├── LICENSE                         ← Apache-2.0
├── pyproject.toml
└── settings.json
```

---

## Quick Start Checklist

- [ ] Run `claude plugin validate .` — fix any errors
- [ ] Create GitHub repo: `gh repo create Rlin1027/claudistotle --public`
- [ ] `git init && git add . && git commit -m "Initial release v1.0.0"`
- [ ] `git remote add origin git@github.com:Rlin1027/claudistotle.git`
- [ ] `git push -u origin main`
- [ ] `git tag -a v1.0.0 -m "v1.0.0" && git push origin v1.0.0`
- [ ] Test install: `/plugin marketplace add Rlin1027/claudistotle`
- [ ] Submit to official marketplace via https://claude.ai/settings/plugins/submit
