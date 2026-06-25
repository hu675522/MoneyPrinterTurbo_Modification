import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "webui"))

import audio_panel
from app.services import voice


class TestWebuiAudioPanel(unittest.TestCase):
    def test_get_tts_servers_includes_elevenlabs(self):
        servers = audio_panel.get_tts_servers(lambda key: key)

        self.assertIn(("elevenlabs", "ElevenLabs TTS"), servers)

    def test_get_saved_tts_server_index_returns_saved_or_default(self):
        servers = [("a", "A"), ("b", "B")]

        self.assertEqual(audio_panel.get_saved_tts_server_index(servers, "b"), 1)
        self.assertEqual(audio_panel.get_saved_tts_server_index(servers, "missing"), 0)

    def test_filter_voices_for_azure_tts_versions(self):
        with patch.object(
            audio_panel.voice,
            "get_all_azure_voices",
            return_value=["zh-CN-XiaoxiaoNeural-Female", "zh-CN-XiaoxiaoV2Neural-Female"],
        ):
            self.assertEqual(
                audio_panel.filter_voices_for_tts_server("azure-tts-v1"),
                ["zh-CN-XiaoxiaoNeural-Female"],
            )
            self.assertEqual(
                audio_panel.filter_voices_for_tts_server("azure-tts-v2"),
                ["zh-CN-XiaoxiaoV2Neural-Female"],
            )

    def test_filter_voices_for_elevenlabs_uses_api_key(self):
        with patch.object(
            audio_panel.voice,
            "get_elevenlabs_voices",
            return_value=["elevenlabs:abc:Adam"],
        ) as get_voices:
            self.assertEqual(
                audio_panel.filter_voices_for_tts_server("elevenlabs", "api-key"),
                ["elevenlabs:abc:Adam"],
            )

        get_voices.assert_called_once_with("api-key")

    def test_build_friendly_voice_names_translates_gender_tokens(self):
        names = audio_panel.build_friendly_voice_names(
            ["en-US-GuyNeural-Male", "en-US-JennyNeural-Female"],
            "azure-tts-v1",
            lambda key: {"Male": "M", "Female": "F"}.get(key, key),
        )

        self.assertEqual(names["en-US-GuyNeural-Male"], "en-US-Guy-M")
        self.assertEqual(names["en-US-JennyNeural-Female"], "en-US-Jenny-F")

    def test_build_friendly_voice_names_handles_no_voice(self):
        names = audio_panel.build_friendly_voice_names(
            [voice.NO_VOICE_NAME],
            voice.NO_VOICE_NAME,
            lambda key: {"No Voice": "Silent"}.get(key, key),
        )

        self.assertEqual(names, {voice.NO_VOICE_NAME: "Silent"})

    def test_get_saved_voice_index_prefers_saved_then_locale(self):
        friendly_names = {
            "zh-CN-XiaoxiaoNeural-Female": "zh",
            "en-US-JennyNeural-Female": "en",
        }
        filtered_voices = list(friendly_names.keys())

        self.assertEqual(
            audio_panel.get_saved_voice_index(
                friendly_names=friendly_names,
                filtered_voices=filtered_voices,
                saved_voice_name="en-US-JennyNeural-Female",
                ui_language="zh",
            ),
            1,
        )
        self.assertEqual(
            audio_panel.get_saved_voice_index(
                friendly_names=friendly_names,
                filtered_voices=filtered_voices,
                saved_voice_name="missing",
                ui_language="zh",
            ),
            0,
        )

    def test_get_custom_audio_file_types_includes_uppercase_variants(self):
        upload_types = audio_panel.get_custom_audio_file_types()

        self.assertIn("mp3", upload_types)
        self.assertIn("MP3", upload_types)
        self.assertIn("ogg", upload_types)
        self.assertIn("OGG", upload_types)

    def test_get_value_index_returns_saved_value_or_default(self):
        values = [0.8, 1.0, 1.2]

        self.assertEqual(audio_panel.get_value_index(values, 1.2), 2)
        self.assertEqual(audio_panel.get_value_index(values, 2.0), 0)
        self.assertEqual(audio_panel.get_value_index(values, 2.0, default=1), 1)

    def test_get_option_value_index_returns_saved_value_or_default(self):
        options = [("No BGM", ""), ("Random", "random"), ("Custom", "custom")]

        self.assertEqual(audio_panel.get_option_value_index(options, "custom"), 2)
        self.assertEqual(audio_panel.get_option_value_index(options, "missing"), 0)
        self.assertEqual(
            audio_panel.get_option_value_index(options, "missing", default=1),
            1,
        )
