# Deployment — Structurizr DSL

`deploymentEnvironment`, `deploymentGroup`, `deploymentNode`, `infrastructureNode`, `softwareSystemInstance`, `containerInstance`, `instanceOf`, `healthCheck`, and the related deployment view.

## Table of contents

- [`deploymentEnvironment`](#deploymentenvironment)
- [`deploymentGroup`](#deploymentgroup)
- [`deploymentNode`](#deploymentnode)
- [`infrastructureNode`](#infrastructurenode)
- [`softwareSystemInstance`](#softwaresysteminstance)
- [`containerInstance`](#containerinstance)
- [`instanceOf`](#instanceof)
- [`instances`](#instances)
- [`healthCheck`](#healthcheck)
- [Deployment view](#deployment-view)

## `deploymentEnvironment`

A named environment such as `Development`, `Staging`, `Production`. Lives inside `model { ... }`.

```
deploymentEnvironment <name> {
    ...
}
```

Permitted children: `group`, `deploymentGroup`, `deploymentNode`, `-> (relationship)`, `-/> (remove relationship)`.

## `deploymentGroup`

Restricts the scope in which inter-instance relationships are replicated.

```
deploymentGroup <name>
```

By default, when software-system or container instances are added to an environment, all relationships between those elements are replicated between **every** instance. Use deployment groups to control this fan-out. See the Structurizr DSL cookbook for examples.

## `deploymentNode`

A physical/virtual node (server, container host, region, etc.). Can be nested.

```
deploymentNode <name> [description] [technology] [tags] [instances] {
    ...
}
```

Default tags: `Element`, `Deployment Node`.

Permitted children: `group`, `deploymentNode` (nested), `infrastructureNode`, `softwareSystemInstance`, `containerInstance`, `instanceOf`, `-> (relationship)`, `description`, `technology`, `instances`, `tags`, `url`, `properties`, `perspectives`.

## `infrastructureNode`

A load balancer, firewall, DNS service, etc.

```
infrastructureNode <name> [description] [technology] [tags] {
    ...
}
```

Default tags: `Element`, `Infrastructure Node`.

Permitted children: `-> (relationship)`, `description`, `technology`, `tags`, `url`, `properties`, `perspectives`.

## `softwareSystemInstance`

An instance of a software system deployed on the parent deployment node.

```
softwareSystemInstance <softwareSystemIdentifier> [deploymentGroups] [tags] {
    ...
}
```

`deploymentGroups` is a comma-separated list of `deploymentGroup` identifiers.

Default tags: those inherited from the software system, plus `Software System Instance`.

Permitted children: `-> (relationship)`, `description`, `tags`, `url`, `properties`, `perspectives`, `healthCheck`.

## `containerInstance`

```
containerInstance <containerIdentifier> [deploymentGroups] [tags] {
    ...
}
```

Default tags: those inherited from the container, plus `Container Instance`.

Permitted children: `-> (relationship)`, `description`, `tags`, `url`, `properties`, `perspectives`, `healthCheck`.

## `instanceOf`

Alias for `softwareSystemInstance` / `containerInstance`.

```
instanceOf <identifier> [deploymentGroups] [tags] {
    ...
}
```

## `instances`

Sets the number of instances of a deployment node. Static number or range.

```
instances "4"
instances "1..N"
instances "0..*"
```

## `healthCheck`

An HTTP health check attached to a software-system or container instance.

```
healthCheck <name> <url> [interval] [timeout]
```

`interval` is in seconds (default `60s`). `timeout` is in milliseconds (default `0ms`).

## Deployment view

See `views.md → deployment` for the view syntax. In brief:

```
views {
    deployment <*|softwareSystemId> <environment> [key] [description] {
        include *
        autoLayout
    }
}
```

## Example

```
model {
    web = softwareSystem "Web App" {
        api = container "API"
        db  = container "Database"
    }

    deploymentEnvironment "Production" {
        deploymentNode "AWS" {
            deploymentNode "ECS Cluster" {
                apiInstance = containerInstance api
            }
            deploymentNode "RDS" {
                dbInstance = containerInstance db
            }
            infrastructureNode "ALB" {
                -> apiInstance "Routes requests to"
            }
        }
    }
}
```

# Source

- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/71-language.md (deploymentEnvironment, deploymentGroup, deploymentNode, infrastructureNode, softwareSystemInstance, containerInstance, instanceOf, healthCheck, instances, deployment view)

Pulled: 2026-05-12
