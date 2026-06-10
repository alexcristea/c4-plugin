---
name: structurize
description: Scaffold a C4 architecture workspace. Standalone mode for an empty directory; embedded mode adds an architecture/ subdirectory to an existing project.
allowed-tools: Read, Write, Edit, Bash(ls:*), Bash(test:*), Bash(mkdir:*), Bash(cp:*), Bash(touch:*), Bash(scripts/validate-dsl.sh:*), Bash(docker:*)
---

# structurize — scaffold a C4 workspace

Create the minimal file layout required to start authoring a Structurizr DSL workspace alongside ADRs and supplementary docs.

## When to run

- The user asks: *"set up C4 here"*, *"structurize a new architecture repo"*, *"add C4 to this project"*, *"scaffold the architecture docs"*.
- After installation, this is the first skill most users will invoke.

## Modes

Pick the mode automatically from the current working directory:

1. **Standalone** — cwd is empty (no files other than `.git`, `.gitignore`, `LICENSE`, `README.md`) **or** the user explicitly says "new repo" / "standalone".
2. **Embedded** — cwd already contains an existing project (any source code, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Dockerfile`, etc.).

If you're unsure, **ask the user** which mode they want.

### Standalone layout

Create at the repo root:

```
.
├── workspace.dsl
├── README.md            # short pointer to the workspace + how to render it
├── .gitignore           # adds .structurizr/ and build/
├── adrs/
│   └── 0001-use-c4-model-with-structurizr.md
├── docs/
│   ├── 0001-system-overview.md
│   ├── 0002-actors.md
│   └── 0003-use-cases.md
└── bin/local/run.sh     # convenience: starts Structurizr Local for previewing
```

### Embedded layout

Create under `architecture/` so the existing project's root stays clean:

```
architecture/
├── workspace.dsl
├── README.md            # explains what this subdirectory is, for anyone browsing the host project
├── .gitignore           # ignores architecture/.structurizr/ and architecture/build/
├── adrs/
│   └── 0001-use-c4-model-with-structurizr.md
├── docs/
│   ├── 0001-system-overview.md
│   ├── 0002-actors.md
│   └── 0003-use-cases.md
└── bin/local/run.sh     # convenience: starts Structurizr Local for previewing
```

The nested `architecture/.gitignore` makes the subdirectory self-contained. As a belt-and-suspenders measure, if the **project root** already has a `.gitignore`, also append `architecture/.structurizr/` and `architecture/build/` to it — idempotent, skip if already present.

## Templates

The seed files live in a single source tree and are identical for both modes — only the **destination** differs:

```
${CLAUDE_PLUGIN_ROOT}/templates/workspace/
├── workspace.dsl
├── README.md
├── .gitignore
├── adrs/
│   └── 0001-use-c4-model-with-structurizr.md
├── docs/
│   ├── 0001-system-overview.md
│   ├── 0002-actors.md
│   └── 0003-use-cases.md
└── bin/local/run.sh
```

Copy the entire tree to:

- **Standalone mode** → the current working directory (`.`)
- **Embedded mode** → `./architecture/`

After copying, **replace the placeholders** in the copied files:

- `{{PROJECT_NAME}}` — derive from the cwd directory name unless the user provides one
- `{{TODAY}}` — current date in `YYYY-MM-DD`

## Rules

- **Never** run `git init` and **never** create a commit.
- **Never** overwrite a file that already exists. If a target file is present, ask the user whether to skip, diff, or replace.
- After scaffolding, print a short next-step hint: `/c4:update`, `/c4:validate`, `/c4:preview`.

## References

If the user asks anything about file naming, ADR format, or doc structure during scaffolding, consult:

- `${CLAUDE_PLUGIN_ROOT}/references/adrs-and-docs.md`

## Validation

After copying and placeholder substitution, validate the seeded `workspace.dsl` to catch template corruption or bad substitution before the user starts editing:

```
${CLAUDE_PLUGIN_ROOT}/scripts/validate-dsl.sh <path-to-workspace.dsl>
```

Handle the result:

- **Docker available, validation passes** → report success along with the file list.
- **Docker available, validation fails** → this is a bug in the plugin's templates. Surface the CLI output verbatim and ask the user to file an issue at <https://github.com/alexcristea/c4-plugin/issues>. The scaffolded files remain in place; do **not** delete them.
- **Docker unavailable** (script exit `127`) → skip validation, print `Docker not detected — workspace validation skipped. Run /c4:validate when Docker is available.` and continue.

## Verification

End by listing the files that were created and reporting the validation status (passed / skipped / failed).
