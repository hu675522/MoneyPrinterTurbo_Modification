import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "webui"))

from basic_settings_panel import (
    format_config_keys,
    get_basic_settings_column_weights,
    get_douyin_config_visibility,
    get_douyin_mode_index,
    get_llm_provider_options,
    get_provider_defaults_and_tips,
    get_provider_index,
    parse_config_keys,
)


class FakeAppConfig:
    def get_default_ollama_base_url(self):
        return "http://localhost:11434/v1"

    def is_running_in_container(self):
        return False


class TestWebuiBasicSettingsPanel(unittest.TestCase):
    def test_basic_settings_columns_give_forms_more_room(self):
        weights = get_basic_settings_column_weights()

        self.assertEqual(len(weights), 3)
        self.assertGreater(weights[1], weights[0])
        self.assertGreater(weights[2], weights[0])

    def test_llm_provider_options_keep_stable_provider_ids(self):
        options = get_llm_provider_options("en", lambda key: f"T:{key}")
        values = [value for _, value in options]

        self.assertIn(("AIHubMix (T:Recommended)", "aihubmix"), options)
        self.assertIn("openai", values)
        self.assertIn("groq", values)
        self.assertIn("litellm", values)

    def test_llm_provider_options_use_chinese_recommended_label(self):
        options = get_llm_provider_options("zh", lambda key: key)

        self.assertIn(("AIHubMix\uff08\u63a8\u8350\uff09", "aihubmix"), options)

    def test_get_provider_index_returns_saved_provider_or_default(self):
        options = [("OpenAI", "openai"), ("Groq", "groq")]

        self.assertEqual(get_provider_index(options, "groq"), 1)
        self.assertEqual(get_provider_index(options, "GROQ"), 1)
        self.assertEqual(get_provider_index(options, "missing"), 0)

    def test_format_and_parse_config_keys_preserve_batch_key_contract(self):
        self.assertEqual(format_config_keys("abc"), "abc")
        self.assertEqual(format_config_keys(["abc", "def"]), "abc, def")
        self.assertEqual(format_config_keys([]), "")

        self.assertEqual(parse_config_keys("abc, def"), ["abc", "def"])
        self.assertEqual(parse_config_keys(""), None)

    def test_douyin_config_visibility_switches_fields_by_mode(self):
        direct = get_douyin_config_visibility("direct")
        metadata = get_douyin_config_visibility("metadata")

        self.assertTrue(direct["direct"])
        self.assertFalse(direct["metadata"])
        self.assertFalse(direct["enhance"])
        self.assertTrue(metadata["metadata"])
        self.assertTrue(metadata["enhance"])
        self.assertFalse(metadata["direct"])

    def test_get_douyin_mode_index_returns_saved_mode_or_default(self):
        options = [("Direct", "direct"), ("Metadata", "metadata")]

        self.assertEqual(get_douyin_mode_index(options, "metadata"), 1)
        self.assertEqual(get_douyin_mode_index(options, "missing"), 0)

    def test_provider_defaults_fill_known_model_and_base_url(self):
        model_name, base_url, tips = get_provider_defaults_and_tips(
            app_config=FakeAppConfig(),
            llm_provider="groq",
            llm_model_name="",
            llm_base_url="",
        )

        self.assertEqual(model_name, "llama-3.3-70b-versatile")
        self.assertEqual(base_url, "https://api.groq.com/openai/v1")
        self.assertIn("Groq", tips)

    def test_provider_tips_render_readable_chinese(self):
        model_name, base_url, tips = get_provider_defaults_and_tips(
            app_config=FakeAppConfig(),
            llm_provider="deepseek",
            llm_model_name="",
            llm_base_url="",
        )

        self.assertEqual(model_name, "deepseek-chat")
        self.assertEqual(base_url, "https://api.deepseek.com")
        self.assertIn("DeepSeek \u914d\u7f6e\u8bf4\u660e", tips)
        self.assertIn("\u70b9\u51fb\u5230\u5b98\u7f51\u7533\u8bf7", tips)
        self.assertNotIn("????", tips)

    def test_ollama_defaults_use_config_default_base_url(self):
        model_name, base_url, tips = get_provider_defaults_and_tips(
            app_config=FakeAppConfig(),
            llm_provider="ollama",
            llm_model_name="",
            llm_base_url="",
        )

        self.assertEqual(model_name, "qwen:7b")
        self.assertEqual(base_url, "http://localhost:11434/v1")
        self.assertIn("Ollama", tips)
