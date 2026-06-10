# Model elements — Structurizr DSL

Defines the `model` block and every element type that lives inside it:
`person`, `softwareSystem`, `container`, `component`, `group`, `element`, plus user-defined `archetypes`.

## Table of contents

- [`model`](#model)
- [`person`](#person)
- [`softwareSystem`](#softwaresystem)
- [`container`](#container)
- [`component`](#component)
- [`group`](#group)
- [`element` (custom)](#element-custom)
- [Common children](#common-children)
- [Archetypes](#archetypes)

## `model`

Each workspace must contain a `model` block.

```
model {
    ...
}
```

Permitted children: `!identifiers`, `archetypes`, `group`, `person`, `softwareSystem`, `deploymentEnvironment`, `element`, `-> (relationship)`.

## `person`

Defines a user, actor, role, or persona.

```
person <name> [description] [tags] {
    ...
}
```

Default tags: `Element`, `Person`.

Permitted children: `description`, `tags`, `url`, `properties`, `perspectives`, `-> (relationship)`.

## `softwareSystem`

Defines a software system.

```
softwareSystem <name> [description] [tags] {
    ...
}
```

Default tags: `Element`, `Software System`.

Permitted children: `!docs`, `!adrs`, `group`, `container`, `description`, `tags`, `url`, `properties`, `perspectives`, `-> (relationship)`.

## `container`

Defines a container within a software system.

```
container <name> [description] [technology] [tags] {
    ...
}
```

Default tags: `Element`, `Container`.

Permitted children: `!docs`, `!adrs`, `group`, `component`, `!components`, `description`, `technology`, `tags`, `url`, `properties`, `perspectives`, `-> (relationship)`.

## `component`

Defines a component within a container.

```
component <name> [description] [technology] [tags] {
    ...
}
```

Default tags: `Element`, `Component`.

Permitted children: `!docs`, `!adrs`, `description`, `technology`, `tags`, `url`, `properties`, `perspectives`, `group`, `-> (relationship)`.

## `group`

Renders a boundary around child elements **at the same level of abstraction**.

```
group <name> {
    ...
}
```

| Location        | Permitted child elements   |
|-----------------|----------------------------|
| Model           | People and software systems |
| Software System | Containers                  |
| Container       | Components                  |

`group` can also be used **as a property** to assign a component to a group:

```
component "Component Name" {
    group "Group Name"
}
```

Groups can be nested.

## `element` (custom)

A custom element that sits outside the C4 model (useful for diagrams of business processes, data flows, etc.).

```
element <name> [metadata] [description] [tags] {
    ...
}
```

Default tag: `Element`. Custom elements are the only thing that can appear on `custom` views.

Permitted children: `description`, `tags`, `url`, `properties`, `perspectives`, `-> (relationship)`.

## Common children

These can be set on most elements:

```
description "..."
technology "..."           # container, component, deploymentNode, infrastructureNode
tag "TagA"
tags "TagA,TagB"
tags "TagA" "TagB"
url https://example.com
properties {
    <name> <value>
}
perspectives {
    <name> <description> [value]
}
```

## Archetypes

User-defined types that extend the basic element/relationship types with sensible defaults. Reduce repetition and let teams build a shared vocabulary on top of C4.

```
workspace {
    model {
        archetypes {
            application = container {
                technology "Java"
                tag "Application"
            }
            springBootApplication = application {
                technology "Spring Boot"
            }
            datastore = container {
                technology "MySQL"
                tag "Data Store"
            }
        }

        softwareSystem "A" {
            webapp = springBootApplication "Web Application"
            db    = datastore "Database Schema"
            webapp -> db "Reads from"
        }
    }
}
```

Element archetypes are available for: `person`, `softwareSystem`, `container`, `component`, `deploymentNode`, `infrastructureNode`, `group`, `element`.

Defaults you can set on an archetype: description, technology (containers/components), properties, perspectives, tags, metadata (custom elements only).

Archetypes can extend other archetypes.

# Source

- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/71-language.md (model, person, softwareSystem, container, component, group, element)
- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/06-archetypes.md

Pulled: 2026-05-12
