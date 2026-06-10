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

Edit via the `c4-architect` Claude Code plugin:

| Task              | Command                          |
|-------------------|----------------------------------|
| Edit the model    | `/c4:update "describe change"`   |
| Validate          | `/c4:validate`                   |
| Preview in browser| `/c4:preview`                    |
| Export diagrams   | `/c4:export plantuml`            |

Without the plugin, run `bin/local/run.sh` and open <http://localhost:8080>. You can also use the official Structurizr CLI directly — see the [plugin README](https://github.com/alexcristea/c4-plugin) for details.

## Why this lives in version control

Keeping the architecture model alongside the code means:

- Diagrams stay reviewable in pull requests (DSL is text, not binary).
- The model evolves with the code, instead of rotting in a separate wiki.
- New contributors see the design alongside the implementation.

Every architectural change should land in the same PR as the code change that motivates it.
