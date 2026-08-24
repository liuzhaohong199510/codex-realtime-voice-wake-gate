@echo off
chcp 65001 >nul
set "PYTHONUTF8=1"
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
set "MODEL_DIR=%~dp0models\sherpa-onnx-kws-zipformer-zh-en-3M-2025-12-20"
if not exist "%PYTHON_EXE%" (
  echo 未找到项目 Python 环境，请把此窗口截图发给 Codex。
  pause
  exit /b 2
)
if not exist "%MODEL_DIR%" (
  echo 未找到本地关键词模型，请把此窗口截图发给 Codex。
  pause
  exit /b 2
)
"%PYTHON_EXE%" "%~dp0run_live_bridge.py" --model "%MODEL_DIR%"
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if not "%EXIT_CODE%"=="0" (
  echo 门控未正常运行，请把上面的错误信息发给 Codex。
)
echo 门控已停止，请把 Codex 麦克风恢复为系统默认。
pause
exit /b %EXIT_CODE%
