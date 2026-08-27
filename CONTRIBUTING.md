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
│   ├── structurize/
│   ├── update/
│   ├── validate/
│   ├── export/
│   ├── preview/
│   └── conventions/
├── templates/
│   └── workspace/               # single template tree; /c4:structurize copies it to . or architecture/
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

In a scratch Claude Code session (i.e. **not** inside this repo — make a separate sandbox directory so you can exercise `/c4:structurize`):

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
/c4:structurize
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
description: <what it does> + <when to use it, in the words a user would actually say>
allowed-tools: Read, Write, Edit, Bash(scripts/your-script.sh:*)
# Optional: limit activation to matching files
# paths: "**/*.dsl"
---

# <name> — <short tagline>

## Workflow

1. <step>
2. <step>

## References

Use `${CLAUDE_PLUGIN_ROOT}/references/<file>.md` to access bundled grammar docs.

## Verification

<how the skill should confirm success>
```

### Frontmatter fields

| Field           | Required | Meaning                                                                                                                                                                                    |
|-----------------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `name`          | yes      | Skill name (lowercase, no spaces). Combined with the plugin name from `.claude-plugin/plugin.json` to form the slash command (e.g. plugin `c4` + skill `structurize` → `/c4:structurize`). |
| `description`   | yes      | **The only thing Claude sees when choosing a skill.** See "Writing a description" below. No character cap — two or three sentences is normal.                                              |
| `allowed-tools` | yes      | Comma-separated list. Matching is on the *expanded command prefix*, so `Bash(git:*)` means "bash, git commands only".                                                                      |
| `paths`         | no       | Glob(s) that *limit* activation to matching files. It narrows when a skill may load; it does not force loading, so the description still has to earn the match.                            |

### Writing a description

The description is the whole triggering mechanism. The SKILL.md body — including any "when to run" list — is only read *after* Claude has already decided to invoke the skill, so trigger phrases placed there do no work.

Write the description to carry both halves:

1. **What it does**, naming the concrete nouns a user would say — formats, file types, element kinds. `export`'s description names PlantUML, Mermaid and JSON because users ask by format name.
2. **When to use it**, in the user's words rather than yours, plus the boundary against any sibling skill that could plausibly claim the same request.

Claude tends to *under*-trigger skills, so lean towards being explicit and a little pushy. `skills/update/SKILL.md` is the reference: it lists the element kinds by name and states the situations that call for it.

Keep genuine sibling disambiguation in the body under a `## Choosing between <a> and <b>` heading — that is guidance for a skill already running, not a trigger.

Descriptions are measurable. `evals/measure_routing.py` runs the full query pool against the working tree and reports which skill actually fires; see "Measuring skill routing" below.

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

### Manual LLM-behavior checklist

For changes that affect skill instructions, reference content, or conventions, run through this checklist in a real Claude Code session before opening the PR. Tick each box in the PR description.

In an empty scratch directory, with the plugin installed:

- [ ] `/c4:structurize` produces the standalone layout; `workspace.dsl` validates clean.
- [ ] `/c4:update "add a Postgres database called orders-db and connect the API to it"` — workspace.dsl gains a `Container` with technology `Postgres`, a relationship with present-tense verb, and validates clean.
- [ ] `/c4:update "add a System Context view keyed 'Overview'"` — view is added with an explicit key; auto-validate passes.
- [ ] `/c4:update "record an ADR about choosing Kafka over RabbitMQ"` — file appears as `adrs/000N-...-kafka...md` (4-digit prefix) with the next sequential number, Nygard sections present, Status `Proposed` or `Accepted`.
- [ ] `/c4:update "supersede ADR 0002 with a new ADR about CQRS"` — old ADR's Status line is changed to `Superseded by [ADR-000N](...)`; old body unchanged; new ADR's Context links back.
- [ ] `/c4:validate` exits clean.
- [ ] `/c4:export plantuml` produces files under `build/diagrams/`.
- [ ] `/c4:preview` serves diagrams at `http://localhost:8080`; `/c4:preview stop` removes the container.

In a sibling scratch directory containing a small existing project (e.g. a `Dockerfile` + `package.json`):

- [ ] `/c4:structurize` chooses embedded mode and creates `architecture/`.
- [ ] `/c4:update --discover "model this codebase as C4"` — agent inspects manifests, proposes a model, then writes `architecture/workspace.dsl` that validates clean.

Skipping a checkbox is fine if the change is unrelated; note which boxes you skipped and why.

### Measuring skill routing

Whether a skill fires is measurable and worth measuring whenever you touch a `description`. The checklist above spot-checks a handful of phrasings; this measures the whole pool.

`evals/build_trigger_evals.py` holds the query pool — ten realistic phrasings per skill, plus out-of-domain near-misses. `evals/measure_routing.py` runs every query against the **working tree** (via `claude -p --plugin-dir`, which overrides any installed copy) and records which skill Claude actually reached for:

```sh
python3 evals/build_trigger_evals.py            # regenerate the per-skill JSON sets
python3 evals/measure_routing.py --runs 1 --workdir /path/to/scratch/workspace
```

Run it from a directory that contains a real C4 workspace, so queries aren't answered in an empty tree. Budget roughly a minute per query — 68 queries at 5 workers is about 12 minutes.

The output is a routing confusion matrix, not a per-skill pass rate. That distinction matters: the risk with six sibling skills is not that one fails to fire but that the *wrong* one does. A miss row reading `exp=export got=preview` is telling you two descriptions overlap, which is the thing to go fix.

A note on tooling: skill-creator's `run_eval.py` is not used here. It tests one skill at a time against a synthetic stand-in, so it cannot observe siblings competing — and with the real plugin installed, the stand-in and the genuine skill both fire, contaminating the result.

## Style guide

### SKILL.md

- `description` is active voice — *"Edit a C4 workspace ..."*, not *"This skill is used to edit ..."* — and carries the trigger phrases. No length cap; see [Writing a description](#writing-a-description). The six shipped descriptions run 380–500 characters.
- No `## When to run` section. Trigger phrases belong in the description, which is the only part read at selection time. Sibling boundaries go under `## Choosing between <a> and <b>`.
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

- Use `{{PROJECT_NAME}}` and `{{TODAY}}` placeholders. The `structurize` skill replaces them at copy time.
- A freshly-scaffolded workspace must immediately pass `/c4:validate`.

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
