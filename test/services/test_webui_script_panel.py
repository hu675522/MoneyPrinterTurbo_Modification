import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "webui"))

from script_panel import (
    build_video_language_options,
    format_script_generation_button_label,
    get_compact_text_area_height,
)


class TestWebuiScriptPanel(unittest.TestCase):
    def test_build_video_language_options_includes_auto_detect_first(self):
        options = build_video_language_options(
            ["zh-CN", "en-US"],
            lambda key: {"Auto Detect": "Auto"}.get(key, key),
        )

        self.assertEqual(options, [("Auto", ""), ("zh-CN", "zh-CN"), ("en-US", "en-US")])

    def test_compact_text_area_height_keeps_script_fields_small(self):
        self.assertEqual(get_compact_text_area_height(), 68)

    def test_script_generation_button_label_breaks_keywords_to_new_line(self):
        label = "点击使用AI根据**主题**生成 【视频文案】 和 【视频关键词】"

        self.assertEqual(
            format_script_generation_button_label(label),
            "点击使用AI根据主题\n生成【视频文案】和【视频关键词】",
        )
