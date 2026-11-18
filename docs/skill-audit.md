# Antigravity Skill Audit Record

**Audit date:** 2026-11-17  
**Status:** Archive-level audit completed; live Antigravity runtime audit remains pending.  
**Source:** User-uploaded `antigravity-all-skills.zip`.

## Archive verification

- Catalog manifest: **339 active skills**.
- Catalog breakdown: **14 built-in**, **28 user skills**, **297 plugin skills**.
- Physical archive paths: **339 primary `SKILL.md` files** + **10 nested upstream copies** = **349 `SKILL.md` paths**.
- Interpretation: the 10 nested `upstream/SKILL.md` files are source copies inside plugin bundles and are not extra active skills.
- The catalog index is preserved at `docs/ANTIGRAVITY_SKILL_CATALOG.md`.
- Task-to-skill mapping and activation policy are preserved at `docs/SKILL_USAGE_MATRIX.md`.

## Audit method

1. Read the supplied archive README and complete 339-entry skill index.
2. Compared the indexed count with primary `SKILL.md` paths in the ZIP.
3. Identified and read the full skill instructions for the ORS-relevant workflow, architecture/API, Python dependencies, React/UI, data handling, performance, debugging, verification, and code-review skills.
4. Inspected Antigravity customization guidance and its skill/rule discovery notes.
5. Separated directly applicable skills from skills that require external tools/services or target unrelated stacks.

## Directly applicable skills

See `docs/SKILL_USAGE_MATRIX.md` for the full table, source path, ORS use, and activation point. High-priority skill groups include:

- Process: `using-superpowers`, `brainstorming`, `planning`, `writing-plans`, `executing-plans`, `build`.
- Engineering quality: `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `code-review`.
- Architecture/API/backend: `api-and-interface-design`, `managing-python-dependencies`.
- Frontend: `frontend-design`, `design-taste-frontend`, `ui-ux-pro-max`, `design-system`, `ui-styling`, `emil-design-eng`, `vercel-composition-patterns`, `vercel-react-best-practices`.
- Performance and file workflows: `performance-optimization`, `webperf`, `xlsx`.

## Applicability limitations

- A skill's presence in the export does not prove an associated MCP server, CLI, browser instrumentation, account, license, credential, or package is available in the current Antigravity session.
- GCP-only skills such as Dataplex/BigQuery/GCS autocleaning are not used for local CSV/XLSX ingestion.
- Flutter, Unity, React Native, Firebase, Auth0, Vercel, Figma, CodeRabbit, SonarQube, Chrome DevTools, and other integration-specific skills are conditional on the task and actual runtime availability.
- No dedicated general Operations Research / POM-QM solver skill was identified in the active index. ORS-specific project skills cover this gap.

## Live Antigravity check still required

The agent operating inside the user's Antigravity environment must verify the actual installed/loaded skill list, workspace/global discovery, plugins, MCP servers, and tool availability. This chat can inspect the supplied ZIP but cannot inspect the user's live IDE state or run its local agent tools.

| Check | Status | Evidence required |
|---|---|---|
| Uploaded skill archive/index | Complete | 339 catalog entries and matching 339 primary SKILL.md paths |
| ORS relevance mapping | Complete | `docs/SKILL_USAGE_MATRIX.md` |
| Full selected-skill review | Complete for listed ORS-relevant skills | Actual `SKILL.md` content and referenced files read as needed |
| Live Customizations > Installed | Pending | Screenshot/export or direct Antigravity inspection |
| MCP / CLI / auth availability | Pending | Per-tool preflight in Antigravity |
| Skill refresh/reload behavior | Pending | Verify in the actual Antigravity surface/version |

## Rule

Do not claim every one of the 339 skills was used. Select and apply the matching skill(s) for each task using progressive disclosure, and record the actually used skills in implementation/release notes.
