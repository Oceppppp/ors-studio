# ORS Studio — Design System Master

> This document is the source of truth for the visual language of ORS Studio. Page-specific notes may add detail but must not contradict these foundations.

**Product:** Operations Research Studio (ORS)  
**Product type:** Local-first analytical workbench for Operations Research and Production Management  
**Primary users:** Students, operations analysts, industrial engineers, lecturers, and planners  
**Design direction:** Engineering workbench — measured, quiet, technical, data-first  
**Density:** Dense but readable  
**Motion:** Minimal and purposeful

## Product experience principles

1. **Work before decoration.** Every panel should help a user import data, configure a model, inspect a result, or understand an assumption.
2. **Information hierarchy over card count.** Use clear section boundaries, compact readout strips, and aligned tables. Do not wrap every number in a floating tile.
3. **Mathematical clarity.** Values, coefficients, IDs, and parameter text use tabular or monospaced numerals. Prose stays in a humanist sans-serif.
4. **Make assumptions visible.** Model readiness, supported variants, limitations, and validation errors are part of the working surface—not hidden in tooltips.
5. **Local means local.** The UI should communicate that projects and imported data remain on the user's computer.
6. **Quiet confidence.** Avoid gradients, glass effects, giant rounded cards, excessive shadows, decorative charts, fake activity metrics, and animated decoration.

## Color tokens

| Token | Value | Usage |
|---|---:|---|
| `--ors-ink` | `#172A38` | Primary text and headings |
| `--ors-ink-2` | `#294354` | Secondary headings |
| `--ors-muted` | `#60717D` | Supporting text |
| `--ors-muted-2` | `#657781` | Muted but readable text |
| `--ors-line` | `#D9E0E4` | Main dividers and panel borders |
| `--ors-line-soft` | `#E8EDEF` | Subtle table and section separators |
| `--ors-paper` | `#FFFFFF` | Working surfaces |
| `--ors-canvas` | `#F1F4F5` | Application background |
| `--ors-rail` | `#142B3B` | Navigation rail |
| `--ors-rail-2` | `#1D394C` | Navigation hover and secondary rail surface |
| `--ors-primary` | `#245B87` | Primary action, selection, links |
| `--ors-primary-hover` | `#19486F` | Primary hover |
| `--ors-primary-soft` | `#E8F0F6` | Selected/soft primary surface |
| `--ors-amber` | `#B87928` | Caution, active step, and limited emphasis |
| `--ors-amber-soft` | `#F7EFE2` | Caution surface |
| `--ors-teal` | `#247B68` | Success state |
| `--ors-teal-soft` | `#E8F3EF` | Success surface |
| `--ors-danger` | `#A94742` | Errors and destructive action |
| `--ors-danger-soft` | `#F8E9E8` | Error surface |

### Color rules

- Use primary blue for actions and current location, not for every decorative element.
- Amber indicates caution or a deliberate emphasis. It must not be used as a generic accent on every component.
- Success, warning, and error always include readable text; color alone never communicates state.
- Maintain WCAG AA text contrast (4.5:1 for normal text, 3:1 for large text and essential non-text UI where applicable).
- Charts use a restrained categorical palette and direct labels/legends. Do not rely on hue alone to distinguish lines.

## Typography

- **UI/body:** Fira Sans, with system sans-serif fallback.
- **Data/code:** Fira Code, with Cascadia Code/Consolas/monospace fallback.
- Use Fira Code for values, model parameters, metrics, IDs, and code editors—not for long headings or body copy.
- Use sentence case for page titles, buttons, navigation, and section headings.
- Use tabular numerals for all metrics and numeric columns.
- Keep labels concise and descriptive; avoid all-caps paragraphs. Small uppercase eyebrow labels are allowed sparingly.
- Do not use font-size below 11px for information essential to completing a task.

## Layout and spacing

- Desktop shell uses a fixed 252px navigation rail and a fluid main work area.
- Main content has a readable maximum width and 34px desktop side padding; compact to 24px tablet and 16px mobile.
- Use a 4px base spacing rhythm, with 8/12/16/24/32px as common intervals.
- Panels use 6–7px radius and no default shadow. Reserve elevation for overlays only.
- Data tables are full-width within a horizontally scrollable container; headers remain visually distinct and sticky only when the table requires it.
- The analytical configuration page uses a persistent narrow model browser plus a wide configuration surface on desktop; stack the surfaces on smaller screens.
- KPI values use a separated readout strip with vertical dividers—not four floating KPI cards.

## Component rules

### Buttons
- Primary: solid ORS blue, compact, clear verb; one primary action per working surface.
- Secondary: white surface with neutral border.
- Ghost/text: only for lower-priority navigation or reversible actions.
- Active feedback may use a subtle `scale(.98)`; no jumping or large transformations.
- Every icon-only button needs an accessible name.

### Navigation
- Dark graphite rail with a clear active marker.
- SVG line icons share a consistent 24px viewBox and 1.6–1.8px stroke.
- Selected destination must be apparent without color alone (`aria-current="page"`).

### Forms and model editors
- Labels name the data being requested. Inputs retain visible focus states.
- JSON parameters use a neutral code surface and monospaced type; avoid syntax-color overload.
- Keep data mapping separate from model parameter editing and explain what column replaces what parameter.
- Errors appear adjacent to the relevant control and in an announced status region where appropriate.

### Tables and charts
- Table headings use a quiet contrast surface, medium-weight text, and consistent alignment.
- Numeric columns should align right when applicable and use tabular numerals.
- Charts include a title, axis/context note, and legend or direct labels. Provide a text/table equivalent for key data.
- No 3D charts, decorative gauges, gratuitous gradients, or chart junk.

### Status
- Use restrained labels (`SUCCEEDED`, `FAILED`, `RUNNING`, `QUEUED`) with readable text and distinctive shape/background.
- Never use emoji as interface icons.

## Motion and interaction

- Use motion only to clarify a state change or spatial transition.
- Typical duration: 120–180ms; easing: `cubic-bezier(.23, 1, .32, 1)` for entry and simple ease for color changes.
- Never use `transition: all`.
- Respect `prefers-reduced-motion: reduce`.
- Hover must not shift layout. Maintain a visible `:focus-visible` ring for keyboard users.

## Responsive breakpoints

| Width | Behavior |
|---|---|
| 1440px+ | Full workbench layout |
| 1024–1439px | Tightened paddings and two-column featured modules |
| 768–1023px | Navigation becomes a drawer; analytical surfaces stack when necessary |
| 375–767px | Single-column layouts, compact readout grid, full-width form controls |

## Prohibited visual patterns

- Generic SaaS dashboard made from identical rounded cards.
- Purple-blue/pink gradients, glassmorphism, oversized blur shadows, and floating pills everywhere.
- Unmotivated illustrations, emoji icons, or chart imagery that doesn't represent real data.
- All-caps body copy, tiny low-contrast metadata, or buttons that use only an icon without a label.
- Fake metrics, fake activity, and status indicators that don't reflect API state.

## Acceptance checklist

- [ ] A new user can identify the next action without reading a long instruction.
- [ ] The dashboard prioritizes data, models, and analysis history over decoration.
- [ ] Model scope and assumptions are visible before/after a run.
- [ ] Import, preview, and mapping are keyboard accessible.
- [ ] Tables and chart labels remain legible at 375, 768, 1024, and 1440px.
- [ ] All text and controls meet the stated contrast/focus requirements.
- [ ] Reduced-motion preference is respected.
- [ ] No generic AI-template motifs are introduced.
