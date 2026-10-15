@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1
set GRADIO_ANALYTICS_ENABLED=False
set "NO_PROXY=localhost,127.0.0.1,::1,%NO_PROXY%"
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo Run setup.ps1 first. See README.md.
    pause
    exit /b 1
)
echo Open http://127.0.0.1:7861 after the model loads.
"%~dp0.venv\Scripts\python.exe" -u scripts\app.py
pause
