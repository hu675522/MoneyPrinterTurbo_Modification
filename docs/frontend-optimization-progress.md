# Frontend Optimization Progress

## 本轮更新（2026-06-24）

- 修复抖音素材来源模式切换体验和字段标题冗余。
  - 给抖音来源模式下拉、排序下拉和相关输入框增加稳定 `key`，模式变化时主动刷新，切换后表单内容即时收放。
  - 中文字段标题去掉重复的“抖音”前缀，例如“第三方数据接口地址”“授权解析服务 Key”“素材 AI 增强接口地址”。
  - 新增 `get_douyin_mode_index()` 测试，保护模式索引和默认回退逻辑。
- 优化抖音素材来源配置区的条件展示。
  - 选择“直接素材接口”时，仅展示直接素材接口地址、Key 和排序配置。
  - 选择“第三方数据接口 + 授权解析服务”时，展示元数据接口、授权解析服务、可选 AI 增强/重绘服务和排序配置。
  - 新增 `get_douyin_config_visibility()` 统一维护不同方案对应的表单展示规则，避免所有配置项堆在同一屏。
- 新增抖音“第三方数据接口 + 授权解析服务”素材方案。
  - 保留原有 `direct` 授权在线素材源方案，同时新增 `metadata` 模式。
  - `metadata` 模式会按主题、文案或关键词调用第三方数据接口，支持 `hot`、`most_liked`、`latest` 排序权重，获取 `aweme_id` / `video_url` 等元数据。
  - 新增授权解析服务配置：把 `aweme_id` 或公开 `video_url` 转换为可合法下载的素材直链，再交给原素材下载和合成流程。
  - 新增可选 AI 增强/重绘服务钩子：素材下载到本地后，可上传给配置的增强服务；服务返回视频二进制或 JSON 下载地址均可。
  - 未实现去水印、绕过反爬或规避平台访问控制；解析服务需由官方、授权或自有合规服务提供。
  - `config.example.toml` 已补充 direct / metadata / resolver / enhance 的接口契约示例。
  - 已补充素材服务、WebUI 校验、多语言和任务链路相关测试覆盖。
- 调整“视频来源：抖音”为授权在线素材源。
  - `douyin` 不再要求上传本地素材，而是像 Pexels/Pixabay/Coverr 一样进入关键词检索和素材下载流程。
  - 新增 `search_videos_douyin()`，根据“视频主题 / 视频文案 / 视频关键词”生成或读取关键词，再调用已配置的授权抖音素材接口。
  - 新增 `douyin_material_api_url`、`douyin_material_api_key`、`douyin_material_sort`、`douyin_material_limit` 配置；基础设置里可填写接口地址、Key，并选择热门优先或最新优先。
  - 授权接口返回视频 URL 时直接下载；返回图片 URL 时会先转成短视频片段，再继续原合成流程。
  - 明确不实现绕过抖音反爬机制；该功能需要接入官方或授权素材服务，避免影响平台合规、版权和账号安全。
  - 已补充素材源、WebUI 校验、任务流程、CLI 和 i18n 测试覆盖。
- 历史记录：曾开发“视频来源：抖音”上传素材模式，现已由上方“授权在线素材源”方案替代。
  - `webui/video_panel.py` 将抖音从“敬请期待”改为可选来源，选择后显示素材上传入口和说明。
  - `webui/generation_panel.py` 允许 `douyin` 来源，并在生成前校验是否已上传抖音素材。
  - `app/services/task.py` 将 `douyin` 作为本地素材型来源处理，复用本地素材预处理，不影响 Pexels、Pixabay、Coverr 在线素材下载流程。
  - `cli.py` 支持 `--video-source douyin`，并要求配套 `--video-materials`，避免无素材时误入生成流程。
  - 已补充 WebUI、任务服务、CLI 和 i18n 测试覆盖。
- 修复 Streamlit `System` 主题模式显示不一致的问题。
  - `webui/theme.py` 的主题同步脚本新增 `system` 识别，选择 System 时通过 `prefers-color-scheme` 跟随系统真实明暗模式。
  - 主题属性写入仍保持“仅变化时更新”，避免页面卡死或反复触发。
- 优化顶部折叠区布局。
  - `webui/main_page.py` 将“基础设置”和“点击以显示 API Key 管理功能”调整为同一行两列展示，列宽为 `1.0 / 1.08`，默认仍为收起状态。
- 优化文案生成按钮换行。
  - `webui/script_panel.py` 将中文“生成【视频文案】和【视频关键词】”按钮文案拆为两行。
  - `webui/theme.py` 将按钮 `white-space` 改为 `pre-line`，确保换行能真实显示。
- 更新测试：
  - `test/services/test_webui_main_page.py` 覆盖顶部两列布局。
  - `test/services/test_webui_script_panel.py` 覆盖按钮文案换行 helper。
  - `test/services/test_webui_theme.py` 覆盖 System 主题判断和按钮换行 CSS。
- 本轮已通过：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\main_page.py webui\script_panel.py webui\theme.py test\services\test_webui_main_page.py test\services\test_webui_script_panel.py test\services\test_webui_theme.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_main_page test.services.test_webui_script_panel test.services.test_webui_theme test.services.test_webui_i18n`
  - `http://127.0.0.1:8501` 已用最新代码重启并返回 200。

## 本轮更新（2026-06-24）

- 修复点击 Streamlit `Dark` 后页面只切换顶栏、内容区仍为浅色的问题。
  - `webui/theme.py` 新增主题同步脚本，通过 Streamlit 本地主题设置和顶栏颜色判断当前 Light/Dark 状态，并给页面挂载 `data-mpt-theme`。
  - CSS 新增 `data-mpt-theme="light"` / `data-mpt-theme="dark"` 两套覆盖变量，确保页面背景、配置面板、输入框、折叠区和文字颜色同步切换。
  - 主内容容器、`stAppViewContainer` 和 `stMain` 背景统一走 `--mpt-bg`，避免出现截图中的“顶栏深色、内容区浅色”割裂。
- 更新测试：
  - `test/services/test_webui_theme.py` 覆盖 `data-mpt-theme` 选择器、主题同步脚本、`localStorage` 主题读取和 Streamlit 顶栏检测。
- 本轮已通过：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\theme.py test\services\test_webui_theme.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_theme test.services.test_webui_i18n`
  - 新页面 `http://127.0.0.1:8527` 已启动，CSS 和同步脚本确认包含 Dark 修复逻辑。

## 本轮更新（2026-06-24）

- 修复按钮文字仍显示为深色的问题。
  - `webui/theme.py` 增加 `.stButton > button p/span/div` 内部文本覆盖，解决 Streamlit 按钮内层 `p` 标签被 `.stApp p` 规则覆盖的问题。
  - `test/services/test_webui_theme.py` 增加按钮内部文字选择器断言。
- 本轮已通过：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\theme.py test\services\test_webui_theme.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_theme test.services.test_webui_i18n`
  - 新页面 `http://127.0.0.1:8524` 已启动，CSS 确认包含按钮内部文字白色覆盖规则。

## 本轮更新（2026-06-24）

- 根据反馈优化按钮文字颜色。
  - `webui/theme.py` 将普通按钮、主按钮、hover 和 disabled 状态的文字统一固定为白色，避免被 Streamlit 默认主题或 Dark 模式覆盖。
  - `test/services/test_webui_theme.py` 增加白色按钮文字断言。
- 本轮已通过：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\theme.py test\services\test_webui_theme.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_theme test.services.test_webui_i18n`
  - 新页面 `http://127.0.0.1:8523` 已启动，CSS 确认包含白色按钮文字规则。

## 本轮更新（2026-06-24）

- 按反馈将其它按钮也统一为参考图风格。
  - `webui/theme.py` 将普通 `.stButton > button` 也调整为亮青蓝按钮：细亮边、内高光、外发光、hover 轻微上浮。
  - 主按钮继续保留更高高度和 CSS 视频图标，用于区分“生成视频”等核心操作。
  - 普通按钮不添加视频图标，避免“删除”“加载参数”等非视频语义按钮出现不合适图标。
- 更新测试：
  - `test/services/test_webui_theme.py` 增加普通按钮 action 背景和发光阴影断言。
- 本轮已通过：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\theme.py test\services\test_webui_theme.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_theme test.services.test_webui_main_page test.services.test_webui_script_panel test.services.test_webui_i18n`
  - 新页面 `http://127.0.0.1:8522` 已启动，CSS 确认普通按钮和主按钮新样式均已注入。

## 本轮更新（2026-06-24）

- 根据参考图继续优化主操作按钮视觉。
  - `webui/theme.py` 将 `type="primary"` 的主按钮调整为亮青蓝 CTA 风格：高亮边框、内高光、外发光、轻微悬浮抬升。
  - 使用 CSS `::before` 绘制小视频图标，让“生成视频”主按钮更接近参考图里的“剪辑视频”按钮气质。
  - 样式只作用于主按钮，不影响普通按钮、历史任务按钮和 API Key 管理按钮。
- 更新测试：
  - `test/services/test_webui_theme.py` 增加主按钮 CTA 风格断言，保护青蓝主色、图标伪元素、发光阴影和文字高光。
- 本轮已通过：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\theme.py test\services\test_webui_theme.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_theme test.services.test_webui_main_page test.services.test_webui_script_panel test.services.test_webui_i18n`
  - 新页面 `http://127.0.0.1:8521` 已启动，CSS 确认包含新的主按钮样式且未引入渐变。

## 本轮更新（2026-06-24）

- 根据反馈继续优化 WebUI 配置区体验。
  - `webui/main_page.py` 将“点击以显示 API Key 管理功能”移动到“基础设置”下方，减少主配置面板之后的查找成本。
  - `webui/script_panel.py` 将“视频文案”和“视频关键词”两个输入框调整为 `68px` 紧凑高度。
- 重做主题色和 Dark 模式兼容。
  - `webui/theme.py` 新增浅色/深色两套 CSS 变量，避免点击 Streamlit 的 `Dark` 后出现浅色硬编码导致的文字、背景、输入框显示异常。
  - 页面背景从普通浅灰调整为更有质感的浅青灰，面板使用更明显的阴影、顶部强调色和蓝绿主色，提升首屏识别度。
  - 输入框、选择器、按钮、折叠区都改为使用统一变量，确保 Light/Dark 下颜色一起切换。
- 更新测试：
  - `test/services/test_webui_main_page.py` 覆盖 API Key 面板位于基础设置之后、主配置四列之前。
  - `test/services/test_webui_script_panel.py` 覆盖紧凑文本域高度。
  - `test/services/test_webui_theme.py` 覆盖浅色/深色变量和主题关键样式。
- 本轮已通过：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\main_page.py webui\script_panel.py webui\theme.py test\services\test_webui_main_page.py test\services\test_webui_script_panel.py test\services\test_webui_theme.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_main_page test.services.test_webui_script_panel test.services.test_webui_theme test.services.test_webui_i18n`
  - 浏览器实测 `http://127.0.0.1:8520`：API Key 管理位于基础设置下方；“视频文案”和“视频关键词”输入框均为 `68px`；深色环境下背景、面板、输入框和文字颜色正常。

## 本轮更新（2026-06-23）

- 根据截图反馈修复 WebUI 顶部标题被 Streamlit 顶栏遮挡的问题。
  - `webui/theme.py` 将主内容容器顶部留白调整为 `4rem`，确保 `MoneyPrinterTurbo v...` 标题在页面顶部可见。
  - 保留标题下方的紧凑间距，避免修复遮挡后重新产生过大的首屏空白。
- 收紧四个主配置面板的纵向节奏。
  - 全局 Streamlit 纵向块 `gap` 调整为 `0.65rem`。
  - 主配置面板内边距从 `0.9rem 1rem` 收紧到 `0.75rem 0.9rem`，移动端进一步收紧为 `0.65rem 0.75rem`。
  - 面板内部字段容器不再叠加额外上下 padding，避免每个表单项都被撑高。
  - 表单标签、面板内元素和折叠区标题高度同步压缩，减少截图中字段之间过松的问题。
- 更新 `test/services/test_webui_theme.py`，把顶部标题留白、紧凑 gap、面板内边距和标签样式纳入测试保护。
- 浏览器实测 `http://127.0.0.1:8512`：标题位于 Streamlit 顶栏下方，四个主配置面板同排展示且无横向溢出。

## 本轮更新（2026-06-23）

- 完成前端体验优化专项第三批：窄屏适配与操作密度检查。
  - `webui/theme.py` 新增响应式媒体查询：`1100px` 以下允许 Streamlit 列布局换行，`700px` 以下改为单列堆叠。
  - 主内容区在窄屏下降低左右边距，面板内边距同步收紧，减少手机宽度下的空白浪费。
  - 按钮增加 `white-space: normal` 和 `overflow-wrap: anywhere`，避免长按钮文案撑破容器。
  - 浏览器实测 `960px` 和 `390px` 宽度下均无横向溢出，四个主配置面板能正常单列堆叠。
- 更新测试：
  - `test/services/test_webui_theme.py` 覆盖响应式断点、列换行、按钮换行与单列堆叠约束。
- 本轮已通过：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\theme.py test\services\test_webui_theme.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_theme test.services.test_webui_main_page test.services.test_webui_task_history_panel test.services.test_webui_task_status_panel test.services.test_webui_i18n`
  - 浏览器验证 `http://127.0.0.1:8501`：`960px` / `390px` 均无横向滚动溢出。

## 本轮更新（2026-06-22）

- 完成前端体验优化专项第二批：任务状态/历史操作区整理。
  - `webui/task_history_panel.py` 将历史任务常用操作整理为一行四列：查看、加载参数、重试、打开目录。
  - 取消任务和删除任务移动到每条历史任务内的独立折叠区，降低常规浏览时的按钮拥挤感，也减少误触风险。
  - `webui/task_status_panel.py` 为当前任务状态面板增加状态摘要行，左侧显示任务状态，右侧显示缩略 Task ID，再展示进度条和结果/日志。
  - 新增纯函数 helper，保护进度裁剪、Task ID 缩略和操作区列宽配置。
- 更新测试：
  - `test/services/test_webui_task_history_panel.py` 覆盖历史任务常用/危险操作列宽。
  - 新增 `test/services/test_webui_task_status_panel.py`，覆盖当前任务状态摘要相关 helper。
- 本轮已通过：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\task_history_panel.py webui\task_status_panel.py test\services\test_webui_task_history_panel.py test\services\test_webui_task_status_panel.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_history_panel test.services.test_webui_task_status_panel test.services.test_webui_theme test.services.test_webui_i18n`
- 按反馈完成主配置面板四栏对齐。
  - `webui/main_page.py` 将“文案设置 / 视频设置 / 音频设置 / 字幕设置”改为同一行四列展示。
  - API Key 管理从右侧字幕列下方移到四个主配置面板之后的独立折叠区，减少第一行视觉拥挤。
  - 四栏宽度调整为 `1.1 / 1.0 / 1.0 / 0.95`，文案区略宽，字幕区略紧凑。
  - 浏览器实测四个面板标题 `top` 坐标一致，确认在同一水平行。
- 本轮已通过：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\main_page.py test\services\test_webui_main_page.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_main_page test.services.test_webui_i18n`
- 完成前端体验优化专项第一批：页面布局整理与轻量 CSS 美化。
  - 新增 `webui/theme.py`，集中管理 Streamlit 页面主题样式，`webui/Main.py` 改为调用 `apply_streamlit_style()`。
  - 页面背景改为浅中性色，主内容最大宽度限制为 `1500px`，减少宽屏下表单横向拉伸。
  - 主要配置面板统一白底、`8px` 圆角、浅边框和轻量阴影；输入框、选择器、按钮统一高度和 `6px` 圆角。
  - 主页面三栏列宽从平均分配调整为 `1.08 / 1.08 / 0.92`，让脚本和视频/音频配置区获得更多编辑空间。
  - 进度条、提示框、按钮 hover 与主按钮样式统一到中性蓝/青绿/琥珀点缀色系，避免大面积单色或渐变背景。
- 更新测试：
  - 新增 `test/services/test_webui_theme.py`，覆盖主题 CSS 关键约束和避免负字距、渐变、viewport 字号等不稳定样式。
  - 更新 `test/services/test_webui_main_page.py`，覆盖主页面列宽配置。
- 本轮已通过：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\Main.py webui\main_page.py webui\theme.py test\services\test_webui_main_page.py test\services\test_webui_theme.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_main_page test.services.test_webui_theme test.services.test_webui_i18n`
  - 浏览器验证 `http://127.0.0.1:8501`：页面渲染正常，背景、主内容宽度、面板圆角/边框、按钮高度和标题字号均已生效。
- 完成历史任务搜索能力。
  - `app/controllers/v1/video.py` 新增任务搜索匹配逻辑，`get_tasks_page(...)` 支持 `search_query`，FastAPI `/tasks` 支持 `search` 查询参数。
  - 搜索范围覆盖 Task ID 和任务参数快照里的 `video_subject`，并与状态筛选、最新优先、分页逻辑组合使用。
  - `webui/task_history_panel.py` 在历史任务筛选区新增搜索输入框，搜索词变化时自动回到第 1 页。
  - 历史任务列表标题与分页摘要里的异常分隔符替换为 ASCII 分隔符，减少乱码显示风险。
- 更新测试：
  - `test/services/test_video.py` 覆盖按 Task ID / 主题搜索。
  - `test/services/test_webui_task_history_panel.py` 覆盖搜索词透传和筛选签名重置。
- 本轮已通过：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile app\controllers\v1\video.py webui\task_history_panel.py test\services\test_video.py test\services\test_webui_task_history_panel.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_video test.services.test_webui_task_history_panel test.services.test_webui_i18n`
- 完成历史任务“加载参数”后的复用摘要展示。
  - 从历史任务参数快照中抽取主题、素材源、比例、数量、配音、背景音乐、字幕开关等核心字段。
  - 加载历史参数后，在任务历史面板顶部展示摘要，避免只看到表单变化却不清楚复用了哪些设置。
  - 摘要数据保存在 `st.session_state["loaded_task_params_summary"]`，语言切换时由当前 `tr(...)` 实时格式化。
- 更新 `webui/task_history_panel.py`
  - 新增 `build_loaded_params_summary(...)` 和 `format_loaded_params_summary(...)`。
  - `load_task_params_to_form(...)` 在回填表单时同步保存摘要。
  - `render_task_history_panel(...)` 在“参数已加载”提示下展示摘要。
- 更新 `test/services/test_webui_task_history_panel.py`
  - 覆盖摘要字段抽取、摘要格式化、加载参数时保存摘要。
- 更新 `webui/i18n/en.json`、`webui/i18n/zh.json`、`webui/i18n/ru.json`
  - 补充摘要字段、启用/关闭状态翻译。
- 本轮已通过：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\task_history_panel.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_history_panel test.services.test_webui_i18n`
- 继续完成 WebUI 任务历史与 FastAPI `/tasks` 响应结构对齐。
  - 在 `app/controllers/v1/video.py` 中新增共享的 `format_task_for_response(...)` 和 `get_tasks_page(...)`。
  - FastAPI `/tasks` 列表接口和 `/tasks/{task_id}` 单任务接口复用同一套输出文件 URI 格式化逻辑。
  - `webui/task_history_panel.py` 的历史任务读取改为调用 `video_controller.get_tasks_page(...)`，不再直接访问 `app.services.state`。
  - WebUI 调用共享分页 helper 时保留本地视频路径，避免 Streamlit 预览被 API 相对 URI 影响。
- 本轮新增验证：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile app\controllers\v1\video.py webui\task_history_panel.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_video.TestSecurityControls test.services.test_webui_task_history_panel test.services.test_webui_i18n`
- 完成一键启动包 Python 版本与项目声明对齐。
  - 便携包当前 Python 为 `3.10.14`，项目声明从 `>=3.11,<3.13` 调整为 `>=3.10,<3.13`。
  - `.python-version` 调整为 `3.10`。
  - `uv.lock` 顶部 `requires-python` 调整为 `>=3.10, <3.13`，与 `pyproject.toml` 保持一致。
  - `docs/MoneyPrinterTurbo.ipynb` 中的 `uv python install` / `uv sync --python` 示例调整为 `3.10`。
  - 新增 `scripts/check_python_runtime.py`，一键包 `start.bat`、`api.bat`、`update.bat` 会在启动或更新前检查当前 Python 是否满足项目声明。
  - 新增 `test/services/test_python_runtime_version.py`，保护 `pyproject.toml`、`.python-version`、`uv.lock` 与当前运行 Python 的兼容性。
- 本轮新增验证：
  - `D:\MoneyPrinter\lib\python\python.exe scripts\check_python_runtime.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_python_runtime_version`
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile scripts\check_python_runtime.py test\services\test_python_runtime_version.py`
- 完成生成流程协作式取消检查点。
  - `app/services/task.py` 新增 `is_task_canceled(...)` 和 `stop_if_task_canceled(...)`。
  - 在脚本、关键词、音频、字幕、素材、最终视频生成、跨平台发布等阶段之间插入取消检查。
  - `generate_final_videos(...)` 会在每个视频合成前、合成后、最终渲染后检查中止状态，避免继续生成后续视频。
  - 已中止任务仍依赖 state 层终态保护，后续普通进度更新不会把任务覆盖成完成或失败。
  - 新增任务服务测试，覆盖脚本阶段后取消、视频合成后取消两类关键路径。
- 本轮新增验证：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile app\services\task.py test\services\test_task.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_task test.services.test_webui_task_runner`
- 完成历史任务运行中“软中止”入口。
  - 新增 `TASK_STATE_CANCELED`，WebUI 状态面板和历史面板都会显示“任务已中止”。
  - `app.services.state` 会保护已中止任务，后续后台进度更新不能把它改回运行中或完成。
  - `app/controllers/v1/video.py` 新增 `cancel_task(...)`，保留原任务参数快照并将运行中任务标记为中止。
  - `webui/task_runner.py` 会跳过已经在排队期间被中止的任务；运行中软中止后，后续异常收尾不会误标为失败。
  - `webui/task_history_panel.py` 新增“确认中止 / 中止任务”入口，仅运行中任务可用；删除规则仍保持运行中不可删除。
- 本轮新增验证：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile app\models\const.py app\services\state.py app\controllers\v1\video.py webui\task_runner.py webui\task_status_panel.py webui\task_history_panel.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_state test.services.test_video.TestSecurityControls test.services.test_webui_task_runner test.services.test_webui_task_history_panel test.services.test_webui_i18n`
- 完成任务历史分页/筛选 UI。
  - `app/controllers/v1/video.py` 的 `get_tasks_page(...)` 支持 `state_filter` 和 `newest_first`，默认 API 行为保持兼容。
  - `webui/task_history_panel.py` 新增任务状态筛选、每页数量和页码输入。
  - 历史任务默认最新优先展示，避免旧任务长期占据第一页。
  - 筛选条件或每页数量变化时自动回到第 1 页，避免页码越界。
  - 页码会根据筛选后的总数自动限制范围，任务多时不再一次性铺满面板。
- 本轮新增验证：
  - `D:\MoneyPrinter\lib\python\python.exe -m py_compile app\controllers\v1\video.py webui\task_history_panel.py`
  - `D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_video.TestSecurityControls test.services.test_webui_task_history_panel test.services.test_webui_i18n`

## 当前阶段

阶段 2 进行中：已完成 WebUI 生成任务后台化、API Key 管理脱敏和组件化，并开始拆分 `webui/Main.py`。

## 已完成改动

- 新增 `webui/task_runner.py`
  - WebUI 任务提交改为复用 `app.controllers.v1.video.submit_task(...)`，与 FastAPI `/videos` 使用同一套任务队列、限流和 state 初始化逻辑。
  - 复用现有 `app.services.state` 保存任务状态和进度。
  - 捕获任务日志，供 WebUI 折叠展示。
  - 任务异常时自动标记为失败，避免页面一直停留在处理中。
  - WebUI 任务结束后会把生成参数快照写回 task state，供历史任务重试使用。

- 更新 `app/controllers/v1/video.py`
  - 从 `create_task(...)` 中抽出共享的 `submit_task(...)`。
  - 从删除接口中抽出共享 `delete_task(...)`，供 API 和 WebUI 共用。
  - API `/videos`、`/subtitle`、`/audio` 继续通过 `create_task(...)` 暴露接口。
  - WebUI 可以传入预生成 `task_id` 和日志包装任务函数，保留上传文件落盘与页面日志能力，同时共享 API 任务队列。
  - 队列已满时会删除刚创建的 task state，避免残留不可执行任务。
  - 删除任务目录时使用任务目录白名单路径解析，避免 unsafe task id 影响任务根目录之外的路径。

- 更新 `webui/Main.py`
  - 移除页面主线程中的 `tm.start(...)` 同步调用。
  - 点击 `Generate Video` 后提交后台任务，并保存 `active_task_id`。
  - 任务运行中禁用生成按钮，避免重复提交。
  - 新增任务状态面板：显示 Task ID、进度条、运行/完成/失败状态。
  - 生成完成后展示视频结果，并保留原有打开任务目录行为。
  - 日志改为折叠展示，最多显示最近 200 行，避免页面被长日志撑开。

- 新增 `test/services/test_webui_task_runner.py`
  - 验证 WebUI 任务会通过共享 API 任务入口提交并成功调用生成服务。
  - 验证生成异常时任务会被标记为失败。
  - 验证任务完成或失败后仍保留参数快照。

- 更新 `test/services/test_video.py`
  - 验证共享 `submit_task(...)` 会使用传入的 task id 和任务函数。
  - 验证任务队列已满时会清理 state。
  - 验证共享 `delete_task(...)` 会删除 state 和任务目录，任务不存在时返回空结果。

- 新增 `webui/api_key_manager.py`
  - 将 Pexels、Pixabay、Coverr 三段重复的 API Key 管理逻辑收敛为通用组件。
  - 已保存 API Key 只做脱敏展示，例如 `abcd****wxyz`。
  - 新增 API Key 输入框使用 password 类型，减少误露风险。
  - 删除 API Key 时页面展示脱敏值，内部仍按索引删除真实 key。

- 更新 `webui/Main.py`
  - API Key 管理区改为调用通用组件。
  - 移除已保存密钥的明文 `st.code(key)` 展示。

- 新增 `test/services/test_webui_api_key_manager.py`
  - 验证长密钥只展示前后 4 位。
  - 验证短密钥完全隐藏。
  - 验证空值处理。

- 新增 `webui/session_state.py`
  - 将 `st.session_state` 默认值初始化从 `Main.py` 中拆出。
  - 保留“不覆盖已有会话值”的行为，避免用户正在编辑时被默认值重置。

- 新增 `webui/task_status_panel.py`
  - 将后台任务状态、进度条、日志折叠面板、结果视频展示从 `Main.py` 中拆出。
  - `Main.py` 只保留提交任务和调用状态面板的协调逻辑。

- 新增 `webui/api_key_panel.py`
  - 将 API Key 管理区域的 expander、tabs、三个素材源面板从 `Main.py` 中拆出。
  - `Main.py` 只保留 `render_api_key_panel(config=config, tr=tr)` 调用。

- 新增 `webui/header_panel.py`
  - 将顶部标题和语言选择器从 `Main.py` 中拆出。
  - 提供 `get_language_options(...)` 纯函数，便于测试语言选项和默认选中逻辑。
  - `Main.py` 不再重复加载 `locales`，顶部语言选择和 `tr(...)` 复用同一份语言数据。

- 新增 `webui/generation_panel.py`
  - 将底部 `Generate Video` 按钮、提交前校验、上传音频落盘、本地素材落盘/复用、后台任务提交从 `Main.py` 中拆出。
  - 提供 `get_generation_error_key(...)` 纯函数，便于测试生成前校验。
  - `Main.py` 只保留 `render_generation_controls(...)` 调用。

- 新增 `webui/webui_utils.py`
  - 将字体/音乐资源枚举、任务目录打开、滚动到底部、日志初始化从 `Main.py` 中拆出。
  - 提供 `resolve_task_folder(...)` 纯函数，保留 UUID 校验和任务目录边界检查。
  - 删除 `Main.py` 中未使用的 `song_dir` 和 `config_file` 变量。

- 新增 `webui/script_panel.py`
  - 将左侧“文案设置”面板从 `Main.py` 中拆出。
  - 覆盖主题输入、脚本语言、高级提示词、AI 生成文案和关键词、文案/关键词文本框。
  - 提供 `build_video_language_options(...)` 纯函数，便于测试语言选项。

- 新增 `webui/video_panel.py`
  - 将中间栏“视频设置”面板从 `Main.py` 中拆出。
  - 覆盖素材源、本地文件上传、拼接模式、转场、比例、片段时长、生成数量、按文案匹配素材、编码器设置。
  - 面板函数返回 `uploaded_files`，供生成提交模块继续处理本地素材落盘。
  - 提供本地上传类型、默认比例、选项索引、编码器选项等纯函数，便于测试。

- 新增 `webui/audio_panel.py`
  - 将中间栏“音频设置”面板从 `Main.py` 中拆出。
  - 覆盖 TTS 服务选择、声音筛选、试听、自定义音频上传、Azure/SiliconFlow/MiMo 密钥输入、语速音量、背景音乐设置。
  - 面板函数返回 `uploaded_audio_file`，供生成提交模块继续处理自定义音频落盘。
  - 提供 TTS 服务选项、声音筛选、友好名称、自定义音频类型等纯函数，便于测试。

- 新增 `webui/subtitle_panel.py`
  - 将右侧“字幕设置”面板从 `Main.py` 中拆出。
  - 覆盖字幕开关、字体、位置、自定义位置、颜色、字号、描边、字幕背景、圆角背景设置。
  - 保留原有 `config.ui` 写回行为，用户保存的字幕偏好仍会自动回填。
  - 提供选项索引和自定义位置校验纯函数，便于测试。

- 新增 `webui/basic_settings_panel.py`
  - 将顶部“基础设置”折叠面板从 `Main.py` 中拆出。
  - 覆盖隐藏配置、隐藏日志、LLM Provider、模型名称、Base URL、API Key、ERNIE Secret Key、Cloudflare Account ID、视频素材源批量 Key 输入。
  - 保留 Groq 模型列表自动拉取和 5 分钟缓存。
  - 提供 Provider 选项、保存项索引、批量 Key 格式化/解析、Provider 默认模型和地址等纯函数，便于测试。

- 新增 `webui/main_page.py`
  - 将 WebUI 主页面三栏布局、各业务面板组合、生成按钮区、任务状态区从 `Main.py` 中拆出。
  - 集中维护脚本语言支持列表 `SUPPORT_LOCALES`。
  - 提供 `create_video_params(...)`，统一从 session 初始化当前生成参数。
  - `Main.py` 进一步收敛为启动入口：路径准备、页面配置、session/i18n 初始化、渲染主页面、保存配置。

- 新增 `webui/task_history_panel.py`
  - 在主页面底部新增“任务历史”折叠面板。
  - 从 `app.services.state.get_all_tasks(...)` 读取最近任务，展示状态、进度、Task ID 和生成视频。
  - 支持将历史任务设为当前任务，方便回看任务状态与日志。
  - 支持基于历史任务参数快照重新提交任务。
  - 支持将历史任务参数加载回当前表单，便于先编辑再重新生成。
  - 历史参数回填已覆盖脚本、关键词、高级脚本设置、视频源、拼接模式、转场、比例、片段时长、生成数量、TTS 声音、语速音量、背景音乐、字幕偏好等主要字段。
  - 支持打开任务目录，便于直接查看输出文件。
  - 支持确认后删除非运行中的历史任务，并同步清理任务状态和输出目录。
  - 加载参数后会自动展开任务历史、脚本高级设置和视频高级设置，并保留“参数已加载”提示，方便继续编辑。

- 更新 `webui/video_panel.py`
  - 视频拼接模式、转场模式、视频比例、片段时长、生成数量改为从配置回填默认值。
  - 上述字段变更后会写回配置，供历史参数加载和页面刷新复用。

- 更新 `webui/audio_panel.py`
  - 语音音量、语音速度、背景音乐类型、背景音乐音量改为从配置回填默认值。
  - 自定义背景音乐文件输入继续支持从 session state 回填。

- 新增 `test/services/test_webui_session_state.py`
  - 验证 session 默认值初始化。
  - 验证已有会话值不会被覆盖。

- 新增 `test/services/test_webui_header_panel.py`
  - 验证当前语言能正确选中。
  - 验证找不到当前语言时默认选择第一个语言项。

- 新增 `test/services/test_webui_generation_panel.py`
  - 验证生成前校验：空主题/文案、无效素材源、缺少在线素材源 API Key、有效本地请求、已配置在线素材源。

- 新增 `test/services/test_webui_utils.py`
  - 验证资源文件后缀筛选和排序。
  - 验证字体/音乐资源枚举。
  - 验证任务目录 UUID 校验和路径解析。

- 新增 `test/services/test_webui_script_panel.py`
  - 验证脚本语言选项会把“自动检测”放在第一位。

- 新增 `test/services/test_webui_video_panel.py`
  - 验证本地上传类型包含大小写扩展名。
  - 验证 Coverr 默认横屏，其它素材源默认竖屏。
  - 验证保存选项索引和编码器默认项。

- 新增 `test/services/test_webui_audio_panel.py`
  - 验证 TTS 服务保存项索引。
  - 验证 Azure V1/V2 声音筛选。
  - 验证声音友好名称生成和无配音模式。
  - 验证自定义音频上传类型包含大小写扩展名。

- 新增 `test/services/test_webui_subtitle_panel.py`
  - 验证字幕选项保存值能正确回填。
  - 验证自定义字幕位置只接受 0 到 100 的数值。

- 新增 `test/services/test_webui_basic_settings_panel.py`
  - 验证 LLM Provider 展示标签和稳定 provider id 的映射。
  - 验证保存的 provider 能正确回填。
  - 验证批量 API Key 输入的格式化/解析契约。
  - 验证 Groq、Ollama 等 Provider 默认模型和 Base URL。

- 新增 `test/services/test_webui_main_page.py`
  - 验证脚本语言支持列表包含俄语。
  - 验证页面生成参数会读取“按文案匹配素材”session 状态。

- 新增 `test/services/test_webui_task_history_panel.py`
  - 验证任务进度会被限制在 0 到 100。
  - 验证任务状态标签复用已有生成状态文案。
  - 验证长 Task ID 会被缩略展示。
  - 验证删除任务必须先确认，且运行中任务不能删除。
  - 验证历史任务重试必须具备参数快照，且运行中任务不能重试。
  - 验证历史任务参数会正确回填到 session state 和 WebUI 配置。

- 更新 `test/services/test_webui_video_panel.py`
  - 验证数值型 selectbox 能按保存值回填默认项。

- 更新 `test/services/test_webui_audio_panel.py`
  - 验证音频数值选项和背景音乐选项能按保存值回填默认项。

- 更新 `test/services/test_webui_i18n.py`
  - 从只扫描 `webui/Main.py` 改为扫描 `webui/*.py`。
  - 后续继续拆分前端模块时，静态 `tr("...")` 文案仍会被翻译覆盖测试保护。
  - 脚本语言支持列表检查改为扫描多模块，适配 `SUPPORT_LOCALES` 从 `Main.py` 迁移到 `main_page.py`。

## 已验证

执行过以下验证：

```powershell
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\Main.py webui\task_runner.py test\services\test_webui_task_runner.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_task test.services.test_webui_i18n test.services.test_webui_task_runner
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\Main.py webui\task_runner.py webui\api_key_manager.py test\services\test_webui_api_key_manager.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_task test.services.test_webui_i18n test.services.test_webui_task_runner test.services.test_webui_api_key_manager
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\Main.py webui\task_status_panel.py webui\session_state.py webui\api_key_manager.py webui\task_runner.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_task test.services.test_webui_i18n test.services.test_webui_task_runner test.services.test_webui_api_key_manager test.services.test_webui_session_state
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\Main.py webui\api_key_panel.py webui\api_key_manager.py webui\task_status_panel.py webui\session_state.py webui\task_runner.py
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\Main.py webui\header_panel.py webui\api_key_panel.py webui\api_key_manager.py webui\task_status_panel.py webui\session_state.py webui\task_runner.py
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\Main.py webui\generation_panel.py webui\header_panel.py webui\api_key_panel.py webui\api_key_manager.py webui\task_status_panel.py webui\session_state.py webui\task_runner.py
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\Main.py webui\webui_utils.py webui\generation_panel.py webui\header_panel.py webui\api_key_panel.py webui\api_key_manager.py webui\task_status_panel.py webui\session_state.py webui\task_runner.py
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\Main.py webui\script_panel.py webui\webui_utils.py webui\generation_panel.py webui\header_panel.py webui\api_key_panel.py webui\api_key_manager.py webui\task_status_panel.py webui\session_state.py webui\task_runner.py
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\Main.py webui\video_panel.py webui\script_panel.py webui\webui_utils.py webui\generation_panel.py webui\header_panel.py webui\api_key_panel.py webui\api_key_manager.py webui\task_status_panel.py webui\session_state.py webui\task_runner.py
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\Main.py webui\audio_panel.py webui\video_panel.py webui\script_panel.py webui\webui_utils.py webui\generation_panel.py webui\header_panel.py webui\api_key_panel.py webui\api_key_manager.py webui\task_status_panel.py webui\session_state.py webui\task_runner.py
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\Main.py webui\subtitle_panel.py webui\audio_panel.py webui\video_panel.py webui\script_panel.py webui\webui_utils.py webui\generation_panel.py webui\header_panel.py webui\api_key_panel.py webui\api_key_manager.py webui\task_status_panel.py webui\session_state.py webui\task_runner.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_subtitle_panel
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_task test.services.test_subtitle_background_settings test.services.test_webui_i18n test.services.test_webui_task_runner test.services.test_webui_api_key_manager test.services.test_webui_session_state test.services.test_webui_header_panel test.services.test_webui_generation_panel test.services.test_webui_utils test.services.test_webui_script_panel test.services.test_webui_video_panel test.services.test_webui_audio_panel test.services.test_webui_subtitle_panel
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\Main.py webui\basic_settings_panel.py webui\subtitle_panel.py webui\audio_panel.py webui\video_panel.py webui\script_panel.py webui\webui_utils.py webui\generation_panel.py webui\header_panel.py webui\api_key_panel.py webui\api_key_manager.py webui\task_status_panel.py webui\session_state.py webui\task_runner.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_basic_settings_panel
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_task test.services.test_subtitle_background_settings test.services.test_webui_i18n test.services.test_webui_task_runner test.services.test_webui_api_key_manager test.services.test_webui_session_state test.services.test_webui_header_panel test.services.test_webui_generation_panel test.services.test_webui_utils test.services.test_webui_script_panel test.services.test_webui_video_panel test.services.test_webui_audio_panel test.services.test_webui_subtitle_panel test.services.test_webui_basic_settings_panel
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\Main.py webui\main_page.py webui\basic_settings_panel.py webui\subtitle_panel.py webui\audio_panel.py webui\video_panel.py webui\script_panel.py webui\webui_utils.py webui\generation_panel.py webui\header_panel.py webui\api_key_panel.py webui\api_key_manager.py webui\task_status_panel.py webui\session_state.py webui\task_runner.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_main_page test.services.test_webui_i18n
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_task test.services.test_subtitle_background_settings test.services.test_webui_i18n test.services.test_webui_task_runner test.services.test_webui_api_key_manager test.services.test_webui_session_state test.services.test_webui_header_panel test.services.test_webui_generation_panel test.services.test_webui_utils test.services.test_webui_script_panel test.services.test_webui_video_panel test.services.test_webui_audio_panel test.services.test_webui_subtitle_panel test.services.test_webui_basic_settings_panel test.services.test_webui_main_page
D:\MoneyPrinter\lib\python\python.exe -m py_compile app\controllers\v1\video.py webui\task_runner.py webui\generation_panel.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_runner test.services.test_video.TestSecurityControls
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_video test.services.test_task test.services.test_subtitle_background_settings test.services.test_webui_i18n test.services.test_webui_task_runner test.services.test_webui_api_key_manager test.services.test_webui_session_state test.services.test_webui_header_panel test.services.test_webui_generation_panel test.services.test_webui_utils test.services.test_webui_script_panel test.services.test_webui_video_panel test.services.test_webui_audio_panel test.services.test_webui_subtitle_panel test.services.test_webui_basic_settings_panel test.services.test_webui_main_page
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\Main.py webui\main_page.py webui\task_history_panel.py webui\task_status_panel.py webui\task_runner.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_history_panel test.services.test_webui_i18n
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_video test.services.test_task test.services.test_subtitle_background_settings test.services.test_webui_i18n test.services.test_webui_task_runner test.services.test_webui_api_key_manager test.services.test_webui_session_state test.services.test_webui_header_panel test.services.test_webui_generation_panel test.services.test_webui_utils test.services.test_webui_script_panel test.services.test_webui_video_panel test.services.test_webui_audio_panel test.services.test_webui_subtitle_panel test.services.test_webui_basic_settings_panel test.services.test_webui_main_page test.services.test_webui_task_history_panel
D:\MoneyPrinter\lib\python\python.exe -m py_compile app\controllers\v1\video.py webui\task_history_panel.py webui\main_page.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_history_panel test.services.test_video.TestSecurityControls test.services.test_webui_i18n
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_video test.services.test_task test.services.test_subtitle_background_settings test.services.test_webui_i18n test.services.test_webui_task_runner test.services.test_webui_api_key_manager test.services.test_webui_session_state test.services.test_webui_header_panel test.services.test_webui_generation_panel test.services.test_webui_utils test.services.test_webui_script_panel test.services.test_webui_video_panel test.services.test_webui_audio_panel test.services.test_webui_subtitle_panel test.services.test_webui_basic_settings_panel test.services.test_webui_main_page test.services.test_webui_task_history_panel
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\task_runner.py webui\task_history_panel.py webui\main_page.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_runner test.services.test_webui_task_history_panel test.services.test_webui_i18n
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_video test.services.test_task test.services.test_subtitle_background_settings test.services.test_webui_i18n test.services.test_webui_task_runner test.services.test_webui_api_key_manager test.services.test_webui_session_state test.services.test_webui_header_panel test.services.test_webui_generation_panel test.services.test_webui_utils test.services.test_webui_script_panel test.services.test_webui_video_panel test.services.test_webui_audio_panel test.services.test_webui_subtitle_panel test.services.test_webui_basic_settings_panel test.services.test_webui_main_page test.services.test_webui_task_history_panel
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\task_history_panel.py webui\audio_panel.py webui\main_page.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_history_panel test.services.test_webui_audio_panel test.services.test_webui_i18n
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_video test.services.test_task test.services.test_subtitle_background_settings test.services.test_webui_i18n test.services.test_webui_task_runner test.services.test_webui_api_key_manager test.services.test_webui_session_state test.services.test_webui_header_panel test.services.test_webui_generation_panel test.services.test_webui_utils test.services.test_webui_script_panel test.services.test_webui_video_panel test.services.test_webui_audio_panel test.services.test_webui_subtitle_panel test.services.test_webui_basic_settings_panel test.services.test_webui_main_page test.services.test_webui_task_history_panel
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\video_panel.py webui\audio_panel.py webui\task_history_panel.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_video_panel test.services.test_webui_audio_panel test.services.test_webui_task_history_panel
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_video test.services.test_task test.services.test_subtitle_background_settings test.services.test_webui_i18n test.services.test_webui_task_runner test.services.test_webui_api_key_manager test.services.test_webui_session_state test.services.test_webui_header_panel test.services.test_webui_generation_panel test.services.test_webui_utils test.services.test_webui_script_panel test.services.test_webui_video_panel test.services.test_webui_audio_panel test.services.test_webui_subtitle_panel test.services.test_webui_basic_settings_panel test.services.test_webui_main_page test.services.test_webui_task_history_panel
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\task_history_panel.py webui\script_panel.py webui\video_panel.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_history_panel test.services.test_webui_script_panel test.services.test_webui_video_panel test.services.test_webui_i18n
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_video test.services.test_task test.services.test_subtitle_background_settings test.services.test_webui_i18n test.services.test_webui_task_runner test.services.test_webui_api_key_manager test.services.test_webui_session_state test.services.test_webui_header_panel test.services.test_webui_generation_panel test.services.test_webui_utils test.services.test_webui_script_panel test.services.test_webui_video_panel test.services.test_webui_audio_panel test.services.test_webui_subtitle_panel test.services.test_webui_basic_settings_panel test.services.test_webui_main_page test.services.test_webui_task_history_panel
```

结果：相关测试通过，当前相关回归集为 130 个测试通过、1 个按项目配置跳过。

## 当前收益

- 页面不会在生成视频时被 `tm.start(...)` 长时间阻塞。
- 用户可以看到任务进度，而不是只能等待。
- 生成失败会有明确失败状态。
- API Key 不再在页面上明文展示。
- API Key 管理重复代码减少，后续增加素材源时更容易维护。
- `Main.py` 开始从单文件巨型页面向模块化 WebUI 演进。
- session 初始化已有单测保护，后续拆分页面面板时更稳。
- i18n 测试已适配多模块 WebUI，继续拆分时不容易漏翻译。
- 顶部语言选择器已模块化，`locales` 不再重复加载。
- 生成提交逻辑已有单测保护，后续调整任务提交方式时更稳。
- WebUI 基础工具函数已抽离，`Main.py` 中非页面编排逻辑继续减少。
- 左侧文案业务面板已模块化，`Main.py` 进一步接近页面编排层。
- 中间栏视频设置业务面板已模块化，本地素材上传仍通过返回值接入生成流程。
- 中间栏音频设置业务面板已模块化，自定义音频上传仍通过返回值接入生成流程。
- 右侧字幕设置业务面板已模块化，字幕位置和背景偏好仍由配置文件统一保存。
- 基础配置面板已模块化，LLM Provider 选择和视频素材源批量 Key 输入脱离 `Main.py`。
- 主页面四栏编排已模块化，`Main.py` 基本退化为清晰的 Streamlit 启动入口。
- WebUI 任务提交已复用 API controller 的共享任务入口，不再维护独立线程池，任务并发和队列上限与 API 模式保持一致。
- WebUI 已具备轻量任务历史入口，可以回看最近任务、播放结果、重新设为当前任务、加载主要参数到当前表单并自动展开相关设置区、按参数快照重试任务、打开输出目录，并确认删除已结束任务。
- 为后续任务历史、取消任务、失败重试、API 化 WebUI 调用打好了基础。

## 下一步建议

1. 梳理一键包更新流程，逐步从 `requirements.txt` 迁移到锁文件安装。

## 2026-06-24：顶部基础/API 设置同步展开优化

- 将「基础设置」和「点击以显示 API Key 管理功能」从两个独立折叠区，调整为同一行两个同步控制入口。
- 默认保持收起；点击任意一个入口时，两列会同时展开或同时收起。
- 展开后改为两列内容区，其中「基础设置」获得更宽展示空间，减少内部三列挤压。
- 拆分 `render_basic_settings_content` 和 `render_api_key_content`，保留旧面板入口，方便后续继续复用和测试。
- 修复 `basic_settings_panel.py` 文件头 BOM，避免 i18n 静态扫描解析失败。
- 恢复 AIHubMix 中文推荐标签为正常显示。

验证：

```powershell
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\main_page.py webui\basic_settings_panel.py webui\api_key_panel.py webui\script_panel.py test\services\test_webui_main_page.py test\services\test_webui_basic_settings_panel.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_main_page test.services.test_webui_basic_settings_panel test.services.test_webui_theme test.services.test_webui_i18n
```

结果：26 个相关测试通过。

## 2026-06-24：修复基础设置中文乱码与文本溢出

- 修复 `basic_settings_panel.py` 中大模型配置说明的硬编码中文乱码。
- 将 provider 提示文案改为更短、更适合窄列展示的说明。
- 为 Markdown、Alert、Caption、Tabs 等内容增加自动换行保护，长链接和中英文混排不会再冲出容器。
- 更新基础设置测试，覆盖 DeepSeek 中文提示可读性。

验证：

```powershell
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\basic_settings_panel.py webui\theme.py test\services\test_webui_basic_settings_panel.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_basic_settings_panel test.services.test_webui_theme test.services.test_webui_main_page test.services.test_webui_i18n
```

结果：27 个相关测试通过。

## 2026-06-24：修复字幕滑块数字换行

- 修复字幕大小、描边粗细滑块的当前值被拆成两行显示的问题。
- 为 Streamlit Slider 增加专属样式覆盖：滑块数字保持单行，不受 Markdown 长文本换行规则影响。

验证：

```powershell
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\theme.py test\services\test_webui_theme.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_theme test.services.test_webui_subtitle_panel
```

结果：11 个相关测试通过。

## 2026-06-24：调整文案生成按钮换行

- 将「点击使用AI根据主题生成【视频文案】和【视频关键词】」按钮改为固定两行显示。
- 第一行显示「点击使用AI根据主题」，第二行完整显示「生成【视频文案】和【视频关键词】」。
- 去掉按钮文案中的 Markdown 粗体标记，避免按钮里出现不稳定的断行宽度。

验证：

```powershell
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\script_panel.py test\services\test_webui_script_panel.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_script_panel test.services.test_webui_theme
```

结果：10 个相关测试通过。

## 2026-06-24：整理任务历史筛选栏与结果摘要

- 将任务历史筛选栏列宽抽成 `get_task_history_filter_column_weights()`，后续继续调密度时更容易维护。
- 新增 `format_task_history_result_summary()`，统一展示「结果：当前显示 / 总数 | 页码」摘要。
- 为 `zh/en/ru` 补充 `Task History Results` 翻译键，避免静态 i18n 扫描遗漏。
- 顺手修正顶部同步展开按钮标题清理逻辑，避免 Streamlit 标记剥离后留下孤立冒号。

验证：

```powershell
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\task_history_panel.py test\services\test_webui_task_history_panel.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_history_panel test.services.test_webui_i18n test.services.test_webui_main_page
```

结果：33 个相关测试通过。

## 2026-06-24：优化任务历史分页控件

- 将任务历史右侧页码数字输入框替换为更轻量的上一页 / 下一页按钮。
- 新增 `get_task_history_page_nav_column_weights()`、`can_navigate_history_page()`、`get_history_page_after_navigation()`，把分页边界逻辑从渲染层拆出。
- 新增 `.mpt-page-indicator` 样式，中间显示当前页 / 总页数，避免原生数字输入框的 `- / +` 步进器挤压布局。

验证：

```powershell
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\task_history_panel.py webui\theme.py test\services\test_webui_task_history_panel.py test\services\test_webui_theme.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_history_panel test.services.test_webui_theme test.services.test_webui_i18n
```

结果：32 个相关测试通过。

## 2026-06-24：优化当前任务状态摘要区

- 将当前任务状态区从两段 caption 改为三列摘要：任务状态、Task ID、打开目录。
- 新增 `get_active_task_summary_column_weights()` 和 `format_task_summary_pill_html()`，并对 HTML 文本做转义，避免异常 Task ID 或翻译文本影响页面结构。
- 新增 `.mpt-task-summary-pill` 样式，让任务状态摘要和任务历史分页视觉保持一致。
- 当前任务面板增加「打开目录」按钮，生成完成后仍可手动再次打开输出目录。

验证：

```powershell
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\task_status_panel.py webui\theme.py test\services\test_webui_task_status_panel.py test\services\test_webui_theme.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_status_panel test.services.test_webui_theme test.services.test_webui_i18n
```

结果：18 个相关测试通过。

## 2026-06-24：优化当前任务生成结果预览

- 将当前任务完成后的生成视频预览改为最多三列网格。
- 取消旧的间隔列布局，避免多视频结果在宽屏下过度拉开。
- 当前任务结果区增加「生成的视频」标题，与任务历史预览保持一致。
- 新增 `get_active_task_video_column_count()`，用测试保护预览列数规则。

验证：

```powershell
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\task_status_panel.py test\services\test_webui_task_status_panel.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_status_panel test.services.test_webui_i18n
```

结果：10 个相关测试通过。

## 2026-06-24：优化当前任务日志折叠区

- 将当前任务日志折叠标题从硬编码 `Log` 改为可翻译的 `Task Logs`。
- 新增 `TASK_LOG_DISPLAY_LIMIT`、`get_recent_task_logs()` 和 `format_task_log_expander_label()`。
- 日志折叠标题现在显示最近日志行数和总日志行数，例如 `任务日志（最近行数：200/280）`。
- 为 `zh/en/ru` 补充 `Task Logs` 和 `Recent Log Lines` 翻译键。

验证：

```powershell
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\task_status_panel.py test\services\test_webui_task_status_panel.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_status_panel test.services.test_webui_i18n
```

结果：12 个相关测试通过。

## 2026-06-24：优化任务历史空状态

- 将任务历史无数据时的普通 caption 改为 `.mpt-empty-state` 空状态提示块。
- 新增 `format_task_history_empty_state_html()`，并对标题/说明文本做 HTML 转义。
- 为 `zh/en/ru` 补充 `Task History Empty Help` 翻译键。
- 空状态会提示生成完成后视频结果和可复用任务参数会显示在这里。

验证：

```powershell
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\task_history_panel.py webui\theme.py test\services\test_webui_task_history_panel.py test\services\test_webui_theme.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_history_panel test.services.test_webui_theme test.services.test_webui_i18n
```

结果：35 个相关测试通过。

## 2026-06-24：区分任务历史空状态与无匹配结果

- 新增 `get_task_history_empty_state_keys()`，根据当前搜索词和状态筛选选择不同空状态文案。
- 没有任何任务时显示「暂无任务」；有搜索/筛选条件但无结果时显示「没有匹配的任务」。
- 为 `zh/en/ru` 补充 `Task History No Matches` 和 `Task History No Matches Help` 翻译键。

验证：

```powershell
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\task_history_panel.py test\services\test_webui_task_history_panel.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_history_panel test.services.test_webui_i18n
```

结果：26 个相关测试通过。

## 2026-06-24：优化任务历史条目标题可读性

- 任务历史每条记录标题新增视频主题，便于从列表中快速识别任务。
- 新增 `get_task_history_subject()`、`shorten_task_subject()` 和 `format_task_history_item_title()`。
- 长主题会自动截断，避免撑开折叠标题；没有主题时保持原来的状态 / Task ID / 进度结构。
- 标题分隔符统一为 `|`，减少旧式横杠分隔在中英文混排中的歧义。

验证：

```powershell
D:\MoneyPrinter\lib\python\python.exe -m py_compile webui\task_history_panel.py test\services\test_webui_task_history_panel.py
D:\MoneyPrinter\lib\python\python.exe -m unittest test.services.test_webui_task_history_panel test.services.test_webui_i18n
```

结果：28 个相关测试通过。

## 2026-06-25：v2.0.0 发版准备

- 清空本地 `config.toml` 中的 `DeepSeek API Key` 和 `Pexels API Key`，避免发版携带个人密钥。
- 将项目版本从 `1.3.0` 升级到 `2.0.0`，同步更新 `pyproject.toml`、默认配置版本和素材服务请求头版本标识。
- 新增最新 UI 截图 `docs/webui-v2.0.0.png`，截图已确认页面标题显示 `MoneyPrinterTurbo v2.0.0`。
- 新增 Release 说明文档 `docs/release-v2.0.0.md`，用于 GitHub Release 描述。
- 优化 `webui.bat`，支持识别上级目录中的便携 Python、FFmpeg 和 ImageMagick 运行组件，方便 Windows 一键包启动。
- 准备 Windows 发版压缩包：`dist/MoneyPrinterTurbo_Modification_v2.0.0_Windows.zip`。

验证：

```powershell
Invoke-WebRequest -UseBasicParsing -Uri http://127.0.0.1:8501
```

结果：WebUI 本地启动成功，页面返回 200。
