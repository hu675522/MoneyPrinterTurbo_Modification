def init_session_state(
    session_state,
    *,
    app_config: dict,
    ui_config: dict,
    system_locale: str,
    default_system_prompt: str,
):
    defaults = {
        "video_subject": "",
        "video_script": "",
        "video_terms": "",
        "video_script_prompt": "",
        "custom_system_prompt": default_system_prompt,
        "use_custom_system_prompt": False,
        "match_materials_to_script": bool(
            app_config.get("match_materials_to_script", False)
        ),
        "ui_language": ui_config.get("language", system_locale),
        "local_video_materials": [],
        "active_task_id": "",
        "opened_task_folder_id": "",
    }

    for key, value in defaults.items():
        if key not in session_state:
            session_state[key] = value
