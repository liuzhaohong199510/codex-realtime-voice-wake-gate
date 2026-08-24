# 第三方软件与许可声明

本项目自身代码和文档采用 Apache License 2.0。以下第三方组件不因本项目许可证而改变其授权条件。

## Python 依赖

版本以 `requirements.txt` 为准。

| 组件 | 当前固定版本 | 上游项目 | 许可证 |
|---|---:|---|---|
| Click | 8.2.1 | [pallets/click](https://github.com/pallets/click) | BSD-3-Clause |
| NumPy | 2.3.5 | [numpy/numpy](https://github.com/numpy/numpy) | BSD-3-Clause |
| pypinyin | 0.55.0 | [mozillazg/python-pinyin](https://github.com/mozillazg/python-pinyin) | MIT |
| SentencePiece | 0.2.2 | [google/sentencepiece](https://github.com/google/sentencepiece) | Apache-2.0 |
| sherpa-onnx | 1.13.6 | [k2-fsa/sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) | Apache-2.0 |
| sounddevice | 0.5.6 | [spatialaudio/python-sounddevice](https://github.com/spatialaudio/python-sounddevice) | MIT |

这些依赖由使用者通过 Python 包管理器安装，本仓库不提交其源代码或二进制包。制作二进制分发包时，分发者必须重新收集并随包提供适用的许可证和 NOTICE。

## sherpa-onnx 关键词模型

项目使用：

```text
sherpa-onnx-kws-zipformer-zh-en-3M-2025-12-20
```

上游在官方 Release 提供模型下载，但截至本项目开源准备审计时，没有找到该模型权重、词表和相关文件明确的模型专用再分发许可证。上游也存在公开的许可证澄清请求：

- [官方模型文档](https://k2-fsa.github.io/sherpa/onnx/kws/pretrained_models/index.html#sherpa-onnx-kws-zipformer-zh-en-3m-2025-12-20-chinese-english)
- [模型许可证澄清 Issue](https://github.com/k2-fsa/sherpa-onnx/issues/3760)

因此本项目：

- 不把模型提交到 Git。
- 不把模型放入 GitHub Release。
- 不镜像或重新托管模型。
- 只指向上游官方来源，由使用者自行下载和核对适用条件。

上述做法是风险控制，不代表对模型权利状态作出法律结论。

## VB-CABLE

VB-CABLE 是 VB-Audio 的 Donationware 虚拟音频驱动：

- [官方产品页](https://vb-audio.com/Cable/index.htm)
- [官方许可与分发说明](https://vb-audio.com/Services/licensing.htm)
- [官方参考手册](https://vb-audio.com/Cable/VBCABLE_ReferenceManual.pdf)

VB-CABLE 不是开源依赖。本项目：

- 不打包或重新分发驱动安装程序。
- 不执行静默安装。
- 不把 VB-CABLE 许可证包含在 Apache-2.0 授权范围内。
- 要求用户从 VB-Audio 官网自行下载安装。
- 提醒公司、机构和专业用户按上游规则购买或确认适用许可。

## 产品名称和商标

Codex、OpenAI、Microsoft、Windows、VB-CABLE、VB-Audio、sherpa-onnx 及其他名称可能是其各自所有者的商标或项目名称。本项目仅为说明兼容性而合理引用，不表示任何隶属、授权或背书。

## 不是法律意见

本文件记录项目当前采用的合规边界，不构成法律意见。进行商业分发、企业部署或二进制打包前，请重新核对所有上游许可证并在需要时咨询专业人士。
