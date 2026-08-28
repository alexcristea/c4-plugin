#!/usr/bin/env python3
"""Build per-skill trigger eval sets from one shared query pool.

Why a shared pool: scripts/run_eval.py tests a single skill in isolation, so it
cannot see that two sibling descriptions both match "show me the diagrams". By
drawing each skill's negatives from its siblings' positives, optimising one
description can no longer silently poach a sibling's queries -- the boundary is
scored explicitly.

Usage: python3 evals/build_trigger_evals.py
Writes evals/trigger-<skill>.json (20 queries each: 10 positive, 10 negative).
"""

import json
import pathlib

POSITIVES = {
    "structurize": [
        "just made a new repo for our platform architecture docs, totally empty right now. can you set up whatever c4 needs so i can start writing the model",
        "we've got a fairly big django monorepo at ~/work/atlas and zero architecture documentation. i want to start keeping c4 diagrams and ADRs in the repo without cluttering the root",
        "scaffold the architecture docs for this project please",
        "my team lead wants us to start doing the c4 model thing and i have no idea where the files go. can you lay it out",
        "set up structurizr in here with the adr and docs folders",
        "starting a new architecture repo from scratch for the payments platform. need workspace.dsl plus somewhere to put decision records",
        "i want to add a c4 model to this go service but keep it in its own subdirectory so it doesn't get in the way of the source",
        "can you bootstrap the c4 workspace, i'll fill in the actual systems after",
        "new project, no docs yet. give me the skeleton for structurizr dsl + adrs + a way to preview locally",
        "add architecture documentation to this repo - the c4 setup with the dsl file and adr templates",
    ],
    "update": [
        "add a redis cache in front of the catalog service, the api reads from it",
        "i forgot the notification worker - it's a python service that consumes from kafka and calls sendgrid. add it to the model",
        "record an adr about why we picked postgres over dynamodb for the orders store, we already agreed on it",
        "there's a new server i missed: tag-server, it's the express + nuxt thing behind tag.example.io",
        "can you make external systems show up grey and dashed in the diagrams",
        "model this codebase as c4 - have a look at the Dockerfiles, the k8s manifests and the routes and figure out what the containers are",
        "add a deployment view for production, we run on EKS with RDS behind an ALB",
        "the api doesn't talk to stripe directly anymore, it goes through the payments service now. fix the relationships",
        "supersede adr 0003, we're moving to CQRS for the orders service",
        "rename the 'API' container to 'Public API' and drop the legacy worker, we killed it last sprint",
    ],
    "validate": [
        "i hand-edited workspace.dsl in vim and i'm not sure i closed all the braces. can you check it",
        "is the workspace valid?",
        "run the structurizr validation before i push this",
        "check the dsl for errors please",
        "lint the architecture model",
        "someone on the team edited architecture/workspace.dsl in a PR, can you verify it actually parses before i approve it",
        "quality gate check on the c4 model before merging",
        "does workspace.dsl still compile after that merge conflict resolution",
        "i merged main into my branch and the dsl file had conflicts. verify nothing's broken",
        "just double check the workspace file is syntactically fine, i didn't change anything through you",
    ],
    "export": [
        "we're moving the arch docs into the team wiki which only renders mermaid, can you get me the container diagram out of architecture/workspace.dsl in a format i can paste in",
        "give me plantuml for the system context diagram, it's going in confluence",
        "i need the workspace as json so i can feed it into a script",
        "build a static site for the architecture that i can host on github pages",
        "export the diagrams",
        "can i get svg versions of these diagrams for the slide deck on thursday",
        "generate mermaid for the README so it renders on github",
        "our docs pipeline consumes plantuml files, dump them into build/ for me",
        "i want to deploy the architecture docs to cloudflare pages, what do i need to produce",
        "get the theme json out of the workspace so i can reuse the styles in another model",
    ],
    "preview": [
        "open the diagrams so i can look at them",
        "start the local structurizr server",
        "i want to see the container view rendered, not the dsl",
        "preview",
        "can you render this in a browser, i'm trying to eyeball whether the layout makes any sense",
        "spin up the preview on a different port, 8080 is taken by my dev server",
        "stop the preview",
        "shut down that structurizr container",
        "let me see what this looks like while i'm editing - something that refreshes when i save",
        "fire up the local viewer for the architecture model",
    ],
    "conventions": [
        "what naming style should i use for identifiers vs names in the dsl",
        "i'm about to hand-write a bunch of containers in workspace.dsl, what are our rules for the description and technology fields",
        "how should i number a new adr in adrs/",
        "am i supposed to mark external systems somehow in our model",
        "writing docs/0004-migration-plan.md - what's the house style for these",
        "should relationship descriptions be present tense or past tense in our dsl",
        "do i need explicit view keys or can structurizr just generate them",
        "remind me what our c4 conventions are before i start editing this dsl",
        "i'm adding an adr that replaces 0002, what's the correct way to mark the old one",
        "does my workspace.dsl follow the project style rules",
    ],
}

# Near-misses from outside the plugin: adjacent domains, conceptual questions,
# and debugging that merely mentions the same tools. Deliberately not obviously
# irrelevant -- an easy negative like "write a fibonacci function" tests nothing.
DISTRACTORS = [
    "draw me a sequence diagram of the oauth handshake in figjam",
    "our terraform is a mess, can you refactor the eks module so the node groups aren't duplicated",
    "write a README section explaining in prose how the services talk to each other",
    "generate an ER diagram from the prisma schema in packages/db",
    "what's the actual difference between a container and a component in the c4 model? never been clear on it",
    "docker compose up isn't working, the structurizr container exits immediately with code 1",
    "summarise what changed in the architecture since last release from the git log",
    "our confluence space is a mess, help me reorganise the engineering docs tree",
]

# How many negatives to draw from each sibling. Weighted towards the pairs most
# at risk of overlapping: export/preview both surface diagrams, structurize and
# update both "add C4", validate and update both touch a workspace being changed.
NEGATIVE_MIX = {
    "structurize": {"update": 3, "conventions": 2, "validate": 1},
    "update":      {"structurize": 3, "validate": 2, "conventions": 2},
    "validate":    {"update": 3, "conventions": 2, "export": 1},
    "export":      {"preview": 4, "update": 1, "validate": 1},
    "preview":     {"export": 4, "validate": 1, "update": 1},
    "conventions": {"update": 3, "structurize": 2, "validate": 1},
}

TARGET = 20


def build(skill: str) -> list[dict]:
    items = [{"query": q, "should_trigger": True} for q in POSITIVES[skill]]

    negatives: list[str] = []
    for sibling, count in NEGATIVE_MIX[skill].items():
        negatives.extend(POSITIVES[sibling][:count])
    # Top up with out-of-domain near-misses, rotating the start so the six sets
    # don't all lean on the same handful.
    offset = sorted(POSITIVES).index(skill)
    need = TARGET - len(items) - len(negatives)
    for i in range(need):
        negatives.append(DISTRACTORS[(offset + i) % len(DISTRACTORS)])

    items.extend({"query": q, "should_trigger": False} for q in negatives)
    return items


def main() -> None:
    out_dir = pathlib.Path(__file__).parent
    for skill in POSITIVES:
        items = build(skill)
        pos = sum(1 for i in items if i["should_trigger"])
        assert len(items) == TARGET, f"{skill}: {len(items)} queries, expected {TARGET}"
        assert len({i["query"] for i in items}) == TARGET, f"{skill}: duplicate queries"
        path = out_dir / f"trigger-{skill}.json"
        path.write_text(json.dumps(items, indent=2) + "\n")
        print(f"{path.name}: {pos} positive, {TARGET - pos} negative")


if __name__ == "__main__":
    main()
