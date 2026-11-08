"""Regression checks for the README mascot. Run: python -m unittest discover -s scripts."""
import unittest
import re

import build_assets as assets
import hedgehog


class HedgehogStripTests(unittest.TestCase):
    def test_four_short_steps(self):
        self.assertEqual(len(hedgehog.ROLL['walk']), 4)
        self.assertEqual(hedgehog.STEP, .11)
        frames = hedgehog.FRAMES
        self.assertEqual((hedgehog.W, hedgehog.H), (27, 20))
        self.assertEqual(len({tuple(frames[i]) for i in hedgehog.ROLL['walk']}), 4)
        for i in hedgehog.ROLL['walk']:
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
        frames, roll = hedgehog.FRAMES, hedgehog.ROLL
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
        light_palette, dark_palette = hedgehog.palette('light'), hedgehog.palette('dark')
        light = hedgehog.FRAMES
        self.assertEqual(light_palette['r'], light_palette['o'])
        self.assertNotEqual(dark_palette['r'], dark_palette['o'])
        self.assertEqual(light_palette['q'], dark_palette['q'])
        self.assertEqual(dark_palette['q'], dark_palette['o'])
        self.assertTrue(all(any('q' in row for row in frame) for frame in light))
        self.assertEqual(light[0][10][20:22], 'oo')

    def test_dark_nose_is_visible_without_changing_shape(self):
        light_palette, dark_palette = hedgehog.palette('light'), hedgehog.palette('dark')
        light = dark = hedgehog.FRAMES
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
        self.assertEqual(hedgehog.PALETTE['n'], '#0b1024')

    def test_short_paws_remain_attached_to_belly(self):
        frames, width, height = hedgehog.FRAMES, hedgehog.W, hedgehog.H
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

    def test_all_variants_render(self):
        for theme in assets.THEMES:
            for mobile in (False, True):
                svg = assets.strip(theme, mobile)
                gait = float(re.search(r'animation:wf3 ([\d.]+)s', svg)[1])
                self.assertAlmostEqual(gait, .44, delta=.002)
                self.assertIn('prefers-reduced-motion', svg)
                self.assertIn('y="68" width="10"', svg)
                period = float(re.search(r'animation:walk ([\d.]+)s', svg)[1])
                self.assertAlmostEqual(period / gait, round(period / gait), delta=.002)

    def test_walking_speed_is_preserved_while_stopping_at_edges(self):
        for mobile, expected in ((False, 20), (True, 14)):
            travel = (720 if mobile else 1200) - 81
            _, stops, spans, _ = assets._motion(travel, expected)
            for (a, xa), (b, xb) in zip(stops, stops[1:]):
                if any(lo <= (a+b)/2 < hi for lo, hi in spans['walk']):
                    self.assertAlmostEqual(abs(xb-xa)/(b-a), travel/expected)

    def test_both_collision_types_recover_before_turning_and_loop_continuously(self):
        period, stops, spans, trips = assets._motion(1119, 20)
        self.assertEqual(len(spans['walk_impact']), 1)
        self.assertEqual(len(spans['ball_impact']), 1)
        self.assertEqual(len(spans['shake']), 2)
        self.assertAlmostEqual(stops[0][1], stops[-1][1])
        self.assertEqual(stops[-1][0], period)
        for a, b in spans['shake']:
            self.assertAlmostEqual(b-a, .75)
            self.assertFalse(any(a < turn < b for turn, _ in trips))

    def test_each_edge_alternates_bumping_and_quietly_turning(self):
        trips = assets.TRIPS
        for direction in (+1, -1):
            self.assertEqual(sorted(b for d, _, b in trips if d == direction), [False, True])
        for rolls in (True, False):
            self.assertEqual(sorted(b for _, r, b in trips if r == rolls), [False, True])
        period, stops, spans, starts = assets._motion(1119, 20, 12)
        # Quiet turns stay on the edge: no impact, no recoil, no head shake.
        self.assertEqual(len(starts), 4)
        self.assertEqual(len(spans['blink']), 4)
        self.assertEqual(len(spans['ball_slow']), 1)

    def test_rolling_turn_brakes_before_resting_at_the_edge(self):
        period, stops, spans, _ = assets._motion(1119, 20, 12)
        speed = lambda a, b: abs(dict(stops)[b] - dict(stops)[a]) / (b - a)
        (fa, fb), = [s for s in spans['ball'] if s[1] == spans['ball_slow'][0][0]]
        sa, sb = spans['ball_slow'][0]
        self.assertAlmostEqual(speed(fa, fb) / speed(sa, sb), 3)
        self.assertEqual(dict(stops)[sb], 0.0)
        self.assertIn(sb, [a for a, _ in spans['ball_rest']])

    def test_every_scripted_phase_has_exactly_one_pose(self):
        _, _, spans, _ = assets._motion(1119, 20, 12)
        for phase in spans:
            self.assertEqual(sum(phase in pose.phases for pose in assets.POSES), 1)
        self.assertEqual([pose.cls for pose in assets.POSES if pose.shown], ['gw'])
        with self.assertRaises(ValueError):
            assets._pose('sniff')

    def test_edges_have_no_visible_bars(self):
        for theme in assets.THEMES:
            for mobile in (False, True):
                self.assertNotIn('<path', assets.strip(theme, mobile))

    def test_airborne_rebound_does_not_light_cells(self):
        tracks = assets._contact_tracks(hedgehog.FRAMES, hedgehog.ROLL, .11, 3,
                                       [(0, 1119), (.7, 1029)],
                                       {'ball_recoil': [(0, .7)]}, [(0, 1)])
        self.assertEqual(tracks, [])

    def test_recovery_keeps_original_side_profile_and_planted_feet(self):
        frames = hedgehog.FRAMES
        poses = hedgehog.recovery()
        self.assertEqual(poses['blink'][17:], frames[0][17:])
        self.assertEqual(poses['blink'][10][25:27], frames[0][10][25:27])
        for frame in poses.values():
            self.assertEqual(sum(row.count('h') for row in frame), 1)

    def test_roll_keeps_square_bounds_on_floor(self):
        frame = hedgehog.FRAMES[hedgehog.ROLL['ball']]
        points = [(x, y) for y, row in enumerate(frame) for x, ch in enumerate(row) if ch != '.']
        self.assertEqual(max(x for x, _ in points) - min(x for x, _ in points),
                         max(y for _, y in points) - min(y for _, y in points))
        self.assertEqual(max(y for _, y in points), 19)


if __name__ == '__main__':
    unittest.main()
