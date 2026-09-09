# BOTW ReadRiddle E 段候选（匹配替换前原版电平）

这是基于 V16 的增量候选，只替换神庙提示音真实资源位：
`content/Pack/TitleBG.pack` 内 `source/TriggerTag.bars` 的唯一 `FWAV`
（`BGM_ReadRiddle`）。它不是完整 V16 包，使用时把这个 `TitleBG.pack`
覆盖到 V16 的同路径即可。

## 本次处理

- 来源：`E_高潮核心_6.80-8.80s.mp3`
- 可听内容：48 kHz、双声道、2.000 秒
- 电平基准：从本机保存的 BOTW 1.6.0 原始 `TitleBG.pack` 中直接提取替换前
  的 `BGM_ReadRiddle`，原始成员 SHA-256 为
  `c1fb6d8609a32a39f72031893f6d1fe8bbb4eb94af7a1c7638aa47cb6b4958e1`
- 原版实测：`-23.7 LUFS-I`、`-11.1 dBFS` 峰值
- 本次处理：E 段整体 `+14.3 dB`，不改变 `6.80–8.80s` 的裁切内容
- 游戏槽位：109,501 samples，名义 2.281271 秒
- 2 秒之后：无声填充，仅用于保持 V16 原槽位尺寸和容器布局
- 编码：Nintendo DSP 4-bit ADPCM

## 文件

- `content/Pack/TitleBG.pack`：可用于 V16 覆盖测试的游戏资源文件
- `preview/BGM_ReadRiddle_E_高潮核心_6.80-8.80s_匹配原版电平_2s.mp3`：两秒 E 段试听
- `preview/BGM_ReadRiddle_E_游戏编码试听_匹配原版电平_2.281s.mp3`：按游戏编码回读后的试听，末尾含槽位静音
- `pending/BGM_ReadRiddle_E_高潮核心_6.80-8.80s_匹配原版电平.bfwav`：独立替换资源
- `pending/BGM_ReadRiddle_E_高潮核心_6.80-8.80s_匹配原版电平_input.wav`：编码输入，便于复现

E 段和原版素材的动态不同，因此峰值和算术平均值不能同时逐项相等；本次以
原版实际综合响度 `-23.7 LUFS-I` 为匹配目标。新游戏编码资源回读为
`-23.7 LUFS-I`、`-12.9 dBFS` 峰值，保留安全裕量，没有削波。

## 已完成验证

- `TitleBG.pack`：147,198,458 bytes，尺寸未变化
- `TriggerTag.bars`：324,656 bytes，尺寸未变化
- 嵌入 FWAV 与独立 BFWAV 逐字节一致
- vgmstream 可读：48 kHz、双声道、Nintendo DSP ADPCM
- 回读综合响度：`-23.7 LUFS-I`
- 回读峰值：`-12.9 dBFS`，无削波
- 2 秒之后的槽位填充为静音

本候选只在 `codex/task-worktree` 独立分支/worktree 中生成，未写 SD 卡，未修改 main，未提交 commit。
