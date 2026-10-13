---
name: c4
description: Author C4 architecture diagrams as Structurizr DSL, with Nygard ADRs and supplementary docs — scaffold a new workspace, edit the model, validate, export, and preview. Use when the user wants to set up C4 or Structurizr in a repo ("set up C4 here", "scaffold the architecture docs"); add or change a server, service, container, component, database, queue, actor, relationship, view, style, or deployment environment in workspace.dsl; model an existing codebase or its AWS/Kubernetes infrastructure as C4; record or supersede an architecture decision; check whether workspace.dsl is valid; get PlantUML, Mermaid, workspace JSON, or a static HTML site out of the model (or asks for PNG/SVG); or start or stop a live browser preview of the diagrams. Also consult before writing any .dsl file, ADR, or architecture doc for the house style.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(bash:*), Bash(docker:*), Bash(ls:*), Bash(find:*), Bash(cat:*), Bash(test:*), Bash(mkdir:*), Bash(cp:*), Bash(touch:*)
---

# c4 — C4 architecture as Structurizr DSL

One skill, six workflows. Pick the workflow that matches the request, read its file, and follow it. Every bundled path is relative to `${CLAUDE_SKILL_DIR}`, the directory holding this file. When a workflow says `c4 <name>`, it means the workflow in `${CLAUDE_SKILL_DIR}/workflows/<name>.md`.

## Dispatch

| The user wants to…                                                              | Read                                         |
|---------------------------------------------------------------------------------|----------------------------------------------|
| Start C4 docs where no `workspace.dsl` exists yet                               | `${CLAUDE_SKILL_DIR}/workflows/structurize.md` |
| Change the model, views, styles, deployment, ADRs, or docs; model a codebase    | `${CLAUDE_SKILL_DIR}/workflows/update.md`      |
| Check that the workspace is valid, without changing it                          | `${CLAUDE_SKILL_DIR}/workflows/validate.md`    |
| Get files out of the model: PlantUML, Mermaid, JSON, static site, PNG/SVG       | `${CLAUDE_SKILL_DIR}/workflows/export.md`      |
| Look at the diagrams in a browser, or stop that preview                         | `${CLAUDE_SKILL_DIR}/workflows/preview.md`     |
| Ask about naming, ADR numbering, or other house style                           | `${CLAUDE_SKILL_DIR}/workflows/conventions.md` |

Read the matching workflow first. Then, before writing or editing any `.dsl` file, ADR, or file under `docs/`, also read `${CLAUDE_SKILL_DIR}/workflows/conventions.md` — the house style is cheaper to follow than to retrofit.

<!-- choosing-between -->

## If bundled files are not on disk

Some hosts load a skill's files without writing them to a directory. In that case, run a bundled script by piping its contents to bash (`bash -s -- <args>` with the script on standard input), and scaffold the workspace by writing each file under `templates/workspace/` from its contents rather than copying the directory.
