from uuid import uuid4
from html import escape

import streamlit as st

from app.controllers.v1 import video as video_controller
from app.models import const
from app.models.schema import VideoParams

import task_runner


TASK_HISTORY_PAGE_SIZES = [5, 10, 20, 50]


def clamp_progress(progress) -> int:
    progress = int(progress or 0)
    return max(0, min(progress, 100))


def get_task_status_label(state: int, tr) -> str:
    if state == const.TASK_STATE_COMPLETE:
        return tr("Video Generation Completed")
    if state == const.TASK_STATE_FAILED:
        return tr("Video Generation Failed")
    if state == const.TASK_STATE_CANCELED:
        return tr("Task Canceled")
    if state == const.TASK_STATE_PROCESSING:
        return tr("Generating Video")
    return tr("Unknown Status")


def shorten_task_id(task_id: str, keep: int = 8) -> str:
    if len(task_id) <= keep * 2 + 1:
        return task_id
    return f"{task_id[:keep]}...{task_id[-keep:]}"


def shorten_task_subject(subject: str, keep: int = 24) -> str:
    subject = str(subject or "").strip()
    if len(subject) <= keep:
        return subject
    return f"{subject[:keep].rstrip()}..."


def get_task_history_subject(task: dict) -> str:
    params = task.get("params", {})
    if not isinstance(params, dict):
        return ""
    return str(params.get("video_subject") or "").strip()


def format_task_history_item_title(
    *, task: dict, status_label: str, task_id: str, progress: int
) -> str:
    title_parts = [status_label]
    subject = shorten_task_subject(get_task_history_subject(task))
    if subject:
        title_parts.append(subject)
    title_parts.extend([shorten_task_id(task_id), f"{progress}%"])
    return " | ".join(title_parts)


def get_task_history_filter_options(tr) -> list[tuple[str, int | None]]:
    return [
        (tr("All Tasks"), None),
        (tr("Generating Video"), const.TASK_STATE_PROCESSING),
        (tr("Video Generation Completed"), const.TASK_STATE_COMPLETE),
        (tr("Video Generation Failed"), const.TASK_STATE_FAILED),
        (tr("Task Canceled"), const.TASK_STATE_CANCELED),
    ]


def get_task_history_action_column_weights() -> list[float]:
    return [1, 1, 1, 1]


def get_task_history_destructive_column_weights() -> list[float]:
    return [1, 1]


def get_task_history_filter_column_weights() -> list[float]:
    return [0.42, 0.24, 0.16, 0.18]


def get_task_history_page_nav_column_weights() -> list[float]:
    return [0.28, 0.44, 0.28]


def format_task_history_result_summary(
    *, visible_count: int, total: int, current_page: int, total_pages: int, tr
) -> str:
    return (
        f"{tr('Task History Results')}: {visible_count} / {total} | "
        f"{tr('Page')} {current_page}/{total_pages}"
    )


def format_task_history_empty_state_html(*, title: str, detail: str) -> str:
    return (
        '<div class="mpt-empty-state">'
        f"<strong>{escape(str(title))}</strong>"
        f"<span>{escape(str(detail))}</span>"
        "</div>"
    )


def get_task_history_empty_state_keys(*, state_filter, search_query: str) -> tuple[str, str]:
    has_filter = state_filter is not None or bool((search_query or "").strip())
    if has_filter:
        return "Task History No Matches", "Task History No Matches Help"
    return "No Tasks Yet", "Task History Empty Help"


def get_total_pages(total: int, page_size: int) -> int:
    if page_size <= 0:
        return 1
    return max(1, (int(total) + page_size - 1) // page_size)


def clamp_history_page(page: int, total_pages: int) -> int:
    return max(1, min(int(page or 1), int(total_pages or 1)))


def can_navigate_history_page(
    *, current_page: int, total_pages: int, direction: str
) -> bool:
    if direction == "previous":
        return current_page > 1
    if direction == "next":
        return current_page < total_pages
    return False


def get_history_page_after_navigation(
    *, current_page: int, total_pages: int, direction: str
) -> int:
    if direction == "previous":
        return clamp_history_page(current_page - 1, total_pages)
    if direction == "next":
        return clamp_history_page(current_page + 1, total_pages)
    return clamp_history_page(current_page, total_pages)


def reset_history_page_when_filters_change(
    session_state,
    *,
    state_filter,
    page_size,
    search_query: str = "",
):
    signature = (state_filter, page_size, (search_query or "").strip())
    if session_state.get("task_history_filter_signature") != signature:
        session_state["task_history_filter_signature"] = signature
        session_state["task_history_page"] = 1
        session_state.pop("task_history_page_input", None)


def get_recent_tasks(
    page: int = 1,
    page_size: int = 10,
    state_filter: int | None = None,
    search_query: str = "",
) -> tuple[list[dict], int]:
    response = video_controller.get_tasks_page(
        page=page,
        page_size=page_size,
        request_id="webui",
        include_output_urls=False,
        state_filter=state_filter,
        newest_first=True,
        search_query=search_query,
    )
    return response["tasks"], response["total"]


def can_delete_task(state: int, confirmed: bool) -> bool:
    return confirmed and state != const.TASK_STATE_PROCESSING


def can_cancel_task(state: int, confirmed: bool) -> bool:
    return confirmed and state == const.TASK_STATE_PROCESSING


def can_retry_task(task: dict) -> bool:
    return (
        task.get("state") != const.TASK_STATE_PROCESSING
        and isinstance(task.get("params"), dict)
        and bool(task.get("params"))
    )


def can_load_task_params(task: dict) -> bool:
    return can_retry_task(task)


def build_retry_params(task: dict) -> VideoParams:
    return VideoParams(**task["params"])


def format_video_terms(video_terms) -> str:
    if isinstance(video_terms, list):
        return ", ".join(str(term) for term in video_terms)
    return video_terms or ""


def to_plain_value(value):
    if hasattr(value, "value"):
        return value.value
    return value


def build_loaded_params_summary(params: VideoParams) -> dict:
    return {
        "subject": params.video_subject or "",
        "source": params.video_source or "",
        "aspect": to_plain_value(params.video_aspect) or "",
        "count": params.video_count or 1,
        "voice": params.voice_name or "",
        "bgm": params.bgm_type or "",
        "subtitle": bool(params.subtitle_enabled),
    }


def format_loaded_params_summary(summary: dict, tr) -> str:
    enabled_label = tr("Enabled") if summary.get("subtitle") else tr("Disabled")
    items = [
        f"{tr('Summary Subject')}: {summary.get('subject') or '-'}",
        f"{tr('Summary Source')}: {summary.get('source') or '-'}",
        f"{tr('Summary Aspect')}: {summary.get('aspect') or '-'}",
        f"{tr('Summary Count')}: {summary.get('count') or 1}",
        f"{tr('Summary Voice')}: {summary.get('voice') or '-'}",
        f"{tr('Summary BGM')}: {summary.get('bgm') or tr('None')}",
        f"{tr('Summary Subtitle')}: {enabled_label}",
    ]
    return " | ".join(items)


def load_task_params_to_form(*, task: dict, config, session_state):
    params = build_retry_params(task)
    task_id = task.get("task_id", "")

    session_state["video_subject"] = params.video_subject or ""
    session_state["video_script"] = params.video_script or ""
    session_state["video_terms"] = format_video_terms(params.video_terms)
    session_state["paragraph_number_input"] = params.paragraph_number
    session_state["video_script_prompt"] = params.video_script_prompt or ""
    session_state["custom_system_prompt"] = params.custom_system_prompt or ""
    session_state["use_custom_system_prompt"] = bool(params.custom_system_prompt)
    session_state["match_materials_to_script"] = params.match_materials_to_script
    session_state["custom_bgm_file_input"] = params.bgm_file or ""
    session_state["custom_position_input"] = str(params.custom_position)
    session_state["expand_advanced_script_settings"] = True
    session_state["expand_advanced_video_settings"] = True
    session_state["expand_task_history"] = True
    session_state["loaded_task_params_id"] = task_id
    session_state["loaded_task_params_summary"] = build_loaded_params_summary(params)

    config.app["video_source"] = params.video_source
    config.app["video_concat_mode"] = to_plain_value(params.video_concat_mode)
    config.app["video_transition_mode"] = to_plain_value(params.video_transition_mode)
    config.app["video_aspect"] = to_plain_value(params.video_aspect)
    config.app["video_clip_duration"] = params.video_clip_duration
    config.app["video_count"] = params.video_count
    config.app["match_materials_to_script"] = params.match_materials_to_script

    config.ui["voice_name"] = params.voice_name
    config.ui["voice_volume"] = params.voice_volume
    config.ui["voice_rate"] = params.voice_rate
    config.ui["bgm_type"] = params.bgm_type
    config.ui["bgm_volume"] = params.bgm_volume
    config.ui["font_name"] = params.font_name
    config.ui["subtitle_position"] = params.subtitle_position
    config.ui["custom_position"] = params.custom_position
    config.ui["text_fore_color"] = params.text_fore_color
    config.ui["font_size"] = params.font_size
    config.ui["subtitle_background_enabled"] = bool(params.text_background_color)
    if isinstance(params.text_background_color, str):
        config.ui["subtitle_background_color"] = params.text_background_color
    config.ui["rounded_subtitle_background"] = params.rounded_subtitle_background


def render_task_history_panel(*, config, tr, open_task_folder, page_size: int = 10):
    loaded_task_params_id = st.session_state.get("loaded_task_params_id", "")
    with st.expander(
        tr("Task History"),
        expanded=bool(st.session_state.get("expand_task_history", False)),
    ):
        if loaded_task_params_id:
            st.success(f"{tr('Params Loaded')}: {shorten_task_id(loaded_task_params_id)}")
            loaded_summary = st.session_state.get("loaded_task_params_summary", {})
            if loaded_summary:
                st.caption(format_loaded_params_summary(loaded_summary, tr))

        filter_options = get_task_history_filter_options(tr)
        filter_labels = [label for label, _state in filter_options]
        control_columns = st.columns(get_task_history_filter_column_weights())
        with control_columns[0]:
            search_query = st.text_input(
                f"{tr('Task ID')} / {tr('Summary Subject')}",
                value=st.session_state.get("task_history_search_query", ""),
                placeholder=f"{tr('Task ID')} / {tr('Summary Subject')}",
                key="task_history_search_query",
            )
        with control_columns[1]:
            selected_filter_label = st.selectbox(
                tr("Task Status"),
                filter_labels,
                index=0,
                key="task_history_status_filter",
            )
        with control_columns[2]:
            selected_page_size = st.selectbox(
                tr("Page Size"),
                TASK_HISTORY_PAGE_SIZES,
                index=TASK_HISTORY_PAGE_SIZES.index(page_size)
                if page_size in TASK_HISTORY_PAGE_SIZES
                else 1,
                key="task_history_page_size",
            )

        state_filter = dict(filter_options)[selected_filter_label]
        reset_history_page_when_filters_change(
            st.session_state,
            state_filter=state_filter,
            page_size=selected_page_size,
            search_query=search_query,
        )

        current_page = int(st.session_state.get("task_history_page", 1))
        tasks, total = get_recent_tasks(
            page=current_page,
            page_size=selected_page_size,
            state_filter=state_filter,
            search_query=search_query,
        )
        total_pages = get_total_pages(total, selected_page_size)
        clamped_page = clamp_history_page(current_page, total_pages)
        if clamped_page != current_page:
            st.session_state["task_history_page"] = clamped_page
            tasks, total = get_recent_tasks(
                page=clamped_page,
                page_size=selected_page_size,
                state_filter=state_filter,
                search_query=search_query,
            )
            current_page = clamped_page

        with control_columns[3]:
            page_nav_columns = st.columns(get_task_history_page_nav_column_weights())
            with page_nav_columns[0]:
                previous_page_clicked = st.button(
                    "<",
                    key="task_history_previous_page",
                    use_container_width=True,
                    disabled=not can_navigate_history_page(
                        current_page=current_page,
                        total_pages=total_pages,
                        direction="previous",
                    ),
                )
            with page_nav_columns[1]:
                st.markdown(
                    (
                        '<div class="mpt-page-indicator">'
                        f"{tr('Page')}<br><strong>{current_page}/{total_pages}</strong>"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )
            with page_nav_columns[2]:
                next_page_clicked = st.button(
                    ">",
                    key="task_history_next_page",
                    use_container_width=True,
                    disabled=not can_navigate_history_page(
                        current_page=current_page,
                        total_pages=total_pages,
                        direction="next",
                    ),
                )

        if previous_page_clicked or next_page_clicked:
            direction = "previous" if previous_page_clicked else "next"
            st.session_state["task_history_page"] = get_history_page_after_navigation(
                current_page=current_page,
                total_pages=total_pages,
                direction=direction,
            )
            st.rerun()

        if not tasks:
            empty_title_key, empty_detail_key = get_task_history_empty_state_keys(
                state_filter=state_filter,
                search_query=search_query,
            )
            st.markdown(
                format_task_history_empty_state_html(
                    title=tr(empty_title_key),
                    detail=tr(empty_detail_key),
                ),
                unsafe_allow_html=True,
            )
            return

        st.caption(
            format_task_history_result_summary(
                visible_count=len(tasks),
                total=total,
                current_page=current_page,
                total_pages=total_pages,
                tr=tr,
            )
        )
        for task in tasks:
            task_id = task.get("task_id", "")
            if not task_id:
                continue

            state = task.get("state")
            progress = clamp_progress(task.get("progress"))
            status_label = get_task_status_label(state, tr)
            title = format_task_history_item_title(
                task=task,
                status_label=status_label,
                task_id=task_id,
                progress=progress,
            )

            with st.expander(title, expanded=loaded_task_params_id == task_id):
                st.caption(f"{tr('Task ID')}: {task_id}")
                st.progress(progress, text=f"{progress}%")

                videos = task.get("videos", [])
                if videos:
                    st.write(tr("Generated Videos"))
                    video_columns = st.columns(min(len(videos), 3))
                    for index, video_file in enumerate(videos):
                        video_columns[index % len(video_columns)].video(video_file)

                action_columns = st.columns(get_task_history_action_column_weights())
                with action_columns[0]:
                    if st.button(
                        tr("View Task"),
                        key=f"task_history_view_{task_id}",
                        use_container_width=True,
                    ):
                        st.session_state["active_task_id"] = task_id
                        st.session_state["opened_task_folder_id"] = ""
                        st.rerun()

                with action_columns[1]:
                    if st.button(
                        tr("Load Params"),
                        key=f"task_history_load_params_{task_id}",
                        use_container_width=True,
                        disabled=not can_load_task_params(task),
                    ):
                        load_task_params_to_form(
                            task=task,
                            config=config,
                            session_state=st.session_state,
                        )
                        st.rerun()

                with action_columns[2]:
                    if st.button(
                        tr("Retry Task"),
                        key=f"task_history_retry_{task_id}",
                        use_container_width=True,
                        disabled=not can_retry_task(task),
                    ):
                        retry_task_id = str(uuid4())
                        task_runner.submit_task(retry_task_id, build_retry_params(task))
                        st.session_state["active_task_id"] = retry_task_id
                        st.session_state["opened_task_folder_id"] = ""
                        st.success(tr("Task Retry Started"))
                        st.rerun()

                    if not can_retry_task(task):
                        st.caption(tr("Cannot Retry Task"))

                with action_columns[3]:
                    if st.button(
                        tr("Open Folder"),
                        key=f"task_history_open_{task_id}",
                        use_container_width=True,
                    ):
                        open_task_folder(task_id)

                with st.expander(
                    f"{tr('Cancel Task')} / {tr('Delete Task')}",
                    expanded=False,
                ):
                    destructive_columns = st.columns(
                        get_task_history_destructive_column_weights()
                    )
                    with destructive_columns[0]:
                        confirm_cancel = st.checkbox(
                            tr("Confirm Cancel Task"),
                            key=f"task_history_confirm_cancel_{task_id}",
                            disabled=state != const.TASK_STATE_PROCESSING,
                        )
                        if st.button(
                            tr("Cancel Task"),
                            key=f"task_history_cancel_{task_id}",
                            use_container_width=True,
                            disabled=not can_cancel_task(state, confirm_cancel),
                        ):
                            video_controller.cancel_task(task_id)
                            st.warning(tr("Task Canceled"))
                            st.rerun()

                    with destructive_columns[1]:
                        confirm_delete = st.checkbox(
                            tr("Confirm Delete Task"),
                            key=f"task_history_confirm_delete_{task_id}",
                            disabled=state == const.TASK_STATE_PROCESSING,
                        )
                        if st.button(
                            tr("Delete Task"),
                            key=f"task_history_delete_{task_id}",
                            use_container_width=True,
                            disabled=not can_delete_task(state, confirm_delete),
                        ):
                            video_controller.delete_task(task_id)
                            if st.session_state.get("active_task_id") == task_id:
                                st.session_state["active_task_id"] = ""
                            st.success(tr("Task Deleted"))
                            st.rerun()

                        if state == const.TASK_STATE_PROCESSING:
                            st.caption(tr("Cannot Delete Running Task"))
