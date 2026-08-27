---
name: export
description: Render a C4 workspace to PlantUML, Mermaid, WebSequenceDiagrams, workspace JSON, a theme file, or a browsable static HTML site. Use whenever the user wants diagram source or files out of the model — "export the diagrams", Mermaid for a README, PlantUML for a wiki or Confluence, the workspace JSON for tooling, or a static site to host on GitHub Pages. Also use when they ask for PNG or SVG, to route them to a supported path.
allowed-tools: Read, Bash(scripts/export-diagrams.sh:*), Bash(ls:*), Bash(find:*), Bash(docker:*)
---

# export — render diagrams

Shells out to `structurizr/structurizr export` in Docker to produce files in the requested format.

## Supported formats

These are the formats accepted by `structurizr/structurizr export -f`:

| Format                  | Output                                                                                              |
|-------------------------|-----------------------------------------------------------------------------------------------------|
| `plantuml`              | PlantUML source (`.puml`) — Structurizr's default PlantUML flavour.                                 |
| `plantuml/structurizr`  | PlantUML source using the Structurizr macros.                                                       |
| `plantuml/c4plantuml`   | PlantUML source using the [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) macros.     |
| `mermaid`               | Mermaid source (`.mmd`).                                                                            |
| `websequencediagrams`   | Sequence-diagram source for [websequencediagrams.com](https://websequencediagrams.com).             |
| `json`                  | Structurizr workspace JSON (useful for tooling).                                                    |
| `theme`                 | A `theme.json` describing the workspace's element/relationship styles.                              |
| `static`                | **Browsable static HTML site** — `index.html`, `css/`, `js/`, `img/`, `workspace.js`. Deployable to any static host (GitHub Pages, S3, Cloudflare Pages, Vercel). |
| `fqcn`                  | Use a custom exporter — pass the fully-qualified class name of a `WorkspaceExporter` implementation. |

### PNG and SVG

**Not supported by the open-source build.** Running `export -f png` (or `svg`) returns: *"Exporting to PNG/SVG is not supported in this build"*. The `-url`/`-mode` flags in the CLI's `--help` are stubs for a feature only in Structurizr's paid offering.

If the user wants raster/vector output, route them to one of:

1. **`/c4:preview`** — runs Structurizr Local in a browser, where rendered diagrams can be exported as PNG/SVG via the UI's download button.
2. **`/c4:export static`** — produces a fully-functional static site they can browse and screenshot.
3. **`/c4:export plantuml`** then a separate render with PlantUML's own CLI (`plantuml/plantuml` Docker image) → PNG/SVG.

## Workflow

1. **Locate workspace.dsl.** Search root, then `architecture/`.
2. **Pick a format.** If unspecified, default to `plantuml`. If the user mentioned a site / web page / deployment, suggest `static`.
3. **Pick an output directory.** Default: `build/diagrams/` (or `build/site/` if the format is `static`).
4. **Run the script:**

   ```
   ${CLAUDE_PLUGIN_ROOT}/scripts/export-diagrams.sh <format> <workspace.dsl> <output-dir>
   ```

5. **Report.** List the generated files. For `static`, mention how to serve them locally (`python3 -m http.server` in the output dir or any equivalent).

## Prerequisites

- Docker installed and running.
- The script will create the output directory if it doesn't exist.
- On Apple Silicon the script passes `--platform linux/amd64` automatically (the `structurizr/structurizr` image has no native ARM build).

## Verification

After the export, `ls` the output directory and report the files produced. For `static`, confirm that `index.html` is present at the output-directory root.
