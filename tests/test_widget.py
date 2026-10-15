"""Unit tests for the non-GUI logic in src/widget.py.

Run with:  py -m unittest discover -s tests -v
"""
import json, sys, tempfile, unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import widget  # noqa: E402


class SanitizeConfigTests(unittest.TestCase):
    def test_non_dict_returns_defaults(self):
        for raw in (None, [], 'x', 42, True):
            self.assertEqual(widget.sanitize_cfg(raw), widget.DEFAULT)

    def test_valid_values_are_kept(self):
        raw = {'x': 10, 'y': 20, 'width': 300, 'height': 50, 'opacity': 0.5,
               'unit': 'Mbps', 'interface': 'Wi-Fi', 'interval_ms': 1000,
               'font_color': '#ABCDEF', 'font_weight': 'bold', 'font_size': 11,
               'background': '#000000', 'border': '#111111', 'autostart': False,
               'first_run_complete': True, 'topmost_refresh_ms': 2000}
        self.assertEqual(widget.sanitize_cfg(raw), raw)

    def test_unknown_keys_are_dropped(self):
        c = widget.sanitize_cfg({'evil': '__import__("os")', 'unit': 'Kbps'})
        self.assertNotIn('evil', c)
        self.assertEqual(c['unit'], 'Kbps')

    def test_wrong_types_fall_back_to_defaults(self):
        c = widget.sanitize_cfg({'width': '300', 'opacity': 'high', 'autostart': 'yes',
                                 'font_size': True, 'interface': 7, 'x': [1]})
        for k in ('width', 'opacity', 'autostart', 'font_size', 'interface', 'x'):
            self.assertEqual(c[k], widget.DEFAULT[k], k)

    def test_non_finite_numbers_are_rejected(self):
        c = widget.sanitize_cfg({'width': float('inf'), 'opacity': float('nan'),
                                 'interval_ms': float('-inf')})
        self.assertEqual(c['width'], widget.DEFAULT['width'])
        self.assertEqual(c['opacity'], widget.DEFAULT['opacity'])
        self.assertEqual(c['interval_ms'], widget.DEFAULT['interval_ms'])

    def test_ranges_are_clamped(self):
        c = widget.sanitize_cfg({'width': 10**9, 'height': -5, 'interval_ms': 1,
                                 'topmost_refresh_ms': 0, 'opacity': 0.0, 'font_size': 999})
        self.assertEqual((c['width'], c['height']), (2000, 30))
        self.assertEqual(c['interval_ms'], 200)
        self.assertEqual(c['topmost_refresh_ms'], 500)
        self.assertEqual(c['opacity'], 0.2)
        self.assertEqual(c['font_size'], 32)

    def test_colors_must_be_hex(self):
        for bad in ('red', '#12345', '#1234567', '#GGGGGG', '#123456\n', '[exec x]'):
            self.assertEqual(widget.sanitize_cfg({'font_color': bad})['font_color'],
                             widget.DEFAULT['font_color'], bad)

    def test_enums_must_match(self):
        c = widget.sanitize_cfg({'unit': 'TBps', 'font_weight': 'heavy'})
        self.assertEqual(c['unit'], widget.DEFAULT['unit'])
        self.assertEqual(c['font_weight'], widget.DEFAULT['font_weight'])

    def test_overlong_interface_name_rejected(self):
        self.assertEqual(widget.sanitize_cfg({'interface': 'a' * 1000})['interface'], 'All')


class ConfigFileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name) / 'cfg'
        self.patches = [mock.patch.object(widget, 'CFG_DIR', d),
                        mock.patch.object(widget, 'CFG_FILE', d / 'settings.json')]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def test_missing_file_gives_defaults(self):
        self.assertEqual(widget.load_cfg(), widget.DEFAULT)

    def test_round_trip_and_no_temp_file_left(self):
        c = dict(widget.DEFAULT, unit='Mbps', x=5, y=6)
        self.assertTrue(widget.save_cfg(c))
        self.assertEqual(widget.load_cfg(), c)
        self.assertEqual([p.name for p in widget.CFG_DIR.iterdir()], ['settings.json'])

    def test_corrupt_json_gives_defaults(self):
        widget.CFG_DIR.mkdir(parents=True)
        for text in ('{not json', '[' * 50000, '\x00\xff'):
            widget.CFG_FILE.write_text(text, encoding='utf-8', errors='ignore')
            self.assertEqual(widget.load_cfg(), widget.DEFAULT)

    def test_oversized_file_is_ignored(self):
        widget.CFG_DIR.mkdir(parents=True)
        widget.CFG_FILE.write_text(json.dumps({'unit': 'Mbps', 'pad': 'x' * widget.MAX_CFG_BYTES}),
                                   encoding='utf-8')
        self.assertEqual(widget.load_cfg(), widget.DEFAULT)


class FormatAndStartupTests(unittest.TestCase):
    def test_fmt_speed(self):
        self.assertEqual(widget.fmt_speed(0, 'auto_bytes'), '0 B/s')
        self.assertEqual(widget.fmt_speed(1500, 'auto_bytes'), '1.50 KB/s')
        self.assertEqual(widget.fmt_speed(125000, 'auto_bits'), '1.00 Mbps')
        self.assertEqual(widget.fmt_speed(2e6, 'MBps'), '2.00 MB/s')
        self.assertEqual(widget.fmt_speed(1e3, 'Kbps'), '8.0 Kbps')

    def test_startup_command_is_quoted(self):
        cmd = widget.startup_command()
        self.assertTrue(cmd.startswith('"'), cmd)
        self.assertEqual(cmd.count('"') % 2, 0, cmd)

    def test_frozen_startup_command_is_single_quoted_path(self):
        with mock.patch.object(sys, 'frozen', True, create=True), \
             mock.patch.object(sys, 'executable', r'C:\Program Files\My App\app.exe'):
            self.assertEqual(widget.startup_command(), '"C:\\Program Files\\My App\\app.exe"')


if __name__ == '__main__':
    unittest.main()
