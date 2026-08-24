@echo off
chcp 65001 >nul
set "PYTHONUTF8=1"
cd /d "%~dp0"
set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=%~dp0..\..\.venv\Scripts\python.exe"
set "MODEL_DIR=%~dp0models\sherpa-onnx-kws-zipformer-zh-en-3M-2025-12-20"
if not exist "%MODEL_DIR%" set "MODEL_DIR=%~dp0..\..\models\sherpa-onnx-kws-zipformer-zh-en-3M-2025-12-20"
"%PYTHON_EXE%" "run_stage_a_acceptance.py" --model "%MODEL_DIR%" --keywords-file "%~dp0config\keywords.txt"
if errorlevel 1 (
  echo.
  echo 验收尚未通过，请把上面的结果发给 Codex。
  pause
)
