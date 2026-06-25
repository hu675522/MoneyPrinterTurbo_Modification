# MoneyPrinterTurbo Modification v2.0.0

## Release Highlights

- Upgraded the project version from `1.3.0` to `2.0.0`.
- Cleared local DeepSeek API Key and Pexels API Key values from `config.toml` for release safety.
- Added the latest WebUI screenshot: `docs/webui-v2.0.0.png`.
- Improved Windows startup compatibility: `webui.bat` now also detects the bundled Python, FFmpeg, and ImageMagick runtime tools from the parent `lib` directory.
- Included the recent WebUI polish, compact layout, theme fixes, task panels, API key manager layout, and Douyin material source modes.
- Added Douyin material source support for the authorized online source, third-party metadata API plus authorized resolver service, and optional AI redraw/enhance hook.

## Windows Package

The Windows release package is generated as:

`dist/MoneyPrinterTurbo_Modification_v2.0.0_Windows.zip`

Run `webui.bat` from the extracted project directory to start the WebUI.

## Verification

- WebUI started successfully at `http://127.0.0.1:8501`.
- Latest screenshot confirms the header displays `MoneyPrinterTurbo v2.0.0`.
- Local release safety check confirms `pexels_api_keys = []` and `deepseek_api_key = ""`.
