import streamlit as st


def mask_api_key(api_key: str) -> str:
    key = str(api_key or "")
    if not key:
        return ""
    if len(key) <= 8:
        return "*" * len(key)
    return f"{key[:4]}****{key[-4:]}"


def render_api_key_manager(
    *,
    config,
    config_key: str,
    title_key: str,
    empty_key: str,
    add_key: str,
    add_success_key: str,
    select_delete_key: str,
    delete_button_key: str,
    delete_success_key: str,
    widget_prefix: str,
    tr,
):
    st.subheader(tr(title_key))

    api_keys = config.app.get(config_key) or []
    config.app[config_key] = api_keys

    if api_keys:
        st.write(tr("Current Keys:"))
        for index, key in enumerate(api_keys, start=1):
            st.code(f"{index}. {mask_api_key(key)}")
    else:
        st.info(tr(empty_key))

    new_key = st.text_input(
        tr(add_key),
        key=f"{widget_prefix}_new_key",
        type="password",
    )
    if st.button(tr(add_key), key=f"{widget_prefix}_add_button"):
        if new_key and new_key not in api_keys:
            api_keys.append(new_key)
            config.save_config()
            st.success(tr(add_success_key))
        elif new_key in api_keys:
            st.warning(tr("This API Key already exists"))
        else:
            st.error(tr("Please enter a valid API Key"))

    if api_keys:
        delete_index = st.selectbox(
            tr(select_delete_key),
            options=range(len(api_keys)),
            format_func=lambda index: mask_api_key(api_keys[index]),
            key=f"{widget_prefix}_delete_key",
        )
        if st.button(tr(delete_button_key), key=f"{widget_prefix}_delete_button"):
            api_keys.pop(delete_index)
            config.save_config()
            st.success(tr(delete_success_key))
