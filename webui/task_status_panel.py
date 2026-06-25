import time
from html import escape

import streamlit as st

from app.models import const

import task_runner


TASK_LOG_DISPLAY_LIMIT = 200


def clamp_task_progress(progress) -> int:
    progress = int(progress or 0)
    return max(0, min(progress, 100))


def shorten_task_id(task_id: str, keep: int = 12) -> str:
    if len(task_id) <= keep * 2 + 1:
        return task_id
    return f"{task_id[:keep]}...{task_id[-keep:]}"


def get_active_task_status_label(state: int, tr) -> str:
    if state == const.TASK_STATE_COMPLETE:
        return tr("Video Generation Completed")
    if state == const.TASK_STATE_FAILED:
        return tr("Video Generation Failed")
    if state == const.TASK_STATE_CANCELED:
        return tr("Task Canceled")
    return tr("Generating Video")


def get_active_task_summary_column_weights() -> list[float]:
    return [0.32, 0.44, 0.24]


def get_active_task_video_column_count(video_count: int) -> int:
    return min(max(int(video_count or 0), 1), 3)


def get_recent_task_logs(logs: list[str], limit: int = TASK_LOG_DISPLAY_LIMIT) -> list[str]:
    return list(logs or [])[-limit:]


def format_task_log_expander_label(*, visible_count: int, total_count: int, tr) -> str:
    return f"{tr('Task Logs')} ({tr('Recent Log Lines')}: {visible_count}/{total_count})"


def format_task_summary_pill_html(*, label: str, value: str) -> str:
    return (
        '<div class="mpt-task-summary-pill">'
        f'<span>{escape(str(label))}</span>'
        f'<strong>{escape(str(value))}</strong>'
        "</div>"
    )


def render_active_task_status(*, config, tr, open_task_folder):
    task_id = st.session_state.get("active_task_id", "")
    if not task_id:
        return

    task = task_runner.get_task(task_id)
    state = task.get("state")
    progress = clamp_task_progress(task.get("progress"))
    status_label = get_active_task_status_label(state, tr)

    with st.container(border=True):
        status_columns = st.columns(get_active_task_summary_column_weights())
        with status_columns[0]:
            st.markdown(
                format_task_summary_pill_html(
                    label=tr("Task Status"),
                    value=status_label,
                ),
                unsafe_allow_html=True,
            )
        with status_columns[1]:
            st.markdown(
                format_task_summary_pill_html(
                    label=tr("Task ID"),
                    value=shorten_task_id(task_id),
                ),
                unsafe_allow_html=True,
            )
        with status_columns[2]:
            if st.button(
                tr("Open Folder"),
                key=f"active_task_open_folder_{task_id}",
                use_container_width=True,
            ):
                open_task_folder(task_id)

        st.progress(progress, text=f"{progress}%")

        if state == const.TASK_STATE_COMPLETE:
            st.success(status_label)
            video_files = task.get("videos", [])
            if video_files:
                st.write(tr("Generated Videos"))
                player_cols = st.columns(
                    get_active_task_video_column_count(len(video_files))
                )
                for i, url in enumerate(video_files):
                    player_cols[i % len(player_cols)].video(url)

            if st.session_state.get("opened_task_folder_id") != task_id:
                open_task_folder(task_id)
                st.session_state["opened_task_folder_id"] = task_id

        elif state == const.TASK_STATE_FAILED:
            st.error(status_label)

        elif state == const.TASK_STATE_CANCELED:
            st.warning(status_label)

        else:
            st.info(status_label)

        logs = task.get("logs", [])
        if logs and not config.ui.get("hide_log", False):
            visible_logs = get_recent_task_logs(logs)
            with st.expander(
                format_task_log_expander_label(
                    visible_count=len(visible_logs),
                    total_count=len(logs),
                    tr=tr,
                ),
                expanded=False,
            ):
                st.code("\n".join(visible_logs))

    if state == const.TASK_STATE_PROCESSING:
        time.sleep(1)
        st.rerun()
