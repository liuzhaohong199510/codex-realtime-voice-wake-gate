# 安装指南

本指南不会自动修改 Windows 默认音频设备。涉及驱动安装的步骤必须由操作者手动完成。

## 1. 环境要求

已验证环境：

- Windows 11 64 位
- Python 3.11
- Git for Windows
- 可用的真实麦克风
- Codex Desktop
- 管理员权限，仅用于安装或卸载 VB-CABLE

Windows 10 可能可用，但尚未完成项目验收。macOS 和 Linux 当前不受支持。

## 2. 获取代码

仓库公开后，可在 PowerShell 中执行：

```powershell
git clone https://github.com/liuzhaohong199510/codex-realtime-voice-wake-gate.git
Set-Location .\codex-realtime-voice-wake-gate
```

不要把项目放在需要管理员权限才能写入的系统目录中。

## 3. 创建 Python 环境

无需激活虚拟环境，直接使用项目内 Python：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

确认版本：

```powershell
.\.venv\Scripts\python.exe --version
```

预期为 Python 3.11.x。

## 4. 下载关键词模型

本仓库不分发模型权重。请从 sherpa-onnx 官方 Release 下载：

- [sherpa-onnx KWS 模型官方文档](https://k2-fsa.github.io/sherpa/onnx/kws/pretrained_models/index.html#sherpa-onnx-kws-zipformer-zh-en-3m-2025-12-20-chinese-english)
- [官方模型压缩包](https://github.com/k2-fsa/sherpa-onnx/releases/download/kws-models/sherpa-onnx-kws-zipformer-zh-en-3M-2025-12-20.tar.bz2)

将模型解压后放到以下位置：

```text
models/
└── sherpa-onnx-kws-zipformer-zh-en-3M-2025-12-20/
    ├── encoder-epoch-13-avg-2-chunk-16-left-64.onnx
    ├── decoder-epoch-13-avg-2-chunk-16-left-64.onnx
    ├── joiner-epoch-13-avg-2-chunk-16-left-64.onnx
    ├── tokens.txt
    └── ...
```

模型目录已被 `.gitignore` 排除。不要把模型提交到 Fork、Pull Request 或 Release。

## 5. 安装 VB-CABLE

VB-CABLE 是 VB-Audio 提供的独立 Donationware 驱动，不属于本项目。

1. 前往 [VB-Audio 官方产品页](https://vb-audio.com/Cable/index.htm)下载安装包。
2. 解压完整压缩包，不要直接在压缩包内运行安装程序。
3. 右键适合系统架构的安装程序，以管理员身份运行。
4. 完成后重启 Windows。
5. 重启后检查 Windows 默认扬声器和默认麦克风。

> [!WARNING]
> Windows 可能把最后安装的音频设备设为默认设备。若默认输入或输出变成 VB-CABLE，请立即恢复为原来的本机麦克风和扬声器。

本项目不会分发、静默安装或自动下载 VB-CABLE。公司、机构或专业场景请自行核对 [VB-Audio 许可规则](https://vb-audio.com/Services/licensing.htm)。

## 6. 运行只读检查

```powershell
.\.venv\Scripts\python.exe .\diagnose_microphones.py
.\.venv\Scripts\python.exe .\preflight_virtual_audio.py
```

预检只读取设备列表和格式，不打开麦克风、不写音频、不改变默认设备。成功输出类似：

```text
检查通过：将仅路由到 [设备编号] CABLE Input (VB-Audio Virtual Cable) @ 48000 Hz。
```

设备编号由 Windows 动态分配，不要照抄其他电脑或其他启动次数的编号。

## 7. 运行自动化测试

```powershell
$env:PYTHONPATH=(Resolve-Path '.').Path
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

通过测试只能证明核心逻辑和当前模拟设备场景符合预期，不能替代真人麦克风和 Codex 实时语音验收。

## 8. 下一步

继续阅读 [使用指南](USAGE.md)，按照“先启动门控、再临时切换 Codex 麦克风”的顺序操作。

需要恢复系统时，参见 [故障排查：如何完全退出或卸载](TROUBLESHOOTING.md#如何完全退出或卸载)。
