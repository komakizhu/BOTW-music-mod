# BOTW 战斗音乐 V18：`神の怒り` / `ojos tristes` 对调

这是基于 V16 完整包、叠加 V17 神庙提示音修订后的增量覆盖包。V18 只改变两个普通战斗长入口；其余 V16/V17 内容保持不变。将本目录的 `content/` 覆盖到同一套 V16/V17 `content/` 后使用。

## 对调结果

| 游戏入口 | V16/V17 原音乐 | V18 音乐 |
|---|---|---|
| `BGM_FieldBattle_QuickIntro_key2` | `ojos tristes` | `神の怒り` |
| `BGM_FieldBattle_Easy1_key1` | `神の怒り` | `ojos tristes` |

两个 BFSTM 采用原 V16 文件的无损字节交换，因此原有采样率、声道、循环点和响度处理均随歌曲一起保留。为避免 Switch 先播放旧的内嵌预取音，V18 同步更新了：

- `content/Sound/Resource/FieldBattleBgm.bars` 中的 `BGM_FieldBattle_Easy1_key1`
- `content/Sound/Resource/D_FieldBattleBgm.bars` 中的 `BGM_FieldBattle_QuickIntro_key2`

V17 的最新 `content/Pack/TitleBG.pack` 也随包带入，确保神庙提示音修订不会丢失。

## 文件

- `content/`：需要覆盖的五个资源文件。
- `preview/01_QuickIntro_key2_神の怒り_60s.mp3`：对调后 QuickIntro 试听。
- `preview/02_Easy1_key1_ojos_tristes_60s.mp3`：对调后 Easy1 key1 试听。
- `pending/battle-swap-manifest.json`：来源、SHA-256 和对调记录。
- `tools/swap_battle_tracks.py`：从 V16 基线重新生成四个战斗资源和清单的脚本；V18 携带的 V17 `TitleBG.pack` 是刻意保留的上一版资源，试听 MP3 则由生成后的 BFSTM 用 `vgmstream`/`ffmpeg` 导出。

## 文件级验证

- 两个 BFSTM 均可由 `vgmstream` 读取：48 kHz、双声道、Nintendo DSP ADPCM。
- `QuickIntro_key2` 回读为 `1:41.200`，对应 `神の怒り`；`Easy1_key1` 回读为 `3:21.921`，对应 `ojos tristes`。
- 两份 BARS 均保持原文件大小和入口结构，两个目标 BFSTP 的 INFO 与前 `0xC000` 字节预取音频已从对调后的 BFSTM 更新。
- `TitleBG.pack` 保持 V17 文件大小 `147,198,458` bytes。

该项目是 Switch 游戏音频覆盖包，不是 App，因此没有 App 编译步骤；没有写入 SD 卡，也没有修改 `main`。
