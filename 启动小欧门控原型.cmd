@echo off
chcp 65001 >nul
set "PYTHONUTF8=1"
cd /d "%~dp0"
".venv\Scripts\python.exe" "run_live_detector.py"
if errorlevel 1 (
  echo.
  echo 原型未正常启动，请把上面的错误信息发给 Codex。
  pause
)
