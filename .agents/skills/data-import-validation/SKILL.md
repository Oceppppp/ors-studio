---
name: data-import-validation
description: Build safe Excel/CSV import, preview, mapping, validation, normalization, and immutable dataset versioning for ORS.
---
# Data Import and Validation

## Procedure
1. Validate extension, file signature, size, and parser limits.
2. Store the upload under an internal generated path; never trust the supplied filename as a path.
3. Parse passively. Never execute macros, formulas, scripts, external links, or embedded content.
4. Detect CSV dialect/encoding and Excel workbook sheets; expose user override.
5. Generate a preview and require explicit header/range selection if confidence is low.
6. Infer types as suggestions only; allow manual mapping.
7. Run structural, type, domain, relational, and model-specific validations.
8. Return row/column-specific messages and distinguish errors from warnings.
9. Normalize data without modifying the source; calculate checksum and store immutable dataset version.
10. Add malformed, oversized, encoding, locale, empty-sheet, formula-cache, duplicate and path-traversal tests.

## Guardrails
- Uploaded files are untrusted input.
- Do not use spreadsheet formula evaluation.
- Do not silently coerce ambiguous numbers or dates.
- Preserve source provenance and locale metadata.
