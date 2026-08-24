# 开源前审计报告（2026-08-24）

## 审计范围

- 仓库：`liuzhaohong199510/codex-realtime-voice-wake-gate`
- 最终分支：`main`
- 开源资料最终提交：`b6f9e93`
- 审计对象：当前受 Git 跟踪文件、完整 Git 历史、依赖声明、模型和驱动分发边界、自动化测试与本机只读音频预检。

本报告不等于仓库已经公开，也不等于 GitHub Release 已经发布。

## 结论

当前资料已经合并到 `main` 并达到“可提交公开评审”的本地标准，但仍有外部关卡：

1. GitHub About、Topics 和 Private vulnerability reporting 尚未设置。
2. 仓库仍应保持 Private，直到用户最终确认。
3. `v0.1.0` 标签和 Release 尚未创建。
4. README Mermaid 图仍需在 GitHub 页面人工查看。

## 已验证结果

| 检查 | 结果 | 证据边界 |
|---|---|---|
| 自动化测试 | PASS，74 项 | 证明当前代码和模拟场景通过，不覆盖所有真实设备 |
| VB-CABLE 预检 | PASS | 唯一选择 WASAPI `CABLE Input`，48 kHz；不打开音频流 |
| 本地 Markdown 相对链接 | PASS | 证明仓库内目标文件存在，不证明所有外部网站永久可用 |
| `git diff --check` | PASS | 无尾随空格或补丁格式错误 |
| Apache-2.0 正文 | PASS | 与本机安装的 sherpa-onnx 所附标准许可证正文一致 |
| 当前文件凭据扫描 | PASS | 未命中常见私钥、GitHub/OpenAI/AWS 令牌或明文 secret 赋值模式 |
| 完整历史凭据扫描 | PASS | 所有可达提交未命中上述模式 |
| 真实邮箱扫描 | PASS | 当前公开资料未发现邮箱地址 |
| 个人绝对路径扫描 | PASS | 未发现包含具体用户名的 Windows 用户目录路径 |
| 禁止扩展名扫描 | PASS | 未跟踪录音、模型、驱动、安装包、数据库、日志或证书 |
| 大对象扫描 | PASS | 最大受跟踪对象为 `LICENSE`，约 11 KB |
| Git 提交邮箱 | 可接受 | 历史使用 `local.invalid` 占位域，不暴露真实邮箱 |

## 第三方边界

### sherpa-onnx

源代码为 Apache-2.0。项目通过 PyPI 安装，不把上游包源码或二进制文件提交到仓库。

### KWS 模型

`sherpa-onnx-kws-zipformer-zh-en-3M-2025-12-20` 的模型权重和配套文件没有找到明确的模型专用再分发许可。项目只提供上游官方下载链接，不提交、不镜像、不打包模型。

### VB-CABLE

VB-CABLE 是 VB-Audio Donationware，不属于 Apache-2.0 项目内容。项目不分发驱动，不执行静默安装；公司、机构和专业使用者需自行核对并满足上游许可。

## 人工验收证据

核心链路已经完成真人端到端验收：

- 未说“小欧”时，Codex 不响应普通测试语音。
- 说“小欧”后，门控显示已唤醒，Codex 能收到后续语音。
- 说“结束”后，门控恢复静音，Codex 不响应新的普通测试语音。
- 验收结束后，Codex 麦克风恢复为“系统默认”。

详细记录见 `stage-b-human-e2e-acceptance-2026-08-24.md`。

## 公开前剩余动作

1. 设置仓库 About 和 Topics。
2. 开启 Private vulnerability reporting。
3. 用户明确确认将仓库设为 Public。
4. 使用未登录窗口验证 README、LICENSE 和文档可访问。
5. 确认稳定后创建实验性 `v0.1.0` Release，不附带模型或驱动。
