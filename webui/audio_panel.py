import os
from uuid import uuid4

import streamlit as st

from app.services import voice
from app.utils import utils


def get_tts_servers(tr) -> list[tuple[str, str]]:
    return [
        (voice.NO_VOICE_NAME, tr("No Voice")),
        ("azure-tts-v1", "Azure TTS V1"),
        ("azure-tts-v2", "Azure TTS V2"),
        ("siliconflow", "SiliconFlow TTS"),
        ("gemini-tts", "Google Gemini TTS"),
        ("mimo-tts", "Xiaomi MiMo TTS"),
    ]


def get_saved_tts_server_index(tts_servers: list[tuple[str, str]], saved_tts_server: str) -> int:
    for i, (server_value, _) in enumerate(tts_servers):
        if server_value == saved_tts_server:
            return i
    return 0


def filter_voices_for_tts_server(selected_tts_server: str) -> list[str]:
    if selected_tts_server == voice.NO_VOICE_NAME:
        return [voice.NO_VOICE_NAME]
    if selected_tts_server == "siliconflow":
        return voice.get_siliconflow_voices()
    if selected_tts_server == "gemini-tts":
        return voice.get_gemini_voices()
    if selected_tts_server == "mimo-tts":
        return voice.get_mimo_voices()

    all_voices = voice.get_all_azure_voices(filter_locals=None)
    if selected_tts_server == "azure-tts-v2":
        return [v for v in all_voices if "V2" in v]
    return [v for v in all_voices if "V2" not in v]


def build_friendly_voice_names(filtered_voices: list[str], selected_tts_server: str, tr) -> dict[str, str]:
    if selected_tts_server == voice.NO_VOICE_NAME:
        return {voice.NO_VOICE_NAME: tr("No Voice")}
    return {
        v: v.replace("Female", tr("Female"))
        .replace("Male", tr("Male"))
        .replace("Neural", "")
        for v in filtered_voices
    }


def get_saved_voice_index(
    *,
    friendly_names: dict[str, str],
    filtered_voices: list[str],
    saved_voice_name: str,
    ui_language: str,
) -> int:
    if saved_voice_name in friendly_names:
        return list(friendly_names.keys()).index(saved_voice_name)

    for i, voice_name in enumerate(filtered_voices):
        if voice_name.lower().startswith(ui_language.lower()):
            return i

    return 0


def get_custom_audio_file_types() -> list[str]:
    custom_audio_file_types = ["mp3", "wav", "m4a", "aac", "flac", "ogg"]
    return custom_audio_file_types + [
        file_type.upper() for file_type in custom_audio_file_types
    ]


def get_value_index(values: list, saved_value, default: int = 0) -> int:
    if saved_value in values:
        return values.index(saved_value)
    return default


def get_option_value_index(
    options: list[tuple[str, str]],
    saved_value: str,
    default: int = 0,
) -> int:
    for i, (_, value) in enumerate(options):
        if value == saved_value:
            return i
    return default


def render_audio_panel(*, config, params, tr):
    uploaded_audio_file = None

    with st.container(border=True):
        st.write(tr("Audio Settings"))

        tts_servers = get_tts_servers(tr)
        saved_tts_server = config.ui.get("tts_server", "azure-tts-v1")
        saved_tts_server_index = get_saved_tts_server_index(
            tts_servers, saved_tts_server
        )

        selected_tts_server_index = st.selectbox(
            tr("TTS Servers"),
            options=range(len(tts_servers)),
            format_func=lambda x: tts_servers[x][1],
            index=saved_tts_server_index,
        )

        selected_tts_server = tts_servers[selected_tts_server_index][0]
        config.ui["tts_server"] = selected_tts_server

        filtered_voices = filter_voices_for_tts_server(selected_tts_server)
        friendly_names = build_friendly_voice_names(
            filtered_voices, selected_tts_server, tr
        )

        saved_voice_name = config.ui.get("voice_name", "")
        saved_voice_name_index = get_saved_voice_index(
            friendly_names=friendly_names,
            filtered_voices=filtered_voices,
            saved_voice_name=saved_voice_name,
            ui_language=st.session_state["ui_language"],
        )

        if saved_voice_name_index >= len(friendly_names) and friendly_names:
            saved_voice_name_index = 0

        voice_name = ""
        if friendly_names:
            selected_friendly_name = st.selectbox(
                tr("Speech Synthesis"),
                options=list(friendly_names.values()),
                index=min(saved_voice_name_index, len(friendly_names) - 1),
            )

            voice_name = list(friendly_names.keys())[
                list(friendly_names.values()).index(selected_friendly_name)
            ]
            params.voice_name = voice_name
            config.ui["voice_name"] = voice_name
        else:
            st.warning(
                tr(
                    "No voices available for the selected TTS server. Please select another server."
                )
            )
            params.voice_name = ""
            config.ui["voice_name"] = ""

        if (
            friendly_names
            and selected_tts_server != voice.NO_VOICE_NAME
            and st.button(tr("Play Voice"))
        ):
            play_content = params.video_subject
            if not play_content:
                play_content = params.video_script
            if not play_content:
                play_content = tr("Voice Example")
            with st.spinner(tr("Synthesizing Voice")):
                temp_dir = utils.storage_dir("temp", create=True)
                audio_file = os.path.join(temp_dir, f"tmp-voice-{str(uuid4())}.mp3")
                sub_maker = voice.tts(
                    text=play_content,
                    voice_name=voice_name,
                    voice_rate=params.voice_rate,
                    voice_file=audio_file,
                    voice_volume=params.voice_volume,
                )
                if not sub_maker:
                    play_content = "This is a example voice. if you hear this, the voice synthesis failed with the original content."
                    sub_maker = voice.tts(
                        text=play_content,
                        voice_name=voice_name,
                        voice_rate=params.voice_rate,
                        voice_file=audio_file,
                        voice_volume=params.voice_volume,
                    )

                if sub_maker and os.path.exists(audio_file):
                    st.audio(audio_file, format="audio/mp3")
                    if os.path.exists(audio_file):
                        os.remove(audio_file)

        if selected_tts_server == "azure-tts-v2" or (
            voice_name and voice.is_azure_v2_voice(voice_name)
        ):
            saved_azure_speech_region = config.azure.get("speech_region", "")
            saved_azure_speech_key = config.azure.get("speech_key", "")
            azure_speech_region = st.text_input(
                tr("Speech Region"),
                value=saved_azure_speech_region,
                key="azure_speech_region_input",
            )
            azure_speech_key = st.text_input(
                tr("Speech Key"),
                value=saved_azure_speech_key,
                type="password",
                key="azure_speech_key_input",
            )
            config.azure["speech_region"] = azure_speech_region
            config.azure["speech_key"] = azure_speech_key

        if selected_tts_server == "siliconflow" or (
            voice_name and voice.is_siliconflow_voice(voice_name)
        ):
            saved_siliconflow_api_key = config.siliconflow.get("api_key", "")

            siliconflow_api_key = st.text_input(
                tr("SiliconFlow API Key"),
                value=saved_siliconflow_api_key,
                type="password",
                key="siliconflow_api_key_input",
            )

            st.info(
                tr("SiliconFlow TTS Settings")
                + ":\n"
                + "- "
                + tr("Speed: Range [0.25, 4.0], default is 1.0")
                + "\n"
                + "- "
                + tr("Volume: Uses Speech Volume setting, default 1.0 maps to gain 0")
            )

            config.siliconflow["api_key"] = siliconflow_api_key

        if selected_tts_server == "mimo-tts" or (
            voice_name and voice.is_mimo_voice(voice_name)
        ):
            saved_mimo_api_key = config.app.get("mimo_api_key", "")

            mimo_api_key = st.text_input(
                tr("MiMo API Key"),
                value=saved_mimo_api_key,
                type="password",
                key="mimo_tts_api_key_input",
            )

            st.info(
                tr("MiMo TTS Settings")
                + ":\n"
                + "- "
                + tr("Uses Xiaomi MiMo V2.5 TTS preset voices")
                + "\n"
                + "- "
                + tr("Speed and volume are currently handled by the provider defaults")
            )

            config.app["mimo_api_key"] = mimo_api_key

        voice_volume_options = [0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0, 4.0, 5.0]
        params.voice_volume = st.selectbox(
            tr("Speech Volume"),
            options=voice_volume_options,
            index=get_value_index(
                voice_volume_options,
                config.ui.get("voice_volume", 1.0),
                default=2,
            ),
        )
        config.ui["voice_volume"] = params.voice_volume

        voice_rate_options = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5, 1.8, 2.0]
        params.voice_rate = st.selectbox(
            tr("Speech Rate"),
            options=voice_rate_options,
            index=get_value_index(
                voice_rate_options,
                config.ui.get("voice_rate", 1.0),
                default=2,
            ),
        )
        config.ui["voice_rate"] = params.voice_rate

        uploaded_audio_file = st.file_uploader(
            tr("Custom Audio File"),
            type=get_custom_audio_file_types(),
            accept_multiple_files=False,
            key="custom_audio_file_uploader",
        )
        if uploaded_audio_file:
            st.audio(uploaded_audio_file, format="audio/mp3")
            st.info(
                tr(
                    "Custom audio will be used directly. TTS synthesis will be skipped for this task."
                )
            )

        bgm_options = [
            (tr("No Background Music"), ""),
            (tr("Random Background Music"), "random"),
            (tr("Custom Background Music"), "custom"),
        ]
        selected_index = st.selectbox(
            tr("Background Music"),
            index=get_option_value_index(
                bgm_options,
                config.ui.get("bgm_type", "random"),
                default=1,
            ),
            options=range(len(bgm_options)),
            format_func=lambda x: bgm_options[x][0],
        )
        params.bgm_type = bgm_options[selected_index][1]
        config.ui["bgm_type"] = params.bgm_type

        if params.bgm_type == "custom":
            custom_bgm_file = st.text_input(
                tr("Custom Background Music File"),
                value=st.session_state.get("custom_bgm_file_input", ""),
                key="custom_bgm_file_input",
            )
            if custom_bgm_file:
                params.bgm_file = custom_bgm_file.strip()

        bgm_volume_options = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        params.bgm_volume = st.selectbox(
            tr("Background Music Volume"),
            options=bgm_volume_options,
            index=get_value_index(
                bgm_volume_options,
                config.ui.get("bgm_volume", 0.2),
                default=2,
            ),
        )
        config.ui["bgm_volume"] = params.bgm_volume

    return uploaded_audio_file
