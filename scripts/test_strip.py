"""Regression checks for the README mascot. Run: python -m unittest discover -s scripts."""
import unittest
import re

import build_assets as assets
import creatures


class HedgehogStripTests(unittest.TestCase):
    def test_four_short_steps(self):
        hedgehog = creatures.CREATURES['hedgehog']
        self.assertEqual(len(hedgehog['roll']['walk']), 4)
        self.assertEqual(hedgehog['step'], .11)
        _, frames, width, height = creatures.get('hedgehog')
        self.assertEqual((width, height), (27, 20))
        self.assertEqual(len({tuple(frames[i]) for i in hedgehog['roll']['walk']}), 4)
        for i in hedgehog['roll']['walk']:
            self.assertEqual(frames[i][:17], frames[0][:17])
            self.assertGreaterEqual(sum(row.count('f') for row in frames[i]), 4)

    def test_front_contact_precedes_body_center(self):
        # Front paw at x=16..18 reaches this cell while the body centre is x=13.5.
        tracks = [(0, 1, 16, 17, 2)]
        self.assertEqual(assets._cell_contacts(18, 2, tracks), [(0, 1)])
        self.assertEqual(assets._cell_contacts(10, 2, tracks), [])

    def test_return_and_separate_contacts(self):
        tracks = [(0, 1, 20, 10, 2), (2, 3, 10, 20, 2)]
        intervals = assets._cell_contacts(16, 2, tracks)
        self.assertAlmostEqual(intervals[0][0], .3)
        self.assertAlmostEqual(intervals[0][1], .7)
        self.assertAlmostEqual(intervals[1][0], 2.3)
        self.assertAlmostEqual(intervals[1][1], 2.7)

    def test_only_grounded_paws_make_tracks(self):
        _, frames, _, _ = creatures.get('hedgehog')
        roll = creatures.CREATURES['hedgehog']['roll']
        spans = {'walk': [(0, .88)]}
        tracks = assets._contact_tracks(frames, roll, .22, 3, [(0, 0), (.88, 12)], spans, [(0, 1)])
        first = [track for track in tracks if track[0] == 0]
        self.assertEqual([track[2] for track in first], [21, 45])
        # Raised rear paw at x=11 is excluded, although its shadow is visible.
        self.assertFalse(any(track[2] == 33 for track in first))
        reverse = assets._contact_tracks(frames, roll, .22, 3, [(0, 12), (.88, 0)], spans, [(0, -1)])
        for right, left in zip(tracks, reverse):
            self.assertAlmostEqual(right[2] + left[2] + right[4], 93)

    def test_dark_spine_rim_keeps_face_and_eye(self):
        _, light, _, _ = creatures.get('hedgehog', 'light')
        _, dark, _, _ = creatures.get('hedgehog', 'dark')
        self.assertNotEqual(light[0][:8], dark[0][:8])
        self.assertEqual([row[15:] for row in light[0][8:]], [row[15:] for row in dark[0][8:]])
        self.assertEqual(light[0][10][20:22], 'oo')

    def test_dark_nose_is_visible_without_changing_shape(self):
        light_palette, light, _, _ = creatures.get('hedgehog', 'light')
        dark_palette, dark, _, _ = creatures.get('hedgehog', 'dark')
        self.assertEqual(light_palette['n'], light_palette['o'])
        self.assertEqual(light_palette['h'], light_palette['o'])
        self.assertNotEqual(dark_palette['h'], dark_palette['n'])
        self.assertNotEqual(dark_palette['n'], dark_palette['o'])
        for index in range(6):
            nose = [(x, y) for y, row in enumerate(light[index]) for x, ch in enumerate(row) if ch in 'nh']
            self.assertGreaterEqual(len(nose), 2)
            self.assertTrue(all(dark[index][y][x] == light[index][y][x] for x, y in nose))
            self.assertEqual(sum(row.count('h') for row in dark[index]), 1)
        self.assertFalse(any(ch in 'nh' for row in light[6] for ch in row))
        self.assertEqual(creatures.CREATURES['hedgehog']['palette']['n'], '#0b1024')

    def test_short_paws_remain_attached_to_belly(self):
        _, frames, width, height = creatures.get('hedgehog')
        for frame in frames[:4]:
            seen, pending = {(12, 16)}, [(12, 16)]
            while pending:
                x, y = pending.pop()
                for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen and frame[ny][nx] in 'Yyf':
                        seen.add((nx, ny))
                        pending.append((nx, ny))
            for y in range(17, 20):
                for x, ch in enumerate(frame[y]):
                    if ch in 'Yyf':
                        self.assertIn((x, y), seen)

    def test_all_variants_and_optional_mascots_render(self):
        for theme in assets.THEMES:
            for mobile in (False, True):
                svg = assets.strip(theme, mobile)
                gait = float(re.search(r'animation:wf3 ([\d.]+)s', svg)[1])
                self.assertAlmostEqual(gait, .44, delta=.002)
                self.assertIn('prefers-reduced-motion', svg)
                self.assertIn('y="68" width="10"', svg)
                period = float(re.search(r'animation:walk ([\d.]+)s', svg)[1])
                self.assertAlmostEqual(period / gait, round(period / gait), delta=.002)
            for mascot in creatures.CREATURES:
                self.assertIn('<svg', assets.strip(theme, False, mascot))

    def test_original_crossing_time(self):
        for mobile, expected in ((False, 20), (True, 14)):
            svg = assets.strip('light', mobile)
            period = float(re.search(r'animation:walk ([\d.]+)s', svg)[1])
            keyframes = re.search(r'@keyframes walk\{(.*?)\}\.flip', svg)[1]
            stops = [(float(t) * period / 100, float(x)) for t, x in
                     re.findall(r'([\d.]+)%\{transform:translate\(([\d.]+)px', keyframes)]
            travel = (720 if mobile else 1200) - 81
            crossings = [b-a for (a, xa), (b, xb) in zip(stops, stops[1:]) if abs(xb-xa) == travel]
            self.assertEqual(len(crossings), 2)
            for duration in crossings:
                self.assertAlmostEqual(duration, expected, delta=.002)

    def test_roll_keeps_square_bounds_on_floor(self):
        hedgehog = creatures.CREATURES['hedgehog']
        frame = hedgehog['frames'][hedgehog['roll']['ball']]
        points = [(x, y) for y, row in enumerate(frame) for x, ch in enumerate(row) if ch != '.']
        self.assertEqual(max(x for x, _ in points) - min(x for x, _ in points),
                         max(y for _, y in points) - min(y for _, y in points))
        self.assertEqual(max(y for _, y in points), 19)


if __name__ == '__main__':
    unittest.main()
