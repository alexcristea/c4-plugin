# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code plugin (`c4`, manifest in `.claude-plugin/plugin.json`) for authoring C4 architecture diagrams as Structurizr DSL, plus Nygard ADRs and docs. There is no build step. The "code" consists of skill instructions (`skills/*/SKILL.md`), bash scripts that wrap the `structurizr/structurizr` Docker image (`scripts/`), curated DSL reference docs (`references/`), and a workspace template (`templates/workspace/`).

## Commands

```sh
shellcheck scripts/*.sh templates/workspace/bin/local/run.sh   # lint (CI)
python3 tests/check-skill-grants.py                            # allowed-tools grants can actually match (not in CI)
scripts/validate-dsl.sh examples/simple-web-app/workspace.dsl  # validate one workspace (needs Docker)
tests/smoke.sh                                                 # end-to-end: template → validate → export → preview (needs Docker)
scripts/update-references.sh                                   # list upstream Structurizr DSL doc changes since references/.upstream-sha
```

`tests/smoke.sh` refuses to run if a `c4-architect-local` container exists; `C4_SMOKE_PORT` overrides its port (default 8081). It installs a `docker` shim on `PATH` that fails any `docker run structurizr/structurizr` lacking `--user $(id -u):$(id -g)`.

To measure which skill fires for which phrasing (slow — runs `claude -p` per query, ~12 min):

```sh
python3 evals/build_trigger_evals.py
python3 evals/measure_routing.py --runs 1 --workdir /path/to/scratch/c4/workspace
```

To try skills manually, install the plugin from a separate scratch directory (`/plugin install --plugin-dir <abs path>`), then `/plugin reload c4` after editing a `SKILL.md`. Edits to `references/*.md` need no reload.

## Architecture

**Skills → scripts → Docker.** The six skills (`structurize`, `update`, `validate`, `export`, `preview`, and `conventions`, a house-style skill limited by `paths` to `.dsl`/ADR/doc files) do not call Docker logic themselves. Every Docker interaction goes through a script in `scripts/`. `update` runs `validate-dsl.sh` after every `workspace.dsl` edit and self-corrects up to 3 times.

**Permission grants are subtle.** Claude Code matches `Bash(...)` grants on the expanded command prefix, so skills must invoke scripts as `bash ${CLAUDE_PLUGIN_ROOT}/scripts/<name>.sh` and grant `Bash(bash:*)`. A grant like `Bash(scripts/foo.sh:*)` never matches, and a bare `scripts/foo.sh` path resolves against the user's project rather than the plugin. `tests/check-skill-grants.py` enforces both rules.

**Descriptions are the routing mechanism.** Only the frontmatter `description` is seen when Claude picks a skill, so trigger phrases must live there, never in a `## When to run` body section. Sibling disambiguation goes under `## Choosing between <a> and <b>`. The main risk is the wrong sibling firing (e.g. export vs preview), not a skill failing to fire. Use the routing evals above when changing any description.

**References are curated excerpts, not mirrors.** `references/*.md` are hand-condensed from `structurizr/structurizr.github.io/dsl`. Skills load only the files they need (index in `skills/update/SKILL.md`). Each file needs a one-sentence purpose line, a `# Source` footer with upstream URL(s) and `Pulled: YYYY-MM-DD` (CI checks for the footer), and copy-paste-valid DSL examples. After syncing upstream changes by hand, write the newest upstream SHA to `references/.upstream-sha`.

**One template, two layouts.** `structurize` copies `templates/workspace/` to `.` (standalone, empty dir) or `architecture/` (embedded, existing project), substituting `{{PROJECT_NAME}}` and `{{TODAY}}`. A freshly scaffolded workspace must validate immediately.

## Conventions

- SKILL.md frontmatter requires `name`, `description` (active voice), and `allowed-tools`. Always reference bundled files via `${CLAUDE_PLUGIN_ROOT}/...`.
- Shell scripts: `#!/usr/bin/env bash` + `set -euo pipefail`. Exit codes: `127` for missing docker, `1` for a stopped daemon, `2` for a missing input file. Every `docker run` of the structurizr image uses `--platform linux/amd64` (no ARM build) and `--user "$(id -u):$(id -g)"` (the image's default uid can't write bind mounts on Linux).
- Behaviour changes update README or the relevant reference in the same change. History is not squashed.
