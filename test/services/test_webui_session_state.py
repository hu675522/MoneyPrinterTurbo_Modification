import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "webui"))

from session_state import init_session_state


class TestWebuiSessionState(unittest.TestCase):
    def test_init_session_state_sets_defaults(self):
        session_state = {}

        init_session_state(
            session_state,
            app_config={"match_materials_to_script": True},
            ui_config={"language": "en"},
            system_locale="zh",
            default_system_prompt="default prompt",
        )

        self.assertEqual(session_state["video_subject"], "")
        self.assertEqual(session_state["custom_system_prompt"], "default prompt")
        self.assertTrue(session_state["match_materials_to_script"])
        self.assertEqual(session_state["ui_language"], "en")
        self.assertEqual(session_state["local_video_materials"], [])
        self.assertEqual(session_state["active_task_id"], "")

    def test_init_session_state_preserves_existing_values(self):
        session_state = {
            "video_subject": "existing subject",
            "ui_language": "ru",
            "match_materials_to_script": False,
        }

        init_session_state(
            session_state,
            app_config={"match_materials_to_script": True},
            ui_config={"language": "en"},
            system_locale="zh",
            default_system_prompt="default prompt",
        )

        self.assertEqual(session_state["video_subject"], "existing subject")
        self.assertEqual(session_state["ui_language"], "ru")
        self.assertFalse(session_state["match_materials_to_script"])
