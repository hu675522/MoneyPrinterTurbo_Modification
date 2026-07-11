# MoneyPrinterTurbo_Modification v2.1.0

## Release package

`dist/MoneyPrinterTurbo_Modification_v2.1.0_Full.zip`

SHA-256: `dccdf9a3d5f7071bd286bc114a420cf0117b44b956b25dd3bcc623492c307915`

The full package contains the source code, Windows portable Python/FFmpeg/ImageMagick/Git runtime, the current macOS virtual environment, Wav2Lip source code and local model weights. It is intended for a GitHub Release asset and must not be committed into the Git repository.

The release configuration does not contain API keys. Users must enter their own keys after startup. The package does not include Git metadata; `update.bat` and `update.sh` therefore skip source pulling and only check or update dependencies.

## Added

- Added local talking-head lip sync for a local recorded video and generated or uploaded audio.
- Added `tools/lipsync/run_wav2lip.py` as a cross-platform Wav2Lip launcher.
- Added Windows `run_wav2lip.bat` and retained the macOS/Linux `run_wav2lip.sh` launcher.
- Added `{python}` support to the configurable lip-sync command.
- Added configurable lip-sync enable switch, command and timeout in WebUI and TOML configuration.
- Added custom-audio subtitle fallback: when uploaded audio has no TTS subtitle object, Whisper can generate subtitles from the audio.
- Added API key management for Pexels, Pixabay and Coverr.
- Added authorized Douyin material API modes, metadata/resolver integration and optional enhancement hook.
- Added background task execution, cancellation checkpoints, history search/filter/paging, retry and parameter restore.
- Added macOS/Linux root startup and update scripts alongside the Windows one-click scripts.

## Optimized and fixed

- Fixed Light, Dark and System theme synchronization and component color inconsistencies.
- Aligned the top Basic Settings and API Key controls with their content regions.
- Improved compact WebUI layout, button wrapping, subtitle controls, task summaries and empty states.
- Split the large Streamlit entry page into focused modules and centralized theme styles.
- Improved FFmpeg discovery across macOS and the Windows portable package.
- Improved Douyin API request compatibility, nested response parsing, error messages and secret masking.
- Improved TTS, local material and task failure messages.
- Fixed several dependency compatibility issues for Wav2Lip, PyTorch and librosa on macOS.

## Verified

- macOS WebUI startup and HTTP access.
- macOS FFmpeg installation and video decoding.
- Uploaded custom audio generation path and related automated tests.
- Real 4-second local Wav2Lip output at 360x640, 30 fps, 9:16 with AAC audio.
- Full automated test suite: 307 tests passed, 5 skipped.

## Not completed

- Windows real-machine end-to-end verification for WebUI, FFmpeg, custom audio and Wav2Lip.
- Windows portable runtime still needs Torch, torchvision, librosa, numba, scipy and soundfile verification before lip sync can be declared ready on Windows.
- Long-video lip-sync performance and memory tests for 30-second, 1-minute and 1080x1920 inputs.
- Lip-sync quality tuning for face detection stability, padding, batch size and speed/quality balance.
- Full manual WebUI acceptance run covering local video, uploaded audio, subtitles and lip sync in one task.
- Bilibili and Xiaohongshu material sources remain hidden and are not connected to the backend.

## Security note

Two API keys were removed from `config.toml` during release preparation. Because they existed in a local working copy, revoke them at their providers and create new keys before further use. Never put the replacement keys in a commit or release archive.
