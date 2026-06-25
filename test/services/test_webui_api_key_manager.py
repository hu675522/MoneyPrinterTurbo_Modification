import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "webui"))

from api_key_manager import mask_api_key


class TestWebuiApiKeyManager(unittest.TestCase):
    def test_mask_api_key_hides_middle_characters(self):
        self.assertEqual(mask_api_key("abcd12345678wxyz"), "abcd****wxyz")

    def test_mask_api_key_hides_short_keys_entirely(self):
        self.assertEqual(mask_api_key("abc123"), "******")

    def test_mask_api_key_handles_empty_values(self):
        self.assertEqual(mask_api_key(""), "")
        self.assertEqual(mask_api_key(None), "")
