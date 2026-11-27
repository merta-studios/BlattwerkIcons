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
            'tabelle': '2', 'runde-kurven': '12', 'eckige-linien': '12',
            'kurven-und-linien': '12', 'objekt-hinzufuegen': '12',
            'sticker-hinzufuegen': '12', 'verschieben': '12', 'blitz': '32',
            'textfeld-stil': '1', 'rueckgaengig-dick': '2', 'vorgaengig-dick': '2',
            'dicken': '2', 'zoom-fenster': '12',
        }
        actual = {slug: code for _, items in generate.BETA_GROUPS for slug, _, _, code in items}
        self.assertEqual(actual, expected)
        self.assertEqual(generate.varianten(actual['tabelle']), ['schwarz', 'weiss'])
        self.assertEqual(generate.varianten(actual['blitz']), ['farbe', 'schwarz', 'weiss'])
        moved_beta = {item[0] for item in generate.GROUPS[17][1]}
        self.assertEqual(moved_beta, {
            'bild-zuschneiden', 'tabelle', 'rueckgaengig', 'vorgaengig', 'sperren', 'entsperren',
            'schriftart', 'text-links', 'text-mittig', 'text-rechts', 'textformat',
            'textzeilenabstand', 'stecknadel', 'bild', 'datei', 'ki-bild-playground',
            'dokument-scannen', 'kamera', 'importieren',
        })
        for slug, _, _, code in generate.GROUPS[17][1]:
            for variant in generate.varianten(code):
                self.assertTrue((ROOT / 'Normal/SVG/G18' / f'g18-{slug}-{variant}.svg').exists())
        self.assertEqual(generate.varianten('23'), ['farbe', 'schwarz', 'weiss'])
        # Die neuen Beta-Alternativen ersetzen keine bestehenden Normal-Geometrien.
        self.assertIn('duplizieren', {item[0] for item in generate.GROUPS[7][1]})
        self.assertIn('bild-zuschneiden', {item[0] for item in generate.GROUPS[7][1]})
        self.assertIn('verschieben', {item[0] for item in generate.GROUPS[16][1]})
        self.assertEqual(generate.bicon('dicken'), generate.icon('dicken'))
        self.assertEqual(generate.varianten(actual['dicken']), ['schwarz', 'weiss'])

    def test_dickere_verlaufspfeile_sind_sichtbar_staerker(self):
        for slug in ('rueckgaengig', 'vorgaengig'):
            thick_path = ROOT / 'Beta/PNG/256/B06' / f'b06-{slug}-dick-schwarz.png'
            thin_path = ROOT / 'Normal/PNG/256/G18' / f'g18-{slug}-schwarz.png'
            thick = Image.open(thick_path).convert('RGBA').getchannel('A')
            thin = Image.open(thin_path).convert('RGBA').getchannel('A')
            thick_coverage = sum(level * count for level, count in enumerate(thick.histogram()))
            thin_coverage = sum(level * count for level, count in enumerate(thin.histogram()))
            self.assertGreater(thick_coverage, thin_coverage, slug)

    def test_pluszeichen_bleiben_in_mono_sichtbar(self):
        for slug, x, y in (('objekt-hinzufuegen', 47, 46), ('sticker-hinzufuegen', 49, 48)):
            for variant in ('schwarz', 'weiss'):
                path = ROOT / 'Beta/PNG/256/B03' / f'b03-{slug}-{variant}.png'
                alpha = Image.open(path).convert('RGBA').getchannel('A')
                px, py = round(x * 4), round(y * 4)
                self.assertGreater(alpha.getpixel((px, py)), 240, f'{slug} {variant} plus missing')

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
