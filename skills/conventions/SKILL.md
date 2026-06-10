---
name: conventions
description: Project-level conventions are loaded automatically whenever a .dsl file, an ADR, or a doc is edited. Not user-invocable.
paths: "**/*.dsl, **/adrs/**, **/docs/**"
allowed-tools: Read
---

# conventions — project-level rules (auto-loaded)

This skill is **not** invoked manually. The `paths:` trigger loads it into context whenever the agent edits a Structurizr DSL file, an ADR, or a supplementary doc, so the rules below are always in mind.

This file is the source of truth for our **project style** on top of valid DSL. For the DSL **grammar** itself — what each keyword does and how it's spelled — read the relevant file under `${CLAUDE_PLUGIN_ROOT}/references/`.

## DSL conventions

- One `workspace.dsl` per project. Use `!include` to split large workspaces — see `${CLAUDE_PLUGIN_ROOT}/references/basics.md`.
- **Explicit view keys** on every view (`systemContext shop "ShopContext"`). Auto-generated keys are unstable and break manual layout.
- **Explicit identifiers** on elements you will reference (`api = container "API"`). Anonymous elements cannot be linked.
- **Names** are human-readable Title Case (`"Order Service"`). **Identifiers** are camelCase, lowercase first letter (`orderService`).
- **Descriptions are mandatory** on every `person`, `softwareSystem`, `container`, `component`. Aim for a single sentence describing what it *does*, not what it *is*.
- **Technology** is mandatory on every container/component. Use canonical names: `Java`, `Spring Boot`, `Node.js`, `Postgres`, `Redis`, `Kafka`, `Next.js`. Not `JS`, `K8s`, or other abbreviations.
- **External systems** get the `External` tag and a distinct style under `views { styles { ... } }` — see `${CLAUDE_PLUGIN_ROOT}/references/styles-and-themes.md`.
- Use `!identifiers hierarchical` only when names genuinely collide across systems; otherwise leave it flat (the default).

## Relationship conventions

- Descriptions are **verbs in present tense**: `"Reads from"`, `"Sends events to"`, `"Authenticates via"`. Not `"Read from"` or `"Reading"`.
- Avoid generic `"Uses"` — say *how* (`"Persists data in"`, `"Queries"`, `"Publishes events to"`).
- Specify `technology` on every relationship that crosses a process boundary (`"HTTPS/JSON"`, `"gRPC"`, `"SQL/TCP"`, `"Kafka protocol"`).
- Don't pre-create implied parent-to-parent relationships — let Structurizr generate them. See `${CLAUDE_PLUGIN_ROOT}/references/relationships.md` for how the `!impliedRelationships` strategy works.

## View conventions

- Every workspace must have **at least**: one System Landscape (or one System Context per system) and one Container view per system.
- Each view: explicit key, descriptive title, `autoLayout` unless there's a curated layout to preserve.
- Use `filtered` views to surface focused perspectives (e.g. read-paths only) instead of cramming everything into one diagram. Syntax in `${CLAUDE_PLUGIN_ROOT}/references/views.md`.
- `deployment` views: one per environment per system. Don't mix staging and production into a single diagram.

## ADR and doc conventions

ADR and supplementary-doc rules — filename pattern, Nygard template, status vocabulary, superseding/amending mechanics, doc base set, and cross-linking — are defined in detail in:

- `${CLAUDE_PLUGIN_ROOT}/references/adrs-and-docs.md`

Read that file before adding or editing anything under `adrs/` or `docs/`. The most important rules to keep in mind:

- Filenames are 4-digit zero-padded, kebab-case (`0001-use-c4-model-with-structurizr.md`). The adr-tools-compatible importer used by Structurizr requires 4 digits — 3-digit names fail validation. Numbers are **append-only**, never renumbered.
- When superseding an ADR, edit **only** the old ADR's Status line. The new ADR's Context must link back to the old one.

## Validation

The `update` skill auto-validates after each edit. If you touch `workspace.dsl` directly via `Edit` / `Write` without going through `update`, **manually run** `${CLAUDE_PLUGIN_ROOT}/scripts/validate-dsl.sh` before reporting completion.
