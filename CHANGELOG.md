# 更新日志

本项目的重要变化记录在此。版本格式遵循 [Semantic Versioning](https://semver.org/)。

## [Unreleased]

### Added

- 开源项目首页、安装、使用、架构和故障排查文档。
- Apache License 2.0、隐私说明、安全政策和第三方许可边界。
- 贡献指南、社区行为准则、支持说明和 GitHub 协作模板。

## [0.1.0] - 2026-08-24

### Added

- 默认关闭的“小欧”/“结束”两状态门控。
- sherpa-onnx 本地开放词表关键词检测。
- 控制词延迟缓冲和下游抑制。
- 真实麦克风到 VB-CABLE 的 16 kHz 至 48 kHz 音频桥。
- VB-CABLE 唯一端点和格式只读预检。
- 异常时失败关闭，拒绝回退到系统默认扬声器。
- Windows UTF-8 设备名称兼容处理。
- 自动化测试、真人场景验收和 Codex 实时语音端到端验收。

### Known limitations

- 真人验收仅覆盖单任务场景；其他 Codex 任务同时运行时，Codex Desktop 可能发生实时语音会话状态或事件路由冲突。
- 本项目不修改 Codex 客户端，因此不保证多任务实时语音可用。

[Unreleased]: https://github.com/liuzhaohong199510/codex-realtime-voice-wake-gate/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/liuzhaohong199510/codex-realtime-voice-wake-gate/releases/tag/v0.1.0
