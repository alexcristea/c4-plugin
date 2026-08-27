---
name: update
description: Edit an existing C4 workspace — add or change elements (server, service, container, component, database, queue, actor), relationships, views, styles, deployment environments, ADRs, and docs. Use when the user describes a new or missing server/service, adds a dependency between systems, records an architecture decision, restyles a diagram, or makes any other model change — and when they ask to reverse-engineer or model an existing codebase as C4. Auto-validates after every workspace.dsl edit.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(scripts/validate-dsl.sh:*), Bash(find:*), Bash(ls:*), Bash(cat:*)
---

# update — edit the workspace

A single editing skill for **any** change to the C4 workspace: model, views, relationships, styles, deployment, ADRs, supplementary docs. Designed to be the everyday command — the user describes the change in natural language and you make it happen.

## Workflow

1. **Locate the workspace.** Look for `workspace.dsl` at the repo root, then under `architecture/`. If neither exists, suggest running `/c4:structurize` first.
2. **Identify what to edit.** Match the request to one of:
   - Model elements → `model { ... }` block
   - Relationships → use `->` inside the relevant scope
   - Views → `views { ... }` block
   - Styles → `views { styles { ... } }`
   - Deployment → `model { deploymentEnvironment ... }` + a `views { deployment ... }`
   - ADRs → add a new file under `adrs/` (or `architecture/adrs/`), preserving numbering
   - Docs → add or edit a file under `docs/` (or `architecture/docs/`)
3. **Load only the references you need** from `${CLAUDE_PLUGIN_ROOT}/references/`. Examples:
   - "add a database + relationship" → `model-elements.md`, `relationships.md`
   - "add a container view" → `views.md`, possibly `expressions.md`
   - "style external systems" → `styles-and-themes.md`
   - "add a deployment view" → `deployment.md`, `views.md`
   - "write an ADR" → `adrs-and-docs.md`
4. **Make the edit** with `Edit` (preferred) or `Write` (only for new files).
5. **Auto-validate.** Immediately run `scripts/validate-dsl.sh <path-to-workspace.dsl>`.
6. **Self-correct.** If validation fails, read the error, re-consult references, fix, and re-validate. Repeat until it passes (max 3 attempts; if still failing, surface the error to the user with a clear diagnosis).
7. **Report.** State exactly what was changed (paths + summary), plus the validation result.

## Auto-validation

The validation step is the default. Skip only when one of these is true:

- The user passes `--no-validate` in the prompt.
- Docker is not available on the machine (validation script will exit `127`; surface this once, then fall back to a syntax-only review).
- The edit is to an `.md` file under `adrs/` or `docs/` only (no DSL touched).

## Discovery mode

When the user asks for a C4 model of an **existing** codebase, switch into discovery mode before writing any DSL:

1. **Scan for evidence**, in roughly this order:
   - Container hints: `Dockerfile`, `docker-compose.yml`, `Procfile`, `fly.toml`, `vercel.json`
   - Service hints: `package.json` (workspaces/services), `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`
   - Routing: API routes in `app/**`, `routes/**`, `pages/api/**`, `cmd/**`
   - Datastores: `prisma/schema.prisma`, `migrations/**`, `*.sql`, env vars like `*_DATABASE_URL`
   - Infrastructure: `terraform/**`, `pulumi/**`, `k8s/**`, `helm/**`
   - CI: `.github/workflows/**`, `gitlab-ci.yml`, `circleci/**`
2. **Map to C4 abstractions**:
   - One repo / one running service ≈ one **container**.
   - A monorepo with multiple deployables ≈ multiple **containers** within the same **softwareSystem**.
   - External managed services (Stripe, Auth0, S3) ≈ separate **softwareSystem** with the `External` tag.
   - Databases and queues ≈ **containers** of the system that owns them.
3. **Propose** the model in DSL form, summarising the evidence (which file → which abstraction) **before** writing. Let the user confirm or adjust.
4. **Write** the DSL and validate.

## References

Stored at `${CLAUDE_PLUGIN_ROOT}/references/`:

- `basics.md` — DSL rules, identifiers, constants, comments, `workspace`, `!include`
- `model-elements.md` — `model`, `person`, `softwareSystem`, `container`, `component`, `group`, `element`, archetypes
- `relationships.md` — `->`, scope-based syntax, implied relationships, `-/>`, archetypes
- `views.md` — all view types + `include`/`exclude`/`autoLayout`
- `expressions.md` — `element.*` and `relationship.*` expressions
- `styles-and-themes.md` — element/relationship styles, light/dark, themes, terminology
- `deployment.md` — deployment environments, nodes, instances, health checks
- `adrs-and-docs.md` — `!docs`, `!adrs`, Nygard ADR template, doc structure, filenames

Only read the files you actually need for the current request.

## ADR-specific rules

When adding an ADR (see `adrs-and-docs.md` for the full template):

- Filename: 4-digit zero-padded number + `-` + kebab-case slug, e.g. `0004-introduce-kafka.md`. (3-digit names cause `NumberFormatException` in the Structurizr importer — always use 4 digits.)
- Number = max existing number + 1. **Never** reuse or renumber.
- Status is `Proposed` unless the user says it's already agreed.
- If the new ADR replaces a previous one, set the old one's **Status line only** to `Superseded by [ADR-NNNN](NNNN-slug.md)`. Do not edit any other line of the old ADR.

## Verification

Every edit ends with the validation result. State whether the workspace is currently valid and, if not, what's still wrong.
