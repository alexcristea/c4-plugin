---
name: preview
description: Start or stop Structurizr Local to render the workspace at http://localhost:8080.
allowed-tools: Read, Bash(scripts/preview-start.sh:*), Bash(scripts/preview-stop.sh:*), Bash(docker:*), Bash(ls:*)
---

# preview — live diagram preview at localhost:8080

Runs Structurizr Local (`structurizr/structurizr local`) in Docker so the user can view the rendered workspace in a browser. The container watches the workspace directory and re-renders on save. On Apple Silicon, the script passes `--platform linux/amd64` because the image has no native ARM build.

## When to run

- The user asks: *"preview"*, *"open the diagrams"*, *"start the server"*, *"render this in a browser"*.
- Also: *"stop the preview"*, *"shut it down"* → invoke the stop path.

## Workflow

### Start

1. **Locate the workspace directory.** Default: the directory containing `workspace.dsl` (root, then `architecture/`).
2. **Run:**

   ```
   ${CLAUDE_PLUGIN_ROOT}/scripts/preview-start.sh <workspace-dir>
   ```

3. **Report:**
   - On success: `Preview running at http://localhost:8080`.
   - The container is named `c4-architect-local`; if it was already running, the script restarts it cleanly.
   - Custom port: set `C4_PREVIEW_PORT=<n>` before running.

### Stop

```
${CLAUDE_PLUGIN_ROOT}/scripts/preview-stop.sh
```

Idempotent — succeeds silently if nothing is running.

## Prerequisites

- Docker installed and running.
- Port 8080 (or `$C4_PREVIEW_PORT`) free. If the port is taken, `docker run` will fail — suggest stopping the conflicting process or setting `C4_PREVIEW_PORT`.

## Verification

After starting, the preview is reachable at the printed URL. Re-running `preview-start.sh` cleanly replaces the existing container.
