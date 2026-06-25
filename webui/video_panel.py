import streamlit as st

from app.models.schema import VideoAspect, VideoConcatMode, VideoTransitionMode


LOCAL_MATERIAL_SOURCES = {"local"}


def get_option_index(options: list[tuple[str, str]], saved_value: str, default: int = 0) -> int:
    values = [value for _, value in options]
    if saved_value in values:
        return values.index(saved_value)
    return default


def get_local_file_upload_types() -> list[str]:
    local_file_types = ["mp4", "mov", "avi", "flv", "mkv", "jpg", "jpeg", "png"]
    return local_file_types + [file_type.upper() for file_type in local_file_types]


def get_default_aspect_index(video_source: str) -> int:
    return 1 if video_source == "coverr" else 0


def get_video_codec_options() -> list[tuple[str, str]]:
    return [
        ("libx264 (CPU)", "libx264"),
        ("NVIDIA NVENC (h264_nvenc)", "h264_nvenc"),
        ("AMD AMF (h264_amf)", "h264_amf"),
        ("Intel QSV (h264_qsv)", "h264_qsv"),
        ("Windows MediaFoundation (h264_mf)", "h264_mf"),
        ("macOS VideoToolbox (h264_videotoolbox)", "h264_videotoolbox"),
    ]


def get_value_index(values: list, saved_value, default: int = 0) -> int:
    if saved_value in values:
        return values.index(saved_value)
    return default


def render_video_panel(*, config, params, tr):
    uploaded_files = []

    with st.container(border=True):
        st.write(tr("Video Settings"))
        video_concat_modes = [
            (tr("Sequential"), "sequential"),
            (tr("Random"), "random"),
        ]
        video_sources = [
            (tr("Pexels"), "pexels"),
            (tr("Pixabay"), "pixabay"),
            (tr("Coverr"), "coverr"),
            (tr("Local file"), "local"),
            (tr("TikTok"), "douyin"),
            (tr("Bilibili"), "bilibili"),
            (tr("Xiaohongshu"), "xiaohongshu"),
        ]

        saved_video_source_name = config.app.get("video_source", "pexels")
        saved_video_source_index = get_option_index(video_sources, saved_video_source_name)

        selected_index = st.selectbox(
            tr("Video Source"),
            options=range(len(video_sources)),
            format_func=lambda x: video_sources[x][0],
            index=saved_video_source_index,
        )
        params.video_source = video_sources[selected_index][1]
        config.app["video_source"] = params.video_source

        if params.video_source in LOCAL_MATERIAL_SOURCES:
            uploaded_files = st.file_uploader(
                tr("Upload Local Files"),
                type=get_local_file_upload_types(),
                accept_multiple_files=True,
            )
        elif params.video_source == "douyin":
            st.caption(tr("Douyin Material API Help"))

        selected_index = st.selectbox(
            tr("Video Concat Mode"),
            index=get_option_index(
                video_concat_modes,
                config.app.get("video_concat_mode", "random"),
                default=1,
            ),
            options=range(len(video_concat_modes)),
            format_func=lambda x: video_concat_modes[x][0],
        )
        params.video_concat_mode = VideoConcatMode(video_concat_modes[selected_index][1])
        config.app["video_concat_mode"] = params.video_concat_mode.value

        video_transition_modes = [
            (tr("None"), VideoTransitionMode.none.value),
            (tr("Shuffle"), VideoTransitionMode.shuffle.value),
            (tr("FadeIn"), VideoTransitionMode.fade_in.value),
            (tr("FadeOut"), VideoTransitionMode.fade_out.value),
            (tr("SlideIn"), VideoTransitionMode.slide_in.value),
            (tr("SlideOut"), VideoTransitionMode.slide_out.value),
        ]
        selected_index = st.selectbox(
            tr("Video Transition Mode"),
            options=range(len(video_transition_modes)),
            format_func=lambda x: video_transition_modes[x][0],
            index=get_option_index(
                video_transition_modes,
                config.app.get("video_transition_mode", VideoTransitionMode.none.value),
            ),
        )
        params.video_transition_mode = VideoTransitionMode(
            video_transition_modes[selected_index][1]
        )
        config.app["video_transition_mode"] = params.video_transition_mode.value

        video_aspect_ratios = [
            (tr("Portrait"), VideoAspect.portrait.value),
            (tr("Landscape"), VideoAspect.landscape.value),
        ]
        selected_index = st.selectbox(
            tr("Video Ratio"),
            options=range(len(video_aspect_ratios)),
            format_func=lambda x: video_aspect_ratios[x][0],
            index=get_option_index(
                video_aspect_ratios,
                config.app.get("video_aspect", ""),
                default=get_default_aspect_index(params.video_source),
            ),
            key=f"video_aspect_for_{params.video_source}",
        )
        params.video_aspect = VideoAspect(video_aspect_ratios[selected_index][1])
        config.app["video_aspect"] = params.video_aspect.value

        clip_duration_options = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        params.video_clip_duration = st.selectbox(
            tr("Clip Duration"),
            options=clip_duration_options,
            index=get_value_index(
                clip_duration_options,
                config.app.get("video_clip_duration", 3),
                default=1,
            ),
        )
        config.app["video_clip_duration"] = params.video_clip_duration

        video_count_options = [1, 2, 3, 4, 5]
        params.video_count = st.selectbox(
            tr("Number of Videos Generated Simultaneously"),
            options=video_count_options,
            index=get_value_index(
                video_count_options,
                config.app.get("video_count", 1),
            ),
        )
        config.app["video_count"] = params.video_count

        with st.expander(
            tr("Advanced Video Settings"),
            expanded=bool(st.session_state.get("expand_advanced_video_settings", False)),
        ):
            params.match_materials_to_script = st.checkbox(
                tr("Match Materials to Script Order"),
                help=tr("Match Materials to Script Order Help"),
                key="match_materials_to_script",
            )
            config.app["match_materials_to_script"] = params.match_materials_to_script

            video_codec_options = get_video_codec_options()
            saved_video_codec = config.app.get("video_codec", "libx264")
            selected_codec_index = get_option_index(video_codec_options, saved_video_codec)
            selected_codec_index = st.selectbox(
                tr("Video Encoder"),
                options=range(len(video_codec_options)),
                index=selected_codec_index,
                format_func=lambda x: video_codec_options[x][0],
                help=tr("Video Encoder Help"),
            )
            config.app["video_codec"] = video_codec_options[selected_codec_index][1]

    return uploaded_files
