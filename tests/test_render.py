"""Basic tests; run: python -m unittest discover -s tests -v"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from render_diagram import render  # noqa: E402


class CollisionSketchTests(unittest.TestCase):
    def setUp(self):
        self.scene = json.loads((ROOT / 'examples' / 'fictional_parking_lot.json').read_text())

    def test_render_svg_and_evidence_notes(self):
        svg = render(self.scene)
        self.assertTrue(svg.startswith('<svg'))
        self.assertIn('Not to scale', svg)
        self.assertIn('DOOR OPEN', svg)
        self.assertIn('Fictional example', svg)
        self.assertIn('marker-end="url(#arrowhead)"', svg)

    def test_escape_untrusted_labels(self):
        self.scene['vehicles'][0]['label'] = '<script>alert(1)</script>'
        svg = render(self.scene)
        self.assertNotIn('<script>', svg)
        self.assertIn('&lt;script&gt;', svg)

    def test_reject_unsupported_door_side(self):
        self.scene['vehicles'][1]['door']['side'] = 'maybe'
        with self.assertRaises(ValueError):
            render(self.scene)


if __name__ == '__main__':
    unittest.main()