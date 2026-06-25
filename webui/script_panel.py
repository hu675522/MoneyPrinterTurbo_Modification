import streamlit as st

from app.services import llm


COMPACT_TEXT_AREA_HEIGHT = 68


def build_video_language_options(support_locales: list[str], tr) -> list[tuple[str, str]]:
    video_languages = [(tr("Auto Detect"), "")]
    for code in support_locales:
        video_languages.append((code, code))
    return video_languages


def get_compact_text_area_height() -> int:
    return COMPACT_TEXT_AREA_HEIGHT


def format_script_generation_button_label(label: str) -> str:
    label = label.replace("**", "")
    return label.replace(
        "生成 【视频文案】 和 【视频关键词】",
        "\n生成【视频文案】和【视频关键词】",
    )


def render_script_panel(*, params, support_locales: list[str], tr):
    with st.container(border=True):
        st.write(tr("Video Script Settings"))
        params.video_subject = st.text_input(
            tr("Video Subject"),
            key="video_subject",
        ).strip()

        video_languages = build_video_language_options(support_locales, tr)
        selected_index = st.selectbox(
            tr("Script Language"),
            index=0,
            options=range(len(video_languages)),
            format_func=lambda x: video_languages[x][0],
        )
        params.video_language = video_languages[selected_index][1]

        with st.expander(
            tr("Advanced Script Settings"),
            expanded=bool(st.session_state.get("expand_advanced_script_settings", False)),
        ):
            params.paragraph_number = st.slider(
                tr("Script Paragraph Number"),
                min_value=llm.MIN_SCRIPT_PARAGRAPH_NUMBER,
                max_value=llm.MAX_SCRIPT_PARAGRAPH_NUMBER,
                value=st.session_state.get("paragraph_number_input", 1),
                key="paragraph_number_input",
            )
            params.video_script_prompt = st.text_area(
                tr("Custom Script Requirements"),
                height=100,
                max_chars=llm.MAX_SCRIPT_PROMPT_LENGTH,
                placeholder=tr("Custom Script Requirements Placeholder"),
                key="video_script_prompt",
            ).strip()

            use_custom_system_prompt = st.checkbox(
                tr("Use Custom System Prompt"),
                help=tr("Use Custom System Prompt Help"),
                key="use_custom_system_prompt",
            )

            if use_custom_system_prompt:
                custom_system_prompt = st.text_area(
                    tr("Custom System Prompt"),
                    height=240,
                    max_chars=llm.MAX_SCRIPT_SYSTEM_PROMPT_LENGTH,
                    key="custom_system_prompt",
                ).strip()
                params.custom_system_prompt = custom_system_prompt
            else:
                params.custom_system_prompt = ""

        if st.button(
            format_script_generation_button_label(
                tr("Generate Video Script and Keywords")
            ),
            key="auto_generate_script",
        ):
            with st.spinner(tr("Generating Video Script and Keywords")):
                script = llm.generate_script(
                    video_subject=params.video_subject,
                    language=params.video_language,
                    paragraph_number=params.paragraph_number,
                    video_script_prompt=params.video_script_prompt,
                    custom_system_prompt=params.custom_system_prompt,
                )
                terms = llm.generate_terms(
                    params.video_subject,
                    script,
                    amount=8 if params.match_materials_to_script else 5,
                    match_script_order=params.match_materials_to_script,
                )
                if "Error: " in script:
                    st.error(tr(script))
                elif "Error: " in terms:
                    st.error(tr(terms))
                else:
                    st.session_state["video_script"] = script
                    st.session_state["video_terms"] = ", ".join(terms)

        params.video_script = st.text_area(
            tr("Video Script"),
            value=st.session_state["video_script"],
            height=get_compact_text_area_height(),
        )
        if st.button(tr("Generate Video Keywords"), key="auto_generate_terms"):
            if not params.video_script:
                st.error(tr("Please Enter the Video Subject"))
                st.stop()

            with st.spinner(tr("Generating Video Keywords")):
                terms = llm.generate_terms(
                    params.video_subject,
                    params.video_script,
                    amount=8 if params.match_materials_to_script else 5,
                    match_script_order=params.match_materials_to_script,
                )
                if "Error: " in terms:
                    st.error(tr(terms))
                else:
                    st.session_state["video_terms"] = ", ".join(terms)

        params.video_terms = st.text_area(
            tr("Video Keywords"),
            value=st.session_state["video_terms"],
            height=get_compact_text_area_height(),
        )
