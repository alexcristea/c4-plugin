# c4-architect

A Claude Code plugin for authoring [C4 architecture diagrams](https://c4model.com) as [Structurizr DSL](https://docs.structurizr.com/dsl), with Michael Nygard-style ADRs and supplementary docs alongside the model.

You describe the change in plain English; Claude edits `workspace.dsl`, validates it against the official `structurizr/structurizr` Docker image, and reports the result. Diagrams can be previewed in a browser or exported to PlantUML, Mermaid, or Graphviz.

## What this plugin gives you

| Skill           | Purpose                                                                                  |
|-----------------|------------------------------------------------------------------------------------------|
| `/c4:init`         | Scaffold a new workspace — standalone repo, or `architecture/` inside an existing one.   |
| `/c4:update`       | Make any change to the model, views, styles, deployment, ADRs, or docs. Auto-validates.  |
| `/c4:validate`     | Run `structurizr/structurizr validate` on demand.                                        |
| `/c4:export`       | Render the workspace to PlantUML, Mermaid, JSON, or a browsable static HTML site.        |
| `/c4:preview`      | Start Structurizr Local at `http://localhost:8080` for live in-browser preview.          |
| `conventions`   | Auto-loaded when editing `.dsl`, `adrs/**`, or `docs/**`. Not user-invocable.            |

All skills share a curated set of Structurizr DSL references bundled at the plugin root — no network roundtrips, no truncation.

## Prerequisites

- [Claude Code](https://docs.claude.com/claude-code) installed.
- [Docker](https://docs.docker.com/get-docker/) — required only for `/c4:validate`, `/c4:export`, and `/c4:preview`. `/c4:init` and `/c4:update` (without auto-validate) work without it.

## Install

### From a marketplace

In a Claude Code session:

```
/plugin marketplace add alexcristea/claude-marketplace
/plugin install c4@over-engineering-plugins
```

`alexcristea/claude-marketplace` is the [over-engineering-plugins marketplace](https://github.com/alexcristea/claude-marketplace), which lists this plugin among others. This plugin lives in its own repo, so any other marketplace can list it too — see its entry format in the marketplace README.

### Directly from this repo

```
/plugin install alexcristea/c4-plugin
```

### From a local clone (for development)

```sh
git clone https://github.com/alexcristea/c4-plugin.git
```

In a Claude Code session:

```
/plugin install --plugin-dir /absolute/path/to/c4-plugin
```

## Quickstart

In an empty directory:

```
/c4:init
/c4:update "we have a Next.js web app talking to a Node.js API talking to Postgres"
/c4:preview
```

Open `http://localhost:8080` — your diagram is rendered and updates as you edit.

## Use cases

> **Both invocation styles work.** Every example below shows the explicit slash-command form (`/c4:update "..."`), but you can also drop the prefix and just describe what you want — `add a Postgres database and connect it to the API` triggers `/c4:update` automatically. The double quotes around the prompt are a visual convention for the docs, not required syntax — `/c4:update add a database` parses the same as `/c4:update "add a database"`. Use whichever feels natural.

### Greenfield: design from scratch

Start in an empty directory:

| Slash command                                                                                          | Or just say…                                                          |
|--------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| `/c4:init`                                                                                                | "set up C4 in this empty directory"                                   |
| `/c4:update "add a person 'Customer' who uses our system"`                                                | "add a person 'Customer' who uses our system"                         |
| `/c4:update "add three containers: a Next.js storefront, a Go catalog service, and a Postgres catalog database"` | "add three containers: a Next.js storefront, a Go catalog service, and a Postgres catalog database" |
| `/c4:update "add a container view named 'Storefront' showing how requests flow through the system"`      | "add a container view named 'Storefront' showing how requests flow through the system" |

### Brownfield: reverse-engineer an existing repo

In an existing project directory:

| Slash command                                                                                                       | Or just say…                                                                          |
|---------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| `/c4:init`                                                                                                             | "add a C4 architecture model to this project" → triggers embedded mode                |
| `/c4:update --discover "model this codebase as C4 — scan Dockerfiles, package.json, k8s/, and routes/"`                | "model this codebase as C4 — scan Dockerfiles, package.json, k8s/, and routes/"       |

Claude scans manifests, infra config, and routing, proposes a model, then writes `architecture/workspace.dsl` after you confirm.

### Documentation-first: ADRs and supplementary docs alongside the model

| Slash command                                                                                                  | Or just say…                                                                  |
|----------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| `/c4:update "record an ADR titled 'Adopt Kafka for cross-service events'"`                                        | "record an ADR titled 'Adopt Kafka for cross-service events'"                 |
| `/c4:update "supersede ADR 003 with a new ADR introducing CQRS for the orders service"`                           | "supersede ADR 003 with a new ADR introducing CQRS for the orders service"    |
| `/c4:update "fill in docs/0002-actors.md with the four roles we discussed"`                                       | "fill in docs/0002-actors.md with the four roles we discussed"                |

ADRs follow the Michael Nygard format and live in `adrs/` (or `architecture/adrs/`).

## Supported use cases by skill

A complete inventory of what each skill handles. Every row shows two ways to invoke the same thing: the explicit **slash command**, and the **natural-language** phrase Claude will route to the same skill. Use whichever feels natural. Legend: ✅ covered · ⚠️ partial (see note) · ❌ not covered (workaround in note).

### `/c4:init` — bootstrap a workspace

| Use case                                       | Status | Slash command | Or just say…                                                |
|------------------------------------------------|:------:|---------------|-------------------------------------------------------------|
| Set up a new architecture repo                 | ✅     | `/c4:init`       | "set up C4 in this empty directory"                         |
| Add C4 architecture to my existing project     | ✅     | `/c4:init`       | "add a C4 architecture model to this project"               |

### `/c4:update` — all editing

#### Model elements

| Use case                                                   | Status | Slash command                                                                                          | Or just say…                                                                                  |
|------------------------------------------------------------|:------:|--------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Add a person / software system / container / component     | ✅     | `/c4:update "add a 'Reporting Service' container running on Java"`                                        | "add a 'Reporting Service' container running on Java"                                         |
| Remove or rename an element                                | ✅     | `/c4:update "rename the 'API' container to 'Public API' and remove the unused 'Legacy Worker' container"` | "rename the 'API' container to 'Public API' and remove the unused 'Legacy Worker' container"  |
| Add a group to organise containers by squad                | ✅     | `/c4:update "wrap the checkout and payments containers in a group called 'Checkout Squad'"`               | "wrap the checkout and payments containers in a group called 'Checkout Squad'"                |
| Define archetypes for reusable element types               | ✅     | `/c4:update "add an archetype for Spring Boot containers and use it for the API"`                         | "add an archetype for Spring Boot containers and use it for the API"                          |

#### Relationships

| Use case                                          | Status | Slash command                                                                                          | Or just say…                                                                                  |
|---------------------------------------------------|:------:|--------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Add a relationship between API and database       | ✅     | `/c4:update "connect the API container to the Postgres container — reads/writes over SQL/TCP"`            | "connect the API container to the Postgres container — reads/writes over SQL/TCP"             |
| Change the technology label on a relationship     | ✅     | `/c4:update "change the API → Stripe relationship's technology to 'HTTPS/JSON'"`                          | "change the API → Stripe relationship's technology to 'HTTPS/JSON'"                           |
| Remove a relationship                             | ✅     | `/c4:update "remove the relationship between the Web App and Stripe"`                                     | "remove the relationship between the Web App and Stripe"                                      |

#### Views

| Use case                                                 | Status | Slash command                                                                                          | Or just say…                                                                                  |
|----------------------------------------------------------|:------:|--------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Add a system context / container / component diagram     | ✅     | `/c4:update "add a container view for the 'Checkout' system, keyed 'CheckoutContainers'"`                 | "add a container view for the 'Checkout' system, keyed 'CheckoutContainers'"                  |
| Add a deployment view for production                     | ✅     | `/c4:update "add a deployment view for the Production environment showing all containers"`                | "add a deployment view for the Production environment showing all containers"                 |
| Add a dynamic view showing the login flow                | ✅     | `/c4:update "add a dynamic view showing the login flow: browser → web → auth → db"`                       | "add a dynamic view showing the login flow: browser → web → auth → db"                        |
| Add a filtered view for the legacy lane only             | ✅     | `/c4:update "add a filtered view derived from 'Containers' that only shows elements tagged 'Legacy'"`     | "add a filtered view derived from 'Containers' that only shows elements tagged 'Legacy'"      |
| Change include/exclude expressions on a view             | ✅     | `/c4:update "exclude all relationships tagged 'Async' from the Containers view"`                          | "exclude all relationships tagged 'Async' from the Containers view"                           |

#### Deployment

| Use case                                      | Status | Slash command                                                                                          | Or just say…                                                                                  |
|-----------------------------------------------|:------:|--------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Add a production deployment environment       | ✅     | `/c4:update "add a 'Production' deployment environment with one deployment node for our EKS cluster"`     | "add a 'Production' deployment environment with one deployment node for our EKS cluster"      |
| Model the AWS topology with EKS, RDS, ALB     | ✅     | `/c4:update "model production on AWS: EKS for app containers, RDS for the database, ALB in front"`        | "model production on AWS: EKS for app containers, RDS for the database, ALB in front"         |

#### Styles

| Use case                               | Status | Slash command                                                                                          | Or just say…                                                                                  |
|----------------------------------------|:------:|--------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Make databases look like cylinders     | ✅     | `/c4:update "give every element tagged 'Data Store' a cylinder shape"`                                    | "give every element tagged 'Data Store' a cylinder shape"                                     |
| Apply the AWS theme                    | ✅     | `/c4:update "apply the AWS theme so deployment nodes use AWS icons"`                                      | "apply the AWS theme so deployment nodes use AWS icons"                                       |
| Change colours for the legacy lane     | ✅     | `/c4:update "style elements tagged 'Legacy' with a grey background and dashed border"`                    | "style elements tagged 'Legacy' with a grey background and dashed border"                     |

#### Documentation

| Use case                                             | Status | Slash command                                                                                          | Or just say…                                                                                  |
|------------------------------------------------------|:------:|--------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Add an ADR for choosing PostgreSQL                   | ✅     | `/c4:update "record an ADR 'Adopt PostgreSQL as the primary store' — accepted, with context, decision, consequences"` | "record an ADR 'Adopt PostgreSQL as the primary store' — accepted, with context, decision, consequences" |
| Add an architecture doc about the migration plan     | ✅     | `/c4:update "create a docs/005 page describing the migration plan from MySQL to PostgreSQL"`              | "create a docs/005 page describing the migration plan from MySQL to PostgreSQL"               |

#### Maintenance

| Use case                                   | Status | Slash command                                                                                          | Or just say…                                                                                  |
|--------------------------------------------|:------:|--------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Modernise my DSL to latest syntax          | ✅     | `/c4:update "audit workspace.dsl against the bundled Structurizr references and update any deprecated keywords"` | "audit workspace.dsl against the bundled Structurizr references and update any deprecated keywords" |
| Split my workspace into multiple files     | ✅     | `/c4:update "split workspace.dsl: move the model into model/*.dsl and views into views/*.dsl, wire them with !include"` | "split workspace.dsl: move the model into model/*.dsl and views into views/*.dsl, wire them with !include" |
| Refactor the model structure               | ✅     | `/c4:update "restructure: pull the auth concerns into their own software system called 'Identity'"`       | "restructure: pull the auth concerns into their own software system called 'Identity'"        |

#### Discovery

| Use case                                 | Status | Slash command                                                                                          | Or just say…                                                                                  |
|------------------------------------------|:------:|--------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Create a C4 model from this codebase     | ✅     | `/c4:update --discover "model this codebase as C4 — scan Dockerfiles, package.json, k8s/, and routes/"`   | "model this codebase as C4 — scan Dockerfiles, package.json, k8s/, and routes/"               |

### `/c4:validate` — quality gate

| Use case                             | Status | Slash command   | Or just say…                                                                                                                                                                                                                          |
|--------------------------------------|:------:|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Is my workspace.dsl valid?           | ✅     | `/c4:validate`     | "validate the workspace" — runs `structurizr/structurizr validate` in Docker.                                                                                                                                                          |
| Check conventions before merging     | ⚠️     | `/c4:validate`     | "check conventions before I merge" — DSL syntax/semantic rules (unique names, valid relationships) are enforced. **Project-level conventions** in `conventions/SKILL.md` (naming, ADR numbering, view keys) are advisory — applied by `update` while editing, not enforced by `validate`. |

### `/c4:export` — output

| Use case                              | Status | Slash command            | Or just say…                                                                                                                                                                                                |
|---------------------------------------|:------:|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Export as Mermaid for README          | ✅     | `/c4:export mermaid`     | "export the diagrams as Mermaid"                                                                                                                                                                             |
| Export as PlantUML for wiki           | ✅     | `/c4:export plantuml`    | "export to PlantUML for the wiki"                                                                                                                                                                            |
| Export workspace JSON for tooling     | ✅     | `/c4:export json`        | "give me the workspace JSON"                                                                                                                                                                                 |
| Generate a static HTML site           | ✅     | `/c4:export static`      | "build a static site for the architecture I can host on GitHub Pages" — produces `index.html` + `css/`, `js/`, `img/`, `workspace.js` under the output dir, ready to deploy.                                  |
| Render as PNG or SVG                  | ❌     | _not supported_          | The open-source Structurizr build rejects `-f png` and `-f svg` ("not supported in this build"). Workarounds: (a) `/c4:preview` and use the UI's download button, (b) `/c4:export plantuml` then render with the [`plantuml/plantuml`](https://hub.docker.com/r/plantuml/plantuml) Docker image. |

### `/c4:preview` — local browser preview

| Use case                           | Status | Slash command       | Or just say…                                       |
|------------------------------------|:------:|---------------------|----------------------------------------------------|
| Start the local preview server     | ✅     | `/c4:preview`          | "preview the diagrams" / "start the local server"  |
| Stop the preview server            | ✅     | `/c4:preview stop`     | "stop the preview"                                 |

### Out of scope (handled conversationally — no skill needed)

| Use case                             | How Claude handles it                                                            |
|--------------------------------------|----------------------------------------------------------------------------------|
| Explain the current architecture     | Reads `workspace.dsl` and walks through it in plain English.                     |
| What changed since last commit?      | Runs `git diff workspace.dsl` and summarises.                                    |
| Compare two versions                 | Reads both versions and reasons about the delta.                                 |

## Examples

Two end-to-end workspaces live in [`examples/`](./examples):

- **[simple-web-app](./examples/simple-web-app)** — one system, three containers, two views. The smallest viable C4 model.
- **[microservices](./examples/microservices)** — multi-container system, event bus, two external systems, full production deployment view.

Render either example via `scripts/preview-start.sh` from inside its directory.

## Workspace layout

`/c4:init` creates one of two layouts depending on whether the cwd is empty:

**Standalone** (empty cwd or you say "new repo"):

```
.
├── workspace.dsl
├── README.md
├── .gitignore
├── adrs/
│   └── 0001-use-c4-model-with-structurizr.md
├── docs/
│   ├── 0001-system-overview.md
│   ├── 0002-actors.md
│   └── 0003-use-cases.md
└── bin/local/run.sh        # convenience preview launcher
```

**Embedded** (existing project):

```
architecture/
├── workspace.dsl
├── README.md
├── .gitignore
├── adrs/
├── docs/
└── bin/local/run.sh        # convenience preview launcher
```

`/c4:init` will **never** run `git init` and will **never** commit. You decide when to version-control the result.

## Troubleshooting

| Symptom                                                                | Cause / fix                                                                                       |
|------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| `error: docker is not installed`                                       | Install Docker Desktop or the Engine. Required for `/c4:validate`, `/c4:export`, `/c4:preview` only.       |
| `error: docker daemon is not running`                                  | Start Docker. On macOS, open Docker Desktop.                                                      |
| Port 8080 already in use                                               | `C4_PREVIEW_PORT=8081 /c4:preview` (or run `scripts/preview-stop.sh` to remove a stale container).      |
| Validation says "Software with name ... already exists"                | Two `softwareSystem`s share a name. Names must be unique — see `references/basics.md`.            |
| Container view is empty                                                | Add `include *` (or specific identifiers) inside the view block. See `references/views.md`.       |
| `/c4:update` keeps failing validation                                     | The skill self-corrects up to 3 attempts. Beyond that, run `/c4:validate` to see the raw error.       |

## How it works

`/c4:update` doesn't memorise the Structurizr grammar — it reads from the bundled `references/` directory on demand:

```
references/
├── basics.md                 # DSL rules, identifiers, workspace, includes
├── model-elements.md         # person, softwareSystem, container, component, archetypes
├── relationships.md          # ->, implied relationships, archetypes
├── views.md                  # all view types + include/exclude/autoLayout
├── expressions.md            # element / relationship expressions
├── styles-and-themes.md      # element/relationship styles, light/dark, themes
├── deployment.md             # deploymentEnvironment, nodes, instances
└── adrs-and-docs.md          # !docs, !adrs, Nygard template, doc structure
```

The references are curated from the upstream [`structurizr/structurizr.github.io`](https://github.com/structurizr/structurizr.github.io) repository. Each file ends with a `# Source` footer pointing to the upstream URL and the date the content was pulled. Run `scripts/update-references.sh` to print a diff against the latest upstream.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for repo layout, local development, testing instructions, and the style guide.

## License

[MIT](./LICENSE).
