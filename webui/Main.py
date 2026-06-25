import os
import sys

import streamlit as st

# Add the root directory of the project to the system path to allow importing modules from the project
root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)
    print("******** sys.path ********")
    print(sys.path)
    print("")

from app.config import config
from app.services import llm
from app.utils import utils

from main_page import render_main_page
from session_state import init_session_state
from theme import apply_streamlit_style
from webui_utils import init_log

st.set_page_config(
    page_title="MoneyPrinterTurbo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "Report a bug": "https://github.com/harry0703/MoneyPrinterTurbo/issues",
        "About": "# MoneyPrinterTurbo\nSimply provide a topic or keyword for a video, and it will "
        "automatically generate the video copy, video materials, video subtitles, "
        "and video background music before synthesizing a high-definition short "
        "video.\n\nhttps://github.com/harry0703/MoneyPrinterTurbo",
    },
)

apply_streamlit_style()

# 定义资源目录
font_dir = os.path.join(root_dir, "resource", "fonts")
i18n_dir = os.path.join(root_dir, "webui", "i18n")
system_locale = utils.get_system_locale()

init_session_state(
    st.session_state,
    app_config=config.app,
    ui_config=config.ui,
    system_locale=system_locale,
    default_system_prompt=llm.DEFAULT_SCRIPT_SYSTEM_PROMPT,
)

# 加载语言文件
locales = utils.load_locales(i18n_dir)


init_log(root_dir)


def tr(key):
    loc = locales.get(st.session_state["ui_language"], {})
    return loc.get("Translation", {}).get(key, key)

render_main_page(
    config=config,
    root_dir=root_dir,
    font_dir=font_dir,
    locales=locales,
    tr=tr,
)

config.save_config()
