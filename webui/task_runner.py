import threading
import traceback
from concurrent.futures import Future

from loguru import logger

from app.models import const
from app.controllers.v1 import video as video_controller
from app.models.schema import VideoParams
from app.services import state as sm
from app.services import task as tm


_lock = threading.RLock()
_futures: dict[str, Future] = {}
_logs: dict[str, list[str]] = {}


def serialize_params(params: VideoParams) -> dict:
    return params.model_dump(mode="json")


def _store_params_snapshot(task_id: str, params: VideoParams):
    task = sm.state.get_task(task_id) or {}
    state = task.get("state", const.TASK_STATE_PROCESSING)
    progress = task.get("progress", 0)
    preserved_fields = {
        key: value
        for key, value in task.items()
        if key not in {"task_id", "state", "progress"}
    }
    preserved_fields["params"] = serialize_params(params)
    sm.state.update_task(task_id, state=state, progress=progress, **preserved_fields)


def _append_log(task_id: str, message: str):
    with _lock:
        _logs.setdefault(task_id, []).append(message.rstrip())


def _run_task_with_logs(task_id: str, params: VideoParams, stop_at: str = "video"):
    handler_id = logger.add(lambda msg: _append_log(task_id, str(msg)))
    try:
        current_task = sm.state.get_task(task_id)
        if current_task and current_task.get("state") == const.TASK_STATE_CANCELED:
            logger.info("Task Canceled")
            return None

        logger.info("Start Generating Video")
        result = tm.start(task_id=task_id, params=params, stop_at=stop_at)
        if not result:
            current_task = sm.state.get_task(task_id)
            if current_task and current_task.get("state") == const.TASK_STATE_CANCELED:
                logger.info("Task Canceled")
            elif not current_task or current_task.get("state") == const.TASK_STATE_PROCESSING:
                sm.state.update_task(
                    task_id, state=const.TASK_STATE_FAILED, progress=100
                )
                logger.error("Video Generation Failed")
        return result
    except Exception as exc:
        _append_log(task_id, traceback.format_exc())
        logger.exception(f"Video generation failed: {exc}")
        current_task = sm.state.get_task(task_id)
        if not current_task or current_task.get("state") != const.TASK_STATE_CANCELED:
            sm.state.update_task(task_id, state=const.TASK_STATE_FAILED, progress=100)
        return None
    finally:
        _store_params_snapshot(task_id, params)
        logger.remove(handler_id)


def submit_task(task_id: str, params: VideoParams) -> Future:
    with _lock:
        if task_id in _futures and not _futures[task_id].done():
            return _futures[task_id]
        _logs[task_id] = []
        future = Future()
        _futures[task_id] = future

    try:
        task = video_controller.submit_task(
            body=params,
            stop_at="video",
            request_id="webui",
            task_id=task_id,
            task_func=_run_task_with_logs,
        )
        future.set_result(task)
    except Exception as exc:
        future.set_exception(exc)
        sm.state.update_task(task_id, state=const.TASK_STATE_FAILED, progress=100)
        _append_log(task_id, traceback.format_exc())
        logger.exception(f"WebUI task submit failed: {exc}")

    return future


def get_task(task_id: str) -> dict:
    task = sm.state.get_task(task_id) or {
        "task_id": task_id,
        "state": const.TASK_STATE_PROCESSING,
        "progress": 0,
    }
    with _lock:
        future = _futures.get(task_id)
        logs = list(_logs.get(task_id, []))

    task["done"] = bool(
        task.get("state")
        in {const.TASK_STATE_COMPLETE, const.TASK_STATE_FAILED, const.TASK_STATE_CANCELED}
        or (future and future.done() and task.get("state") != const.TASK_STATE_PROCESSING)
    )
    task["logs"] = logs
    return task


def is_running(task_id: str | None) -> bool:
    if not task_id:
        return False
    with _lock:
        future = _futures.get(task_id)
    task = sm.state.get_task(task_id)
    return bool(task and task.get("state") == const.TASK_STATE_PROCESSING)
