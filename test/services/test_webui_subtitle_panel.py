import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "webui"))

from subtitle_panel import get_option_index, get_value_index, parse_custom_position


class TestWebuiSubtitlePanel(unittest.TestCase):
    def test_get_option_index_returns_saved_value_or_default(self):
        options = [("Top", "top"), ("Center", "center"), ("Bottom", "bottom")]

        self.assertEqual(get_option_index(options, "center"), 1)
        self.assertEqual(get_option_index(options, "missing"), 0)
        self.assertEqual(get_option_index(options, "missing", default=2), 2)

    def test_get_value_index_returns_saved_value_or_default(self):
        values = ["a.ttf", "b.ttf"]

        self.assertEqual(get_value_index(values, "b.ttf"), 1)
        self.assertEqual(get_value_index(values, "missing"), 0)
        self.assertEqual(get_value_index(values, "missing", default=1), 1)

    def test_parse_custom_position_accepts_zero_to_one_hundred(self):
        self.assertEqual(parse_custom_position("0"), (0.0, None))
        self.assertEqual(parse_custom_position("70.5"), (70.5, None))
        self.assertEqual(parse_custom_position("100"), (100.0, None))

    def test_parse_custom_position_rejects_invalid_values(self):
        self.assertEqual(
            parse_custom_position("-1"),
            (None, "Please enter a value between 0 and 100"),
        )
        self.assertEqual(
            parse_custom_position("101"),
            (None, "Please enter a value between 0 and 100"),
        )
        self.assertEqual(
            parse_custom_position("abc"),
            (None, "Please enter a valid number"),
        )
