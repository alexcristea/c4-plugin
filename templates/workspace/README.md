# {{PROJECT_NAME}} — Architecture

This workspace contains the C4 architecture model for **{{PROJECT_NAME}}**, authored with [Structurizr DSL](https://docs.structurizr.com/dsl). Diagrams are generated from `workspace.dsl`; decisions live in `adrs/`; supplementary documentation lives in `docs/`.

## Layout

```
workspace.dsl        # the C4 model and views
adrs/                # architecture decision records (Nygard format)
docs/                # supplementary documentation
bin/local/run.sh     # convenience preview launcher
```

## Working with the model

Edit by asking Claude Code, with the `c4` plugin or skill installed:

| Task               | Example request                                 |
|--------------------|-------------------------------------------------|
| Edit the model     | "add a Redis cache in front of the API"         |
| Validate           | "is the workspace valid?"                       |
| Preview in browser | "preview the diagrams"                          |
| Export diagrams    | "export the diagrams as PlantUML"               |

Without Claude Code, run `bin/local/run.sh` and open <http://localhost:8080>. You can also use the official Structurizr CLI directly — see the [c4 README](https://github.com/alexcristea/c4-plugin) for details.

## Why this lives in version control

Keeping the architecture model alongside the code means:

- Diagrams stay reviewable in pull requests (DSL is text, not binary).
- The model evolves with the code, instead of rotting in a separate wiki.
- New contributors see the design alongside the implementation.

Every architectural change should land in the same PR as the code change that motivates it.
