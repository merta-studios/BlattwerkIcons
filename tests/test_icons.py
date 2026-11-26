"""Regressionstests für Freigabe, Stern-Codes und generierte Beta-Assets.

Nach `python generate.py` ausführen: python -m unittest discover -s tests
"""
import json
from pathlib import Path
import unittest

from PIL import Image, ImageChops
import generate

ROOT = Path(__file__).resolve().parents[1]


class IconsTest(unittest.TestCase):
    def test_freigabe_und_beta_motive(self):
        promoted = {item[0] for item in generate.GROUPS[16][1]}
        self.assertEqual(promoted, {'duplizieren', 'verschieben', 'einklappen-pfeile',
                                    'ausklappen-pfeile', 'einklappen', 'ausklappen'})
        expected = {
            'bild-zuschneiden': '1', 'tabelle': '1', 'rueckgaengig': '2', 'vorgaengig': '2',
            'schriftart': '1', 'sperren': '1', 'entsperren': '1', 'text-links': '12',
            'text-mittig': '12', 'text-rechts': '12', 'textformat': '1',
            'textzeilenabstand': '1', 'stecknadel': '23', 'bild': '1', 'datei': '1',
            'ki-bild-playground': '1', 'dokument-scannen': '1', 'kamera': '1', 'importieren': '1',
        }
        actual = {slug: code for _, items in generate.BETA_GROUPS for slug, _, _, code in items}
        self.assertEqual(actual, expected)
        self.assertEqual(generate.varianten(actual['stecknadel']), ['farbe', 'schwarz', 'weiss'])
        # Die neue Alternative ersetzt keine bestehende Normal-Geometrie.
        self.assertIn('duplizieren', {item[0] for item in generate.GROUPS[7][1]})
        self.assertIn('bild-zuschneiden', {item[0] for item in generate.GROUPS[7][1]})

    def test_alle_beta_exporte(self):
        for number, (_, items) in enumerate(generate.BETA_GROUPS, 1):
            tag = f'B{number:02}'
            for slug, _, palette, code in items:
                if '1' in code:
                    self.assertEqual(palette, 'fern')
                for variant in generate.varianten(code):
                    key = f'{tag.lower()}-{slug}-{variant}'
                    with self.subTest(key=key):
                        self.assertTrue((ROOT / 'Beta/SVG' / tag / (key + '.svg')).exists())
                        for size in generate.GROESSEN:
                            im = Image.open(ROOT / 'Beta/PNG' / str(size) / tag / (key + '.png')).convert('RGBA')
                            self.assertEqual(im.size, (size, size))
                            self.assertIsNotNone(im.getchannel('A').getbbox())
                            self.assertEqual(im.getpixel((0, 0))[3], 0)
                            if size == 256:
                                alpha = im.getchannel('A')
                                for edge in (alpha.crop((0, 0, 256, 1)), alpha.crop((0, 255, 256, 256)),
                                             alpha.crop((0, 0, 1, 256)), alpha.crop((255, 0, 256, 256))):
                                    self.assertLessEqual(edge.getextrema()[1], 8)
                            if variant in ('schwarz', 'weiss'):
                                rgb = (0, 0, 0) if variant == 'schwarz' else (255, 255, 255)
                                self.assertTrue(all(pixel[:3] == rgb for _, pixel in im.getcolors(65536) if pixel[3]))
                        asset = ROOT / 'Beta/Blattwerk-Beta.xcassets' / (key + '.imageset')
                        data = json.loads((asset / 'Contents.json').read_text())
                        for image in data['images']:
                            self.assertTrue((asset / image['filename']).exists())
                if '2' in code:
                    for size in generate.GROESSEN:
                        directory = ROOT / 'Beta/PNG' / str(size) / tag
                        black = Image.open(directory / f'{tag.lower()}-{slug}-schwarz.png').getchannel('A')
                        white = Image.open(directory / f'{tag.lower()}-{slug}-weiss.png').getchannel('A')
                        self.assertIsNone(ImageChops.difference(black, white).getbbox())


if __name__ == '__main__':
    unittest.main()
