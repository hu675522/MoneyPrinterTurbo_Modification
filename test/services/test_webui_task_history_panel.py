import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "webui"))

from app.models import const
from app.models.schema import VideoAspect
from task_history_panel import (
    build_loaded_params_summary,
    can_cancel_task,
    can_load_task_params,
    can_navigate_history_page,
    build_retry_params,
    can_delete_task,
    can_retry_task,
    clamp_progress,
    clamp_history_page,
    format_loaded_params_summary,
    format_task_history_empty_state_html,
    format_task_history_item_title,
    format_task_history_result_summary,
    format_video_terms,
    get_history_page_after_navigation,
    get_task_history_subject,
    get_task_history_action_column_weights,
    get_task_history_destructive_column_weights,
    get_task_history_empty_state_keys,
    get_task_history_filter_column_weights,
    get_task_history_page_nav_column_weights,
    get_task_history_filter_options,
    get_task_status_label,
    get_total_pages,
    get_recent_tasks,
    load_task_params_to_form,
    reset_history_page_when_filters_change,
    shorten_task_subject,
    shorten_task_id,
    to_plain_value,
)


class FakeConfig:
    def __init__(self):
        self.app = {}
        self.ui = {}


class TestWebuiTaskHistoryPanel(unittest.TestCase):
    def test_clamp_progress_keeps_progress_in_valid_range(self):
        self.assertEqual(clamp_progress(-1), 0)
        self.assertEqual(clamp_progress(42), 42)
        self.assertEqual(clamp_progress(101), 100)
        self.assertEqual(clamp_progress(None), 0)

    def test_get_task_status_label_uses_existing_status_labels(self):
        tr = lambda key: f"T:{key}"

        self.assertEqual(
            get_task_status_label(const.TASK_STATE_COMPLETE, tr),
            "T:Video Generation Completed",
        )
        self.assertEqual(
            get_task_status_label(const.TASK_STATE_FAILED, tr),
            "T:Video Generation Failed",
        )
        self.assertEqual(
            get_task_status_label(const.TASK_STATE_PROCESSING, tr),
            "T:Generating Video",
        )
        self.assertEqual(
            get_task_status_label(const.TASK_STATE_CANCELED, tr),
            "T:Task Canceled",
        )
        self.assertEqual(get_task_status_label(999, tr), "T:Unknown Status")

    def test_shorten_task_id_preserves_short_and_abbreviates_long_ids(self):
        self.assertEqual(shorten_task_id("short-id"), "short-id")
        self.assertEqual(
            shorten_task_id("12345678-1234-5678-1234-567812345678"),
            "12345678...12345678",
        )

    def test_task_history_title_includes_shortened_subject_when_available(self):
        task = {
            "params": {
                "video_subject": "coffee beans review for morning routines",
            }
        }

        self.assertEqual(
            shorten_task_subject("coffee beans review for morning routines", keep=12),
            "coffee beans...",
        )
        self.assertEqual(get_task_history_subject(task), "coffee beans review for morning routines")
        self.assertEqual(
            format_task_history_item_title(
                task=task,
                status_label="Done",
                task_id="12345678-1234-5678-1234-567812345678",
                progress=100,
            ),
            "Done | coffee beans review for... | 12345678...12345678 | 100%",
        )

    def test_task_history_title_omits_missing_subject(self):
        self.assertEqual(get_task_history_subject({"params": None}), "")
        self.assertEqual(
            format_task_history_item_title(
                task={},
                status_label="Done",
                task_id="short-id",
                progress=50,
            ),
            "Done | short-id | 50%",
        )

    def test_task_history_filter_options_map_labels_to_states(self):
        tr = lambda key: f"T:{key}"

        options = get_task_history_filter_options(tr)

        self.assertEqual(options[0], ("T:All Tasks", None))
        self.assertIn(("T:Generating Video", const.TASK_STATE_PROCESSING), options)
        self.assertIn(
            ("T:Video Generation Completed", const.TASK_STATE_COMPLETE),
            options,
        )
        self.assertIn(("T:Video Generation Failed", const.TASK_STATE_FAILED), options)
        self.assertIn(("T:Task Canceled", const.TASK_STATE_CANCELED), options)

    def test_task_history_action_columns_are_grouped_by_frequency(self):
        self.assertEqual(get_task_history_action_column_weights(), [1, 1, 1, 1])
        self.assertEqual(get_task_history_destructive_column_weights(), [1, 1])
        self.assertEqual(get_task_history_filter_column_weights(), [0.42, 0.24, 0.16, 0.18])
        self.assertEqual(get_task_history_page_nav_column_weights(), [0.28, 0.44, 0.28])

    def test_task_history_result_summary_is_readable(self):
        summary = format_task_history_result_summary(
            visible_count=5,
            total=23,
            current_page=2,
            total_pages=5,
            tr=lambda key: f"T:{key}",
        )

        self.assertEqual(summary, "T:Task History Results: 5 / 23 | T:Page 2/5")

    def test_task_history_empty_state_html_escapes_text(self):
        html = format_task_history_empty_state_html(
            title="No <tasks>",
            detail="Generated & reusable",
        )

        self.assertIn("mpt-empty-state", html)
        self.assertIn("No &lt;tasks&gt;", html)
        self.assertIn("Generated &amp; reusable", html)

    def test_task_history_empty_state_keys_reflect_filters(self):
        self.assertEqual(
            get_task_history_empty_state_keys(state_filter=None, search_query=""),
            ("No Tasks Yet", "Task History Empty Help"),
        )
        self.assertEqual(
            get_task_history_empty_state_keys(
                state_filter=const.TASK_STATE_COMPLETE,
                search_query="",
            ),
            ("Task History No Matches", "Task History No Matches Help"),
        )
        self.assertEqual(
            get_task_history_empty_state_keys(state_filter=None, search_query="coffee"),
            ("Task History No Matches", "Task History No Matches Help"),
        )

    def test_task_history_page_helpers_keep_page_in_range(self):
        self.assertEqual(get_total_pages(total=0, page_size=10), 1)
        self.assertEqual(get_total_pages(total=21, page_size=10), 3)
        self.assertEqual(get_total_pages(total=21, page_size=0), 1)
        self.assertEqual(clamp_history_page(0, 3), 1)
        self.assertEqual(clamp_history_page(2, 3), 2)
        self.assertEqual(clamp_history_page(5, 3), 3)

    def test_task_history_page_navigation_helpers_clamp_edges(self):
        self.assertFalse(
            can_navigate_history_page(
                current_page=1,
                total_pages=3,
                direction="previous",
            )
        )
        self.assertTrue(
            can_navigate_history_page(
                current_page=2,
                total_pages=3,
                direction="previous",
            )
        )
        self.assertTrue(
            can_navigate_history_page(
                current_page=2,
                total_pages=3,
                direction="next",
            )
        )
        self.assertFalse(
            can_navigate_history_page(
                current_page=3,
                total_pages=3,
                direction="next",
            )
        )
        self.assertEqual(
            get_history_page_after_navigation(
                current_page=1,
                total_pages=3,
                direction="previous",
            ),
            1,
        )
        self.assertEqual(
            get_history_page_after_navigation(
                current_page=2,
                total_pages=3,
                direction="next",
            ),
            3,
        )

    def test_reset_history_page_when_filters_change_updates_signature(self):
        session_state = {
            "task_history_filter_signature": (None, 10),
            "task_history_page": 3,
            "task_history_page_input": 3,
        }

        reset_history_page_when_filters_change(
            session_state,
            state_filter=const.TASK_STATE_COMPLETE,
            page_size=20,
            search_query="coffee",
        )

        self.assertEqual(
            session_state["task_history_filter_signature"],
            (const.TASK_STATE_COMPLETE, 20, "coffee"),
        )
        self.assertEqual(session_state["task_history_page"], 1)
        self.assertNotIn("task_history_page_input", session_state)

    def test_can_delete_task_requires_confirmation_and_non_running_state(self):
        self.assertFalse(can_delete_task(const.TASK_STATE_COMPLETE, confirmed=False))
        self.assertTrue(can_delete_task(const.TASK_STATE_COMPLETE, confirmed=True))
        self.assertFalse(can_delete_task(const.TASK_STATE_PROCESSING, confirmed=True))

    def test_can_cancel_task_requires_confirmation_and_running_state(self):
        self.assertFalse(can_cancel_task(const.TASK_STATE_PROCESSING, confirmed=False))
        self.assertTrue(can_cancel_task(const.TASK_STATE_PROCESSING, confirmed=True))
        self.assertFalse(can_cancel_task(const.TASK_STATE_COMPLETE, confirmed=True))
        self.assertFalse(can_cancel_task(const.TASK_STATE_CANCELED, confirmed=True))

    def test_can_retry_task_requires_params_and_non_running_state(self):
        self.assertTrue(
            can_retry_task(
                {
                    "state": const.TASK_STATE_COMPLETE,
                    "params": {"video_subject": "coffee"},
                }
            )
        )
        self.assertFalse(
            can_retry_task(
                {
                    "state": const.TASK_STATE_PROCESSING,
                    "params": {"video_subject": "coffee"},
                }
            )
        )
        self.assertFalse(can_retry_task({"state": const.TASK_STATE_COMPLETE}))

    def test_can_load_task_params_matches_retry_safety_rules(self):
        self.assertTrue(
            can_load_task_params(
                {
                    "state": const.TASK_STATE_COMPLETE,
                    "params": {"video_subject": "coffee"},
                }
            )
        )
        self.assertFalse(
            can_load_task_params(
                {
                    "state": const.TASK_STATE_PROCESSING,
                    "params": {"video_subject": "coffee"},
                }
            )
        )

    def test_build_retry_params_restores_video_params(self):
        params = build_retry_params(
            {
                "params": {
                    "video_subject": "coffee",
                    "video_script": "fresh beans",
                }
            }
        )

        self.assertEqual(params.video_subject, "coffee")
        self.assertEqual(params.video_script, "fresh beans")

    def test_get_recent_tasks_uses_controller_page_response_without_output_urls(self):
        calls = []

        def fake_get_tasks_page(**kwargs):
            calls.append(kwargs)
            return {
                "tasks": [
                    {"task_id": "older", "videos": ["D:/tasks/older/final.mp4"]},
                    {"task_id": "newer", "videos": ["D:/tasks/newer/final.mp4"]},
                ],
                "total": 2,
                "page": 1,
                "page_size": kwargs["page_size"],
            }

        with patch(
            "task_history_panel.video_controller.get_tasks_page",
            side_effect=fake_get_tasks_page,
        ):
            tasks, total = get_recent_tasks(
                page=2,
                page_size=5,
                state_filter=const.TASK_STATE_COMPLETE,
                search_query="coffee",
            )

        self.assertEqual([task["task_id"] for task in tasks], ["older", "newer"])
        self.assertEqual(tasks[0]["videos"], ["D:/tasks/older/final.mp4"])
        self.assertEqual(total, 2)
        self.assertEqual(
            calls,
            [
                {
                    "page": 2,
                    "page_size": 5,
                    "request_id": "webui",
                    "include_output_urls": False,
                    "state_filter": const.TASK_STATE_COMPLETE,
                    "newest_first": True,
                    "search_query": "coffee",
                }
            ],
        )

    def test_format_video_terms_handles_lists_and_strings(self):
        self.assertEqual(format_video_terms(["coffee", "beans"]), "coffee, beans")
        self.assertEqual(format_video_terms("coffee, beans"), "coffee, beans")
        self.assertEqual(format_video_terms(None), "")

    def test_to_plain_value_unwraps_enums(self):
        self.assertEqual(to_plain_value(VideoAspect.landscape), "16:9")
        self.assertEqual(to_plain_value("plain"), "plain")

    def test_build_loaded_params_summary_uses_plain_values(self):
        params = build_retry_params(
            {
                "params": {
                    "video_subject": "coffee",
                    "video_source": "coverr",
                    "video_aspect": "16:9",
                    "video_count": 3,
                    "voice_name": "en-US-JennyNeural-Female",
                    "bgm_type": "custom",
                    "subtitle_enabled": False,
                }
            }
        )

        summary = build_loaded_params_summary(params)

        self.assertEqual(summary["subject"], "coffee")
        self.assertEqual(summary["source"], "coverr")
        self.assertEqual(summary["aspect"], "16:9")
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["voice"], "en-US-JennyNeural-Female")
        self.assertEqual(summary["bgm"], "custom")
        self.assertFalse(summary["subtitle"])

    def test_format_loaded_params_summary_uses_translated_labels(self):
        tr = lambda key: f"T:{key}"

        summary_text = format_loaded_params_summary(
            {
                "subject": "coffee",
                "source": "coverr",
                "aspect": "16:9",
                "count": 3,
                "voice": "",
                "bgm": "",
                "subtitle": False,
            },
            tr,
        )

        self.assertIn("T:Summary Subject: coffee", summary_text)
        self.assertIn("T:Summary Source: coverr", summary_text)
        self.assertIn("T:Summary Aspect: 16:9", summary_text)
        self.assertIn("T:Summary Count: 3", summary_text)
        self.assertIn("T:Summary Voice: -", summary_text)
        self.assertIn("T:Summary BGM: T:None", summary_text)
        self.assertIn("T:Summary Subtitle: T:Disabled", summary_text)

    def test_load_task_params_to_form_updates_session_and_config(self):
        config = FakeConfig()
        session_state = {}
        task = {
            "task_id": "loaded-task-id",
            "params": {
                "video_subject": "coffee",
                "video_script": "fresh beans",
                "video_terms": ["coffee", "beans"],
                "paragraph_number": 3,
                "video_script_prompt": "warm tone",
                "custom_system_prompt": "be concise",
                "match_materials_to_script": True,
                "video_source": "coverr",
                "video_concat_mode": "sequential",
                "video_transition_mode": "FadeIn",
                "video_aspect": "16:9",
                "video_clip_duration": 8,
                "video_count": 3,
                "voice_name": "en-US-JennyNeural-Female",
                "voice_volume": 1.2,
                "voice_rate": 1.1,
                "bgm_type": "custom",
                "bgm_file": "song.mp3",
                "bgm_volume": 0.4,
                "font_name": "MicrosoftYaHeiBold.ttc",
                "subtitle_position": "custom",
                "custom_position": 65.0,
                "text_fore_color": "#EEEEEE",
                "text_background_color": "#111111",
                "rounded_subtitle_background": True,
                "font_size": 72,
            }
        }

        load_task_params_to_form(
            task=task,
            config=config,
            session_state=session_state,
        )

        self.assertEqual(session_state["video_subject"], "coffee")
        self.assertEqual(session_state["video_script"], "fresh beans")
        self.assertEqual(session_state["video_terms"], "coffee, beans")
        self.assertEqual(session_state["paragraph_number_input"], 3)
        self.assertEqual(session_state["video_script_prompt"], "warm tone")
        self.assertEqual(session_state["custom_system_prompt"], "be concise")
        self.assertTrue(session_state["use_custom_system_prompt"])
        self.assertTrue(session_state["match_materials_to_script"])
        self.assertEqual(session_state["custom_bgm_file_input"], "song.mp3")
        self.assertEqual(session_state["custom_position_input"], "65.0")
        self.assertTrue(session_state["expand_advanced_script_settings"])
        self.assertTrue(session_state["expand_advanced_video_settings"])
        self.assertTrue(session_state["expand_task_history"])
        self.assertEqual(session_state["loaded_task_params_id"], "loaded-task-id")
        self.assertEqual(session_state["loaded_task_params_summary"]["subject"], "coffee")
        self.assertEqual(session_state["loaded_task_params_summary"]["source"], "coverr")
        self.assertEqual(session_state["loaded_task_params_summary"]["count"], 3)
        self.assertEqual(config.app["video_source"], "coverr")
        self.assertEqual(config.app["video_concat_mode"], "sequential")
        self.assertEqual(config.app["video_transition_mode"], "FadeIn")
        self.assertEqual(config.app["video_aspect"], "16:9")
        self.assertEqual(config.app["video_clip_duration"], 8)
        self.assertEqual(config.app["video_count"], 3)
        self.assertEqual(config.ui["voice_name"], "en-US-JennyNeural-Female")
        self.assertEqual(config.ui["voice_volume"], 1.2)
        self.assertEqual(config.ui["voice_rate"], 1.1)
        self.assertEqual(config.ui["bgm_type"], "custom")
        self.assertEqual(config.ui["bgm_volume"], 0.4)
        self.assertEqual(config.ui["subtitle_position"], "custom")
        self.assertEqual(config.ui["subtitle_background_color"], "#111111")
