# BOTW 音乐替换包

《塞尔达传说：旷野之息》Switch 版音乐覆盖资源及处理脚本，当前版本为 **V18**。

## 使用方式

V18 是基于 V16 完整包并叠加 V17 神庙提示音修订的**增量覆盖包**。本仓库不包含 V16 完整基础包，使用前需要已有的 V16/V17 安装。

将 `BOTW-music-mod-v18-battle-swap-20260909/content/` 的内容覆盖到原有 V16/V17 `content/` 对应位置。

| 游戏入口 | V18 音乐 |
|---|---|
| `BGM_FieldBattle_QuickIntro_key2` | 神の怒り |
| `BGM_FieldBattle_Easy1_key1` | ojos tristes |

详细说明见 [V18 README](BOTW-music-mod-v18-battle-swap-20260909/README.md)。

## 下载资源

大型 `TitleBG.pack` 由 Git LFS 管理，推荐安装 Git LFS 后克隆：

```sh
git lfs install
git clone git@github.com:komakizhu/BOTW-music-mod.git
cd BOTW-music-mod
git lfs pull
```

使用前确认 `TitleBG.pack` 大小为 147,198,458 字节，避免将 LFS 指针当作游戏资源。

## 目录

| 路径 | 内容 |
|---|---|
| `BOTW-music-mod-v18-battle-swap-20260909/` | 当前 V18 增量覆盖包、试听、清单 |
| `BOTW-music-mod-v17-readriddle-e-20260908/` | V17 神庙提示音修订和试听 |
| `tools/` | 音频编码、战斗音乐交换脚本 |
| `audio-candidates/` | 神庙提示音候选试听 |

重新生成 V18 战斗资源需要另外提供 V16 基础资源，使用 `python3 tools/swap_battle_tracks.py --help` 查看参数。
