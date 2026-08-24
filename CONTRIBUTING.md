# 贡献指南

感谢你帮助改进 Codex 实时语音“小欧”唤醒门控。

## 可以贡献什么

- 修复默认关闭、音频路由或设备兼容问题。
- 增加可重复的 Windows 兼容性测试。
- 改善中文文档、安装和故障排查。
- 在不降低隐私边界的前提下优化误唤醒和漏唤醒。
- 为其他虚拟音频设备设计明确、可验证的适配层。

较大的行为变化请先提交功能建议，说明威胁模型、影响范围和验收标准。

## 开发环境

```powershell
git clone https://github.com/liuzhaohong199510/codex-realtime-voice-wake-gate.git
Set-Location .\codex-realtime-voice-wake-gate
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONPATH=(Resolve-Path '.').Path
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

大多数单元测试不需要真实模型或 VB-CABLE。真实设备测试必须由贡献者主动运行，不应在没有操作者确认的情况下打开麦克风。

## 分支和提交

1. Fork 仓库并从最新 `main` 创建短期分支。
2. 保持修改范围单一，避免无关重构。
3. Bug 修复先加入最小复现测试，再修改实现。
4. 提交信息简洁说明结果，例如 `fix: reject duplicate virtual cable endpoints`。
5. 发起 Pull Request 前运行全部测试并检查差异。

## 隐私和文件规则

不得提交：

- 真实录音、转写或测试对话。
- 模型权重、VB-CABLE 安装包或第三方二进制文件。
- `.venv`、缓存、日志或本机生成文件。
- 用户名、邮箱、个人绝对路径、账号截图或设备序列号。
- API 密钥、令牌、证书或任何凭据。

测试音频如确有必要，必须先讨论来源、授权、最小化方案和许可证。默认使用程序生成的无身份合成样本。

## 代码要求

- Python 3.11 兼容。
- 异常必须默认静音，不能为了“尽量工作”回退到系统默认扬声器。
- 设备编号不能硬编码。
- 新行为必须有自动化测试。
- 涉及真实麦克风、系统设置、驱动或网络的操作必须清楚提示并由用户触发。
- 文档必须区分自动化验证、真实设备验证和人工验收。

## Pull Request 检查

- [ ] 修改目标和范围清楚。
- [ ] 已加入或更新测试。
- [ ] 全部测试通过。
- [ ] 没有提交模型、驱动、录音、日志或凭据。
- [ ] 隐私、安全和失败关闭行为没有退化。
- [ ] 用户可见变化已更新 README 或相关文档。
- [ ] 第三方依赖变化已更新 `THIRD_PARTY_NOTICES.md`。

提交贡献即表示你有权提交相关内容，并同意该贡献按项目 Apache License 2.0 授权。
