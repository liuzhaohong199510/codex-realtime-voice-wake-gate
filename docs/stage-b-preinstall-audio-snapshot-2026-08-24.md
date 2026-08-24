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

- 本文件记录安装前状态和官方包核验，不代表驱动已经安装。
- 未修改 Codex 配置、Windows 默认设备或其他应用的录音设置。
