import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "webui"))

import task_runner
from app.models import const
from app.models.schema import VideoParams
from app.services import state as sm


def wait_for_task_state(task_id, expected_state, timeout=5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        task = sm.state.get_task(task_id)
        if task and task.get("state") == expected_state:
            return task
        time.sleep(0.05)
    return sm.state.get_task(task_id)


class TestWebuiTaskRunner(unittest.TestCase):
    def test_submit_task_runs_generation_in_background(self):
        task_id = "test-webui-task-runner-success"
        params = VideoParams(video_subject="coffee")

        def fake_start(task_id, params, stop_at="video"):
            sm.state.update_task(
                task_id,
                state=const.TASK_STATE_COMPLETE,
                progress=100,
                videos=["final.mp4"],
            )
            return {"videos": ["final.mp4"]}

        with patch.object(task_runner.tm, "start", side_effect=fake_start) as start:
            future = task_runner.submit_task(task_id, params)
            task_response = future.result(timeout=5)
            task = wait_for_task_state(task_id, const.TASK_STATE_COMPLETE)

        self.assertEqual(task_response["task_id"], task_id)
        self.assertEqual(task_response["request_id"], "webui")
        start.assert_called_once_with(task_id=task_id, params=params, stop_at="video")

        self.assertIsNotNone(task)
        self.assertEqual(task["state"], const.TASK_STATE_COMPLETE)
        self.assertEqual(task["progress"], 100)
        self.assertEqual(task["videos"], ["final.mp4"])
        self.assertEqual(task["params"]["video_subject"], "coffee")

    def test_submit_task_marks_task_failed_when_generation_raises(self):
        task_id = "test-webui-task-runner-failed"
        params = VideoParams(video_subject="coffee")

        with patch.object(task_runner.tm, "start", side_effect=RuntimeError("boom")):
            future = task_runner.submit_task(task_id, params)
            task_response = future.result(timeout=5)
            task = wait_for_task_state(task_id, const.TASK_STATE_FAILED)

        self.assertEqual(task_response["task_id"], task_id)

        self.assertIsNotNone(task)
        self.assertEqual(task["state"], const.TASK_STATE_FAILED)
        self.assertEqual(task["progress"], 100)
        self.assertEqual(task["params"]["video_subject"], "coffee")
        task = task_runner.get_task(task_id)
        self.assertTrue(any("boom" in log for log in task["logs"]))

    def test_run_task_skips_generation_when_task_was_canceled(self):
        task_id = "test-webui-task-runner-canceled"
        params = VideoParams(video_subject="coffee")
        sm.state.update_task(
            task_id,
            state=const.TASK_STATE_CANCELED,
            progress=100,
            canceled=True,
        )

        with patch.object(task_runner.tm, "start") as start:
            result = task_runner._run_task_with_logs(task_id, params)

        task = sm.state.get_task(task_id)
        start.assert_not_called()
        self.assertIsNone(result)
        self.assertEqual(task["state"], const.TASK_STATE_CANCELED)
        self.assertTrue(task["canceled"])
        self.assertEqual(task["params"]["video_subject"], "coffee")
