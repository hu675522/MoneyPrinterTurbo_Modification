import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "webui"))

from video_panel import (
    get_default_aspect_index,
    get_local_file_upload_types,
    get_option_index,
    get_value_index,
    get_video_codec_options,
)


class TestWebuiVideoPanel(unittest.TestCase):
    def test_get_local_file_upload_types_includes_uppercase_variants(self):
        upload_types = get_local_file_upload_types()

        self.assertIn("mp4", upload_types)
        self.assertIn("MP4", upload_types)
        self.assertIn("png", upload_types)
        self.assertIn("PNG", upload_types)

    def test_get_default_aspect_index_prefers_landscape_for_coverr(self):
        self.assertEqual(get_default_aspect_index("coverr"), 1)
        self.assertEqual(get_default_aspect_index("pexels"), 0)

    def test_get_option_index_returns_saved_value_or_default(self):
        options = [("A", "a"), ("B", "b")]

        self.assertEqual(get_option_index(options, "b"), 1)
        self.assertEqual(get_option_index(options, "missing"), 0)
        self.assertEqual(get_option_index(options, "missing", default=1), 1)

    def test_get_video_codec_options_keeps_libx264_default_available(self):
        codec_values = [value for _, value in get_video_codec_options()]

        self.assertIn("libx264", codec_values)

    def test_get_value_index_returns_saved_value_or_default(self):
        values = [2, 3, 4]

        self.assertEqual(get_value_index(values, 4), 2)
        self.assertEqual(get_value_index(values, 9), 0)
        self.assertEqual(get_value_index(values, 9, default=1), 1)
