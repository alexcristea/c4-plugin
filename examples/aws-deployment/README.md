# Example: AWS deployment

A small web shop deployed to AWS, styled with the bundled AWS theme.

Demonstrates:

- Nested `deploymentNode`s for cloud, region, VPC, ECS cluster and Fargate task
- `infrastructureNode`s for managed plumbing (Route 53, load balancer)
- Owned data stores (RDS, S3) modelled as containers placed on deployment nodes
- `theme amazon-web-services-2025.07` with exact `Amazon Web Services - <Service>` tags for icons
- `systemContext`, `container`, and `deployment` views

Render it:

```sh
../../scripts/validate-dsl.sh workspace.dsl
../../scripts/preview-start.sh .
```

Icons show in the preview and the static HTML export. PlantUML/Mermaid exports drop them.
