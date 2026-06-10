# 1. Use the C4 model with Structurizr DSL

Date: {{TODAY}}

## Status

Accepted

## Context

We need an approach to documenting the architecture of {{PROJECT_NAME}} that:

- Communicates the design at multiple levels of abstraction (system context, containers, components).
- Stays in sync with code as it evolves, rather than rotting in a stale slide deck.
- Is reviewable in pull requests — i.e. lives as text, not as binary diagram files.
- Can be rendered automatically into multiple formats (PlantUML, Mermaid, SVG).

Free-form box-and-line diagrams in Lucidchart / Miro / draw.io tend to drift from reality, lack a shared vocabulary, and cannot be diffed.

## Decision

We will use the [C4 model](https://c4model.com) as our notation, and author the model in [Structurizr DSL](https://docs.structurizr.com/dsl). The model lives in `workspace.dsl` at the repository root, alongside ADRs (`adrs/`) and supplementary docs (`docs/`).

Diagrams are rendered on demand via the `structurizr/structurizr` (Structurizr Local) Docker image; nothing about the rendering toolchain leaks into the source files.

## Consequences

- New architectural changes must be reflected in `workspace.dsl` as part of the same PR.
- Contributors need Docker installed locally to preview diagrams; this is acceptable given the team's existing toolchain.
- We commit to keeping ADRs in the Michael Nygard format (Title, Date, Status, Context, Decision, Consequences) for consistency.
- Future ADRs that change architectural direction will reference and supersede this one rather than amending it in place.
