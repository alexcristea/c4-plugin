# Deployment — Structurizr DSL

`deploymentEnvironment`, `deploymentGroup`, `deploymentNode`, `infrastructureNode`, `softwareSystemInstance`, `containerInstance`, `instanceOf`, `healthCheck`, the related deployment view, and how to model cloud infrastructure (AWS, Azure, GCP, Kubernetes) with themed icons.

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
- [Cloud infrastructure](#cloud-infrastructure)
- [Example](#example)

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

Permitted children: `group`, `deploymentGroup`, `deploymentNode` (nested), `infrastructureNode`, `softwareSystemInstance`, `containerInstance`, `instanceOf`, `-> (relationship)`, `description`, `technology`, `instances`, `tags`, `url`, `properties`, `perspectives`.

`deploymentGroup <identifier>` inside a `deploymentNode` assigns that group to every instance nested under the node, instead of listing it on each `softwareSystemInstance`/`containerInstance`:

```
production = deploymentEnvironment "Production" {
    serviceInstance1 = deploymentGroup "Service instance 1"

    deploymentNode "Server 1" {
        deploymentGroup serviceInstance1
        containerInstance api
        deploymentNode "Database Server" {
            containerInstance database
        }
    }
}
```

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

## Cloud infrastructure

### Mapping cloud services to C4

| Cloud concept                                                                 | DSL element                                                                    |
|-------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Provider, account, region, VPC, subnet                                        | nested `deploymentNode`s                                                       |
| Compute that runs **your** code (EC2, ECS/Fargate, Lambda, EKS)               | `deploymentNode` containing a `containerInstance`                              |
| Data store **you** own (RDS, DynamoDB, S3 bucket, ElastiCache)                | a `container` in the static model; its `containerInstance` sits in a `deploymentNode` for the service |
| Managed plumbing with none of your code (Route 53, load balancer, CloudFront, API Gateway, SQS/SNS used purely as transport) | `infrastructureNode`                                                           |
| Third-party SaaS you don't operate (Stripe, Auth0)                            | `softwareSystem` tagged `External`, not a deployment element                   |

Put the provider's service name in `technology` (`"Amazon RDS for PostgreSQL"`, `"AWS Fargate"`), and use one `deploymentEnvironment` per environment found in Terraform/Kubernetes config.

### Cloud themes (icons and colours)

The `structurizr/structurizr` image bundles prebuilt themes. The plugin's scripts enable them with `-e STRUCTURIZR_THEMES=/usr/local/structurizr-themes`, so reference them **by name**:

```
views {
    theme amazon-web-services-2025.07
}
```

Do **not** use `https://static.structurizr.com/themes/...` URLs: that host went away with the Structurizr cloud service EOL (30 September 2026), and validation fails when a theme can't be loaded.

A theme only styles elements whose tag matches **exactly** (`Amazon Web Services - <Service>`). A misspelled tag silently gets no icon. Common tags in `amazon-web-services-2025.07`:

| Service                         | Tag                                                   |
|---------------------------------|-------------------------------------------------------|
| AWS cloud boundary              | `Amazon Web Services - AWS Cloud`                     |
| Region                          | `Amazon Web Services - Region`                        |
| VPC                             | `Amazon Web Services - Virtual Private Cloud`         |
| Public / private subnet         | `Amazon Web Services - Public subnet` / `Amazon Web Services - Private subnet` |
| EC2                             | `Amazon Web Services - EC2`                           |
| ECS                             | `Amazon Web Services - Elastic Container Service`     |
| EKS                             | `Amazon Web Services - Elastic Kubernetes Service`    |
| Fargate                         | `Amazon Web Services - Fargate`                       |
| Lambda                          | `Amazon Web Services - Lambda`                        |
| RDS / Aurora                    | `Amazon Web Services - RDS` / `Amazon Web Services - Aurora` |
| DynamoDB                        | `Amazon Web Services - DynamoDB`                      |
| ElastiCache                     | `Amazon Web Services - ElastiCache`                   |
| S3                              | `Amazon Web Services - Simple Storage Service`        |
| Load balancer (ALB/NLB)         | `Amazon Web Services - Load Balancing`                |
| Route 53                        | `Amazon Web Services - Route 53`                      |
| CloudFront                      | `Amazon Web Services - CloudFront`                    |
| API Gateway                     | `Amazon Web Services - API Gateway`                   |
| SQS / SNS                       | `Amazon Web Services - Simple Queue Service` / `Amazon Web Services - Simple Notification Service` |
| EventBridge                     | `Amazon Web Services - EventBridge`                   |
| Cognito                         | `Amazon Web Services - Cognito`                       |

Other bundled themes (tag prefix in brackets; tag sets differ between versions, so check the exact name in the theme before using one not listed here):

- Microsoft Azure: `microsoft-azure-2025.11` (`Microsoft Azure - `)
- Google Cloud: `google-cloud-platform-2025.09` (`Google Cloud Platform - `)
- Kubernetes: `kubernetes` (`Kubernetes - `)
- Oracle Cloud: `oracle-cloud-infrastructure-2023.04` (`Oracle Cloud Infrastructure - `)

Older dated versions (e.g. `amazon-web-services-2023.01`) are bundled too. Icons render in `/c4:preview` and the static HTML export; PlantUML/Mermaid exports drop them (see `styles-and-themes.md`).

## Example

An AWS deployment using the theme. Full workspace with context and container views: `examples/aws-deployment/workspace.dsl`.

```
model {
    bookstore = softwareSystem "Bookstore" {
        webApp = container "Web App" "Serves the storefront and checkout API." "Node.js"
        database = container "Database" "Stores catalogue and orders." "Postgres"
    }
    webApp -> database "Reads from and writes to" "SQL/TLS"

    production = deploymentEnvironment "Production" {
        deploymentNode "Amazon Web Services" "" "AWS" {
            tags "Amazon Web Services - AWS Cloud"

            deploymentNode "eu-west-1" "" "AWS Region" {
                tags "Amazon Web Services - Region"

                loadBalancer = infrastructureNode "Load Balancer" "Terminates TLS." "Application Load Balancer" {
                    tags "Amazon Web Services - Load Balancing"
                }

                deploymentNode "ECS Cluster" "" "Amazon ECS" {
                    tags "Amazon Web Services - Elastic Container Service"

                    deploymentNode "Fargate Task" "" "AWS Fargate" "" 2 {
                        tags "Amazon Web Services - Fargate"
                        webAppInstance = containerInstance webApp
                    }
                }

                deploymentNode "Database Server" "" "Amazon RDS for PostgreSQL" {
                    tags "Amazon Web Services - RDS"
                    containerInstance database
                }
            }
        }

        loadBalancer -> webAppInstance "Forwards requests to" "HTTPS"
    }
}

views {
    deployment bookstore production "Production" {
        include *
        autoLayout lr
    }

    theme amazon-web-services-2025.07
}
```

# Source

- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/71-language.md (deploymentEnvironment, deploymentGroup, deploymentNode, infrastructureNode, softwareSystemInstance, containerInstance, instanceOf, healthCheck, instances, deployment view)
- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/cookbook/deployment-groups/index.md (deployment groups set on deployment nodes)
- https://github.com/structurizr/structurizr.github.io/blob/main/dsl/cookbook/amazon-web-services/index.md (AWS deployment modelling)
- https://github.com/structurizr/structurizr.github.io/blob/main/commands/03-server/21-diagrams/04-themes.md (bundled themes, `STRUCTURIZR_THEMES`)
- https://github.com/structurizr/structurizr.github.io/blob/main/eol.md (cloud service EOL)
- Theme tag names: `/usr/local/structurizr-themes/*/theme.json` in the `structurizr/structurizr` image

Pulled: 2026-10-12
