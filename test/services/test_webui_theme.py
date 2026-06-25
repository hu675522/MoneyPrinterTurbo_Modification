import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "webui"))

from theme import get_streamlit_style, get_streamlit_theme_sync_script


class TestWebuiTheme(unittest.TestCase):
    def test_theme_uses_compact_panel_and_control_styling(self):
        css = get_streamlit_style()

        self.assertIn("border-radius: 8px", css)
        self.assertIn("min-height: 2.35rem", css)
        self.assertIn("max-width: 1500px", css)
        self.assertIn("padding-top: 4rem", css)
        self.assertIn("gap: 0.65rem", css)
        self.assertIn("border-top: 3px solid var(--mpt-accent)", css)
        self.assertIn("padding: 0.75rem 0.9rem", css)
        self.assertIn("padding: 0 !important", css)
        self.assertIn("data-testid=\"stWidgetLabel\"", css)
        self.assertIn("data-testid=\"stVerticalBlock\"", css)
        self.assertIn("data-testid=\"stMarkdownContainer\"", css)
        self.assertIn("white-space: pre-line", css)
        self.assertIn("overflow-wrap: anywhere", css)
        self.assertIn(".stButton > button", css)
        self.assertIn("background: var(--mpt-action)", css)
        self.assertIn("color: #ffffff !important", css)
        self.assertIn(".stButton > button p", css)
        self.assertIn(".stButton > button span", css)
        self.assertIn("0 6px 14px var(--mpt-action-shadow)", css)

    def test_theme_styles_primary_action_button_like_video_cta(self):
        css = get_streamlit_style()

        self.assertIn("--mpt-action: #0996d8", css)
        self.assertIn("--mpt-action-border: #39c9f4", css)
        self.assertIn("button[kind=\"primary\"]::before", css)
        self.assertIn("border: 2px solid currentColor", css)
        self.assertIn("0 8px 18px var(--mpt-action-shadow)", css)
        self.assertIn("text-shadow: 0 1px 1px", css)

    def test_theme_keeps_slider_values_on_one_line(self):
        css = get_streamlit_style()

        self.assertIn('data-testid="stSlider"', css)
        self.assertIn('data-baseweb="slider"', css)
        self.assertIn("white-space: nowrap !important", css)
        self.assertIn("word-break: normal !important", css)

    def test_theme_styles_task_history_page_indicator(self):
        css = get_streamlit_style()

        self.assertIn(".mpt-page-indicator", css)
        self.assertIn("min-height: 2.45rem", css)
        self.assertIn("font-size: 0.76rem", css)

    def test_theme_styles_active_task_summary_pills(self):
        css = get_streamlit_style()

        self.assertIn(".mpt-task-summary-pill", css)
        self.assertIn("gap: 0.12rem", css)
        self.assertIn("font-size: 0.72rem", css)

    def test_theme_styles_empty_states(self):
        css = get_streamlit_style()

        self.assertIn(".mpt-empty-state", css)
        self.assertIn("border: 1px dashed var(--mpt-border-strong)", css)
        self.assertIn("min-height: 4.75rem", css)

    def test_theme_has_responsive_column_breakpoints(self):
        css = get_streamlit_style()

        self.assertIn("@media (max-width: 1100px)", css)
        self.assertIn("@media (max-width: 700px)", css)
        self.assertIn("flex-wrap: wrap", css)
        self.assertIn("min-width: calc(50% - 0.75rem)", css)
        self.assertIn("min-width: 100%", css)

    def test_theme_has_light_and_dark_color_tokens(self):
        css = get_streamlit_style()

        self.assertIn("--mpt-bg: #edf4f8", css)
        self.assertIn("--mpt-bg: #0e1726", css)
        self.assertIn("prefers-color-scheme: dark", css)
        self.assertIn("data-theme=\"dark\"", css)
        self.assertIn("--mpt-field-focus", css)
        self.assertIn("var(--background-color", css)
        self.assertIn("var(--secondary-background-color", css)
        self.assertIn("var(--text-color", css)
        self.assertIn("data-testid=\"stAppViewContainer\"", css)
        self.assertIn("data-mpt-theme=\"dark\"", css)
        self.assertIn("data-mpt-theme=\"light\"", css)

    def test_theme_sync_script_tracks_streamlit_toolbar_dark_state(self):
        script = get_streamlit_theme_sync_script()

        self.assertIn("header[data-testid=\"stHeader\"]", script)
        self.assertIn("div[data-testid=\"stToolbar\"]", script)
        self.assertIn("data-mpt-theme", script)
        self.assertIn("localStorage", script)
        self.assertIn("getStoredTheme", script)
        self.assertIn("getSystemTheme", script)
        self.assertIn("prefers-color-scheme: dark", script)
        self.assertIn('text.includes("system")', script)
        self.assertIn('getAttribute("data-mpt-theme") !== theme', script)
        self.assertIn("setInterval(syncTheme, 600)", script)

    def test_theme_avoids_unstable_visual_patterns(self):
        css = get_streamlit_style().lower()

        self.assertNotIn("letter-spacing: -", css)
        self.assertNotIn("linear-gradient", css)
        self.assertNotIn("radial-gradient", css)
        self.assertNotIn("vw", css)


if __name__ == "__main__":
    unittest.main()
