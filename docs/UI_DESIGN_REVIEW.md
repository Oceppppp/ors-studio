# ORS Studio — Operations Workbench Design Review (v0.4.0)

## Design direction

The interface is designed as a workbench for operations analysts rather than a generic SaaS dashboard. The main visual priority is the sequence of work: dataset → model → parameters → execution → result. Data tables and model configuration receive more visual weight than decorative KPIs.

## Principles

- Graphite navigation rail and restrained neutral workspace surfaces.
- Blue is reserved for primary actions and active navigation; amber is used sparingly for attention/warnings; green indicates confirmed completion.
- Typography uses a consistent hierarchy and tabular numerals for quantitative readouts.
- Icons use inline SVG with consistent line weight; emoji are not used as navigation icons.
- Spacing and borders separate real work regions rather than creating a wall of identical cards.
- Responsive layouts preserve table usability and module selection on smaller screens.
- Focus-visible states, keyboard-friendly dialogs, semantic buttons and reduced-motion handling are included.
- Guest/account access screen follows the same ORS visual system; authentication should not feel like an unrelated template.

## Screens reviewed

- Overview and project/workspace context.
- Module browser and parameter configuration.
- Data Center upload, worksheet selection, preview and mapping.
- Batch queue and job status.
- Analysis history and result viewer.
- Settings, project dialog and Web authentication gate.

## Design regression checklist

1. No generic gradient-heavy hero or glassmorphism.
2. No arbitrary stock illustrations or fake analytics.
3. Keep all 29 modules searchable and grouped by domain.
4. Long result tables must remain readable and horizontally scrollable when necessary.
5. Use status labels consistently (`QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED`, `CANCELLED`).
6. Auth errors are visible and associated with the form; password fields use appropriate autocomplete attributes.
7. UI is a presentation of server truth; never fabricate progress or solver results.

The design review records source-level UI standards; it is not a substitute for manual browser QA on the target Windows/browser matrix.
