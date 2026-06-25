import sys
import unittest
import inspect
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "webui"))

from main_page import (
    SUPPORT_LOCALES,
    create_video_params,
    format_settings_toggle_label,
    get_main_page_column_weights,
    get_settings_content_column_weights,
    get_settings_toggle_column_weights,
    is_settings_row_expanded,
    set_settings_row_expanded,
    strip_streamlit_label_markup,
    render_main_page,
)


class TestWebuiMainPage(unittest.TestCase):
    def test_support_locales_include_russian(self):
        self.assertIn("ru-RU", SUPPORT_LOCALES)

    def test_create_video_params_reads_material_matching_state(self):
        params = create_video_params({"match_materials_to_script": True})

        self.assertTrue(params.match_materials_to_script)

    def test_create_video_params_defaults_material_matching_to_false(self):
        params = create_video_params({})

        self.assertFalse(params.match_materials_to_script)

    def test_main_page_column_weights_keep_work_area_balanced(self):
        weights = get_main_page_column_weights()

        self.assertEqual(len(weights), 4)
        self.assertGreater(weights[0], weights[3])
        self.assertGreaterEqual(weights[1], weights[3])
        self.assertGreaterEqual(weights[2], weights[3])

    def test_settings_toggle_row_uses_two_balanced_columns(self):
        self.assertEqual(get_settings_toggle_column_weights(), [1.0, 1.08])

    def test_settings_content_gives_basic_settings_more_room(self):
        weights = get_settings_content_column_weights()

        self.assertEqual(len(weights), 2)
        self.assertGreater(weights[0], weights[1])

    def test_settings_row_defaults_to_collapsed(self):
        self.assertFalse(is_settings_row_expanded({}))

    def test_settings_row_expanded_state_is_shared(self):
        session_state = {}

        set_settings_row_expanded(session_state, True)

        self.assertTrue(is_settings_row_expanded(session_state))

    def test_settings_toggle_label_removes_streamlit_markup_cleanly(self):
        self.assertEqual(
            strip_streamlit_label_markup("**基础设置** (:blue[点击展开])"),
            "基础设置",
        )
        self.assertEqual(
            format_settings_toggle_label("**基础设置** (:blue[点击展开])", True),
            "v 基础设置 (点击收起)",
        )

    def test_api_key_content_is_rendered_after_basic_settings_content(self):
        source = inspect.getsource(render_main_page)

        self.assertLess(
            source.index("basic_settings_col, api_key_col = st.columns"),
            source.index("render_basic_settings_content"),
        )
        self.assertLess(
            source.index("render_basic_settings_content"),
            source.index("render_api_key_content"),
        )
        self.assertLess(source.index("render_api_key_content"), source.index("script_panel"))
