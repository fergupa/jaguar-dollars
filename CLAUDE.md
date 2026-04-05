# Vibe Code System

This is a template project for vibe coding sessions with Claude Code.

## Skills

All skills are in `.claude/skills/`. Before responding to any task, check if a skill applies using the `using-superpowers` skill.

**Mandatory:** Invoke the `brainstorming` skill before any creative work — creating features, building components, adding functionality, or modifying behavior.

### Development Workflow (obra/superpowers)

| Skill | When to Use |
|-------|-------------|
| `using-superpowers` | Every conversation — determines which skills to invoke |
| `brainstorming` | Before any creative work: new features, components, functionality changes |
| `writing-plans` | When you have a spec or requirements for a multi-step task, before coding |
| `executing-plans` | When you have a written implementation plan to execute in a separate session |
| `subagent-driven-development` | When executing implementation plans with independent tasks in the current session |
| `test-driven-development` | When implementing any feature or bugfix, before writing implementation code |
| `systematic-debugging` | When encountering any bug, test failure, or unexpected behavior |
| `dispatching-parallel-agents` | When facing 2+ independent tasks with no shared state |
| `using-git-worktrees` | When starting feature work that needs isolation from current workspace |
| `finishing-a-development-branch` | When implementation is complete and you need to integrate the work |
| `requesting-code-review` | When completing tasks, major features, or before merging |
| `receiving-code-review` | When receiving code review feedback, before implementing suggestions |
| `verification-before-completion` | Before claiming work is complete, fixed, or passing |
| `writing-skills` | When creating or editing skills |

### React & Next.js (vercel-labs)

| Skill | When to Use |
|-------|-------------|
| `react-best-practices` | When writing, reviewing, or refactoring React/Next.js code for performance. 57 rules across 8 categories (waterfalls, bundle size, server perf, client data fetching, re-renders, rendering, JS perf, advanced patterns). See `AGENTS.md` for the full compiled guide. |

### Security (wshobson/agents)

| Skill | When to Use |
|-------|-------------|
| `security-scanning/stride-analysis-patterns` | When conducting threat modeling or analyzing system security using STRIDE |
| `security-scanning/attack-tree-construction` | When mapping attack scenarios or identifying defense gaps |
| `security-scanning/security-requirement-extraction` | When translating threats into actionable requirements or security user stories |
| `security-scanning/threat-mitigation-mapping` | When prioritizing security investments or designing defense-in-depth |
| `security-scanning/sast-configuration` | When setting up Semgrep, SonarQube, or CodeQL for automated vulnerability detection |

### Browser Automation (vercel-labs)

| Skill | When to Use |
|-------|-------------|
| `agent-browser` | When the user needs to interact with websites: navigating pages, filling forms, clicking buttons, taking screenshots, extracting data, testing web apps, or automating any browser task. Core workflow: navigate → snapshot → interact with refs → re-snapshot. |

## Design Documents

Save design documents to `docs/plans/YYYY-MM-DD-<topic>-design.md` and commit them.

## Worktrees

Use `.worktrees/` for git worktrees (already in .gitignore).
