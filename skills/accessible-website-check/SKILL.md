---
name: accessible-website-check
description: Use when the user asks to check, audit, or improve a website or web project for accessibility (a11y), WCAG compliance, screen reader support, keyboard navigation, color contrast, or alt text. Triggers a plan-mode investigation against the TeachAccess design and code checklists, then implements approved fixes.
---

# Accessible Website Check

Audit a web project for accessibility issues against the TeachAccess design and code checklists, propose a prioritized remediation plan in plan mode, and implement the plan after user approval.

## When to Use

Run when the user asks to:
- "Check accessibility" / "audit a11y" / "make this accessible"
- Improve WCAG compliance, keyboard navigation, screen reader support
- Fix color contrast, alt text, ARIA labels, focus indicators, form labels
- Review a website or web component before launch

## Workflow

1. **Identify scope** — Determine which files/pages/components to audit. If unclear, scan the project root for `index.html`, `src/`, `pages/`, `components/`, or framework markers (React/Vue/Svelte/Astro/Next).

2. **Enter plan mode** — Use `EnterPlanMode` before investigating. All investigation is read-only and happens inside plan mode.

3. **Investigate** — Walk the codebase systematically against both checklists below. For each finding, capture: file path, line number, the checklist item it violates, severity (blocker/major/minor), and the concrete fix.

4. **Write the plan** — Group findings by checklist item. Prioritize blockers (keyboard traps, missing alt text on meaningful images, contrast failures on body text) above minor issues. Include a verification step.

5. **Exit plan mode for approval** — Use `ExitPlanMode`. The user reviews and approves.

6. **Implement** — After approval, apply fixes in priority order. Test each change. Run any available linters/a11y tools (see Tooling).

7. **Verify** — Re-run through the checklists on changed files. Report what was fixed and any items deferred.

## Design Checklist

Source: https://teachaccess.github.io/tutorial/design/checklist

- [ ] Sufficient contrast between text and background (WCAG AA: 4.5:1 normal, 3:1 large)
- [ ] Sufficient contrast between UI elements (borders, icons, focus rings) and background (3:1)
- [ ] No information conveyed by color alone — always pair with text, icon, or pattern
- [ ] Written content is simple and easy to understand (plain language, short sentences)
- [ ] No flashing/flickering content (>3 flashes/sec is a seizure risk)
- [ ] Every mouse interaction has a keyboard-only equivalent
- [ ] Captions included with any audio or audio/visual media
- [ ] Timed responses / session timeouts are clearly communicated and extendable

## Code Checklist

Source: https://teachaccess.github.io/tutorial/code/checklist

- [ ] All images have meaningful `alt` text (decorative images use `alt=""`)
- [ ] Every focusable element is operable by keyboard alone (Tab, Enter, Space, arrow keys where appropriate)
- [ ] Consistent visible focus indicator when navigating by keyboard (no `outline: none` without replacement)
- [ ] All controls, frames, and page titles are labeled meaningfully and uniquely (`<label>`, `aria-label`, `aria-labelledby`, `<title>`)
- [ ] Custom controls expose correct name, role, state, value to assistive tech (ARIA roles/states match WAI-ARIA Authoring Practices)
- [ ] Custom components verified with a screen reader (VoiceOver, NVDA, JAWS)
- [ ] Error messages are interpretable by assistive tech (`aria-describedby`, `role="alert"`, `aria-invalid`)
- [ ] Sufficient foreground/background contrast (re-check in code, not just design)
- [ ] Captions on audio/video media (`<track kind="captions">`)

## Common Issues to Grep For

| Pattern | Likely issue |
|---|---|
| `<img` without `alt=` | Missing alt text |
| `outline: none`, `outline: 0` | Removed focus indicator |
| `<div onClick`, `<span onClick` | Non-semantic interactive element (use `<button>`) |
| `<a href="#"` or `<a>` without `href` | Non-navigable link (use `<button>`) |
| `<input` without associated `<label>` | Unlabeled form field |
| `tabindex="-1"` on interactive content, `tabindex` > 0 | Keyboard order issues |
| `role="button"` without `onKeyDown` for Enter/Space | Missing keyboard handler |
| `placeholder=` used as label | Placeholder is not a label |
| `aria-hidden="true"` on focusable element | Hidden from AT but reachable |
| Color-only state (`color: red` for error, no icon/text) | Color-only meaning |
| `<h1>` skipping to `<h3>` | Broken heading hierarchy |
| `<table>` without `<th>` / `scope` | Inaccessible data table |
| `autoplay` on `<video>` / `<audio>` | Unexpected motion/sound |

## Tooling (suggest to user; do not auto-install)

- **axe-core** / **@axe-core/cli** — automated rule checks
- **Pa11y** — CLI a11y testing
- **Lighthouse** (Chrome DevTools) — bundled a11y audit
- **WAVE** browser extension — visual report
- **eslint-plugin-jsx-a11y** — React/JSX lint rules
- Screen readers: **VoiceOver** (macOS, built in), **NVDA** (Windows, free)

If the project already has one of these configured, run it during the Verify step.

## Plan Format

When exiting plan mode, structure the plan as:

```
## Accessibility Audit — Findings

### Blockers (must fix)
- [file:line] <issue> — <fix>

### Major
- [file:line] <issue> — <fix>

### Minor / polish
- [file:line] <issue> — <fix>

### Out of scope / deferred
- <item> — <reason>

### Verification
- <tool/command/manual step>
```

## Common Mistakes

- **Skipping plan mode** — User explicitly wants to approve before fixes land. Always `EnterPlanMode` first.
- **Auto-installing a11y tooling** — Suggest, don't install, unless the user agrees.
- **Adding ARIA where semantic HTML works** — `<button>` beats `<div role="button">`. First rule of ARIA: don't use ARIA.
- **Removing `outline` without a replacement** — Every focus-removal needs a custom `:focus-visible` style.
- **Treating contrast at design layer only** — Re-check final rendered colors, including hover/disabled states.
- **Decorative vs meaningful images** — Not every image needs descriptive alt; purely decorative images need `alt=""` (empty, not missing).
- **Claiming "done" without screen-reader verification** for custom widgets — note explicitly when manual AT testing is deferred to the user.
