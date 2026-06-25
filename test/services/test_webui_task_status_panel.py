import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "webui"))

from app.models import const
from task_status_panel import (
    TASK_LOG_DISPLAY_LIMIT,
    clamp_task_progress,
    format_task_log_expander_label,
    format_task_summary_pill_html,
    get_active_task_status_label,
    get_active_task_summary_column_weights,
    get_active_task_video_column_count,
    get_recent_task_logs,
    shorten_task_id,
)


class TestWebuiTaskStatusPanel(unittest.TestCase):
    def test_clamp_task_progress_keeps_progress_in_valid_range(self):
        self.assertEqual(clamp_task_progress(-1), 0)
        self.assertEqual(clamp_task_progress(42), 42)
        self.assertEqual(clamp_task_progress(101), 100)
        self.assertEqual(clamp_task_progress(None), 0)

    def test_shorten_task_id_preserves_short_and_abbreviates_long_ids(self):
        self.assertEqual(shorten_task_id("short-task"), "short-task")
        self.assertEqual(
            shorten_task_id("12345678-1234-5678-1234-567812345678"),
            "12345678-123...567812345678",
        )

    def test_get_active_task_status_label_reuses_task_status_labels(self):
        tr = lambda key: f"T:{key}"

        self.assertEqual(
            get_active_task_status_label(const.TASK_STATE_COMPLETE, tr),
            "T:Video Generation Completed",
        )
        self.assertEqual(
            get_active_task_status_label(const.TASK_STATE_FAILED, tr),
            "T:Video Generation Failed",
        )
        self.assertEqual(
            get_active_task_status_label(const.TASK_STATE_CANCELED, tr),
            "T:Task Canceled",
        )
        self.assertEqual(
            get_active_task_status_label(const.TASK_STATE_PROCESSING, tr),
            "T:Generating Video",
        )

    def test_active_task_summary_columns_leave_room_for_open_folder(self):
        self.assertEqual(get_active_task_summary_column_weights(), [0.32, 0.44, 0.24])

    def test_active_task_video_preview_columns_are_capped(self):
        self.assertEqual(get_active_task_video_column_count(0), 1)
        self.assertEqual(get_active_task_video_column_count(1), 1)
        self.assertEqual(get_active_task_video_column_count(2), 2)
        self.assertEqual(get_active_task_video_column_count(3), 3)
        self.assertEqual(get_active_task_video_column_count(8), 3)

    def test_recent_task_logs_are_limited_to_latest_lines(self):
        logs = [f"line-{index}" for index in range(TASK_LOG_DISPLAY_LIMIT + 5)]

        recent_logs = get_recent_task_logs(logs)

        self.assertEqual(len(recent_logs), TASK_LOG_DISPLAY_LIMIT)
        self.assertEqual(recent_logs[0], "line-5")
        self.assertEqual(recent_logs[-1], f"line-{TASK_LOG_DISPLAY_LIMIT + 4}")

    def test_task_log_expander_label_shows_visible_and_total_counts(self):
        label = format_task_log_expander_label(
            visible_count=200,
            total_count=280,
            tr=lambda key: f"T:{key}",
        )

        self.assertEqual(label, "T:Task Logs (T:Recent Log Lines: 200/280)")

    def test_task_summary_pill_html_escapes_values(self):
        html = format_task_summary_pill_html(
            label="Task <Status>",
            value="running & ready",
        )

        self.assertIn("mpt-task-summary-pill", html)
        self.assertIn("Task &lt;Status&gt;", html)
        self.assertIn("running &amp; ready", html)


if __name__ == "__main__":
    unittest.main()
