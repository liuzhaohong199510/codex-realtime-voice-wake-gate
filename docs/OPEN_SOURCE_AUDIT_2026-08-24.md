# 开源发布审计报告（2026-08-24）

## 审计范围

- 仓库：`liuzhaohong199510/codex-realtime-voice-wake-gate`
- 最终分支：`main`
- `v0.1.0` 标签提交：`2f3c86b`
- 审计对象：当前受 Git 跟踪文件、完整 Git 历史、依赖声明、模型和驱动分发边界、自动化测试、本机只读音频预检与 GitHub 公开发布结果。

## 结论

仓库已经切换为 Public，`v0.1.0` 已按实验性 Pre-release 发布。公开页面、README、LICENSE、标签、Release、About、Topics、Issues 和私密漏洞报告入口均已核验。

支持边界固定为单任务场景。多任务并行时已观察到 Codex Desktop 实时语音会话状态或事件路由冲突；本项目不通过客户端注入或补丁修复该内部问题。

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
| GitHub 可见性 | PASS，Public | 公开 API 返回 `private=false`、`visibility=public` |
| 仓库展示资料 | PASS | About 和 12 个通用技术 Topics 已公开显示 |
| README Mermaid | PASS | GitHub 页面已实际渲染音频门控流程图 |
| 私密漏洞报告 | PASS | Private vulnerability reporting 已启用 |
| 首版 Release | PASS | `v0.1.0` 为 Pre-release，Release 附件数为 0 |
| 公开文件访问 | PASS | README 和 LICENSE 的公开请求均返回成功 |
| 标签源码树 | PASS，76 个条目 | 不含模型目录、驱动、录音、数据库、日志、证书或禁止扩展名文件 |

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

## 发布后的已知边界

1. 仅在 Windows 11、当前硬件和已记录的 Codex Desktop 版本完成真人验收。
2. 多任务实时语音不保证可用；待 Codex Desktop 官方修复相关会话路由后再重新验证。
3. Windows 10、休眠恢复、设备热插拔和长时间连续运行尚未系统验证。
4. 模型权重和 VB-CABLE 驱动不进入仓库或 Release，使用者必须从上游自行获取并核对许可。
5. 当前项目在 `v0.1.0` 发布后停止继续扩展；保留源码、测试和文档供社区复用。
