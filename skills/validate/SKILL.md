---
name: validate
description: Check a C4 workspace.dsl for syntax and semantic errors by running the Structurizr CLI in Docker, and explain any failure. Use when the user asks to validate, lint, or check the DSL, asks "is the workspace valid?", or wants a quality gate before committing or merging — and after any hand-edit made outside this plugin. For edits made through /c4:update, validation already runs automatically.
allowed-tools: Read, Bash(scripts/validate-dsl.sh:*), Bash(ls:*), Bash(find:*), Bash(docker:*)
---

# validate — run Structurizr CLI against the workspace

Runs `structurizr/structurizr validate` inside Docker against the workspace and reports the result.

## Choosing between validate and update

`update` auto-validates after every edit it makes, so a request that *changes* the model never needs `validate` as a separate step. Invoke `validate` standalone only when the user explicitly asks for a check, or when the workspace was hand-edited outside this plugin and nothing has verified it yet.

## Workflow

1. **Locate workspace.dsl.** Search root, then `architecture/`. If none, tell the user and suggest `/c4:structurize`.
2. **Run the script:**

   ```
   ${CLAUDE_PLUGIN_ROOT}/scripts/validate-dsl.sh <path-to-workspace.dsl>
   ```

3. **Report:**
   - If exit code `0`: `Workspace is valid.`
   - If exit code `127`: Docker not installed. Tell the user; do not retry.
   - If exit code `1`: Docker daemon is not running. Surface the script's stderr verbatim.
   - If exit code `2`: workspace file not found. Surface the script's stderr verbatim.
   - Any other exit code: validation failed. Surface the CLI's error message verbatim, then suggest the likely fix (consult the relevant `${CLAUDE_PLUGIN_ROOT}/references/*.md`).

## Prerequisites

- Docker must be installed and running.
- The script pulls `structurizr/structurizr` on first use.

## Verification

Print the final pass/fail status and, on failure, the literal CLI output so the user can debug.
