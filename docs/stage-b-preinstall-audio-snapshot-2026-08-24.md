# 阶段 B 安装前音频与回退快照

日期：2026-08-24

## 当前系统状态

- VB-CABLE：尚未安装。
- PortAudio 默认输入索引：`1`。
- 默认输入设备：`本机麦克风 (适用于数字麦克风的英特尔® 智音技术)`。
- PortAudio 默认输出索引：`3`。
- 默认输出设备：`本机扬声器 (Audio Device)`。
- Windows 声音设备状态：Realtek、Intel 数字麦克风、Intel USB 音频和 Intel
  蓝牙音频均为 `OK`。
- 阶段 B 的安装操作不得修改 Windows 默认输入或输出设备。

设备索引会在安装驱动后重新编号，因此回退核对以设备名称和用途为准，不能只比较索引。

## 官方安装包核验

- 来源：`https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack45.zip`
- 官方产品页：`https://vb-audio.com/Cable/`
- 文件：`D:\CodexInstallers\VB-CABLE\VBCABLE_Driver_Pack45.zip`
- 大小：`1,318,877` 字节。
- SHA-256：`B950E39F01AF1D04EA623C8F6D8EB9B6EA5C477C637295FABF20631C85116BFB`。
- 64 位安装程序：`VBCABLE_Setup_x64.exe`。
- Authenticode：安装程序、Windows 10 x64 驱动和目录签名均为 `Valid`；驱动目录由
  Microsoft Windows Hardware Compatibility Publisher 签名。

## 安装与回退边界

1. 仅运行官方 64 位安装程序，不设置虚拟设备为 Windows 默认麦克风或扬声器。
2. 安装后先核对原默认设备仍为本机麦克风和本机扬声器，再测试虚拟通道。
3. 官方说明要求安装完成后重启，未重启前只记为“已安装、未完成验证”。
4. 如需回退，使用同一官方安装程序执行卸载并重启，然后按本快照核对原设备。
5. Codex 是否按任务分别保存麦克风尚无官方说明；验证前按“客户端/会话全局”处理，
   不承诺其他 Codex 实时语音任务可独立绕过门控。

## 证据边界

- 本节以上内容是安装前状态和官方包核验；实际安装结果见下方追加记录。
- 尚未修改 Codex 配置或其他应用的录音设置。

## 安装后追加记录

安装程序已于 2026-08-24 运行，VB-Audio Virtual Cable 驱动和端点状态均为
`OK`。官方要求重启，因此重启前状态记为“已安装，尚未完成重启后验证”。

安装器曾自动把 `CABLE Output` 和 `CABLE Input` 设为系统默认输入、输出；程序发现后
立即将三个 Windows 音频角色的默认输入恢复为本机数字麦克风、默认输出恢复为本机
扬声器。恢复后再次通过 PortAudio 读取，设备名称与本文件安装前快照一致。

真实驱动还暴露了两项 PortAudio 兼容差异：

1. 同一物理 `CABLE Input` 会经 MME、DirectSound 和 WASAPI 重复枚举；预检现已明确
   优先唯一的 Windows WASAPI 端点，并在同一接口仍有多个候选时继续安全停止。
2. WASAPI 端点不接受 `16 kHz` 直接输出，但接受原生 `48 kHz` 单声道 PCM16；预检现
   会先检查 16 kHz，再显式检查并记录端点原生采样率。

修复后的真实预检结果：

`检查通过：将仅路由到 [16] CABLE Input (VB-Audio Virtual Cable) @ 48000 Hz。`

设备索引仍可能在重启后变化，运行时必须重新发现，不能把索引 `16` 写死。当前自动
测试为 `66/66` 通过；这证明设备发现和格式预检通过，不代表 Codex 实时语音端到端
路由已经完成。

## 重启后验证

Windows 于 2026-08-24 21:31 完成真正的系统重新启动。重启后核验结果：

- VB-Audio Virtual Cable 驱动及三个音频端点状态均为 `OK`。
- 默认输入仍为本机数字麦克风，默认输出仍为本机扬声器。
- 真实预检仍唯一选择 Windows WASAPI `CABLE Input @ 48000 Hz`。
- 本机麦克风到虚拟线的三秒真实双流试运行退出码为 `0`；未唤醒期间只输出静音，
  退出后音频流关闭。
- 新增重采样、真实桥接和 Windows 启动入口后，自动测试为 `73/73` 通过。

此结果完成驱动和本地虚拟线桥验证；Codex 客户端设备选择与实时语音真人端到端验收
仍是下一道门。
