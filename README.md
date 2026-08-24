# Codex 实时语音“小欧”门控原型

这是仅针对 Codex 实时语音聊天的 Windows 本地门控原型。

当前阶段只完成：

- 默认关闭、说“小欧”开启、说“结束”关闭的状态机。
- Vosk 本地中文控制词识别。
- 默认麦克风的只读枚举和短时输入诊断。
- 合成语音回放验证。
- 异常时回落到关闭状态。

当前阶段尚未完成：

- 不包含虚拟麦克风或 VB-CABLE 驱动。
- 不向 Codex 转发音频。
- 不修改 Windows 默认麦克风或 Codex 设置。
- 尚未进行用户真人声音的准确率验收。

## 本地运行

依赖安装在项目目录的 `.venv` 中，模型目录为
`models/vosk-model-small-cn-0.22`。这两个目录均被 Git 忽略。

双击 `启动小欧门控原型.cmd` 可启动本地检测。程序不保存音频、不上传音频，按
`Ctrl+C` 停止。

## 验证

```powershell
$env:PYTHONPATH=(Resolve-Path '.').Path
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
& '.\.venv\Scripts\python.exe' '.\detect_wave.py' '.\test_audio\synthetic-xiaoou-command-stop.wav'
```

预期：全部单元测试通过，合成回放输出 `EVENTS=OPENED,CLOSED`。

## 安全边界

- Git 不跟踪虚拟环境、识别模型、合成音频、日志或录音。
- 未经用户单独确认，不安装驱动、不修改系统音频路由。
- 程序异常时默认关闭门控。
