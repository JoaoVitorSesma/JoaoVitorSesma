"""Checks every generated asset and the READMEs that show them.

Run: python -m unittest discover -s scripts
"""
import re
import unittest

import build_assets as assets
from svgkit import MIN_PX, smallest

READMES = {"en": assets.ROOT / "README.md", "pt": assets.ROOT / "README.pt-BR.md"}


def _title(svg):
    found = re.search(r"<title[^>]*>([^<]*)</title>", svg)
    return found[1].strip() if found else ""


class GeneratedAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Build everything once, in the same order and with the same code as main().
        cls.built = {}
        for path, build in assets.outputs():
            svg = build()
            cls.built[path.relative_to(assets.ROOT).as_posix()] = (svg, smallest())
        cls.refs = {lang: set(re.findall(r'(?:srcset|src)="\./(assets/[^"]+)"', path.read_text(encoding="utf-8")))
                    for lang, path in READMES.items()}

    def test_every_output_is_a_distinct_file(self):
        paths = [path for path, _ in assets.outputs()]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(len(paths), len(self.built))

    def test_text_is_never_smaller_than_the_minimum(self):
        for name, (_, (size, sample)) in self.built.items():
            if size is not None:
                with self.subTest(name):
                    self.assertGreaterEqual(size, MIN_PX - 0.01, f"{sample!r} renders at {size:.1f}px")

    def test_animations_stop_under_reduced_motion(self):
        for name, (svg, _) in self.built.items():
            if re.search(r"animation:(?!none)", svg):
                with self.subTest(name):
                    self.assertIn("@media (prefers-reduced-motion:reduce)", svg)

    def test_every_asset_has_an_accessible_name(self):
        for name, (svg, _) in self.built.items():
            with self.subTest(name):
                self.assertTrue(_title(svg), "missing or empty <title>")
                if 'aria-labelledby="t d"' in svg:
                    self.assertRegex(svg, r'<desc id="d">[^<]+</desc>')

    def test_portuguese_variants_are_not_left_in_english(self):
        pairs = [(name, name.replace("-pt-", "-en-")) for name in self.built if "-pt-" in name]
        self.assertTrue(pairs)
        for pt, en in pairs:
            with self.subTest(pt):
                self.assertIn(en, self.built)
                self.assertNotEqual(_title(self.built[pt][0]), _title(self.built[en][0]))

    def test_readmes_only_show_assets_that_exist(self):
        for lang, refs in self.refs.items():
            for ref in refs:
                with self.subTest(readme=lang, ref=ref):
                    self.assertTrue((assets.ROOT / ref).is_file())

    def test_every_generated_asset_is_shown_somewhere(self):
        shown = set().union(*self.refs.values())
        for name in self.built:
            with self.subTest(name):
                self.assertIn(name, shown)

    def test_project_stacks_are_in_the_toolbox(self):
        # The line under each project card lists its stack before the links; every
        # tool there must also be in that language's Toolbox panel.
        for lang, path in READMES.items():
            toolbox = {tool for _, tools in assets.STR[lang]["toolbox"] for tool in tools}
            lines = [line for line in path.read_text(encoding="utf-8").splitlines()
                     if line.startswith("Python · ") and "](" in line]
            self.assertEqual(len(lines), 3, f"expected three project stack lines in {path.name}")
            for line in lines:
                for tool in line.split("[", 1)[0].split(" · "):
                    if tool.strip():
                        with self.subTest(readme=lang, tool=tool):
                            self.assertIn(tool.strip(), toolbox)

    def test_each_readme_shows_its_own_language(self):
        # The language buttons are the one place a README shows the other language.
        for lang, other in (("en", "pt"), ("pt", "en")):
            for ref in self.refs[lang]:
                if not ref.startswith("assets/lang/"):
                    with self.subTest(readme=lang, ref=ref):
                        self.assertNotIn(f"-{other}-", ref)


if __name__ == "__main__":
    unittest.main()
