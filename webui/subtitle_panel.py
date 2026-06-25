import streamlit as st

from webui_utils import get_all_fonts


def get_option_index(
    options: list[tuple[str, str]],
    saved_value: str,
    default: int = 0,
) -> int:
    for i, (_, value) in enumerate(options):
        if value == saved_value:
            return i
    return default


def get_value_index(values: list[str], saved_value: str, default: int = 0) -> int:
    if saved_value in values:
        return values.index(saved_value)
    return default


def parse_custom_position(raw_value: str) -> tuple[float | None, str | None]:
    try:
        position = float(raw_value)
    except ValueError:
        return None, "Please enter a valid number"

    if position < 0 or position > 100:
        return None, "Please enter a value between 0 and 100"

    return position, None


def render_subtitle_panel(*, config, params, font_dir: str, tr):
    with st.container(border=True):
        st.write(tr("Subtitle Settings"))
        params.subtitle_enabled = st.checkbox(tr("Enable Subtitles"), value=True)

        font_names = get_all_fonts(font_dir)
        saved_font_name = config.ui.get("font_name", "MicrosoftYaHeiBold.ttc")
        saved_font_name_index = get_value_index(font_names, saved_font_name)
        params.font_name = st.selectbox(
            tr("Font"), font_names, index=saved_font_name_index
        )
        config.ui["font_name"] = params.font_name

        subtitle_positions = [
            (tr("Top"), "top"),
            (tr("Center"), "center"),
            (tr("Bottom"), "bottom"),
            (tr("Custom"), "custom"),
        ]
        saved_subtitle_position = config.ui.get("subtitle_position", "bottom")
        saved_position_index = get_option_index(
            subtitle_positions,
            saved_subtitle_position,
            default=2,
        )
        selected_index = st.selectbox(
            tr("Position"),
            index=saved_position_index,
            options=range(len(subtitle_positions)),
            format_func=lambda x: subtitle_positions[x][0],
        )
        params.subtitle_position = subtitle_positions[selected_index][1]
        config.ui["subtitle_position"] = params.subtitle_position

        if params.subtitle_position == "custom":
            saved_custom_position = config.ui.get("custom_position", 70.0)
            custom_position = st.text_input(
                tr("Custom Position (% from top)"),
                value=str(saved_custom_position),
                key="custom_position_input",
            )
            parsed_position, error_key = parse_custom_position(custom_position)
            if error_key:
                st.error(tr(error_key))
            else:
                params.custom_position = parsed_position
                config.ui["custom_position"] = params.custom_position

        font_cols = st.columns([0.3, 0.7])
        with font_cols[0]:
            saved_text_fore_color = config.ui.get("text_fore_color", "#FFFFFF")
            params.text_fore_color = st.color_picker(
                tr("Font Color"), saved_text_fore_color
            )
            config.ui["text_fore_color"] = params.text_fore_color

        with font_cols[1]:
            saved_font_size = config.ui.get("font_size", 60)
            params.font_size = st.slider(tr("Font Size"), 30, 100, saved_font_size)
            config.ui["font_size"] = params.font_size

        stroke_cols = st.columns([0.3, 0.7])
        with stroke_cols[0]:
            params.stroke_color = st.color_picker(tr("Stroke Color"), "#000000")
        with stroke_cols[1]:
            params.stroke_width = st.slider(tr("Stroke Width"), 0.0, 10.0, 1.5)

        subtitle_bg_cols = st.columns([0.4, 0.6])
        saved_subtitle_background_enabled = config.ui.get(
            "subtitle_background_enabled", True
        )
        with subtitle_bg_cols[0]:
            subtitle_background_enabled = st.checkbox(
                tr("Enable Subtitle Background"),
                value=saved_subtitle_background_enabled,
            )
        config.ui["subtitle_background_enabled"] = subtitle_background_enabled
        if subtitle_background_enabled:
            with subtitle_bg_cols[1]:
                saved_subtitle_background_color = config.ui.get(
                    "subtitle_background_color", "#000000"
                )
                params.text_background_color = st.color_picker(
                    tr("Subtitle Background Color"),
                    saved_subtitle_background_color,
                )
                config.ui["subtitle_background_color"] = params.text_background_color
        else:
            params.text_background_color = False

        saved_rounded_subtitle_background = config.ui.get(
            "rounded_subtitle_background", False
        )
        params.rounded_subtitle_background = st.checkbox(
            tr("Rounded Subtitle Background"),
            value=(
                saved_rounded_subtitle_background
                if subtitle_background_enabled
                else False
            ),
            help=tr("Rounded Subtitle Background Help"),
            disabled=not subtitle_background_enabled,
        )
        if subtitle_background_enabled:
            config.ui["rounded_subtitle_background"] = (
                params.rounded_subtitle_background
            )
