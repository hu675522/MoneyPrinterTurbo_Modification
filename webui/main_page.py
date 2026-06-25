import streamlit as st

from app.models.schema import VideoParams

from audio_panel import render_audio_panel
from api_key_panel import render_api_key_content
from basic_settings_panel import render_basic_settings_content
from generation_panel import render_generation_controls
from header_panel import render_header
from script_panel import render_script_panel
from subtitle_panel import render_subtitle_panel
from task_history_panel import render_task_history_panel
from task_status_panel import render_active_task_status
from video_panel import render_video_panel
from webui_utils import open_task_folder, scroll_to_bottom


SUPPORT_LOCALES = [
    "zh-CN",
    "zh-HK",
    "zh-TW",
    "de-DE",
    "en-US",
    "fr-FR",
    "ru-RU",
    "vi-VN",
    "th-TH",
    "tr-TR",
]


SETTINGS_ROW_EXPANDED_KEY = "mpt_settings_row_expanded"


def get_main_page_column_weights() -> list[float]:
    return [1.1, 1.0, 1.0, 0.95]


def get_settings_toggle_column_weights() -> list[float]:
    return [1.0, 1.08]


def get_settings_content_column_weights() -> list[float]:
    return [1.45, 1.0]


def is_settings_row_expanded(session_state) -> bool:
    return bool(session_state.get(SETTINGS_ROW_EXPANDED_KEY, False))


def set_settings_row_expanded(session_state, expanded: bool):
    session_state[SETTINGS_ROW_EXPANDED_KEY] = expanded


def strip_streamlit_label_markup(label: str) -> str:
    cleaned_label = (
        label.replace("**", "")
        .replace(":blue[", "")
        .replace("]", "")
        .replace("(", "")
        .replace(")", "")
        .replace("点击展开", "")
        .replace("Click to expand", "")
        .strip()
    )
    return cleaned_label.rstrip(":：").strip()


def format_settings_toggle_label(label: str, expanded: bool) -> str:
    state_label = "点击收起" if expanded else "点击展开"
    indicator = "v" if expanded else ">"
    return f"{indicator} {strip_streamlit_label_markup(label)} ({state_label})"


def create_video_params(session_state) -> VideoParams:
    params = VideoParams(video_subject="")
    params.match_materials_to_script = bool(
        session_state.get("match_materials_to_script", False)
    )
    return params


def render_main_page(*, config, root_dir: str, font_dir: str, locales: dict, tr):
    render_header(project_version=config.project_version, locales=locales, config=config)

    settings_expanded = is_settings_row_expanded(st.session_state)
    basic_toggle_col, api_key_toggle_col = st.columns(
        get_settings_toggle_column_weights(),
        gap="medium",
    )
    with basic_toggle_col:
        basic_toggle_clicked = st.button(
            format_settings_toggle_label(tr("Basic Settings"), settings_expanded),
            key="settings_basic_toggle",
            use_container_width=True,
        )
    with api_key_toggle_col:
        api_key_toggle_clicked = st.button(
            format_settings_toggle_label(
                tr("Click to show API Key management"),
                settings_expanded,
            ),
            key="settings_api_key_toggle",
            use_container_width=True,
        )

    if basic_toggle_clicked or api_key_toggle_clicked:
        set_settings_row_expanded(st.session_state, not settings_expanded)
        st.rerun()

    if settings_expanded:
        basic_settings_col, api_key_col = st.columns(
            get_settings_content_column_weights(),
            gap="medium",
        )
        with basic_settings_col:
            with st.container(border=True):
                render_basic_settings_content(config=config, tr=tr)
        with api_key_col:
            with st.container(border=True):
                render_api_key_content(config=config, tr=tr)

    script_panel, video_panel, audio_panel, subtitle_panel = st.columns(
        get_main_page_column_weights(),
        gap="medium",
    )
    params = create_video_params(st.session_state)

    with script_panel:
        render_script_panel(params=params, support_locales=SUPPORT_LOCALES, tr=tr)

    uploaded_files = []
    uploaded_audio_file = None
    with video_panel:
        uploaded_files = render_video_panel(config=config, params=params, tr=tr)

    with audio_panel:
        uploaded_audio_file = render_audio_panel(config=config, params=params, tr=tr)

    with subtitle_panel:
        render_subtitle_panel(config=config, params=params, font_dir=font_dir, tr=tr)

    render_generation_controls(
        config=config,
        params=params,
        uploaded_audio_file=uploaded_audio_file,
        uploaded_files=uploaded_files,
        tr=tr,
        scroll_to_bottom=scroll_to_bottom,
    )

    render_active_task_status(
        config=config,
        tr=tr,
        open_task_folder=lambda task_id: open_task_folder(root_dir, task_id),
    )

    render_task_history_panel(
        config=config,
        tr=tr,
        open_task_folder=lambda task_id: open_task_folder(root_dir, task_id),
    )
