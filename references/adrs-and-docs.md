# ADRs and supplementary docs — Structurizr + project conventions

How to attach Markdown/AsciiDoc documentation and ADRs to a workspace, software system, or container, plus the file-naming and content conventions this plugin enforces.

## Table of contents

- [`!docs` — supplementary docs](#docs--supplementary-docs)
- [`!adrs` — architecture decision records](#adrs--architecture-decision-records)
- [Built-in ADR importer types](#built-in-adr-importer-types)
- [Plugin conventions: filenames](#plugin-conventions-filenames)
- [Plugin conventions: ADR template (Nygard)](#plugin-conventions-adr-template-nygard)
- [Plugin conventions: docs template](#plugin-conventions-docs-template)
- [Cross-linking](#cross-linking)

## `!docs` — supplementary docs

```
!docs <path> [fully qualified class name]
```

- `<path>` is a relative path, in the same directory as the parent DSL file or a subdirectory.
- Default importer: `com.structurizr.importer.documentation.DefaultDocumentationImporter`.
- Behaviour: imports **all** Markdown/AsciiDoc files in the directory, alphabetically by filename. Images in the directory (and subdirectories) are also imported.
- Section headings and numbering: see Structurizr documentation on heading conventions.

Use `!docs` inside `workspace`, `softwareSystem`, or `container`:

```
workspace {
    !docs docs

    model {
        ss = softwareSystem "S" {
            !docs docs/s
            api = container "API" {
                !docs docs/s/api
            }
        }
    }
}
```

## `!adrs` — architecture decision records

```
!adrs <path> [type|fqn]
```

- `<path>` is a relative path, same rules as `!docs`.
- Default importer: `com.structurizr.importer.documentation.AdrToolsDecisionImporter` (Michael Nygard format, as emitted by [adr-tools](https://github.com/npryce/adr-tools)).
- All Markdown files in the directory are imported, alphabetically. Images in the directory (and subdirectories) are imported.

## Built-in ADR importer types

The optional second parameter selects an importer:

| Value           | Importer                                                                         |
|-----------------|----------------------------------------------------------------------------------|
| `adrtools`      | `com.structurizr.importer.documentation.AdrToolsDecisionImporter` (default)      |
| `madr`          | `com.structurizr.importer.documentation.MadrDecisionImporter`                    |
| `log4brains`    | `com.structurizr.importer.documentation.Log4brainsDecisionImporter`              |

Or specify the fully qualified class name of a custom `DocumentationImporter`.

## Plugin conventions: filenames

For both ADRs and supplementary docs, file numbering is **4-digit, hyphen-prefixed, kebab-case slug**:

```
adrs/
  0001-use-c4-model-with-structurizr.md
  0002-introduce-event-bus.md
  0003-adopt-postgres-as-primary-store.md
docs/
  0001-system-overview.md
  0002-actors.md
  0003-use-cases.md
  0004-deployment.md
```

- Always 4 digits, padded with leading zeros (`0001`, not `1` or `001`).
- Sequence is **append-only**; ADRs are never renumbered (status changes — see below — are how decisions are revised).
- Slug is the title in lowercase, hyphen-separated, without stop words like "the", "a".

> **Why 4 digits?** The default importer used by Structurizr (`AdrToolsDecisionImporter`) expects the [adr-tools](https://github.com/npryce/adr-tools) format, which uses 4-digit padding. 3-digit filenames cause a `NumberFormatException` at workspace validation time. We use 4-digit for docs too so the numbering style is consistent across the project.

## Plugin conventions: ADR template (Nygard)

```markdown
# <number>. <title>

Date: <YYYY-MM-DD>

## Status

<Proposed | Accepted | Deprecated | Superseded by [ADR-NNNN](NNNN-slug.md) | Amended by [ADR-NNNN](NNNN-slug.md)>

## Context

<What is the issue we're seeing that is motivating this decision or change?
Describe forces — technical, political, social, project. Neutral tone.>

## Decision

<What is the change that we're proposing or have agreed to?
State it as a positive action: "We will ...">

## Consequences

<What becomes easier or more difficult to do because of this change?
Trade-offs, follow-up work, monitoring obligations.>
```

Status vocabulary:

- **Proposed** — drafted, not yet ratified
- **Accepted** — currently in force
- **Deprecated** — still applies historically; do not adopt for new work
- **Superseded by [ADR-NNNN](NNNN-slug.md)** — replaced by a newer decision; the new ADR's "Context" should link back here
- **Amended by [ADR-NNNN](NNNN-slug.md)** — refined by a newer decision but not fully replaced

When superseding or amending, **never** edit the original ADR's body — change only its status line.

## Plugin conventions: docs template

```markdown
# <number>. <Title>

<One-paragraph summary of what this document covers.>

## ...sections...

<Free-form content. Cross-link other docs and ADRs as needed.>
```

Suggested doc set, in order:

- `0001-system-overview.md` — high-level system description, scope, non-goals
- `0002-actors.md` — who interacts with the system and why
- `0003-use-cases.md` — what the system does, organised by actor or capability
- `0004-deployment.md` (optional) — production topology narrative complementing the deployment diagram

## Cross-linking

From docs to ADRs:

```markdown
For background on why we chose Structurizr, see [ADR-0001](../adrs/0001-use-c4-model-with-structurizr.md).
```

From an ADR's "Consequences" to a doc:

```markdown
Operational implications are documented in [System Overview §4](../docs/0001-system-overview.md#deployment).
```

When you supersede an ADR, the **new** ADR's Context must reference the old one by number.

# Source

- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/51-docs.md
- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/52-adrs.md
- Nygard ADR format: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions

Pulled: 2026-05-12
