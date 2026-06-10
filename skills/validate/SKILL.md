---
name: validate
description: Validate the current Structurizr DSL workspace by running structurizr/structurizr in Docker. Use for an on-demand check.
allowed-tools: Read, Bash(scripts/validate-dsl.sh:*), Bash(ls:*), Bash(find:*), Bash(docker:*)
---

# validate — run Structurizr CLI against the workspace

Runs `structurizr/structurizr validate` inside Docker against the workspace and reports the result.

## When to run

- The user asks: *"validate"*, *"is the workspace valid?"*, *"check the DSL"*, *"lint"*.
- After a manual hand-edit the user made outside this plugin.

The `update` skill already auto-validates after every edit — only invoke `validate` standalone when the user explicitly asks, or when a hand-edit was made.

## Workflow

1. **Locate workspace.dsl.** Search root, then `architecture/`. If none, tell the user and suggest `/c4:init`.
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
