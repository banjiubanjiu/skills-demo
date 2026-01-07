# Repository Guidelines

## Project Structure & Module Organization
- Root contains a static skills showcase: `index.html`, `styles.css`, `script.js`.
- Skill definitions live under `frontend-design/` (for example `frontend-design/SKILL.md`).
- Supporting notes live in `x_tweets.md`; dot-directories like `.claude/` are editor/runtime config and normally not edited.

## Build, Test, and Development Commands
- Local preview (Python 3): `python -m http.server 8000` then open `http://localhost:8000/index.html`.
- You can also open `index.html` directly in a browser for quick checks; prefer a local server when testing animations or relative paths.

## Coding Style & Naming Conventions
- Use vanilla HTML/CSS/JS; avoid adding frameworks without strong justification.
- Follow existing formatting: 4-space indentation, single-responsibility sections, and descriptive class names (for example `skill-card`, `benefit-card`).
- Prefer CSS variables and design tokens defined in `styles.css` for colors, spacing, and typography.
- When changing visual design, consult `frontend-design/SKILL.md` and keep the neo-brutalist terminal aesthetic consistent.

## Testing Guidelines
- No automated test suite; rely on manual testing in at least one Chromium browser.
- Verify layout and interactions at common breakpoints (mobile, tablet, desktop) and ensure animations remain smooth.
- Check for console errors and confirm hover/scroll effects and trigger tags behave as expected.

## Commit & Pull Request Guidelines
- Use short, imperative commit messages (for example `Refine hero animation`, `Add skills grid tweaks`).
- Scope commits narrowly around a coherent change; avoid mixing design refactors and behavior changes.
- Pull requests should include a brief summary, highlight user-facing changes, and attach before/after screenshots for visual updates.

## Agent-Specific Instructions
- Treat this file as the root `AGENTS.md`; its rules apply repository-wide.
- When implementing or modifying UI, prefer reusing existing patterns and follow guidance in `frontend-design/SKILL.md` instead of reinventing styles.

