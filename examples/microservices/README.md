# Example: Microservices

A more realistic workspace: multiple containers, two external systems, an event bus, a deployment environment, and four views.

Demonstrates:

- Multiple `container`s within one `softwareSystem`
- `External` tag on third-party systems (Stripe, SendGrid) styled differently
- An asynchronous container (`Event Bus`) with its own shape (`Pipe`)
- A `deploymentEnvironment "Production"` modelling EKS + MSK + RDS
- `infrastructureNode` for the load balancer with routing relationships to container instances
- `systemLandscape`, `systemContext`, `container`, and `deployment` views

Render it:

```sh
../../scripts/validate-dsl.sh workspace.dsl
../../scripts/preview-start.sh .
../../scripts/export-diagrams.sh plantuml workspace.dsl
```
