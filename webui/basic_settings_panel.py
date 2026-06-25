import requests
import streamlit as st
from loguru import logger


def get_llm_provider_options(ui_language: str, tr) -> list[tuple[str, str]]:
    aihubmix_label = f"AIHubMix ({tr('Recommended')})"
    if ui_language == "zh":
        aihubmix_label = "AIHubMix（推荐）"

    return [
        ("OpenAI", "openai"),
        (aihubmix_label, "aihubmix"),
        ("AIML API", "aimlapi"),
        ("EvoLink", "evolink"),
        ("Moonshot", "moonshot"),
        ("Azure", "azure"),
        ("Qwen", "qwen"),
        ("DeepSeek", "deepseek"),
        ("ModelScope", "modelscope"),
        ("Gemini", "gemini"),
        ("Grok", "grok"),
        ("Groq", "groq"),
        ("Ollama", "ollama"),
        ("G4f", "g4f"),
        ("OneAPI", "oneapi"),
        ("Cloudflare", "cloudflare"),
        ("ERNIE", "ernie"),
        ("MiniMax", "minimax"),
        ("MiMo", "mimo"),
        ("Pollinations", "pollinations"),
        ("LiteLLM", "litellm"),
    ]


def get_provider_index(
    provider_options: list[tuple[str, str]], saved_provider: str
) -> int:
    saved_provider = saved_provider.lower()
    for i, (_, provider_id) in enumerate(provider_options):
        if provider_id == saved_provider:
            return i
    return 0


def format_config_keys(api_keys) -> str:
    if isinstance(api_keys, str):
        api_keys = [api_keys]
    if not api_keys:
        return ""
    return ", ".join(api_keys)


def parse_config_keys(value: str) -> list[str] | None:
    value = value.replace(" ", "")
    if not value:
        return None
    return value.split(",")


def get_douyin_config_visibility(source_mode: str) -> dict[str, bool]:
    source_mode = (source_mode or "direct").strip().lower()
    return {
        "direct": source_mode != "metadata",
        "metadata": source_mode == "metadata",
        "enhance": source_mode == "metadata",
        "sort": True,
    }


def get_douyin_mode_index(mode_options: list[tuple[str, str]], saved_mode: str) -> int:
    saved_mode = (saved_mode or "direct").strip().lower()
    for index, (_, mode_value) in enumerate(mode_options):
        if mode_value == saved_mode:
            return index
    return 0


@st.cache_data(ttl=300, show_spinner=False)
def get_groq_model_ids(api_key: str, base_url: str) -> list[str]:
    if not api_key:
        return []

    normalized_base_url = (
        base_url or "https://api.groq.com/openai/v1"
    ).strip().rstrip("/")
    models_url = f"{normalized_base_url}/models"

    try:
        response = requests.get(
            models_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", [])

        model_ids = []
        for item in data:
            if isinstance(item, dict):
                model_id = item.get("id")
                if isinstance(model_id, str) and model_id.strip():
                    model_ids.append(model_id.strip())

        return sorted(set(model_ids))
    except Exception as e:
        logger.warning(f"failed to fetch groq models: {e}")
        return []


def get_provider_defaults_and_tips(
    *, app_config, llm_provider: str, llm_model_name: str, llm_base_url: str
) -> tuple[str, str, str]:
    if llm_provider == "ollama":
        if not llm_model_name:
            llm_model_name = "qwen:7b"
        if not llm_base_url:
            llm_base_url = app_config.get_default_ollama_base_url()
    if llm_provider == "openai" and not llm_model_name:
        llm_model_name = "gpt-3.5-turbo"
    if llm_provider == "aihubmix":
        if not llm_model_name:
            llm_model_name = "gpt-5.4-mini"
        if not llm_base_url:
            llm_base_url = "https://aihubmix.com/v1"
    if llm_provider == "aimlapi":
        if not llm_model_name:
            llm_model_name = "openai/gpt-4o-mini"
        if not llm_base_url:
            llm_base_url = "https://api.aimlapi.com/v1"
    if llm_provider == "evolink":
        if not llm_model_name:
            llm_model_name = "gpt-5.5"
        if not llm_base_url:
            llm_base_url = "https://direct.evolink.ai/v1"
    if llm_provider == "moonshot" and not llm_model_name:
        llm_model_name = "moonshot-v1-8k"
    if llm_provider == "oneapi" and not llm_model_name:
        llm_model_name = "claude-3-5-sonnet-20240620"
    if llm_provider == "qwen" and not llm_model_name:
        llm_model_name = "qwen-max"
    if llm_provider == "g4f" and not llm_model_name:
        llm_model_name = "gpt-3.5-turbo"
    if llm_provider == "gemini" and not llm_model_name:
        llm_model_name = "gemini-1.0-pro"
    if llm_provider == "grok":
        if not llm_model_name:
            llm_model_name = "grok-4.3"
        if not llm_base_url:
            llm_base_url = "https://api.x.ai/v1"
    if llm_provider == "groq":
        if not llm_model_name:
            llm_model_name = "llama-3.3-70b-versatile"
        if not llm_base_url:
            llm_base_url = "https://api.groq.com/openai/v1"
    if llm_provider == "deepseek":
        if not llm_model_name:
            llm_model_name = "deepseek-chat"
        if not llm_base_url:
            llm_base_url = "https://api.deepseek.com"
    if llm_provider == "mimo":
        if not llm_model_name:
            llm_model_name = "mimo-v2.5-pro"
        if not llm_base_url:
            llm_base_url = "https://api.xiaomimimo.com/v1"
    if llm_provider == "modelscope":
        if not llm_model_name:
            llm_model_name = "Qwen/Qwen3-32B"
        if not llm_base_url:
            llm_base_url = "https://api-inference.modelscope.cn/v1/"
    if llm_provider == "pollinations" and not llm_model_name:
        llm_model_name = "default"
    if llm_provider == "litellm" and not llm_model_name:
        llm_model_name = "openai/gpt-4o-mini"

    tips_by_provider = {
        "ollama": f"""
##### Ollama \u914d\u7f6e\u8bf4\u660e
- **API Key**: \u672c\u5730 Ollama \u53ef\u968f\u4fbf\u586b\u5199\uff0c\u6bd4\u5982 `123`
- **Base Url**: \u901a\u5e38\u4e3a `http://localhost:11434/v1`
- **Model Name**: \u4f7f\u7528 `ollama list` \u67e5\u770b\uff0c\u6bd4\u5982 `qwen:7b`
""",
        "openai": """
##### OpenAI \u914d\u7f6e\u8bf4\u660e
- **API Key**: [\u70b9\u51fb\u5230\u5b98\u7f51\u7533\u8bf7](https://platform.openai.com/api-keys)
- **Base Url**: \u5b98\u65b9 OpenAI \u53ef\u7559\u7a7a\uff1b\u517c\u5bb9\u4f9b\u5e94\u5546\u8bf7\u586b\u5199\u5bf9\u5e94\u63a5\u53e3\u5730\u5740\u3002
- **Model Name**: \u586b\u5199\u5f53\u524d\u8d26\u53f7\u6709\u6743\u9650\u4f7f\u7528\u7684\u6a21\u578b ID\u3002
""",
        "aihubmix": """
##### AIHubMix \u914d\u7f6e\u8bf4\u660e
- **\u6ce8\u518c\u94fe\u63a5**: [\u70b9\u51fb\u6ce8\u518c AIHubMix](https://aihubmix.com/?aff=CEve)
- **Base Url**: `https://aihubmix.com/v1`
- **\u63a8\u8350\u6a21\u578b**: \u9ed8\u8ba4 `gpt-5.4-mini`\uff0c\u4e5f\u53ef\u4ee5\u586b\u5199\u5e73\u53f0\u652f\u6301\u7684\u5176\u5b83\u6a21\u578b ID\u3002
- **\u9002\u5408\u573a\u666f**: \u7edf\u4e00\u63a5\u5165 Claude\u3001GPT\u3001Gemini\u3001Grok\u3001DeepSeek\u3001\u901a\u4e49\u7b49\u6a21\u578b\u3002
""",
        "aimlapi": """
##### AIML API Configuration
- **API Key**: Create one at https://aimlapi.com/app/keys
- **Base Url**: `https://api.aimlapi.com/v1`
- **Model Name**: For example `openai/gpt-4o-mini`, `openai/gpt-4o`, or `google/gemini-3-flash-preview`.
""",
        "evolink": """
##### EvoLink 配置说明
- **API Key**: [点击到官网申请](https://evolink.ai/dashboard/keys)
- **Base Url**: `https://direct.evolink.ai/v1`
- **Model Name**: 默认 `gpt-5.5`，也可以填写 EvoLink 支持的其它模型 ID。
""",
        "moonshot": """
##### Moonshot \u914d\u7f6e\u8bf4\u660e
- **API Key**: [\u70b9\u51fb\u5230\u5b98\u7f51\u7533\u8bf7](https://platform.moonshot.cn/console/api-keys)
- **Base Url**: \u56fa\u5b9a\u4e3a `https://api.moonshot.cn/v1`
- **Model Name**: \u6bd4\u5982 `moonshot-v1-8k`\uff0c\u4e5f\u53ef\u4ee5\u53c2\u8003\u5b98\u65b9\u6a21\u578b\u5217\u8868\u3002
""",
        "oneapi": """
##### OneAPI \u914d\u7f6e\u8bf4\u660e
- **API Key**: \u586b\u5199\u60a8\u7684 OneAPI \u5bc6\u94a5\u3002
- **Base Url**: \u586b\u5199 OneAPI \u7684\u57fa\u7840 URL\u3002
- **Model Name**: \u4f8b\u5982 `claude-3-5-sonnet-20240620`\u3002
""",
        "qwen": """
##### \u901a\u4e49\u5343\u95ee Qwen \u914d\u7f6e\u8bf4\u660e
- **API Key**: [\u70b9\u51fb\u5230\u5b98\u7f51\u7533\u8bf7](https://dashscope.console.aliyun.com/apiKey)
- **Base Url**: \u53ef\u7559\u7a7a\u3002
- **Model Name**: \u6bd4\u5982 `qwen-max`\u3002
""",
        "g4f": """
##### gpt4free \u914d\u7f6e\u8bf4\u660e
> [GitHub \u5f00\u6e90\u9879\u76ee](https://github.com/xtekky/gpt4free)\uff0c\u53ef\u514d\u8d39\u4f7f\u7528\u90e8\u5206\u6a21\u578b\uff0c\u4f46\u7a33\u5b9a\u6027\u8f83\u5f31\u3002
- **API Key**: \u53ef\u968f\u4fbf\u586b\u5199\uff0c\u6bd4\u5982 `123`
- **Base Url**: \u53ef\u7559\u7a7a\u3002
- **Model Name**: \u6bd4\u5982 `gpt-3.5-turbo`\u3002
""",
        "azure": """
##### Azure \u914d\u7f6e\u8bf4\u660e
- **API Key**: [\u70b9\u51fb\u67e5\u770b Azure \u5bc6\u94a5](https://portal.azure.com/#view/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/~/OpenAI)
- **Base Url**: \u53ef\u7559\u7a7a\u3002
- **Model Name**: \u586b\u5199\u60a8\u5728 Azure \u4e2d\u90e8\u7f72\u7684\u6a21\u578b\u540d\u79f0\u3002
""",
        "gemini": """
##### Gemini \u914d\u7f6e\u8bf4\u660e
- **API Key**: [\u70b9\u51fb\u5230\u5b98\u7f51\u7533\u8bf7](https://ai.google.dev/)
- **Base Url**: \u53ef\u7559\u7a7a\u3002
- **Model Name**: \u6bd4\u5982 `gemini-1.0-pro`\u3002
""",
        "grok": """
##### Grok \u914d\u7f6e\u8bf4\u660e
- **API Key**: \u586b\u5199\u60a8\u7684 Grok API \u5bc6\u94a5\u3002
- **Base Url**: `https://api.x.ai/v1`
- **Model Name**: \u6bd4\u5982 `grok-4.3`\u3002
""",
        "groq": """
##### Groq \u914d\u7f6e\u8bf4\u660e
- **API Key**: [\u70b9\u51fb\u5230\u5b98\u7f51\u7533\u8bf7](https://console.groq.com/keys)
- **Base Url**: \u56fa\u5b9a\u4e3a `https://api.groq.com/openai/v1`
- **Model Name**: \u6bd4\u5982 `llama-3.3-70b-versatile`\u3002
""",
        "deepseek": """
##### DeepSeek \u914d\u7f6e\u8bf4\u660e
- **API Key**: [\u70b9\u51fb\u5230\u5b98\u7f51\u7533\u8bf7](https://platform.deepseek.com/api_keys)
- **Base Url**: \u56fa\u5b9a\u4e3a `https://api.deepseek.com`
- **Model Name**: \u56fa\u5b9a\u4e3a `deepseek-chat`
""",
        "mimo": """
##### Xiaomi MiMo \u914d\u7f6e\u8bf4\u660e
- **API Key**: [\u70b9\u51fb\u5230\u5b98\u7f51\u7533\u8bf7](https://platform.xiaomimimo.com/docs/zh-CN/quick-start/first-api-call)
- **Base Url**: \u56fa\u5b9a\u4e3a `https://api.xiaomimimo.com/v1`
- **Model Name**: \u9ed8\u8ba4 `mimo-v2.5-pro`\uff0c\u4e5f\u53ef\u4ee5\u586b\u5199\u5176\u5b83\u53ef\u7528\u6a21\u578b\u3002
""",
        "modelscope": """
##### ModelScope \u914d\u7f6e\u8bf4\u660e
- **API Key**: [\u70b9\u51fb\u5230\u5b98\u7f51\u7533\u8bf7](https://modelscope.cn/docs/model-service/API-Inference/intro)
- **Base Url**: \u56fa\u5b9a\u4e3a `https://api-inference.modelscope.cn/v1/`
- **Model Name**: \u6bd4\u5982 `Qwen/Qwen3-32B`\u3002
""",
        "ernie": """
##### \u767e\u5ea6\u6587\u5fc3\u4e00\u8a00 \u914d\u7f6e\u8bf4\u660e
- **API Key**: [\u70b9\u51fb\u5230\u5b98\u7f51\u7533\u8bf7](https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application)
- **Secret Key**: [\u70b9\u51fb\u5230\u5b98\u7f51\u7533\u8bf7](https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application)
- **Base Url**: \u9700\u8981\u5b8c\u6574\u586b\u5199\uff0c\u8bf7\u53c2\u8003\u5b98\u65b9\u6587\u6863\u3002
""",
        "pollinations": """
##### Pollinations AI Configuration
- **API Key**: Optional. Leave empty for public access.
- **Base Url**: Default is `https://text.pollinations.ai/openai`
- **Model Name**: Use `openai-fast` or specify a model name.
""",
        "litellm": """
##### LiteLLM Configuration
> [LiteLLM](https://github.com/BerriAI/litellm) routes to 100+ LLM providers via a unified interface.
- **Model Name**: Use LiteLLM format, such as `openai/gpt-4o`, `anthropic/claude-sonnet-4-20250514`, or `gemini/gemini-2.5-flash`.
""",
    }

    tips = tips_by_provider.get(llm_provider, "")
    if llm_provider == "ollama" and app_config.is_running_in_container():
        tips += "\n> \u68c0\u6d4b\u5230\u5bb9\u5668\u73af\u5883\uff0c\u672a\u914d\u7f6e Base Url \u65f6\u4f1a\u9ed8\u8ba4\u4f7f\u7528 `http://host.docker.internal:11434/v1`\n"

    return llm_model_name, llm_base_url, tips

def get_basic_settings_column_weights() -> list[float]:
    return [0.66, 1.2, 1.14]


def render_basic_settings_panel(*, config, tr):
    if config.app.get("hide_config", False):
        return

    with st.expander(tr("Basic Settings"), expanded=False):
        render_basic_settings_content(config=config, tr=tr)


def render_basic_settings_content(*, config, tr):
    if config.app.get("hide_config", False):
        return

    left_config_panel, middle_config_panel, right_config_panel = st.columns(
        get_basic_settings_column_weights(),
        gap="medium",
    )
    with left_config_panel:
        hide_config = st.checkbox(
            tr("Hide Basic Settings"), value=config.app.get("hide_config", False)
        )
        config.app["hide_config"] = hide_config

        hide_log = st.checkbox(
            tr("Hide Log"), value=config.ui.get("hide_log", False)
        )
        config.ui["hide_log"] = hide_log

    with middle_config_panel:
        st.write(tr("LLM Settings"))
        provider_options = get_llm_provider_options(config.ui.get("language"), tr)
        provider_labels = [label for label, _ in provider_options]
        provider_values = {label: value for label, value in provider_options}
        saved_provider = config.app.get("llm_provider", "openai")
        saved_provider_index = get_provider_index(provider_options, saved_provider)

        llm_provider_label = st.selectbox(
            tr("LLM Provider"),
            options=provider_labels,
            index=saved_provider_index,
        )
        llm_provider = provider_values[llm_provider_label]
        config.app["llm_provider"] = llm_provider

        llm_api_key = config.app.get(f"{llm_provider}_api_key", "")
        llm_secret_key = config.app.get(f"{llm_provider}_secret_key", "")
        llm_base_url = config.app.get(f"{llm_provider}_base_url", "")
        llm_model_name = config.app.get(f"{llm_provider}_model_name", "")
        llm_account_id = config.app.get(f"{llm_provider}_account_id", "")

        llm_model_name, llm_base_url, tips = get_provider_defaults_and_tips(
            app_config=config,
            llm_provider=llm_provider,
            llm_model_name=llm_model_name,
            llm_base_url=llm_base_url,
        )

        if tips and config.ui["language"] == "zh":
            if llm_provider != "aihubmix":
                st.warning(
                    "\u4e2d\u56fd\u7528\u6237\u5efa\u8bae\u4f7f\u7528 **DeepSeek** \u6216 **Moonshot** \u4f5c\u4e3a\u5927\u6a21\u578b\u63d0\u4f9b\u5546\n- \u56fd\u5185\u53ef\u76f4\u63a5\u8bbf\u95ee\uff0c\u4e0d\u9700\u8981 VPN\n- \u6ce8\u518c\u901a\u5e38\u4f1a\u8d60\u9001\u989d\u5ea6\uff0c\u57fa\u672c\u591f\u7528"
                )
            st.info(tips)

        st_llm_api_key = st.text_input(
            tr("API Key"), value=llm_api_key, type="password"
        )
        st_llm_base_url = st.text_input(tr("Base Url"), value=llm_base_url)
        st_llm_model_name = ""
        if llm_provider != "ernie":
            if llm_provider == "groq":
                effective_api_key = st_llm_api_key or llm_api_key
                effective_base_url = st_llm_base_url or llm_base_url
                groq_models = get_groq_model_ids(
                    api_key=effective_api_key,
                    base_url=effective_base_url,
                )

                if groq_models:
                    selected_index = 0
                    if llm_model_name in groq_models:
                        selected_index = groq_models.index(llm_model_name)

                    st_llm_model_name = st.selectbox(
                        tr("Model Name"),
                        options=groq_models,
                        index=selected_index,
                        key="groq_model_name_select",
                    )
                else:
                    st_llm_model_name = st.text_input(
                        tr("Model Name"),
                        value=llm_model_name,
                        key="groq_model_name_input",
                    )
                    if effective_api_key:
                        st.caption(
                            "Unable to load Groq model list right now. You can still enter a model name manually 鈥?note it won't be validated until generation."
                        )
                    else:
                        st.caption(
                            "Add a Groq API key to load available models automatically."
                        )
            else:
                st_llm_model_name = st.text_input(
                    tr("Model Name"),
                    value=llm_model_name,
                    key=f"{llm_provider}_model_name_input",
                )
            if st_llm_model_name:
                config.app[f"{llm_provider}_model_name"] = st_llm_model_name
        else:
            st_llm_model_name = None

        if st_llm_api_key:
            config.app[f"{llm_provider}_api_key"] = st_llm_api_key
        if st_llm_base_url:
            config.app[f"{llm_provider}_base_url"] = st_llm_base_url
        if st_llm_model_name:
            config.app[f"{llm_provider}_model_name"] = st_llm_model_name
        if llm_provider == "ernie":
            st_llm_secret_key = st.text_input(
                tr("Secret Key"), value=llm_secret_key, type="password"
            )
            config.app[f"{llm_provider}_secret_key"] = st_llm_secret_key

        if llm_provider == "cloudflare":
            st_llm_account_id = st.text_input(
                tr("Account ID"), value=llm_account_id
            )
            if st_llm_account_id:
                config.app[f"{llm_provider}_account_id"] = st_llm_account_id

    with right_config_panel:
        st.write(tr("Video Source Settings"))

        for label_key, config_key in [
            ("Pexels API Key", "pexels_api_keys"),
            ("Pixabay API Key", "pixabay_api_keys"),
            ("Coverr API Key", "coverr_api_keys"),
        ]:
            api_key = st.text_input(
                tr(label_key),
                value=format_config_keys(config.app.get(config_key, [])),
                type="password",
            )
            parsed_keys = parse_config_keys(api_key)
            if parsed_keys:
                config.app[config_key] = parsed_keys

        douyin_mode_options = [
            (tr("Douyin Source Direct"), "direct"),
            (tr("Douyin Source Metadata"), "metadata"),
        ]
        douyin_mode = config.app.get("douyin_material_source_mode", "direct")
        douyin_mode_index = get_douyin_mode_index(douyin_mode_options, douyin_mode)
        selected_douyin_mode_index = st.selectbox(
            tr("Douyin Material Source Mode"),
            options=range(len(douyin_mode_options)),
            index=douyin_mode_index,
            format_func=lambda x: douyin_mode_options[x][0],
            help=tr("Douyin Material Source Mode Help"),
            key="douyin_material_source_mode_select",
        )
        selected_douyin_mode = douyin_mode_options[selected_douyin_mode_index][1]
        if selected_douyin_mode != douyin_mode:
            config.app["douyin_material_source_mode"] = selected_douyin_mode
            st.rerun()
        config.app["douyin_material_source_mode"] = selected_douyin_mode
        douyin_visibility = get_douyin_config_visibility(
            config.app["douyin_material_source_mode"]
        )

        if douyin_visibility["direct"]:
            douyin_api_url = st.text_input(
                tr("Douyin Material API URL"),
                value=config.app.get("douyin_material_api_url", ""),
                help=tr("Douyin Material API URL Help"),
                key="douyin_material_api_url_input",
            )
            config.app["douyin_material_api_url"] = douyin_api_url.strip()

            douyin_api_key = st.text_input(
                tr("Douyin Material API Key"),
                value=config.app.get("douyin_material_api_key", ""),
                type="password",
                help=tr("Douyin Material API Key Help"),
                key="douyin_material_api_key_input",
            )
            config.app["douyin_material_api_key"] = douyin_api_key.strip()

        if douyin_visibility["metadata"]:
            douyin_metadata_api_url = st.text_input(
                tr("Douyin Metadata API URL"),
                value=config.app.get("douyin_metadata_api_url", ""),
                help=tr("Douyin Metadata API URL Help"),
                key="douyin_metadata_api_url_input",
            )
            config.app["douyin_metadata_api_url"] = douyin_metadata_api_url.strip()

            douyin_metadata_api_key = st.text_input(
                tr("Douyin Metadata API Key"),
                value=config.app.get("douyin_metadata_api_key", ""),
                type="password",
                help=tr("Douyin Metadata API Key Help"),
                key="douyin_metadata_api_key_input",
            )
            config.app["douyin_metadata_api_key"] = douyin_metadata_api_key.strip()

            douyin_resolver_api_url = st.text_input(
                tr("Douyin Resolver API URL"),
                value=config.app.get("douyin_resolver_api_url", ""),
                help=tr("Douyin Resolver API URL Help"),
                key="douyin_resolver_api_url_input",
            )
            config.app["douyin_resolver_api_url"] = douyin_resolver_api_url.strip()

            douyin_resolver_api_key = st.text_input(
                tr("Douyin Resolver API Key"),
                value=config.app.get("douyin_resolver_api_key", ""),
                type="password",
                help=tr("Douyin Resolver API Key Help"),
                key="douyin_resolver_api_key_input",
            )
            config.app["douyin_resolver_api_key"] = douyin_resolver_api_key.strip()

        if douyin_visibility["enhance"]:
            douyin_enhance_api_url = st.text_input(
                tr("Douyin Material Enhance API URL"),
                value=config.app.get("douyin_material_enhance_api_url", ""),
                help=tr("Douyin Material Enhance API URL Help"),
                key="douyin_material_enhance_api_url_input",
            )
            config.app["douyin_material_enhance_api_url"] = douyin_enhance_api_url.strip()

            douyin_enhance_api_key = st.text_input(
                tr("Douyin Material Enhance API Key"),
                value=config.app.get("douyin_material_enhance_api_key", ""),
                type="password",
                help=tr("Douyin Material Enhance API Key Help"),
                key="douyin_material_enhance_api_key_input",
            )
            config.app["douyin_material_enhance_api_key"] = douyin_enhance_api_key.strip()

        douyin_sort_options = [
            (tr("Douyin Sort Hot"), "hot"),
            (tr("Douyin Sort Most Liked"), "most_liked"),
            (tr("Douyin Sort Latest"), "latest"),
        ]
        douyin_sort = config.app.get("douyin_material_sort", "hot")
        douyin_sort_index = 0
        for index, (_, sort_value) in enumerate(douyin_sort_options):
            if sort_value == douyin_sort:
                douyin_sort_index = index
                break
        selected_douyin_sort_index = st.selectbox(
            tr("Douyin Material Sort"),
            options=range(len(douyin_sort_options)),
            index=douyin_sort_index,
            format_func=lambda x: douyin_sort_options[x][0],
            key="douyin_material_sort_select",
        )
        config.app["douyin_material_sort"] = douyin_sort_options[
            selected_douyin_sort_index
        ][1]
