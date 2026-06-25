import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "webui"))

from header_panel import get_language_options


class TestWebuiHeaderPanel(unittest.TestCase):
    def test_get_language_options_selects_current_language(self):
        options, selected_index = get_language_options(
            {
                "zh": {"Language": "简体中文"},
                "en": {"Language": "English"},
                "ru": {"Language": "Русский"},
            },
            "en",
        )

        self.assertEqual(
            options,
            ["zh - 简体中文", "en - English", "ru - Русский"],
        )
        self.assertEqual(selected_index, 1)

    def test_get_language_options_defaults_to_first_language(self):
        options, selected_index = get_language_options(
            {
                "zh": {"Language": "简体中文"},
                "en": {"Language": "English"},
            },
            "missing",
        )

        self.assertEqual(options, ["zh - 简体中文", "en - English"])
        self.assertEqual(selected_index, 0)
