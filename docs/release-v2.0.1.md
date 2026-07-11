# MoneyPrinterTurbo_Modification v2.0.1

## Windows Package

`dist/MoneyPrinterTurbo_Modification_v2.0.1_Windows.zip`

Release 压缩包不包含 Git 元数据；`update.bat` 会跳过源码拉取，只执行运行环境检查和依赖补装。需要更新源码时，请下载新的 Release 压缩包或使用 Git clone 版本。

## 修复内容

- 修复抖音素材接口请求方式问题：普通授权素材接口默认使用 GET 参数；TikHub 域名或 `douyin_material_api_method = "post"` 时使用 POST JSON，避免不同服务请求方式不一致导致接口调用失败。
- 增强抖音素材返回解析：兼容 TikHub 抖音搜索结果中的嵌套视频数据结构，提升素材识别成功率。
- 优化 TikHub 错误提示：针对 402、403、404 等状态码给出更准确的日志说明，避免把余额不足、权限不足或接口地址错误误判为网络/VPN问题。
- 增强日志安全性：隐藏 Authorization、Bearer Token、API Key 等敏感信息，避免接口错误响应回显时泄露密钥。
- 修复 WebUI 抖音素材配置校验：区分“直接素材接口”和“第三方数据接口 + 授权解析”两种模式，缺少不同配置时显示对应提示。
- 修复 WebUI 任务日志 handler 重复移除导致的异常：避免出现 ValueError: There is no existing handler with id ...
- 优化任务失败提示：素材下载失败时不再统一提示“大陆网络/VPN问题”，改为提示素材为空、接口报错、余额不足、免费额度不可用、接口地址错误或下载地址无效等可能原因。
- 优化 TTS 失败提示：移除过度指向 VPN 的提示，改为提示检查 TTS 网络、代理、账号额度与语音语言配置。
