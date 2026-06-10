# Views — Structurizr DSL

Defines the `views` block and every view type: `systemLandscape`, `systemContext`, `container`, `component`, `filtered`, `dynamic`, `deployment`, `custom`, `image`. Includes `include`/`exclude`, `autoLayout`, `animation`, `title`, `default`.

## Table of contents

- [`views`](#views)
- [`systemLandscape`](#systemlandscape)
- [`systemContext`](#systemcontext)
- [`container`](#container)
- [`component`](#component)
- [`filtered`](#filtered)
- [`dynamic`](#dynamic)
- [`deployment`](#deployment)
- [`custom`](#custom)
- [`image`](#image)
- [`include`](#include)
- [`exclude`](#exclude)
- [`autoLayout`](#autolayout)
- [`animation`](#animation)
- [`title`](#title)
- [`default`](#default)

## `views`

Wraps all views.

```
views {
    ...
}
```

Permitted children:
`systemLandscape`, `systemContext`, `container`, `component`, `filtered`, `dynamic`, `deployment`, `custom`, `image`, `styles`, `theme`, `themes`, `terminology`, `properties`.

If the `views` block is missing or empty, the parser generates default views (see `basics.md → Defaults`).

## `systemLandscape`

```
systemLandscape [key] [description] {
    include ...
    exclude ...
    autoLayout ...
}
```

Permitted children: `include`, `exclude`, `autoLayout`, `default`, `animation`, `title`, `description`, `properties`.

## `systemContext`

```
systemContext <softwareSystemIdentifier> [key] [description] {
    ...
}
```

Permitted children: same as `systemLandscape`.

## `container`

(as a view — distinct from the model element of the same name)

```
container <softwareSystemIdentifier> [key] [description] {
    ...
}
```

## `component`

(as a view)

```
component <containerIdentifier> [key] [description] {
    ...
}
```

## `filtered`

Derives a new view by filtering an existing one by tag.

```
filtered <baseKey> <include|exclude> <tags> [key] [description] {
    ...
}
```

Once a filtered view is created for a base view, the base view stops appearing in the diagram list. Add a second filtered view with `include "Element,Relationship"` to keep the original visible.

Permitted children: `default`, `title`, `description`, `properties`.

## `dynamic`

```
dynamic <*|softwareSystemId|containerId> [key] [description] {
    [order:] <src> -> <dst> [description] [technology]
    [order:] <relationshipIdentifier> [description]
}
```

Scope determines what can be added:

- `*`: people and software systems
- Software system scope: people, other software systems, and that system's containers
- Container scope: people, other software systems, other containers, that container's components

Unlike static views, dynamic views are populated by **specifying relationships in order** within the block.

Permitted children: `autoLayout`, `default`, `title`, `description`, `properties`.

## `deployment`

```
deployment <*|softwareSystemId> <environment> [key] [description] {
    ...
}
```

Scope:

- `*`: all deployment nodes, infrastructure nodes, and container instances in the environment.
- Software-system scope: all deployment/infrastructure nodes, plus container instances belonging to that system.

Permitted children: `include`, `exclude`, `autoLayout`, `default`, `animation`, `title`, `description`, `properties`.

## `custom`

Only custom elements (defined via the `element` keyword) can appear here.

```
custom [key] [title] [description] {
    include ...
    exclude ...
    autoLayout ...
}
```

## `image`

```
image <*|elementIdentifier> [key] {
    plantuml <file|url|viewKey>      # OR
    mermaid  <file|url|viewKey>      # OR
    kroki    <format> <file|url>     # OR
    image    <file|url>
}
```

PlantUML/Mermaid/Kroki URLs and formats can be configured as view-set properties:

```
views {
    properties {
        "plantuml.url" "http://localhost:7777"
        "plantuml.format" "svg"
        "mermaid.url"  "http://localhost:8888"
        "mermaid.format" "svg"
        "kroki.url"    "http://localhost:9999"
        "kroki.format" "svg"
    }
}
```

## `include`

### Including elements

```
include <*|identifier|expression> [identifier|expression...]
```

Wildcard semantics per view type:

- System Landscape: all people and software systems
- System Context: software system in scope + everything directly connected to it
- Container: containers in scope + people / external software systems directly connected
- Component: components in scope + connected people / software systems / containers
- Deployment: all deployment/infrastructure nodes and container instances in scope

The **reluctant wildcard** `*?` adds only relationships to/from the in-scope element (system context / container / component views).

### Including relationships

```
include <relationshipIdentifier|expression> ...
```

Relationship expressions only operate on elements that are already in the view.

## `exclude`

```
exclude <identifier|expression> [identifier|expression...]
```

To exclude relationships by source/destination:

```
exclude "<*|identifier|expression> -> <*|identifier|expression>"
```

Combinations:

- `* -> *` — all relationships between all elements
- `source -> *` — all relationships from `source`
- `* -> destination` — all relationships to `destination`
- `source -> destination` — all relationships between the two

## `autoLayout`

```
autoLayout [tb|bt|lr|rl] [rankSeparation] [nodeSeparation]
```

Defaults: `tb`, 300 px, 300 px.

If the workspace has no explicit views, the auto-created views also get auto-layout.

## `animation`

```
animation {
    <identifier> [identifier...]   # step 1
    <identifier> [identifier...]   # step 2
}
```

Each line is one animation step.

## `title`

```
title <title>
```

Overrides the rendered title of the view.

## `default`

```
default
```

Marks this view as the default to show.

# Source

- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/71-language.md (views, all view types, include/exclude/autoLayout/animation/title/default)

Pulled: 2026-05-12
