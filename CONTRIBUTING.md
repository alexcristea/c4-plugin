# Contributing to c4

Thank you for considering a contribution! This guide walks through the repo layout, how to develop and test the plugin locally, and the conventions we follow.

## Repository layout

```
c4-plugin/                       # this repo — a standalone Claude Code plugin
├── .github/workflows/ci.yml     # lint, references, smoke, e2e
├── .claude-plugin/
│   └── plugin.json              # plugin manifest
├── references/                  # curated Structurizr DSL docs, loaded by skills on demand
├── scripts/                     # shared shell tools called from skills
├── skills/                      # one directory per skill, each with a SKILL.md
│   ├── init/
│   ├── update/
│   ├── validate/
│   ├── export/
│   ├── preview/
│   └── conventions/
├── templates/
│   └── workspace/               # single template tree; /c4:init copies it to . or architecture/
├── examples/                    # end-to-end workspaces for manual testing
├── tests/
│   └── smoke.sh                 # shell-level end-to-end test (no Claude required)
├── README.md
├── CONTRIBUTING.md              # this file
└── LICENSE
```

## Local development

### 1. Clone

```sh
git clone https://github.com/alexcristea/c4-plugin.git
cd c4-plugin
```

### 2. Install the plugin in Claude Code

In a scratch Claude Code session (i.e. **not** inside this repo — make a separate sandbox directory so you can exercise `/c4:init`):

```
/plugin install --plugin-dir /absolute/path/to/c4-plugin
```

### 3. Iterate

After editing any `SKILL.md`, reload the plugin:

```
/plugin reload c4
```

You don't need to reload when editing `references/*.md` — they're read fresh on every skill invocation.

### 4. Try the skills

Inside an empty scratch directory:

```
/c4:init
/c4:update "add a Postgres database and connect it to the API"
/c4:validate
/c4:export plantuml
/c4:preview
```

## Adding a new skill

Create a new directory under `skills/<name>/` with a single `SKILL.md`. Minimal skeleton:

```markdown
---
name: <name>
description: <one sentence, active voice, under 200 chars>
allowed-tools: Read, Write, Edit, Bash(scripts/your-script.sh:*)
# Optional: paths trigger for auto-loading (not user-invocable)
# paths: "**/*.dsl"
---

# <name> — <short tagline>

## When to run

- <user phrases that should trigger this skill>

## Workflow

1. <step>
2. <step>

## References

Use `${CLAUDE_PLUGIN_ROOT}/references/<file>.md` to access bundled grammar docs.

## Verification

<how the skill should confirm success>
```

### Frontmatter fields

| Field           | Required | Meaning                                                                                                  |
|-----------------|----------|----------------------------------------------------------------------------------------------------------|
| `name`          | yes      | Skill name (lowercase, no spaces). Combined with the plugin name from `.claude-plugin/plugin.json` to form the slash command (e.g. plugin `c4` + skill `init` → `/c4:init`). |
| `description`   | yes      | One sentence, active voice, under 200 characters. Used by Claude to decide whether to invoke the skill.   |
| `allowed-tools` | yes      | Comma-separated list. Use `Bash(scripts/<file>:*)` to grant access to a specific script.                 |
| `paths`         | no       | Glob(s) that trigger automatic loading. Use only for non-invocable skills like `conventions`.            |

## Updating references

The eight files in `references/` are curated from [`structurizr/structurizr.github.io`](https://github.com/structurizr/structurizr.github.io). When the upstream changes:

```sh
scripts/update-references.sh
```

The script downloads all 10 upstream source files that the bundled references are derived from:

`03-basics.md`, `04-defaults.md`, `05-identifiers.md`, `06-archetypes.md`, `07-implied-relationships.md`, `08-expressions.md`, `31-includes.md`, `51-docs.md`, `52-adrs.md`, `71-language.md`

For files with a matching local copy (currently `basics.md` and `expressions.md`), it prints a `diff`. For the rest it prints the full upstream content as "NEW" — the raw material you use while hand-updating the curated references.

It does **not** auto-apply changes. Review the diff, hand-merge what's relevant into the curated references, update the `Pulled:` date in each affected file, and commit deliberately.

## Testing locally

Before opening a PR:

### Syntax-check shell scripts

```sh
shellcheck scripts/*.sh
shellcheck templates/workspace/bin/local/run.sh
```

If you don't have shellcheck, at minimum:

```sh
for f in scripts/*.sh; do bash -n "$f"; done
```

### Validate the example workspaces

```sh
scripts/validate-dsl.sh examples/simple-web-app/workspace.dsl
scripts/validate-dsl.sh examples/microservices/workspace.dsl
```

Both must exit `0`.

### Run the end-to-end smoke test

`tests/smoke.sh` exercises the shell tooling and templates without invoking Claude. It:

1. Copies `templates/workspace/` into a scratch dir (standalone and embedded layouts in turn).
2. Substitutes `{{PROJECT_NAME}}` / `{{TODAY}}` and asserts no placeholder strings survive.
3. Runs `scripts/validate-dsl.sh` against the seeded workspace.
4. Runs `scripts/export-diagrams.sh plantuml` and confirms `.puml` files appear.
5. Starts `scripts/preview-start.sh`, polls `http://localhost:${C4_SMOKE_PORT:-8081}` until it responds, then stops the preview.

```sh
tests/smoke.sh
```

Requires Docker. The script refuses to run if a `c4-architect-local` container is already up (so it doesn't clobber a real preview you have running). Set `C4_SMOKE_PORT=<n>` to use a different port.

This catches: broken templates, placeholder-substitution bugs, script regressions, port conflicts, container-name regressions. **What it cannot catch:** whether Claude picks the right reference file, whether the generated DSL is sensible for a given prompt, whether the conventions skill is being followed. Those require the manual LLM-behaviour checklist below.

### Manual LLM-behaviour checklist

For changes that affect skill instructions, reference content, or conventions, run through this checklist in a real Claude Code session before opening the PR. Tick each box in the PR description.

In an empty scratch directory, with the plugin installed:

- [ ] `/c4:init` produces the standalone layout; `workspace.dsl` validates clean.
- [ ] `/c4:update "add a Postgres database called orders-db and connect the API to it"` — workspace.dsl gains a `Container` with technology `Postgres`, a relationship with present-tense verb, and validates clean.
- [ ] `/c4:update "add a System Context view keyed 'Overview'"` — view is added with an explicit key; auto-validate passes.
- [ ] `/c4:update "record an ADR about choosing Kafka over RabbitMQ"` — file appears as `adrs/000N-...-kafka...md` (4-digit prefix) with the next sequential number, Nygard sections present, Status `Proposed` or `Accepted`.
- [ ] `/c4:update "supersede ADR 0002 with a new ADR about CQRS"` — old ADR's Status line is changed to `Superseded by [ADR-000N](...)`; old body unchanged; new ADR's Context links back.
- [ ] `/c4:validate` exits clean.
- [ ] `/c4:export plantuml` produces files under `build/diagrams/`.
- [ ] `/c4:preview` serves diagrams at `http://localhost:8080`; `/c4:preview stop` removes the container.

In a sibling scratch directory containing a small existing project (e.g. a `Dockerfile` + `package.json`):

- [ ] `/c4:init` chooses embedded mode and creates `architecture/`.
- [ ] `/c4:update --discover "model this codebase as C4"` — agent inspects manifests, proposes a model, then writes `architecture/workspace.dsl` that validates clean.

Skipping a checkbox is fine if the change is unrelated; note which boxes you skipped and why.

## Style guide

### SKILL.md

- `description` is active voice, under 200 characters: *"Edit a C4 workspace ..."*, not *"This skill is used to edit ..."*.
- Workflow is numbered, concrete steps. Avoid hedging language.
- Always reference bundled files via `${CLAUDE_PLUGIN_ROOT}/...`.

### References

- Every file starts with a one-sentence purpose statement.
- Files longer than ~300 lines have a Table of Contents at the top.
- Every file ends with a `# Source` footer naming the upstream URL(s) and `Pulled: YYYY-MM-DD`.
- Examples should be **copy-paste-valid** Structurizr DSL — they appear in tool output and users will copy them.

### Shell scripts

- `#!/usr/bin/env bash` and `set -euo pipefail` at the top.
- Detect missing `docker` with a clear stderr message and exit code `127`.
- Detect a stopped Docker daemon and exit `1`.
- Detect a missing input file and exit `2`.
- No `bashisms` beyond what we explicitly opt into (we use bash, not POSIX `sh`).

### Templates

- Use `{{PROJECT_NAME}}` and `{{TODAY}}` placeholders. The `init` skill replaces them at copy time.
- A freshly-`init`ed workspace must immediately pass `/c4:validate`.

## Filing issues

Open an issue at <https://github.com/alexcristea/c4-plugin/issues>. Include:

- Claude Code version (`/version`)
- Docker version (`docker --version`) if relevant
- The exact prompt you ran
- What you expected vs. what happened

## Pull requests

- One concern per PR. A docs-only PR and a new-skill PR should be separate.
- Update the README or relevant reference file in the same PR if behaviour changes.
- We don't squash; keep your history clean (rebase locally).
