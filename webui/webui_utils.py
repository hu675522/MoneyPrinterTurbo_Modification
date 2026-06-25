import os
import sys
import webbrowser
from uuid import UUID

import streamlit as st
from loguru import logger


def list_files_by_suffix(directory: str, suffixes: tuple[str, ...]) -> list[str]:
    files_found = []
    for _, _, files in os.walk(directory):
        for file in files:
            if file.endswith(suffixes):
                files_found.append(file)
    files_found.sort()
    return files_found


def get_all_fonts(font_dir: str) -> list[str]:
    return list_files_by_suffix(font_dir, (".ttf", ".ttc"))


def get_all_songs(song_dir: str) -> list[str]:
    return list_files_by_suffix(song_dir, (".mp3",))


def resolve_task_folder(root_dir: str, task_id: str) -> str:
    normalized_task_id = str(UUID(str(task_id)))
    tasks_root = os.path.abspath(os.path.join(root_dir, "storage", "tasks"))
    path = os.path.abspath(os.path.join(tasks_root, normalized_task_id))

    if not path.startswith(tasks_root + os.sep):
        raise ValueError(f"invalid task folder path: {path}")
    return path


def open_task_folder(root_dir: str, task_id: str):
    try:
        path = resolve_task_folder(root_dir, task_id)
        if os.path.isdir(path):
            webbrowser.open(f"file://{path}")
    except Exception as e:
        logger.error(e)


def scroll_to_bottom():
    js = """
    <script>
        console.log("scroll_to_bottom");
        function scroll(dummy_var_to_force_repeat_execution){
            var sections = parent.document.querySelectorAll('section.main');
            console.log(sections);
            for(let index = 0; index<sections.length; index++) {
                sections[index].scrollTop = sections[index].scrollHeight;
            }
        }
        scroll(1);
    </script>
    """
    st.components.v1.html(js, height=0, width=0)


def init_log(root_dir: str):
    logger.remove()
    log_level = "DEBUG"

    def format_record(record):
        file_path = record["file"].path
        relative_path = os.path.relpath(file_path, root_dir)
        record["file"].path = f"./{relative_path}"
        record["message"] = record["message"].replace(root_dir, ".")

        return (
            "<green>{time:%Y-%m-%d %H:%M:%S}</> | "
            + "<level>{level}</> | "
            + '"{file.path}:{line}":<blue> {function}</> '
            + "- <level>{message}</>"
            + "\n"
        )

    logger.add(
        sys.stdout,
        level=log_level,
        format=format_record,
        colorize=True,
    )
