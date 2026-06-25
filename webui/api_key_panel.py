import streamlit as st

from api_key_manager import render_api_key_manager


def render_api_key_panel(*, config, tr):
    with st.expander(tr("Click to show API Key management"), expanded=False):
        render_api_key_content(config=config, tr=tr)


def render_api_key_content(*, config, tr):
    st.subheader(tr("Manage Pexels, Pixabay and Coverr API Keys"))

    col1, col2, col3 = st.tabs(
        [
            tr("Pexels API Keys"),
            tr("Pixabay API Keys"),
            tr("Coverr API Keys"),
        ]
    )

    with col1:
        render_api_key_manager(
            config=config,
            config_key="pexels_api_keys",
            title_key="Pexels API Keys",
            empty_key="No Pexels API Keys currently",
            add_key="Add Pexels API Key",
            add_success_key="Pexels API Key added successfully",
            select_delete_key="Select Pexels API Key to delete",
            delete_button_key="Delete Selected Pexels API Key",
            delete_success_key="Pexels API Key deleted successfully",
            widget_prefix="pexels",
            tr=tr,
        )

    with col2:
        render_api_key_manager(
            config=config,
            config_key="pixabay_api_keys",
            title_key="Pixabay API Keys",
            empty_key="No Pixabay API Keys currently",
            add_key="Add Pixabay API Key",
            add_success_key="Pixabay API Key added successfully",
            select_delete_key="Select Pixabay API Key to delete",
            delete_button_key="Delete Selected Pixabay API Key",
            delete_success_key="Pixabay API Key deleted successfully",
            widget_prefix="pixabay",
            tr=tr,
        )

    with col3:
        render_api_key_manager(
            config=config,
            config_key="coverr_api_keys",
            title_key="Coverr API Keys",
            empty_key="No Coverr API Keys currently",
            add_key="Add Coverr API Key",
            add_success_key="Coverr API Key added successfully",
            select_delete_key="Select Coverr API Key to delete",
            delete_button_key="Delete Selected Coverr API Key",
            delete_success_key="Coverr API Key deleted successfully",
            widget_prefix="coverr",
            tr=tr,
        )
