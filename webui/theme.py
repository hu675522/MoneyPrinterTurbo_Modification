import streamlit as st
import streamlit.components.v1 as components


def get_streamlit_style() -> str:
    return """
<style>
:root {
    color-scheme: light dark;
}

.stApp {
    --mpt-bg: #edf4f8;
    --mpt-panel: #ffffff;
    --mpt-panel-soft: #f8fbfc;
    --mpt-field: #f4f7fa;
    --mpt-field-focus: #ffffff;
    --mpt-border: #cfd9e4;
    --mpt-border-strong: #aab8c8;
    --mpt-text: #102033;
    --mpt-muted: #52657a;
    --mpt-primary: #1769e0;
    --mpt-primary-hover: #0f55bf;
    --mpt-action: #0996d8;
    --mpt-action-hover: #08aeea;
    --mpt-action-border: #39c9f4;
    --mpt-action-shadow: rgba(8, 151, 216, 0.34);
    --mpt-accent: #0f9f8f;
    --mpt-accent-soft: #dff7f2;
    --mpt-warning: #b45309;
    --mpt-shadow: 0 12px 30px rgba(26, 45, 64, 0.10);
    --mpt-shadow-soft: 0 4px 12px rgba(26, 45, 64, 0.07);
    background: var(--mpt-bg);
    color: var(--mpt-text);
}

@media (prefers-color-scheme: dark) {
    .stApp {
        --mpt-bg: #0e1726;
        --mpt-panel: #142033;
        --mpt-panel-soft: #101a2b;
        --mpt-field: #0f1b2c;
        --mpt-field-focus: #16253a;
        --mpt-border: #2c3a4e;
        --mpt-border-strong: #3d5069;
        --mpt-text: #edf4ff;
        --mpt-muted: #aab8cc;
        --mpt-primary: #62a8ff;
        --mpt-primary-hover: #8cc0ff;
        --mpt-action: #08a7e8;
        --mpt-action-hover: #1dbff5;
        --mpt-action-border: #57d6ff;
        --mpt-action-shadow: rgba(8, 190, 245, 0.42);
        --mpt-accent: #4fd1c5;
        --mpt-accent-soft: #143a3b;
        --mpt-warning: #f6ad55;
        --mpt-shadow: 0 16px 36px rgba(0, 0, 0, 0.34);
        --mpt-shadow-soft: 0 6px 18px rgba(0, 0, 0, 0.25);
    }
}

html[data-theme="light"] .stApp,
body[data-theme="light"] .stApp,
.stApp[data-theme="light"],
[data-theme="light"] .stApp {
    --mpt-bg: #edf4f8;
    --mpt-panel: #ffffff;
    --mpt-panel-soft: #f8fbfc;
    --mpt-field: #f4f7fa;
    --mpt-field-focus: #ffffff;
    --mpt-border: #cfd9e4;
    --mpt-border-strong: #aab8c8;
    --mpt-text: #102033;
    --mpt-muted: #52657a;
    --mpt-primary: #1769e0;
    --mpt-primary-hover: #0f55bf;
    --mpt-action: #0996d8;
    --mpt-action-hover: #08aeea;
    --mpt-action-border: #39c9f4;
    --mpt-action-shadow: rgba(8, 151, 216, 0.34);
    --mpt-accent: #0f9f8f;
    --mpt-accent-soft: #dff7f2;
    --mpt-warning: #b45309;
    --mpt-shadow: 0 12px 30px rgba(26, 45, 64, 0.10);
    --mpt-shadow-soft: 0 4px 12px rgba(26, 45, 64, 0.07);
}

html[data-theme="dark"] .stApp,
body[data-theme="dark"] .stApp,
.stApp[data-theme="dark"],
[data-theme="dark"] .stApp {
    --mpt-bg: #0e1726;
    --mpt-panel: #142033;
    --mpt-panel-soft: #101a2b;
    --mpt-field: #0f1b2c;
    --mpt-field-focus: #16253a;
    --mpt-border: #2c3a4e;
    --mpt-border-strong: #3d5069;
    --mpt-text: #edf4ff;
    --mpt-muted: #aab8cc;
    --mpt-primary: #62a8ff;
    --mpt-primary-hover: #8cc0ff;
    --mpt-action: #08a7e8;
    --mpt-action-hover: #1dbff5;
    --mpt-action-border: #57d6ff;
    --mpt-action-shadow: rgba(8, 190, 245, 0.42);
    --mpt-accent: #4fd1c5;
    --mpt-accent-soft: #143a3b;
    --mpt-warning: #f6ad55;
    --mpt-shadow: 0 16px 36px rgba(0, 0, 0, 0.34);
    --mpt-shadow-soft: 0 6px 18px rgba(0, 0, 0, 0.25);
}

.stApp {
    --mpt-bg: color-mix(in srgb, var(--background-color, #ffffff) 88%, #0996d8 12%);
    --mpt-panel: color-mix(in srgb, var(--secondary-background-color, #ffffff) 96%, var(--background-color, #ffffff) 4%);
    --mpt-panel-soft: color-mix(in srgb, var(--secondary-background-color, #f8fbfc) 84%, var(--background-color, #ffffff) 16%);
    --mpt-field: color-mix(in srgb, var(--secondary-background-color, #f4f7fa) 78%, var(--background-color, #ffffff) 22%);
    --mpt-field-focus: color-mix(in srgb, var(--background-color, #ffffff) 84%, var(--secondary-background-color, #f4f7fa) 16%);
    --mpt-border: color-mix(in srgb, var(--text-color, #102033) 20%, transparent);
    --mpt-border-strong: color-mix(in srgb, var(--text-color, #102033) 32%, transparent);
    --mpt-text: var(--text-color, #102033);
    --mpt-muted: color-mix(in srgb, var(--text-color, #102033) 64%, var(--background-color, #ffffff) 36%);
}

html[data-mpt-theme="light"] .stApp,
.stApp[data-mpt-theme="light"] {
    --mpt-bg: #edf4f8;
    --mpt-panel: #ffffff;
    --mpt-panel-soft: #f8fbfc;
    --mpt-field: #f4f7fa;
    --mpt-field-focus: #ffffff;
    --mpt-border: #cfd9e4;
    --mpt-border-strong: #aab8c8;
    --mpt-text: #102033;
    --mpt-muted: #52657a;
    --mpt-primary: #1769e0;
    --mpt-primary-hover: #0f55bf;
    --mpt-action: #0996d8;
    --mpt-action-hover: #08aeea;
    --mpt-action-border: #39c9f4;
    --mpt-action-shadow: rgba(8, 151, 216, 0.34);
    --mpt-accent: #0f9f8f;
    --mpt-accent-soft: #dff7f2;
    --mpt-warning: #b45309;
    --mpt-shadow: 0 12px 30px rgba(26, 45, 64, 0.10);
    --mpt-shadow-soft: 0 4px 12px rgba(26, 45, 64, 0.07);
}

html[data-mpt-theme="dark"] .stApp,
.stApp[data-mpt-theme="dark"] {
    --mpt-bg: #0e1726;
    --mpt-panel: #142033;
    --mpt-panel-soft: #101a2b;
    --mpt-field: #0f1b2c;
    --mpt-field-focus: #16253a;
    --mpt-border: #2c3a4e;
    --mpt-border-strong: #3d5069;
    --mpt-text: #edf4ff;
    --mpt-muted: #aab8cc;
    --mpt-primary: #62a8ff;
    --mpt-primary-hover: #8cc0ff;
    --mpt-action: #08a7e8;
    --mpt-action-hover: #1dbff5;
    --mpt-action-border: #57d6ff;
    --mpt-action-shadow: rgba(8, 190, 245, 0.42);
    --mpt-accent: #4fd1c5;
    --mpt-accent-soft: #143a3b;
    --mpt-warning: #f6ad55;
    --mpt-shadow: 0 16px 36px rgba(0, 0, 0, 0.34);
    --mpt-shadow-soft: 0 6px 18px rgba(0, 0, 0, 0.25);
}

.stApp,
.stApp p,
.stApp label {
    color: var(--mpt-text);
}

body,
.stApp,
div[data-testid="stAppViewContainer"],
div[data-testid="stMain"] {
    background: var(--mpt-bg) !important;
}

.block-container {
    max-width: 1500px;
    padding-top: 4rem;
    padding-bottom: 2.5rem;
}

h1 {
    color: var(--mpt-text) !important;
    padding-top: 0 !important;
    padding-bottom: 0.15rem !important;
    margin: 0 0 0.35rem !important;
    font-size: 1.75rem !important;
    line-height: 1.25 !important;
    letter-spacing: 0 !important;
}

h2, h3, h4, h5, h6, p, label, span, button {
    letter-spacing: 0 !important;
}

div[data-testid="stMarkdownContainer"],
div[data-testid="stMarkdownContainer"] *,
div[data-testid="stAlert"],
div[data-testid="stAlert"] *,
div[data-testid="stCaptionContainer"],
div[data-testid="stCaptionContainer"] *,
div[data-testid="stTabs"] *,
.stMarkdown,
.stMarkdown * {
    max-width: 100% !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;
    white-space: normal !important;
}

div[data-testid="stMarkdownContainer"] pre,
div[data-testid="stMarkdownContainer"] code {
    white-space: pre-wrap !important;
    overflow-wrap: anywhere !important;
}

div[data-testid="stSlider"],
div[data-testid="stSlider"] *,
div[data-baseweb="slider"],
div[data-baseweb="slider"] * {
    word-break: normal !important;
    overflow-wrap: normal !important;
    white-space: nowrap !important;
}

div[data-testid="stSlider"] [role="slider"],
div[data-baseweb="slider"] [role="slider"] {
    min-width: 1rem !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.65rem !important;
}

div[data-testid="stVerticalBlock"]:has(
    > div[data-testid="stElementContainer"]:first-child
    div[data-testid="stMarkdownContainer"] > p > strong
) {
    background: var(--mpt-panel);
    border: 1px solid var(--mpt-border);
    border-top: 3px solid var(--mpt-accent);
    border-radius: 8px;
    box-shadow: var(--mpt-shadow);
    padding: 0.75rem 0.9rem !important;
}

div[data-testid="stVerticalBlock"]:has(
    > div[data-testid="stElementContainer"]:first-child
    div[data-testid="stMarkdownContainer"] > p > strong
) > div {
    padding: 0 !important;
}

div[data-testid="stVerticalBlock"]:has(
    > div[data-testid="stElementContainer"]:first-child
    div[data-testid="stMarkdownContainer"] > p > strong
) div[data-testid="stElementContainer"] {
    margin-bottom: 0.15rem !important;
}

div[data-testid="stExpander"] {
    border-color: var(--mpt-border);
    border-radius: 8px;
    background: var(--mpt-panel);
    box-shadow: var(--mpt-shadow-soft);
}

div[data-testid="stExpander"] details > summary {
    min-height: 2.2rem !important;
    font-weight: 600;
    background: var(--mpt-panel-soft);
    color: var(--mpt-text);
}

div[data-testid="stCaptionContainer"] {
    color: var(--mpt-muted);
}

div[data-testid="stWidgetLabel"] {
    margin-bottom: 0.15rem !important;
}

div[data-baseweb="input"],
div[data-baseweb="select"] > div,
textarea,
input {
    border-radius: 6px !important;
    background: var(--mpt-field) !important;
    color: var(--mpt-text) !important;
    border-color: var(--mpt-border) !important;
}

div[data-baseweb="input"],
div[data-baseweb="select"] > div {
    min-height: 2.35rem;
}

textarea {
    line-height: 1.45 !important;
    min-height: 4.25rem !important;
}

textarea:focus,
input:focus {
    background: var(--mpt-field-focus) !important;
    border-color: var(--mpt-primary) !important;
}

textarea::placeholder,
input::placeholder {
    color: var(--mpt-muted) !important;
}

.stButton > button {
    min-height: 2.45rem;
    border: 1px solid var(--mpt-action-border);
    border-radius: 7px;
    background: var(--mpt-action);
    color: #ffffff !important;
    font-weight: 600;
    white-space: pre-line;
    overflow-wrap: anywhere;
    text-shadow: 0 1px 1px rgba(0, 37, 74, 0.24);
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.30),
        inset 0 -1px 0 rgba(0, 72, 126, 0.18),
        0 0 0 1px rgba(255, 255, 255, 0.12),
        0 6px 14px var(--mpt-action-shadow);
    transition: background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease;
}

.stButton > button *,
.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: #ffffff !important;
}

.stButton > button:hover {
    border-color: #85e7ff;
    color: #ffffff !important;
    background: var(--mpt-action-hover);
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.38),
        inset 0 -1px 0 rgba(0, 72, 126, 0.20),
        0 0 0 1px rgba(255, 255, 255, 0.16),
        0 8px 18px var(--mpt-action-shadow);
    transform: translateY(-1px);
}

.stButton > button:disabled {
    color: #ffffff !important;
    opacity: 0.66;
    transform: none;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.18),
        0 4px 10px rgba(0, 0, 0, 0.12);
}

.stButton > button[kind="primary"] {
    min-height: 2.75rem;
    font-size: 0.98rem;
    font-weight: 700;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.36),
        inset 0 -1px 0 rgba(0, 72, 126, 0.22),
        0 0 0 1px rgba(255, 255, 255, 0.16),
        0 8px 18px var(--mpt-action-shadow);
}

.stButton > button[kind="primary"]::before {
    content: "";
    display: inline-block;
    width: 0.95rem;
    height: 0.65rem;
    margin-right: 0.45rem;
    border: 2px solid currentColor;
    border-radius: 3px;
    box-shadow: 0.38rem 0.1rem 0 -0.2rem currentColor;
    opacity: 0.9;
    vertical-align: -0.06rem;
}

.stButton > button[kind="primary"]:hover {
    border-color: #85e7ff;
    background: var(--mpt-action-hover);
    color: #ffffff !important;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.42),
        inset 0 -1px 0 rgba(0, 72, 126, 0.22),
        0 0 0 1px rgba(255, 255, 255, 0.18),
        0 10px 24px var(--mpt-action-shadow);
    transform: translateY(-1px);
}

.stButton > button[kind="primary"]:disabled {
    color: #ffffff !important;
    opacity: 0.68;
    transform: none;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.22),
        0 4px 10px rgba(0, 0, 0, 0.12);
}

div[data-testid="stProgress"] > div > div {
    height: 0.55rem;
    border-radius: 999px;
}

div[data-testid="stAlert"] {
    border-radius: 8px;
    border-color: var(--mpt-border);
}

.mpt-page-indicator {
    min-height: 2.45rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--mpt-border);
    border-radius: 7px;
    background: var(--mpt-panel-soft);
    color: var(--mpt-muted);
    font-size: 0.76rem;
    line-height: 1.05;
    text-align: center;
}

.mpt-page-indicator strong {
    color: var(--mpt-text);
    font-size: 0.86rem;
}

.mpt-task-summary-pill {
    min-height: 2.45rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.12rem;
    border: 1px solid var(--mpt-border);
    border-radius: 7px;
    background: var(--mpt-panel-soft);
    padding: 0.35rem 0.55rem;
    line-height: 1.15;
}

.mpt-task-summary-pill span {
    color: var(--mpt-muted);
    font-size: 0.72rem;
}

.mpt-task-summary-pill strong {
    color: var(--mpt-text);
    font-size: 0.88rem;
    overflow-wrap: anywhere;
}

.mpt-empty-state {
    min-height: 4.75rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.25rem;
    border: 1px dashed var(--mpt-border-strong);
    border-radius: 8px;
    background: var(--mpt-panel-soft);
    color: var(--mpt-muted);
    padding: 0.85rem 1rem;
    text-align: center;
}

.mpt-empty-state strong {
    color: var(--mpt-text);
    font-size: 0.96rem;
}

.mpt-empty-state span {
    color: var(--mpt-muted);
    font-size: 0.82rem;
}

hr {
    border-color: var(--mpt-border);
}

@media (max-width: 1100px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    div[data-testid="stHorizontalBlock"] {
        flex-wrap: wrap;
        row-gap: 0.75rem;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        flex: 1 1 calc(50% - 0.75rem) !important;
        min-width: calc(50% - 0.75rem) !important;
    }
}

@media (max-width: 700px) {
    .block-container {
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }

    h1 {
        font-size: 1.45rem !important;
    }

    div[data-testid="stHorizontalBlock"] {
        row-gap: 0.65rem;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        flex-basis: 100% !important;
        min-width: 100% !important;
    }

    div[data-testid="stVerticalBlock"]:has(
        > div[data-testid="stElementContainer"]:first-child
        div[data-testid="stMarkdownContainer"] > p > strong
    ) {
        padding: 0.65rem 0.75rem !important;
    }
}
</style>
"""


def get_streamlit_theme_sync_script() -> str:
    return """
<script>
(function () {
    function getHostDocument() {
        try {
            return window.parent && window.parent.document
                ? window.parent.document
                : document;
        } catch (error) {
            return document;
        }
    }

    function luminance(color) {
        const match = String(color || "").match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/i);
        if (!match) {
            return 1;
        }
        const channels = [match[1], match[2], match[3]].map(function (value) {
            const normalized = Number(value) / 255;
            return normalized <= 0.03928
                ? normalized / 12.92
                : Math.pow((normalized + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
    }

    function isDark(color) {
        return luminance(color) < 0.28;
    }

    function getSystemTheme(win) {
        try {
            return win.matchMedia("(prefers-color-scheme: dark)").matches
                ? "dark"
                : "light";
        } catch (error) {
            return "light";
        }
    }

    function getStoredTheme(win) {
        try {
            const storage = win.localStorage;
            for (let index = 0; index < storage.length; index += 1) {
                const key = storage.key(index) || "";
                const value = storage.getItem(key) || "";
                const text = (key + " " + value).toLowerCase();
                if (!text.includes("theme")) {
                    continue;
                }
                if (text.includes("system")) {
                    return "system";
                }
                if (text.includes("dark")) {
                    return "dark";
                }
                if (text.includes("light")) {
                    return "light";
                }
            }
        } catch (error) {
            return "";
        }
        return "";
    }

    function syncTheme() {
        const doc = getHostDocument();
        const win = doc.defaultView || window;
        const app = doc.querySelector(".stApp");
        if (!app) {
            return;
        }

        const header = doc.querySelector('header[data-testid="stHeader"]');
        const toolbar = doc.querySelector('div[data-testid="stToolbar"]');
        const candidates = [header, toolbar].filter(Boolean);
        const storedTheme = getStoredTheme(win);
        const resolvedTheme = storedTheme === "system"
            ? getSystemTheme(win)
            : storedTheme;
        const dark = resolvedTheme
            ? resolvedTheme === "dark"
            : getSystemTheme(win) === "dark" || candidates.some(function (node) {
            return isDark(win.getComputedStyle(node).backgroundColor);
        });
        const theme = dark ? "dark" : "light";
        if (app.getAttribute("data-mpt-theme") !== theme) {
            app.setAttribute("data-mpt-theme", theme);
        }
        if (doc.documentElement.getAttribute("data-mpt-theme") !== theme) {
            doc.documentElement.setAttribute("data-mpt-theme", theme);
        }
    }

    syncTheme();
    window.setInterval(syncTheme, 600);
    const observer = new MutationObserver(syncTheme);
    observer.observe(getHostDocument().documentElement, {
        attributes: true,
        childList: true,
        subtree: true
    });
})();
</script>
"""


def apply_streamlit_style():
    st.markdown(get_streamlit_style(), unsafe_allow_html=True)
    components.html(get_streamlit_theme_sync_script(), height=0, width=0)
