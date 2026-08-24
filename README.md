# Codex 实时语音“小欧”门控原型

这是仅针对 Codex 实时语音聊天的 Windows 本地门控原型。

当前阶段只完成：

- 默认关闭、说“小欧”开启、说“结束”关闭的状态机。
- Vosk 完整中文词表的本地识别；只接受最终结果和达到阈值的精确控制词。
- 默认麦克风的只读枚举和短时输入诊断。
- 合成语音回放验证。
- 识别结果到延迟音频门控的本地路由核心，控制词不会进入下游音频。
- VB-CABLE 播放端的只读预检；缺失、重复或格式不兼容时拒绝启动路由。
- 阶段 A 十组真人验收入口；每组由用户按 Enter 后才开麦，只输出事件和状态结果。
- 异常时回落到关闭状态。

当前阶段尚未完成：

- 尚未安装虚拟麦克风或 VB-CABLE 驱动。
- 尚未打开真实的虚拟输出流，也不向 Codex 转发音频。
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
& '.\.venv\Scripts\python.exe' '.\preflight_virtual_audio.py'
& '.\.venv\Scripts\python.exe' '.\run_stage_a_acceptance.py'
```

预期：全部单元测试通过，合成回放输出 `EVENTS=OPENED,CLOSED`。在尚未安装
VB-CABLE 时，预检应返回 `missing` 和退出码 `2`，并明确说明不会启动音频路由。

十组真人验收会逐组显示口述要求。每组只有在按 Enter 后才打开真实麦克风；在提示处
输入 `q` 可在开麦前退出。程序不写录音文件、不输出全文转写，只在最后输出场景编号、
门控事件、最终状态和通过/未通过结果。

真人验收默认使用 `0.65` 最低词置信度。需要校准时可传入
`--min-confidence 0.60` 等参数；不得在没有真人验收证据时把阈值降为 `0`。识别器使用
完整中文词表，避免把“小陈”或普通讲话强行套进只有“小欧/结束”的受限词表。

## 安全边界

- Git 不跟踪虚拟环境、识别模型、合成音频、日志或录音。
- 真人验收结果默认只显示在终端，不自动写入磁盘。
- 未经用户单独确认，不安装驱动、不修改系统音频路由。
- 预检只能选择名为 `CABLE Input` 的专用播放端，绝不回退到系统默认扬声器。
- 程序异常时默认关闭门控。
