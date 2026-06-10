# Expressions — Structurizr DSL

Element and relationship expressions, used with `include` / `exclude` inside views (except `dynamic`), and with the `!elements` / `!relationships` bulk operators.

Quote any expression that contains whitespace:

- `include "element.tag==Tag 1"` (correct)
- `include element.tag=="Tag 1"` (incorrect)

## Element expressions

| Expression                                       | Meaning                                                                 |
|--------------------------------------------------|-------------------------------------------------------------------------|
| `-><identifier\|expression>`                     | the element(s) plus afferent couplings                                  |
| `<identifier\|expression>->`                     | the element(s) plus efferent couplings                                  |
| `-><identifier\|expression>->`                   | the element(s) plus afferent and efferent couplings                     |
| `element.type==<type>`                           | elements of type `Person`, `SoftwareSystem`, `Container`, `Component`, `DeploymentNode`, `InfrastructureNode`, `SoftwareSystemInstance`, `ContainerInstance`, `Custom` |
| `element.parent==<identifier>`                   | elements with the given parent                                          |
| `element.tag==<tag>[,tag]`                       | elements that have **all** specified tags                               |
| `element.tag!=<tag>[,tag]`                       | elements that do **not** have all specified tags                        |
| `element.technology==<technology>`               | elements with the given technology                                      |
| `element.technology!=<technology>`               | elements without the given technology                                   |
| `element.properties[<name>]==<value>`            | elements with the given property/value                                  |
| `element==-><identifier>`                        | the specified element (or group) plus afferent couplings                |
| `element==<identifier>->`                        | the specified element (or group) plus efferent couplings                |
| `element==-><identifier>->`                      | the specified element (or group) plus afferent and efferent couplings   |

## Relationship expressions

| Expression                                        | Meaning                                                              |
|---------------------------------------------------|----------------------------------------------------------------------|
| `*->*`                                            | all relationships                                                    |
| `<identifier>->*`                                 | all relationships from the given source                              |
| `*-><identifier>`                                 | all relationships to the given destination                           |
| `relationship==*`                                 | all relationships                                                    |
| `relationship==*->*`                              | all relationships                                                    |
| `relationship.tag==<tag>[,tag]`                   | relationships with **all** specified tags                            |
| `relationship.tag!=<tag>[,tag]`                   | relationships without all specified tags                             |
| `relationship.properties[<name>]==<value>`        | relationships with the given property/value                          |
| `relationship.source==<identifier>`               | relationships from the given source                                  |
| `relationship.destination==<identifier>`          | relationships to the given destination                               |
| `relationship==<identifier>->*`                   | relationships from the given source                                  |
| `relationship==*-><identifier>`                   | relationships to the given destination                               |
| `relationship==<identifier>-><identifier>`        | relationships between the two specified elements                     |

## Combining expressions

Combine two expressions with `&&` (and) or `||` (or):

```
"element.type==Container && element.parent==abc"
```

For anything more complex, use a DSL `!script` or a plugin.

## Examples

Include all containers belonging to a particular system, plus anything that calls them:

```
container shop {
    include "-> element.parent==shop"
}
```

Exclude all asynchronous relationships from a view:

```
container shop {
    include *
    exclude "relationship.tag==Async"
}
```

# Source

- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/08-expressions.md

Pulled: 2026-05-12
