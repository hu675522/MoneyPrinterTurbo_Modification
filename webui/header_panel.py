import streamlit as st


def get_language_options(locales: dict, current_language: str) -> tuple[list[str], int]:
    display_languages = []
    selected_index = 0
    for i, code in enumerate(locales.keys()):
        display_languages.append(f"{code} - {locales[code].get('Language')}")
        if code == current_language:
            selected_index = i
    return display_languages, selected_index


def render_header(*, project_version: str, locales: dict, config):
    title_col, lang_col = st.columns([3, 1])

    with title_col:
        st.title(f"MoneyPrinterTurbo v{project_version}")

    with lang_col:
        display_languages, selected_index = get_language_options(
            locales, st.session_state.get("ui_language", "")
        )
        selected_language = st.selectbox(
            "Language / 语言",
            options=display_languages,
            index=selected_index,
            key="top_language_selector",
            label_visibility="collapsed",
        )
        if selected_language:
            code = selected_language.split(" - ")[0].strip()
            st.session_state["ui_language"] = code
            config.ui["language"] = code
