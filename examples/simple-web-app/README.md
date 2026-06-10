# Example: Simple Web App

The smallest viable C4 model: one person, one software system, three containers, three relationships, and two views.

Render it:

```sh
# Validate
../../scripts/validate-dsl.sh workspace.dsl

# Preview at http://localhost:8080
../../scripts/preview-start.sh .

# Export PlantUML to build/diagrams/
../../scripts/export-diagrams.sh plantuml workspace.dsl
```

Inspect `workspace.dsl` to see how `systemContext`, `container`, and `styles` fit together. Modify it through the plugin with `/c4:update "..."`.
