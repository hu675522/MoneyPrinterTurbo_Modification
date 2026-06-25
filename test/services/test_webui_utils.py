import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "webui"))

from webui_utils import (
    get_all_fonts,
    get_all_songs,
    list_files_by_suffix,
    resolve_task_folder,
)


class TestWebuiUtils(unittest.TestCase):
    def test_list_files_by_suffix_filters_and_sorts_names(self):
        temp_dir = tempfile.mkdtemp()
        try:
            for name in ["b.ttc", "a.ttf", "ignored.txt"]:
                Path(temp_dir, name).write_text("x", encoding="utf-8")

            self.assertEqual(
                list_files_by_suffix(temp_dir, (".ttf", ".ttc")),
                ["a.ttf", "b.ttc"],
            )
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_get_all_fonts_and_songs_filter_expected_suffixes(self):
        temp_dir = tempfile.mkdtemp()
        try:
            for name in ["font.ttf", "font.ttc", "song.mp3", "image.png"]:
                Path(temp_dir, name).write_text("x", encoding="utf-8")

            self.assertEqual(get_all_fonts(temp_dir), ["font.ttc", "font.ttf"])
            self.assertEqual(get_all_songs(temp_dir), ["song.mp3"])
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_resolve_task_folder_requires_uuid(self):
        with self.assertRaises(ValueError):
            resolve_task_folder(str(ROOT_DIR), "../bad")

    def test_resolve_task_folder_stays_under_tasks_root(self):
        task_id = "11111111-1111-1111-1111-111111111111"
        expected_path = os.path.abspath(
            os.path.join(str(ROOT_DIR), "storage", "tasks", task_id)
        )

        self.assertEqual(resolve_task_folder(str(ROOT_DIR), task_id), expected_path)
