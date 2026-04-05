# Vibe Code System

A template project for starting vibe coding sessions with [Claude Code](https://claude.ai/claude-code). Comes pre-loaded with 21 skills across 4 categories.

## What's Included

### Development Workflow — [obra/superpowers](https://github.com/obra/superpowers) (14 skills)

| Skill | Purpose |
|-------|---------|
| `using-superpowers` | Orchestrates all other skills — determines which to invoke |
| `brainstorming` | Structured ideation before any creative work |
| `writing-plans` | Design documents from specs/requirements |
| `executing-plans` | Execute implementation plans in a separate session |
| `subagent-driven-development` | Parallel execution of independent implementation tasks |
| `test-driven-development` | Write tests before implementation |
| `systematic-debugging` | Root-cause analysis for bugs and failures |
| `dispatching-parallel-agents` | Run 2+ independent tasks concurrently |
| `using-git-worktrees` | Isolated workspaces for feature development |
| `finishing-a-development-branch` | Integration workflow when implementation is complete |
| `requesting-code-review` | Structured self-review before merging |
| `receiving-code-review` | Process and respond to review feedback |
| `verification-before-completion` | Final checks before declaring work done |
| `writing-skills` | Create or edit Claude Code skills |

### React & Next.js — [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) (1 skill, 57 rules)

| Skill | Purpose |
|-------|---------|
| `react-best-practices` | Performance rules across 8 categories: async/waterfalls, bundle size, server, client data fetching, re-renders, rendering, JS performance, advanced patterns |

### Security — [wshobson/agents](https://github.com/wshobson/agents) (5 skills)

| Skill | Purpose |
|-------|---------|
| `stride-analysis-patterns` | STRIDE threat modeling |
| `attack-tree-construction` | Attack scenario mapping |
| `security-requirement-extraction` | Threats → actionable requirements |
| `threat-mitigation-mapping` | Defense-in-depth prioritization |
| `sast-configuration` | Semgrep, SonarQube, CodeQL setup |

### Browser Automation — [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) (1 skill)

| Skill | Purpose |
|-------|---------|
| `agent-browser` | Navigate pages, fill forms, click buttons, take screenshots, extract data |

## Quick Start

### Create a new project from this template

**CLI:**
```bash
gh repo create my-new-app --template fergupa/vibe-code-system --clone --public
cd my-new-app
```

**GitHub UI:** Click **"Use this template"** → **"Create a new repository"**

### Start coding

Open the new project in VS Code with [Claude Code](https://claude.ai/claude-code) and describe what you want to build. The `brainstorming` skill will automatically kick in before any implementation begins.

## Project Structure

```
.claude/
  skills/           ← All 21 skills live here
  settings.local.json
docs/
  plans/            ← Design documents go here
CLAUDE.md           ← Project instructions for Claude Code
```

## License

The skills in this template are sourced from their respective open-source repositories. See each skill's source repo for license details.
