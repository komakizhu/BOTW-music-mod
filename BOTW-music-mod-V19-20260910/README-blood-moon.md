# BOTW Switch 1.6.0 音乐替换包 v18（本地候选，待 Switch 实机验证）

V18 从已确认的 V16 复制，只在当前独立 Worktree 中生成；没有写入 SD、没有修改 main、没有修改原始导出，也没有提交 Git。V16 的 94 个既有 `content/` 文件保持逐文件 SHA-256 不变；V18 新增一个完整的 `content/Pack/Bootup.pack`，用于修复血月音乐的调用层。

## V18 本次修复：血月调用层

- 已确认中断根因不在 `BloodyMoonRelief.sbeventpack`：该事件包中的 `EventBgmCtrlTag` 绑定的是 NPC 的 `Musician012Bgm`，不是血月 Omen 音乐。
- 目标版本 `Bootup.pack → SLink2/SLink2DB.sbslnk` 中，用户 `0x63861a2b` 的 `Omen` 原本是按全局 `时刻` 在 `Level3/2/1/0` 间动态切换的 `Switch`。这解释了 V16 将 `00a` 拉长后仍会“播放一段、再进一点、又被切断”。
- V18 将调用层固定为 `Omen(Sequence 4..4) → Level0(Sequence 10..10) → 00a`，只调用已拉长至 30 秒的 `BGM_OmenOfBloodyMoon00a.bfstm`；不改 BARS、不改事件包、不改其他 143 个 Bootup 成员。
- SLink2 解压后的 XLNK 仅有 3 个 little-endian `u32` 改动：`0x1bf47c: 0→4`、`0x1bf480: 1→4`、`0x1bf478: 13→10`。

## V18 文件级验证

- 原始 1.6.0 `Bootup.pack`：SHA-256 `8bf0fad6b6297a9357817b9628ad0989dad4f3989d9e08d6181bee50c888e443`。
- V18 生成 `Bootup.pack`：SHA-256 `83cce44f273e7347951a38082e9f3519d4e07f50f8506ad909cca5092cac3b98`。
- SARC：144/144 成员可枚举；除 `SLink2/SLink2DB.sbslnk` 外其余 143 个成员逐字节一致；嵌套 Yaz0 → XLNK 回读通过。
- V18 与 V16 同名 `content` 文件：94 个全部一致；新增文件：`content/Pack/Bootup.pack`。
- BARS 保持 V16 版本哈希 `9d4bed889988ebc318b4b8fc3fd6f3b744813b73fbef9aa1ad47a27026850826`；事件包未加入 V18 `content`。
- 详细报告：[slink2-omen-patch-report.json](pending/blood-moon-single-play-20260909/slink2-omen-patch-report.json)；完整验证：[verification-report.md](pending/blood-moon-single-play-20260909/verification-report.md)；可重复生成脚本：[patch_slink2_omen.py](pending/blood-moon-single-play-20260909/patch_slink2_omen.py)。

## V18 交接边界

当前只完成资源格式与调用图静态验证，尚未完成 Switch 实机验收；不能把静态通过表述为已经证明实机无外部停止/重触发。请先备份当前 SD 对应文件，再由用户明确授权后手动覆盖。`backup/original-1.6.0-sources/Bootup.pack` 是原始回退副本；`backup/` 不要复制到 SD。

以下为 V16 历史说明，保留用于回退和追溯。

## 本次包含

- 血月：6 个分段，使用 `Got That Feeling`。
- Guardian：主音乐和结束音乐，使用 `Feels Good to Laugh`；同时补齐固定型 Guardian 使用的 `GuardianFixedBgm.bars` / `BGM_GuardianFixed.bfstm`。
- 骑马：白天循环/结束、夜间循环/结束，分别使用 `Tapestry` 和 `Snooze`。
- 驿站：`7 in the Morning` 的四声道版本。
- 迷宫：`Tip Toe`。
- 大妖精之泉：`As It Was`。
- 村庄固定夜间版：雅哈哈森林、卓拉领地、利特村、鼓隆城、一始村；哈特诺村恢复原版全天音乐。
- 马龙之泉：`windspeaks`。
- 卡卡利科村：夜间版。
- 哈特诺古代研究所：`監視砦`。
- 阿卡莱古代研究所：`あなたは煙草　私はシャボン`。
- 城堡外围：`ハイラル城（地上）`，并重新生成 `CastleBgm.bars` 中的内嵌音频。
- 怪物商店：使用你确认的 `Fly Me to the Moon`（claire）自定义版本；整首约 273.068 秒，前 1.792 秒淡入、结尾 3 秒淡出、关闭循环；v15 最终在原 v15 基础上提升 `+9 dB`，实测约 `-19.1 LUFS-I`。
- 普通战斗：保留四首已确认的自定义战斗音乐；采用已下载的 Fiction Switch MOD 的战斗 BARS 结构。四首长入口分别是 `QuickIntro_key2`、`Easy1_key0`、`Easy1_key1`、`Easy1_key2`；其余 43 个转场入口使用该 MOD 同尺寸的静音占位，防止游戏切回原版动态片段。四首来源均按你的最新确认记录为已获授权。
- 神庙内部背景：采用已确认的王国之泪风格整曲方案，使用 `Event_BGM_PutPicture.bfstm` 和同步更新的 `PutPictureBgm.bars`；主曲保留整首循环，启动预取已嵌入 BARS。此项不使用 `Ylang Ylang`。
- 神庙提示音：此前的 `BGM_DungeonMessage.bfstm` 一始村替换按原样保留；本候选另外将 `TitleBG.pack → source/TriggerTag.bars → BGM_ReadRiddle` 替换为同一首一始村音频的前 2.281 秒，以覆盖录屏 23.5–25 秒对应的正确触发槽位。两个槽位均使用一始村来源，互不合并。
- 神庙完成后短促提示音：将 `Event_NV_Priest006.bfstm` 改为同规格全静音文件；原版文件保存在 `backup/v15-content-before-priest006-mute/`。这项用于消除录屏倒数第三段 23.5–25.5 秒对应的原版提示音。
- 普通战斗的 BARS：使用参考 MOD 的 Switch 版本 BARS，不使用 v7 自行扩展长度的 BARS；四个长入口的内嵌 BFSTP 已按原版 `DATA+0x20` 规则同步到最终 BFSTM，RSTB 日志要求为 0。
- v15 最终响度：驿站 `+9.7 dB`、怪物商店 `+9 dB`、骑马四项 `+15 dB`、普通战斗 QuickIntro `+5 dB`、其他三首普通战斗 `+15 dB`；Guardian 主/结束/固定型分别 `+12.7/+8/+8 dB`；迷宫/大妖精/马龙之泉分别 `+12.5/+11.4/+10.7 dB`；哈特诺/阿卡莱研究所分别 `+6/+3.9 dB`；神庙提示音 `+11.4 dB`。这是整文件增益，不做分段响度匹配或重新拼接。
- 骑马兼容修正：白天、夜间循环均保留原游戏循环槽位的总采样数和循环点，避免自定义长曲在固定位置被截断；结束音乐保持原有结束槽位长度。
- `previews/approved-auditions/`：本次试听通过的可播放 MP3。

## 本次暂不加入或保留原版

- 城堡内部和四神兽内部：取消修改；本包中的城堡项目仅指城堡外围音乐。
- 沃托里村和格鲁德小镇：保留原版全天音乐。
- `BGM_DungeonTitle.bfstm`、`DungeonRewardBgm.bars` 及其相关奖励资源：保留原版；`BGM_DungeonMessage` 是否覆盖所有发现、开门和机关完成提示，仍需实机逐项确认。

## v10–v12 保留内容

- 普通战斗：不再恢复为原版；47 个自定义结构入口已按参考 MOD 重建，3 个结束入口保留原版。
- 四首自定义战斗 BFSTM 在 v15 最终响度修订中按已确认增益重新编码；四个 BARS 内嵌预取音也同步更新。
- v9 的原始内容已保存到 `backup/v9-content-before-shrine-merge/content/`，可回退到 v9。
- Guardian：v9 同时包含普通型和固定型两条资源链；三条自定义音频均为已验证的低响度版本。
- 神庙内部：从旧 v6 的已确认王国之泪方案中恢复 `Event_BGM_PutPicture.bfstm` 与 `PutPictureBgm.bars`，并保留 v9 的战斗、Guardian 和响度修正。
- 响度实测：完整结果见 `pending/loudness-report-20260905.md`；旧版 `pending/loudness-report-20260904.md` 作为历史记录保留。
- 当前已完成 Mac 文件级验证并将 V16 写入 SD；尚未在 Switch 游戏内重新测试。v10/v11/v12/v13/v14/v15 仍未单独写入 SD 卡。

## v11 本次变更

- 哈特诺村 `BGM_Spot_NewHatenoVillage_Allday.bfstm` 已恢复为 BOTW 1.6.0 原始全天文件，不再使用哈特诺村夜间自定义版本。
- v10 中被替换的哈特诺村文件已备份到 `backup/v10-content-before-hateno-restore/content/`，可回退。
- 新文件与原始导出文件 SHA-256 均为 `b25a1e0765b8a3c3b3b45346f10bbdf056f38f835adbfb507a3f8ca50827ce89`。

## v12 本次变更

- 怪物商店 `Bgm_Spot_MamonoShop.bfstm` 已恢复为你确认的 `Fly Me to the Moon` 自定义版本，不再使用 BOTW 原版音乐。
- v11 中的原版怪物商店文件已备份到 `backup/v11-content-before-mamono-shop-restore/content/`，可回退。
- 自定义文件 SHA-256 为 `9893d9ffd71b11cbad27f7939e9bd5abc3b6ab607ef28be102e211538b4cbaa6`；对应 48 kHz、2 声道、约 273.068 秒的 BFSTM。
- 怪物商店使用原有外部文件引用，未改动 `MamonoShopBgm.bars`。

## v13 本次变更

- 神庙提示音 `Sound/Resource/Stream/BGM_DungeonMessage.bfstm` 已从 v12 的待定候选并入 `content/`；来源是已确认的一始村建造过渡音 `Event_BGM_MovingIchikara.bfstm`。
- v12 原始目标文件已备份到 `backup/v12-content-before-shrine-prompt-merge/content/Sound/Resource/Stream/BGM_DungeonMessage.bfstm`，可单文件回退。
- 提示音文件为 48 kHz、2 声道、约 12.397 秒；文件级格式检查通过。当前没有擅自改动 `BGM_DungeonTitle.bfstm`、`DungeonRewardBgm.bars` 或奖励资源。
- 神庙内部背景的王国之泪风格方案继续保留；普通战斗继续是四个长入口加 43 个转场占位；四首普通战斗音乐的授权状态按你的最新确认记录为“已获授权”。

## 安全状态

- v7 曾在 2026-09-03 经确认后合并到 SD 卡；V16 于 2026-09-07 经确认写入同一游戏 `romfs`。V16 写卡前覆盖到的 92 个旧文件已备份到 `work/sd-card-backup-before-v16-20260907/`。
- v10 在本机另存了 v9 内容备份 `backup/v9-content-before-shrine-merge/content/`；v11 另存了 v10 的哈特诺村文件；v12 另存了 v11 的原版怪物商店文件；v13 另存了 v12 的神庙提示音原版文件；v14 另存了 v13 的神庙提示音文件；没有删除 v13、v12、v11、v10、v9、v8 或 v7。
- 没有修改存档。
- 没有修改原始导出目录。
- `content/` 是已写入 SD 的替换内容；`backup/` 只用于回滚，不要复制到 SD 卡。
- 所有输出都已经回读检查采样率、声道数和时长；SD 写入后 94/94 文件哈希一致，仍需进行 Switch 游戏内测试。

## 本次版本确认

- 驿站使用最后确认的整首版本：约 199.394 秒、48 kHz、4 声道、前 1.792 秒淡入、关闭循环。
- 骑马白天循环：48 kHz、立体声、循环点约 4.779 秒、槽位总时长约 90.112 秒。
- 骑马夜间循环：48 kHz、立体声、循环点约 4.779 秒、槽位总时长约 92.051 秒。
- 神庙提示音：`BGM_DungeonMessage.bfstm` 已并入主 `content/`，48 kHz、2 声道、约 12.397 秒；v14 为约 `-41.4 LUFS-I`，真峰值约 `-25.8 dBFS`；v13 文件已在 v14 备份。
- 怪物商店使用 `Fly Me to the Moon` 的 48 kHz、2 声道 BFSTM，约 273.068 秒；对应原始 `MamonoShopBgm.bars` 中的音乐引用是外部文件，因此本次只放入 `Bgm_Spot_MamonoShop.bfstm`，没有改动该 BARS。

## v14 本次变更

- 神庙提示音 `BGM_DungeonMessage.bfstm` 由 v13 的 `-30.1 LUFS-I` 调整为 `-41.4 LUFS-I`，匹配原版目标槽位；真峰值由 `-14.5 dBFS` 降为 `-25.8 dBFS`。
- 保持 48 kHz、2 声道、约 12.397 秒和 Nintendo DSP ADPCM；重新编码后 vgmstream 可正常读取。
- v13 的提示音文件已备份到 `backup/v13-content-before-shrine-loudness-match/content/Sound/Resource/Stream/BGM_DungeonMessage.bfstm`，可回退到 v13。
- 除该提示音外，v14 的 `content/` 与 v13 相同；没有改神庙背景、神庙标题音、奖励音或其他音乐。

## v15 本次变更

- 血月改为单一连续入口方案：`BGM_OmenOfBloodyMoon00a.bfstm` 使用同一首来源音频的前 30 秒，保持 48 kHz、立体声；不再对分段分别匹配响度，也不在线性拼接多个裁切段。
- `00a` 只在最后 3 秒做一次整体余弦淡出；后续 `00b`、`01`、`02a`、`02b`、`03` 保持原槽位时长的合法静音 BFSTM，避免 30 秒后继续触发旧分段声音。
- `OmenOfBloodyMoonBgm.bars` 保留原版资源顺序、音频格式和 `03` 槽位标记，仅将 `00a` 的采样数同步为 1,440,000（30 秒）；没有加入分段响度匹配或额外混音。
- v15 血月六个 BFSTM 均已通过 vgmstream 文件级读取；`00a` 解码为 30.000000 秒，后五个槽位解码后均为全静音。试听文件保存在对应的 v14 `pending/blood-moon-30s-first-slot-fadeout-audition-20260904/preview/` 目录中。
- v15 由 v14 完整复制后仅替换上述血月资源；v14 保留作 A/B 回退。V15 未单独写入 SD 卡；当前 SD 上的内容为 V16。

### v15 最终响度修订

- 在不改变血月 30 秒首槽位方案的前提下，按用户最终确认的增益表重做 19 个主 BFSTM；处理方式是整文件增益后重新编码，未对同一首歌的片段分别匹配响度。
- 战斗和 Guardian 的 BARS 内嵌预取音已从最终 BFSTM 的 `DATA+0x20` 生成并回填；BARS 文件长度、入口数量和 Switch 小端结构保持不变。
- 神庙提示音恢复到最终确认的约 `-30.0 LUFS-I`；哈特诺古代研究所约 `-17.4 LUFS-I`，阿卡莱古代研究所调整为约 `-16.0 LUFS-I`。
- 驿站最终调整为约 `-16.0 LUFS-I`，怪物商店约 `-19.1 LUFS-I`；战斗四个长入口最终约 `-18.3/-19.8/-18.0/-21.1 LUFS-I`（QuickIntro、Easy1 key0、key1、key2）。
- 主音频构建规则在 `pending/build_final_loudness.py`，必须显式提供未加增益的 v15 基准目录，避免重复增益；BARS 预取规则在 `pending/update_prefetch_bars.py`。
- 上述历史响度修改在本地 v15 完成；当前 V16 写入记录见文末，未修改存档、删除旧版本、清空废纸篓或上传 GitHub。

## 一个已报告的兼容性差异

利特村原始资源是 6 声道，而用户提供的夜间音乐是立体声；城堡外围原始资源也是 6 声道，而用户提供的音乐是立体声。当前包对这两项都使用可正常读取的 48kHz 立体声兼容版本；没有把无法读取的 6 声道试验文件放入包内。城堡外围的立体声版本已经嵌入 `CastleBgm.bars`，需要在游戏内重点测试。

## v16 原始变更

- 仅新增 `content/Sound/Resource/Stream/Event_NV_Priest006.bfstm` 的静音替换。
- 保持原版 48 kHz、2 声道、Nintendo DSP ADPCM、约 5.440 秒和原始采样数不变；仅将 BFSTM 的 `DATA` 音频载荷置零。
- 原版文件备份在 `backup/v15-content-before-priest006-mute/content/Sound/Resource/Stream/Event_NV_Priest006.bfstm`。
- 原始 V16 阶段没有新增 `BGM_GetDemoDeluxe` 或 `BGM_DungeonMessage` 的改动；后续追加的 `BGM_ReadRiddle` 与此前的 `BGM_DungeonMessage` 替换见下节。写卡记录见文末；未修改存档、不删除旧版本。

## v16 本次追加：BGM_ReadRiddle

- 保留 V16 的 `Event_NV_Priest006.bfstm` 静音，不移除此前已确认的静音安排。
- `BGM_ReadRiddle` 的真实资源位于原版 `TitleBG.pack` 内的 `source/TriggerTag.bars`，不是 `Sound/Resource/Stream/` 外置文件；本候选只替换该 BARS 内唯一的 `FWAV` 成员。
- `BGM_ReadRiddle` 使用一始村 `Event_BGM_MovingIchikara.bfstm` 的前 109501 个采样（48 kHz、双声道、2.281 秒），保留目标 BFWAV 的文件大小、采样数、声道布局和 Nintendo DSP ADPCM 格式。
- 之前错误替换的 `Sound/Resource/Stream/BGM_DungeonMessage.bfstm` 保持不变，因此 V16 共有两个独立的一始村替换位：`BGM_DungeonMessage` 与 `BGM_ReadRiddle`。
- `content/Pack/TitleBG.pack` 保持原版 147198458 字节；内层 `source/TriggerTag.bars` 保持 324656 字节。该文件已写回 SD；未修改存档、删除旧版本或上传外部平台。
- 新槽位试听保存在 `previews/BGM_ReadRiddle_ichikara_v16_candidate.mp3`；仅为文件级试听，尚未进行 Switch 实机验证。

## V16 SD 写入记录（2026-09-07）

- 写入目标：`/Volumes/Untitled/atmosphere/contents/01007EF00011E000/romfs/`。
- 写入来源：本包的 `content/`；共 94 个文件，采用不删除既有文件的覆盖复制。
- 写卡前已将 92 个同路径旧文件备份到 `work/sd-card-backup-before-v16-20260907/`；另有 2 个文件为新增。
- 写入后逐文件 SHA-256 回读：94/94 匹配，0 个缺失，0 个不一致。
- 本次只操作游戏 `romfs`；没有修改 `JKSV` 或其他存档目录，没有删除旧版本、清空废纸篓或上传 GitHub。
