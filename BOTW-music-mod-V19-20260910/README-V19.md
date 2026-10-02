# BOTW Switch 音乐替换包 V19

本包由已合并并通过文件级验证的 BOTW 资源生成，目标版本为 Switch Title ID `01007EF00011E000`。V19 包含：

- 血月音乐调用链单次播放修复；
- 神庙提示音电平修订；
- 普通战斗 `神の怒り` / `ojos tristes` 入口对调；
- 已验证合并包中的其余音乐资源。

## 安装

将 `content/` 下的 95 个文件覆盖到 SD 卡：

`atmosphere/contents/01007EF00011E000/romfs/`

本次写入脚本只覆盖这 95 个同名资源，不删除目标目录中的其他文件。`V19-MANIFEST.json` 保存每个资源的大小和 SHA-256。

## 来源提交

- `914713cd057822a788649b25049a8e66646b7a77`：匹配神庙提示音原版电平
- `c3a2866c0ddd47096ace35cc6fb4bcdaafa5a7c5`：普通战斗音乐入口对调
- `826b5b28fcf6ffb75ec75f6ec7a320bec2501ff9`：血月单次播放调用链修复

这是 Switch 游戏资源覆盖包，不是 macOS App。
