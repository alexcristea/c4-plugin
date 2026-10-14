#!/usr/bin/env python3
"""Tests for scripts/build-skill.py -- the plugin -> single-skill package build.

The built package must stand on its own: no ${CLAUDE_PLUGIN_ROOT}, no /c4:
slash commands, every bundled path it mentions present, and only frontmatter
keys every skill host accepts.

Usage: python3 tests/test_build_skill.py
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import shutil
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ["structurize", "update", "validate", "export", "preview", "conventions"]
# The keys claude.ai and the Skills API accept; anything else is rejected there.
PORTABLE_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
SKILL_DIR_REF = re.compile(r"\$\{CLAUDE_SKILL_DIR\}/([A-Za-z0-9_./*-]+)")


def load_builder():
    spec = importlib.util.spec_from_file_location("build_skill", REPO / "scripts" / "build-skill.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses look the module up by name
    spec.loader.exec_module(module)
    return module


builder = load_builder()


def frontmatter(text: str) -> str:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    return m.group(1) if m else ""


def top_level_keys(fm: str) -> set[str]:
    return set(re.findall(r"^([a-zA-Z_-]+):", fm, re.MULTILINE))


def grants(fm: str) -> set[str]:
    m = re.search(r"^allowed-tools:\s*(.+)$", fm, re.MULTILINE)
    return {g.strip() for g in re.split(r",\s*(?![^()]*\))", m.group(1))} if m else set()


class BuiltPackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = pathlib.Path(cls.tmp.name) / "c4"
        cls.stats = builder.build(REPO, cls.out)
        cls.skill_md = (cls.out / "SKILL.md").read_text()
        cls.fm = frontmatter(cls.skill_md)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def package_md_files(self):
        return sorted(self.out.rglob("*.md"))

    def test_root_frontmatter_uses_only_portable_keys(self):
        keys = top_level_keys(self.fm)
        self.assertTrue({"name", "description", "allowed-tools", "metadata"} <= keys, keys)
        self.assertTrue(keys <= PORTABLE_KEYS, keys - PORTABLE_KEYS)
        self.assertRegex(self.fm, r"(?m)^name: c4$")

    def test_description_fits_listing_limit(self):
        desc = re.search(r"^description:\s*(.+)$", self.fm, re.MULTILINE).group(1)
        self.assertLessEqual(len(desc), 1536)

    def test_version_stamped_from_plugin_manifest(self):
        version = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())["version"]
        self.assertRegex(self.fm, rf'(?m)^  version: "{re.escape(version)}"$')

    def test_grants_cover_every_source_skill(self):
        needed = set()
        for name in SKILLS:
            needed |= grants(frontmatter((REPO / "skills" / name / "SKILL.md").read_text()))
        self.assertEqual(needed - grants(self.fm), set())

    def test_every_workflow_present_and_stripped(self):
        for name in SKILLS:
            text = (self.out / "workflows" / f"{name}.md").read_text()
            with self.subTest(workflow=name):
                self.assertFalse(text.startswith("---"), "frontmatter not stripped")
                self.assertNotIn("## Choosing between", text)
                self.assertTrue(text.startswith(f"# {name}"), text[:40])

    def test_no_plugin_only_references_remain(self):
        for path in self.package_md_files():
            text = path.read_text()
            with self.subTest(file=str(path.relative_to(self.out))):
                self.assertNotIn("CLAUDE_PLUGIN_ROOT", text)
                self.assertNotRegex(text, r"/c4:\w")
                self.assertNotIn("`paths:` frontmatter", text)

    def test_router_carries_every_choosing_between_section(self):
        for name in SKILLS:
            source = (REPO / "skills" / name / "SKILL.md").read_text()
            for heading in re.findall(r"^## Choosing between .+$", source, re.MULTILINE):
                with self.subTest(heading=heading):
                    self.assertIn(heading, self.skill_md)
        self.assertNotIn("<!-- choosing-between -->", self.skill_md)

    def test_every_skill_dir_path_exists(self):
        for path in self.package_md_files():
            for ref in SKILL_DIR_REF.findall(path.read_text()):
                ref = ref.rstrip(".")
                with self.subTest(file=path.name, ref=ref):
                    self.assertTrue(list(self.out.glob(ref)) or (self.out / ref).exists(), ref)

    def test_scripts_invoked_through_bash(self):
        self.assertIn("Bash(bash:*)", grants(self.fm))
        for path in self.package_md_files():
            text = path.read_text()
            for m in re.finditer(r"\$\{CLAUDE_SKILL_DIR\}/scripts/[\w.-]+\.sh", text):
                with self.subTest(file=path.name, ref=m.group(0)):
                    self.assertTrue(text[:m.start()].endswith("bash "), m.group(0))

    def test_assets_copied(self):
        self.assertIn("{{PROJECT_NAME}}", (self.out / "templates/workspace/workspace.dsl").read_text())
        self.assertTrue((self.out / "templates/workspace/.gitignore").exists())
        self.assertTrue(list((self.out / "references").glob("*.md")))
        for script in ["validate-dsl.sh", "export-diagrams.sh", "preview-start.sh", "preview-stop.sh"]:
            self.assertTrue((self.out / "scripts" / script).exists(), script)
        self.assertFalse((self.out / "scripts/update-references.sh").exists())
        self.assertFalse((self.out / "references/.upstream-sha").exists())

    def test_router_source_not_shipped(self):
        # The router template lives under templates/ but is rendered to SKILL.md, not copied.
        self.assertEqual([self.out / "SKILL.md"], list(self.out.rglob("SKILL.md")))

    def test_stats_match_package(self):
        files = [p for p in self.out.rglob("*") if p.is_file()]
        self.assertEqual(self.stats.files, len(files))
        self.assertEqual(self.stats.bytes, sum(p.stat().st_size for p in files))

    def test_rebuild_replaces_stale_output(self):
        (self.out / "stale.txt").write_text("x")
        builder.build(REPO, self.out)
        self.assertFalse((self.out / "stale.txt").exists())


class BuildFailures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name) / "repo"
        shutil.copytree(REPO, self.repo, ignore=shutil.ignore_patterns(".git", "dist", "examples", "evals"))
        self.out = pathlib.Path(self.tmp.name) / "out"

    def tearDown(self):
        self.tmp.cleanup()

    def append(self, rel: str, text: str):
        path = self.repo / rel
        path.write_text(path.read_text() + text)

    def test_unrewritable_plugin_root_fails(self):
        self.append("skills/validate/SKILL.md", "\nRun $CLAUDE_PLUGIN_ROOT/scripts/x.sh\n")
        with self.assertRaisesRegex(builder.BuildError, "CLAUDE_PLUGIN_ROOT"):
            builder.build(self.repo, self.out)

    def test_missing_patch_target_fails(self):
        path = self.repo / "skills/conventions/SKILL.md"
        path.write_text(re.sub(r"The `paths:` frontmatter.*\n", "", path.read_text()))
        with self.assertRaisesRegex(builder.BuildError, "conventions"):
            builder.build(self.repo, self.out)

    def test_python_bytecode_cache_not_shipped(self):
        # Importing build-skill.py (as these tests do) writes scripts/__pycache__/.
        cache = self.repo / "scripts/__pycache__"
        cache.mkdir(exist_ok=True)
        (cache / "build-skill.cpython-312.pyc").write_bytes(b"\x00\xff\x00")
        builder.build(self.repo, self.out)
        self.assertFalse((self.out / "scripts/__pycache__").exists())

    def test_binary_asset_fails(self):
        (self.repo / "templates/workspace/logo.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\xff")
        with self.assertRaisesRegex(builder.BuildError, "logo.png"):
            builder.build(self.repo, self.out)

    def test_router_without_marker_fails(self):
        path = self.repo / "templates/skill/SKILL.md"
        path.write_text(path.read_text().replace("<!-- choosing-between -->", ""))
        with self.assertRaisesRegex(builder.BuildError, "choosing-between"):
            builder.build(self.repo, self.out)


if __name__ == "__main__":
    unittest.main()
