@echo off
setlocal

if "%~3"=="" (
  echo Usage: %~nx0 ^<input-video^> ^<input-audio^> ^<output-video^>
  exit /b 2
)

set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%..\.."
set "PORTABLE_PYTHON=%PROJECT_DIR%\..\lib\python\python.exe"
set "VENV_PYTHON=%PROJECT_DIR%\.venv\Scripts\python.exe"

if exist "%VENV_PYTHON%" (
  set "PYTHON_BIN=%VENV_PYTHON%"
) else if exist "%PORTABLE_PYTHON%" (
  set "PYTHON_BIN=%PORTABLE_PYTHON%"
) else (
  set "PYTHON_BIN=python"
)

"%PYTHON_BIN%" "%SCRIPT_DIR%run_wav2lip.py" %*
exit /b %ERRORLEVEL%
