# Relationships — Structurizr DSL

The `->` operator, scope-based syntax, the matrix of valid source/destination pairs, implied relationships, removal, and relationship archetypes.

## Table of contents

- [Defining relationships](#defining-relationships)
- [Scope-based syntax](#scope-based-syntax)
- [Valid source/destination combinations](#valid-sourcedestination-combinations)
- [Default tags](#default-tags)
- [Implied relationships](#implied-relationships)
- [Removing a relationship (`-/>`)](#removing-a-relationship--)
- [Tags, URL, properties, perspectives](#tags-url-properties-perspectives)
- [Finding existing relationships](#finding-existing-relationships)
- [Relationship archetypes](#relationship-archetypes)

## Defining relationships

Uni-directional, between any two elements:

```
<sourceIdentifier> -> <destinationIdentifier> [description] [technology] [tags] {
    ...
}
```

Example:

```
user -> softwareSystem "Uses"
```

`->` is the basic form. An archetype-based form is also available: `--<archetype>->` (see [Relationship archetypes](#relationship-archetypes)).

## Scope-based syntax

Inside an element's block, the source defaults to the element in scope:

```
person user {
    -> softwareSystem "Uses"
}
```

This is equivalent to:

```
person user {
    this -> softwareSystem "Uses"
}
```

## Valid source/destination combinations

| Source                   | Destination                                                                  |
|--------------------------|------------------------------------------------------------------------------|
| Person                   | Person, Software System, Container, Component                                |
| Software System          | Person, Software System, Container, Component                                |
| Container                | Person, Software System, Container, Component                                |
| Component                | Person, Software System, Container, Component                                |
| Deployment Node          | Deployment Node                                                              |
| Infrastructure Node      | Deployment Node, Infrastructure Node, Software System Instance, Container Instance |
| Software System Instance | Infrastructure Node                                                          |
| Container Instance       | Infrastructure Node                                                          |

## Default tags

Every relationship gets the `Relationship` tag automatically.

## Implied relationships

By default, relationships between nested elements **imply** relationships between their parents. Example:

```
workspace {
    model {
        u = person "User"
        s = softwareSystem "Software System" {
            webapp = container "Web Application"
        }
        u -> webapp "Uses"   # implies u -> s
    }
}
```

Configure with:

```
!impliedRelationships <true|false|fqcn>
```

- `true` (default): create implied relationships unless any relationship already exists between the parent pair.
- `false`: never create implied relationships.
- `<fqcn>`: a fully qualified Java class name for a custom strategy, e.g. `com.structurizr.model.CreateImpliedRelationshipsUnlessSameRelationshipExistsStrategy`.

## Removing a relationship (`-/>`)

The `-/>` operator removes a previously created relationship (useful when modifying an extended workspace, or when implied relationships need to be deleted).

```
sourceIdentifier -/> destinationIdentifier
```

Available inside a `deploymentEnvironment` block (and elsewhere where modifications make sense).

## Tags, URL, properties, perspectives

Permitted children of a relationship:

```
<src> -> <dest> "Uses" {
    tags "Sync"
    url https://example.com
    properties {
        priority "high"
    }
    perspectives {
        Security "TLS 1.3 only"
    }
}
```

## Finding existing relationships

To extend a previously defined relationship (e.g. to add tags), use `!relationship`:

```
!relationship <identifier> {
    tags "Async"
}
```

Or, in an extended JSON-based workspace, look up by canonical name:

```
<identifier> = !relationship <canonical name> {
    ...
}
```

Bulk operations:

```
!relationships <expression> {
    tag "TaggedByBulk"
}
```

## Relationship archetypes

Define a reusable relationship type with defaults for description, technology, properties, perspectives, and tags:

```
workspace {
    model {
        archetypes {
            sync  = -> {
                tags "Synchronous"
            }
            https = --sync-> {
                technology "HTTPS"
            }
        }

        a = softwareSystem "A"
        b = softwareSystem "B"

        a --https-> b "Makes API calls using"
    }
}
```

Use as `<src> --<archetype>-> <dest>`.

# Source

- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/71-language.md (relationship, !relationship, !relationships, remove relationship)
- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/07-implied-relationships.md
- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/06-archetypes.md (relationship archetypes)

Pulled: 2026-05-12
