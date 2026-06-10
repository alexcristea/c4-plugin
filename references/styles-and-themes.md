# Styles and themes — Structurizr DSL

Element styles, relationship styles, light/dark variants, themes, terminology, and branding. Styles live inside the `views { styles { ... } }` block.

## Table of contents

- [`styles`](#styles)
- [`light` / `dark` (mode wrappers)](#light--dark-mode-wrappers)
- [`element` style](#element-style)
- [`relationship` style](#relationship-style)
- [`theme`](#theme)
- [`themes`](#themes)
- [`terminology`](#terminology)

## `styles`

```
views {
    styles {
        element "Person" {
            shape Person
            background #08427b
            color #ffffff
        }

        relationship "Async" {
            style dashed
            color #707070
        }
    }
}
```

Permitted children of `styles`: `light`, `dark`, `element`, `relationship`.

## `light` / `dark` (mode wrappers)

Define styles that apply only in light or dark mode:

```
styles {
    light {
        element "Person" {
            background "#08427b"
            color "#ffffff"
        }
    }
    dark {
        element "Person" {
            background "#80a2c4"
            color "#000000"
        }
    }
}
```

Permitted children: `element`, `relationship`.

## `element` style

Targets a tag. All sub-properties optional.

```
element <tag> {
    shape         <Box|RoundedBox|Circle|Ellipse|Hexagon|Diamond|Cylinder|Bucket|Pipe|Person|Robot|Folder|WebBrowser|Window|Terminal|Shell|MobileDevicePortrait|MobileDeviceLandscape|Component>
    icon          <file|url>
    width         <integer>
    height        <integer>
    background    <#rrggbb|colorName>
    color         <#rrggbb|colorName>      # alias: colour
    stroke        <#rrggbb|colorName>
    strokeWidth   <integer 1-10>
    fontSize      <integer>
    border        <solid|dashed|dotted>
    opacity       <integer 0-100>
    metadata      <true|false>
    description   <true|false>
    properties {
        name value
    }
}
```

- Colors: hex (`#ffff00`) or CSS named (`yellow`).
- Element styles are tuned for the Structurizr renderers; **shapes and icons may not be honoured** by PlantUML/Mermaid exports.

## `relationship` style

```
relationship <tag> {
    thickness   <integer>
    color       <#rrggbb|colorName>          # alias: colour
    style       <solid|dashed|dotted>
    routing     <Direct|Orthogonal|Curved>
    jump        <true|false>
    fontSize    <integer>
    width       <integer>
    position    <integer 0-100>
    opacity     <integer 0-100>
    properties {
        name value
    }
}
```

PlantUML/Mermaid exports may not honour line colours/styles.

## `theme`

```
theme <name|url|file>
```

- **By name**: must be installed on the renderer (Structurizr playground/local/server).
- **By URL**: loaded dynamically when the workspace is rendered.
- **By file**: inlined into the workspace at parse time.

## `themes`

Multiple themes; resolution order is left-to-right.

```
themes <name|url|file> [name|url|file] ...
```

## `terminology`

Override the default vocabulary used in rendered diagrams.

```
terminology {
    person              <term>
    softwareSystem      <term>
    container           <term>
    component           <term>
    deploymentNode      <term>
    infrastructureNode  <term>
    relationship        <term>
    metadata            <square|round|curly|angle|double-angle|none>
}
```

# Source

- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/71-language.md (styles, light, dark, element style, relationship style, theme, themes, terminology)

Pulled: 2026-05-12
