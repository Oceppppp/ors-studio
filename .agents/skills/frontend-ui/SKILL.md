---
name: frontend-ui
description: Build accessible, typed React and TypeScript interfaces for ORS workspaces, data import, analysis forms, job monitoring, and result reporting.
---
# ORS Frontend UI

## Procedure
1. Read the relevant SRS requirement and API contract before building a screen.
2. Use feature-first folders and shared design-system components; do not create one giant page component.
3. Keep strict TypeScript and validate all API responses at the boundary where appropriate.
4. Separate server state from transient UI state.
5. Keep mathematical computation in the Python backend; the frontend only formats, visualizes, and explains returned data.
6. Build accessible forms with labels, units, field-level errors, keyboard support, and meaningful empty/loading/error states.
7. Use responsive tables with sorting/filtering where useful; preserve precision and units.
8. Add Vitest tests for components/formatting and Playwright coverage for critical user journeys.
9. Verify long-running jobs do not block navigation or freeze the UI.
10. Keep colors, typography, spacing, and chart semantics consistent.

## Guardrails
- Never present a planned module as operational.
- Never infer that a solver succeeded from a non-empty result object; inspect status.
- Never rank methods unless backend comparison metadata confirms metric compatibility.
