---
name: preview
description: Start or stop a live browser preview of the C4 workspace at http://localhost:8080, re-rendering as the DSL is edited. Use whenever the user wants to look at the diagrams rather than get files out of them — "preview", "open the diagrams", "render this in a browser", "start the local server", "let me see the container view" — and equally for "stop the preview" or "shut it down".
allowed-tools: Read, Bash(scripts/preview-start.sh:*), Bash(scripts/preview-stop.sh:*), Bash(docker:*), Bash(ls:*)
---

# preview — live diagram preview at localhost:8080

Runs Structurizr Local (`structurizr/structurizr local`) in Docker so the user can view the rendered workspace in a browser. The container watches the workspace directory and re-renders on save. On Apple Silicon, the script passes `--platform linux/amd64` because the image has no native ARM build.

## Choosing between preview and export

Both surface the diagrams, but they answer different asks. `preview` is for *looking* — it renders in a browser and re-renders on save, so it fits an editing loop. `export` is for *files* — PlantUML, Mermaid, JSON, or a static site the user will commit, paste, or deploy. If the user wants something to hand to another tool or person, that's `export`.

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
