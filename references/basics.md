# Basics — Structurizr DSL

DSL parsing rules, identifiers, constants, comments, defaults, includes, and the top-level `workspace` keyword.

## Table of contents

- [DSL rules](#dsl-rules)
- [Workspace rules](#workspace-rules)
- [Identifiers](#identifiers)
- [Identifier scope](#identifier-scope)
- [String constants and variables](#string-constants-and-variables)
- [String substitution](#string-substitution)
- [Comments](#comments)
- [Defaults](#defaults)
- [The `workspace` keyword](#the-workspace-keyword)
- [Includes (`!include`)](#includes-include)

## DSL rules

- Lines are processed in order, and forward referencing is **not** supported (imperative, not declarative).
- Line breaks matter; split long lines with `\` as the last character on the line.
- Tokens are separated by whitespace, but the quantity of whitespace/indentation is irrelevant.
- Keywords are case-insensitive (`softwareSystem` and `softwaresystem` are equivalent).
- Double quotes (`"..."`) around a property are optional when it contains no whitespace.
- Opening curly brace `{` must be on the same line as the statement.
- Closing curly brace `}` must be on a line of its own.
- Braces are only required when adding child content.
- Use `""` as a placeholder to skip an earlier optional property.
- Tags are comma-separated (`Tag 1,Tag 2,Tag 3`).

## Workspace rules

- Each view must have a unique `key`. Auto-generated keys are **not** guaranteed stable — assign keys explicitly if you care about manual layout.
- Software-system and person names must be unique.
- Container names must be unique within a software system.
- Component names must be unique within a container.
- Deployment-node and infrastructure-node names must be unique within their parent.
- Every relationship from a source element to a destination element must have a unique description.

## Identifiers

By default, elements and relationships are anonymous and cannot be referenced. Assign an identifier with `=`:

```
p  = person "User"
ss = softwareSystem "Software System"
p -> ss "Uses"

rel = p -> ss "Uses"
```

Identifier characters: `a-zA-Z_0-9`. Identifiers are only needed when you need to reference the element/relationship later.

## Identifier scope

Identifiers are **flat** (global) by default. Switch to **hierarchical** scope with `!identifiers hierarchical` if you have name collisions across systems:

```
workspace {
    !identifiers hierarchical

    model {
        softwareSystem1 = softwareSystem "Software System 1" {
            api = container "API"
        }
        softwareSystem2 = softwareSystem "Software System 2" {
            api = container "API"
        }
    }
}
```

Now reference as `softwareSystem1.api` and `softwareSystem2.api`. Note: `!identifiers hierarchical` does **not** apply to groups.

## String constants and variables

```
!const <name> <value>   # immutable
!var   <name> <value>   # may be redefined
```

Names may contain `a-zA-Z0-9-_.`.

## String substitution

```
!const ORGANISATION_NAME "Organisation"
!const GROUP_NAME "Group"

workspace {
    model {
        group "${ORGANISATION_NAME} - ${GROUP_NAME}" {
            user = person "User"
        }
    }
}
```

`${NAME}` substitution targets a constant, variable, or environment variable. If unresolved, no substitution occurs.

## Comments

```
/*
    multi-line comment
*/
/* single-line comment */
# single-line comment
// single-line comment
```

## Defaults

If a workspace omits the `views` block (or it is empty), the parser creates a default set: 1 System Landscape + 1 System Context + 1 Container view per software system, all with auto-layout enabled.

Implied relationships are created by default. See `relationships.md` for control via `!impliedRelationships`.

## The `workspace` keyword

```
workspace [name] [description] {
    ...
}
```

Or, to extend another workspace:

```
workspace extends <file|url> {
    ...
}
```

Permitted children: `name`, `description`, `properties`, `!identifiers`, `!docs`, `!adrs`, `model`, `views`, `configuration`.

Special workspace properties:

- `structurizr.dsl` — base64-encoded DSL source, created automatically when the DSL is "portable".
- `structurizr.dsl.source` — `true` (default) retains the DSL source; `false` discards it.

A workspace is **not** "portable" if it uses any of: `extends <file>`, `!impliedRelationships <fqcn>`, `!include <file|directory>`, `!script <file>`, `!plugin`, `!docs`, `!adrs`/`!decisions`, `!components`, `icon <file>`, `theme <file>`, `logo <file>`.

## Includes (`!include`)

Inline a DSL fragment from another file, directory, or URL — content is inlined in the order discovered:

```
!include people.dsl
!include model/people.dsl
!include model
!include https://example.com/model/people.dsl
```

# Source

- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/03-basics.md
- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/04-defaults.md
- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/05-identifiers.md
- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/31-includes.md
- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/71-language.md (workspace section)

Pulled: 2026-05-12
