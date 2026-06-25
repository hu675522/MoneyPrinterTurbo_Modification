import os
from uuid import uuid4

import streamlit as st
from loguru import logger

from app.models.schema import MaterialInfo
from app.utils import utils

import task_runner


SUPPORTED_VIDEO_SOURCES = {"pexels", "pixabay", "coverr", "local", "douyin"}
LOCAL_MATERIAL_SOURCES = {"local"}


def is_douyin_material_configured(app_config: dict) -> bool:
    source_mode = str(app_config.get("douyin_material_source_mode", "direct") or "direct")
    if source_mode == "metadata":
        return bool(
            app_config.get("douyin_metadata_api_url", "")
            and app_config.get("douyin_resolver_api_url", "")
        )
    return bool(app_config.get("douyin_material_api_url", ""))


def get_generation_error_key(params, app_config: dict) -> str:
    if not params.video_subject and not params.video_script:
        return "Video Script and Subject Cannot Both Be Empty"

    if params.video_source not in SUPPORTED_VIDEO_SOURCES:
        return "Please Select a Valid Video Source"

    if params.video_source == "pexels" and not app_config.get("pexels_api_keys", ""):
        return "Please Enter the Pexels API Key"

    if params.video_source == "pixabay" and not app_config.get("pixabay_api_keys", ""):
        return "Please Enter the Pixabay API Key"

    if params.video_source == "coverr" and not app_config.get("coverr_api_keys", ""):
        return "Please Enter the Coverr API Key"

    if params.video_source == "douyin" and not is_douyin_material_configured(app_config):
        return "Please Configure the Douyin Material API"

    return ""


def persist_uploaded_audio(task_id: str, params, uploaded_audio_file):
    if not uploaded_audio_file:
        return

    task_dir = utils.task_dir(task_id)
    _, audio_ext = os.path.splitext(os.path.basename(uploaded_audio_file.name))
    audio_ext = audio_ext.lower() or ".mp3"
    custom_audio_path = os.path.join(task_dir, f"custom-audio{audio_ext}")
    with open(custom_audio_path, "wb") as f:
        f.write(uploaded_audio_file.getbuffer())
    params.custom_audio_file = custom_audio_path


def persist_uploaded_materials(params, uploaded_files, session_state):
    if uploaded_files:
        local_videos_dir = utils.storage_dir("local_videos", create=True)
        params.video_materials = []
        persisted_local_materials = []
        for file in uploaded_files:
            file_path = os.path.join(local_videos_dir, f"{file.file_id}_{file.name}")
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
                material = MaterialInfo()
                material.provider = (
                    params.video_source
                    if params.video_source in LOCAL_MATERIAL_SOURCES
                    else "local"
                )
                material.url = file_path
                params.video_materials.append(material)
                persisted_local_materials.append(
                    {
                        "provider": material.provider,
                        "url": material.url,
                        "duration": material.duration,
                    }
                )
        session_state["local_video_materials"] = persisted_local_materials
    elif params.video_source in LOCAL_MATERIAL_SOURCES and session_state["local_video_materials"]:
        params.video_materials = []
        for material in session_state["local_video_materials"]:
            material_info = MaterialInfo()
            material_info.provider = material.get("provider", params.video_source)
            material_info.url = material.get("url", "")
            material_info.duration = material.get("duration", 0)
            if material_info.url:
                params.video_materials.append(material_info)


def render_generation_controls(
    *,
    config,
    params,
    uploaded_audio_file,
    uploaded_files,
    tr,
    scroll_to_bottom,
):
    is_task_running = task_runner.is_running(st.session_state.get("active_task_id", ""))
    start_button = st.button(
        tr("Generate Video"),
        use_container_width=True,
        type="primary",
        disabled=is_task_running,
    )
    if not start_button:
        return

    config.save_config()
    task_id = str(uuid4())

    persist_uploaded_materials(params, uploaded_files, st.session_state)

    error_key = get_generation_error_key(params, config.app)
    if error_key:
        st.error(tr(error_key))
        scroll_to_bottom()
        st.stop()

    persist_uploaded_audio(task_id, params, uploaded_audio_file)

    st.toast(tr("Generating Video"))
    logger.info(tr("Start Generating Video"))
    logger.info(utils.to_json(params))
    task_runner.submit_task(task_id, params)
    st.session_state["active_task_id"] = task_id
    st.session_state["opened_task_folder_id"] = ""
    scroll_to_bottom()
    st.rerun()
