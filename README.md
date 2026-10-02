# BOTW Switch 音乐替换包 V19

《塞尔达传说：旷野之息》Switch 版音乐替换资源。当前发布版本为 **V19（2026-09-10）**，包含完整合并后的 95 个资源文件，共 522,254,002 字节。

V19 整合血月音乐调用链单次播放修复、神庙提示音电平修订、普通战斗「神の怒り」与「ojos tristes」入口对调，以及此前已确认的音乐资源。无需另行叠加 V16/V17/V18 覆盖包。

## 下载

大型 `.pack` 文件由 Git LFS 管理。安装 Git LFS 后克隆仓库：

```sh
git lfs install
git clone git@github.com:komakizhu/BOTW-music-mod.git
cd BOTW-music-mod
git lfs pull
```

V19 位于 `BOTW-music-mod-V19-20260910/`。使用前确认该目录中的 `content/Pack/TitleBG.pack` 大小为 147,198,458 字节，避免将 LFS 指针当作游戏资源。

## 安装

将 `BOTW-music-mod-V19-20260910/content/` 内的文件复制到 SD 卡对应目录：

```text
atmosphere/contents/01007EF00011E000/romfs/
```

保持 `Pack/`、`Sound/` 等目录结构，覆盖同名文件即可。安装前备份已有资源。

[V19 说明](BOTW-music-mod-V19-20260910/README-V19.md)包含来源提交和版本信息；[V19 资源清单](BOTW-music-mod-V19-20260910/V19-MANIFEST.json)记录每个文件的大小及 SHA-256。

## 仓库目录

| 目录 | 用途 |
|---|---|
| `BOTW-music-mod-V19-20260910/` | 当前 V19 完整合并包 |
| `BOTW-music-mod-v18-battle-swap-20260909/` | 历史 V18 增量包及试听 |
| `BOTW-music-mod-v17-readriddle-e-20260908/` | 历史 V17 神庙提示音修订及试听 |
| `tools/` | 音频资源处理脚本 |
| `audio-candidates/` | 历史神庙提示音候选试听 |

本仓库为游戏资源覆盖包，不是 macOS App。
