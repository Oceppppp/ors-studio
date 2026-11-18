---
name: antigravity-skill-audit
description: Audit Antigravity skills and project customizations available on the current machine, then map relevant capabilities to ORS work without claiming unavailable skills.
---
# Antigravity Skill Audit

## When to use
Use at project setup, before assigning a specialized development task, and whenever a new skill/plugin/customization is added.

## Procedure
1. Read `docs/ANTIGRAVITY_SKILL_CATALOG.md` and `docs/SKILL_USAGE_MATRIX.md` first; use the catalog as the owner-provided baseline, not as proof of live runtime state.
2. Inspect Antigravity Customizations > Installed when operating in the IDE/App, or use supported CLI listing commands if available.
3. Inspect workspace `.agents/skills/` and the global skill discovery locations for the current Antigravity surface. Do not assume one path applies to every surface/version.
4. Read each task-relevant `SKILL.md` in full, including required references; do not assume directory presence means a skill loaded successfully.
5. Verify connected MCP servers, CLIs, browser tools, and authentication before calling skill-dependent tools.
6. Record skill name, source path/scope, description, ORS task mapping, and whether it was actually used in `docs/skill-audit.md` or task notes.
7. Use relevant skills only; do not load all 339 skills for every task or claim every skill was used.
8. Identify gaps and propose project-specific skill files under `.agents/skills/` only when they add repeatable ORS procedures.
9. Re-check the active skill list after changes and note any surface-specific refresh requirement.

## Output
A timestamped skill inventory, relevance matrix, gaps, and exact source path for each skill. Never copy private global skill contents into the repository without permission.
