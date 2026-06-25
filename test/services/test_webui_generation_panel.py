import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "webui"))

from app.models.schema import VideoParams
from generation_panel import get_generation_error_key


class TestWebuiGenerationPanel(unittest.TestCase):
    def test_generation_validation_requires_subject_or_script(self):
        params = VideoParams(video_subject="", video_script="", video_source="local")

        self.assertEqual(
            get_generation_error_key(params, {}),
            "Video Script and Subject Cannot Both Be Empty",
        )

    def test_generation_validation_rejects_unsupported_video_source(self):
        params = VideoParams(video_subject="coffee", video_source="unsupported")

        self.assertEqual(
            get_generation_error_key(params, {}),
            "Please Select a Valid Video Source",
        )

    def test_generation_validation_requires_douyin_api_url(self):
        params = VideoParams(video_subject="coffee", video_source="douyin")

        self.assertEqual(
            get_generation_error_key(params, {}),
            "Please Configure the Douyin Material API",
        )

    def test_generation_validation_requires_online_source_api_key(self):
        cases = [
            ("pexels", "Please Enter the Pexels API Key"),
            ("pixabay", "Please Enter the Pixabay API Key"),
            ("coverr", "Please Enter the Coverr API Key"),
        ]

        for source, expected_error in cases:
            with self.subTest(source=source):
                params = VideoParams(video_subject="coffee", video_source=source)
                self.assertEqual(get_generation_error_key(params, {}), expected_error)

    def test_generation_validation_allows_valid_local_request(self):
        params = VideoParams(video_subject="coffee", video_source="local")

        self.assertEqual(get_generation_error_key(params, {}), "")

    def test_generation_validation_allows_douyin_with_api_url(self):
        params = VideoParams(video_subject="coffee", video_source="douyin")

        self.assertEqual(
            get_generation_error_key(
                params, {"douyin_material_api_url": "https://materials.example/search"}
            ),
            "",
        )

    def test_generation_validation_allows_douyin_metadata_mode(self):
        params = VideoParams(video_subject="coffee", video_source="douyin")

        self.assertEqual(
            get_generation_error_key(
                params,
                {
                    "douyin_material_source_mode": "metadata",
                    "douyin_metadata_api_url": "https://data.example/search",
                    "douyin_resolver_api_url": "https://resolver.example/resolve",
                },
            ),
            "",
        )

    def test_generation_validation_allows_configured_online_source(self):
        params = VideoParams(video_subject="coffee", video_source="pexels")

        self.assertEqual(
            get_generation_error_key(params, {"pexels_api_keys": ["key"]}),
            "",
        )
