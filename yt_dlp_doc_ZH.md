<!-- MANPAGE: BEGIN EXCLUDED SECTION -->
<div align="center">

[![YT-DLP](https://raw.githubusercontent.com/yt-dlp/yt-dlp/master/.github/banner.svg)](#readme)

[![Release version](https://img.shields.io/github/v/release/yt-dlp/yt-dlp?color=brightgreen&label=Latest&style=for-the-badge)](#%E5%AE%89%E8%A3%85 "安装")
[![Python Version](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fyt-dlp%2Fyt-dlp%2Frefs%2Fheads%2Fmaster%2Fpyproject.toml&style=for-the-badge)](https://github.com/yt-dlp/yt-dlp/blob/master/pyproject.toml "Python 版本")
[![PyPI](https://img.shields.io/badge/-PyPI-blue.svg?logo=pypi&labelColor=555555&style=for-the-badge)](https://pypi.org/project/yt-dlp "PyPI")
[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?&logo=discord&logoColor=white&style=for-the-badge)]([#](https://discord.gg/H5MNcFW63r "Discord")
[![License: Unlicense](https://img.shields.io/badge/-Unlicense-red.svg?style=for-the-badge)](LICENSE "许可证")
[![Commits](https://img.shields.io/github/commit-activity/m/yt-dlp/yt-dlp?label=commits&style=for-the-badge)](https://github.com/yt-dlp/yt-dlp/commits "提交历史")

</div>
<!-- MANPAGE: END EXCLUDED SECTION -->

yt-dlp 是一个功能丰富的命令行音频/视频下载器，支持[数千个网站](supportedsites.md)。该项目是 [youtube-dl](https://github.com/ytdl-org/youtube-dl) 的分支，基于现已停止维护的 [youtube-dlc](https://github.com/blackjack4494/yt-dlc)。

<!-- MANPAGE: MOVE "USAGE AND OPTIONS" SECTION HERE -->

<!-- MANPAGE: BEGIN EXCLUDED SECTION -->
* [安装](#%E5%AE%89%E8%A3%85)
    * [详细说明](https://github.com/yt-dlp/yt-dlp/wiki/Installation)
    * [发布文件](#%E5%8F%91%E5%B8%83%E6%96%87%E4%BB%B6)
    * [更新](#%E6%9B%B4%E6%96%B0)
    * [依赖项](#%E4%BE%9D%E8%B5%96%E9%A1%B9)
    * [编译](#%E7%BC%96%E8%AF%91)
* [用法与选项](#%E7%94%A8%E6%B3%95%E4%B8%8E%E9%80%89%E9%A1%B9)
    * [通用选项](#%E9%80%9A%E7%94%A8%E9%80%89%E9%A1%B9)
    * [网络选项](#%E7%BD%91%E7%BB%9C%E9%80%89%E9%A1%B9)
    * [地理限制](#%E5%9C%B0%E7%90%86%E9%99%90%E5%88%B6)
    * [视频选择](#%E8%A7%86%E9%A2%91%E9%80%89%E6%8B%A9)
    * [下载选项](#%E4%B8%8B%E8%BD%BD%E9%80%89%E9%A1%B9)
    * [文件系统选项](#%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F%E9%80%89%E9%A1%B9)
    * [缩略图选项](#%E7%BC%A9%E7%95%A5%E5%9B%BE%E9%80%89%E9%A1%B9)
    * [快捷方式选项](#%E5%BF%AB%E6%8D%B7%E6%96%B9%E5%BC%8F%E9%80%89%E9%A1%B9)
    * [详细输出与模拟选项](#%E8%AF%A6%E7%BB%86%E8%BE%93%E5%87%BA%E4%B8%8E%E6%A8%A1%E6%8B%9F%E9%80%89%E9%A1%B9)
    * [权变措施 (Workarounds)](#%E6%9D%83%E5%8F%98%E6%8E%AA%E6%96%BD)
    * [视频格式选项](#%E8%A7%86%E9%A2%91%E6%A0%BC%E5%BC%8F%E9%80%89%E9%A1%B9)
    * [字幕选项](#%E5%AD%97%E5%B9%95%E9%80%89%E9%A1%B9)
    * [认证选项](#%E8%AE%A4%E8%AF%81%E9%80%89%E9%A1%B9)
    * [后期处理选项](#%E5%90%8E%E6%9C%9F%E5%A4%84%E7%90%86%E9%80%89%E9%A1%B9)
    * [SponsorBlock 选项](#sponsorblock-%E9%80%89%E9%A1%B9)
    * [提取器选项](#%E6%8F%90%E5%8F%96%E5%99%A8%E9%80%89%E9%A1%B9)
    * [预设别名](#%E9%A2%84%E8%AE%BE%E5%88%AB%E5%90%8D)
* [配置](#%E9%85%8D%E7%BD%AE)
    * [配置文件编码](#%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6%E7%BC%96%E7%A0%81)
    * [使用 netrc 认证](#%E4%BD%BF%E7%94%A8-netrc-%E8%AE%A4%E8%AF%81)
    * [关于环境变量的说明](#%E5%85%B3%E4%BA%8E%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E7%9A%84%E8%AF%B4%E6%98%8E)
* [输出模板](#%E8%BE%93%E5%87%BA%E6%A8%A1%E6%9D%BF)
    * [输出模板示例](#%E8%BE%93%E5%87%BA%E6%A8%A1%E6%9D%BF%E7%A4%BA%E4%BE%8B)
* [格式选择](#%E6%A0%BC%E5%BC%8F%E9%80%89%E6%8B%A9)
    * [过滤格式](#%E8%BF%87%E6%BB%A4%E6%A0%BC%E5%BC%8F)
    * [排序格式](#%E6%8E%92%E5%BA%8F%E6%A0%BC%E5%BC%8F)
    * [格式选择示例](#%E6%A0%BC%E5%BC%8F%E9%80%89%E6%8B%A9%E7%A4%BA%E4%BE%8B)
* [修改元数据](#%E4%BF%AE%E6%94%B9%E5%85%83%E6%95%B0%E6%8D%AE)
    * [修改元数据示例](#%E4%BF%AE%E6%94%B9%E5%85%83%E6%95%B0%E6%8D%AE%E7%A4%BA%E4%BE%8B)
* [提取器参数](#%E6%8F%90%E5%8F%96%E5%99%A8%E5%8F%82%E6%95%B0)
* [插件](#%E6%8F%92%E4%BB%B6)
    * [安装插件](#%E5%AE%89%E8%A3%85%E6%8F%92%E4%BB%B6)
    * [开发插件](#%E5%BC%80%E5%8F%91%E6%8F%92%E4%BB%B6)
* [嵌入 YT-DLP](#%E5%B5%8C%E5%85%A5-yt-dlp)
    * [嵌入示例](#%E5%B5%8C%E5%85%A5%E7%A4%BA%E4%BE%8B)
* [与 YOUTUBE-DL 的区别](#%E4%B8%8E-youtube-dl-%E7%9A%84%E5%8C%BA%E5%88%AB)
    * [新功能](#%E6%96%B0%E5%8A%9F%E8%83%BD)
    * [默认行为的区别](#%E9%BB%98%E8%AE%A4%E8%A1%8C%E4%B8%BA%E7%9A%84%E5%8C%BA%E5%88%AB)
    * [已弃用的选项](#%E5%B7%B2%E5%BC%83%E7%94%A8%E7%9A%84%E9%80%89%E9%A1%B9)
* [参与贡献](CONTRIBUTING.md#contributing-to-yt-dlp)
    * [提交问题 (Issue)](CONTRIBUTING.md#opening-an-issue)
    * [开发者指南](CONTRIBUTING.md#developer-instructions)
* [WIKI](https://github.com/yt-dlp/yt-dlp/wiki)
    * [常见问题 (FAQ)](https://github.com/yt-dlp/yt-dlp/wiki/FAQ)
<!-- MANPAGE: END EXCLUDED SECTION -->


# 安装

<!-- MANPAGE: BEGIN EXCLUDED SECTION -->
[![Windows](https://img.shields.io/badge/-Windows_x64-blue.svg?style=for-the-badge&logo=windows)](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe)
[![Unix](https://img.shields.io/badge/-Linux/BSD-red.svg?style=for-the-badge&logo=linux)](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp)
[![MacOS](https://img.shields.io/badge/-MacOS-lightblue.svg?style=for-the-badge&logo=apple)](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos)
[![PyPI](https://img.shields.io/badge/-PyPI-blue.svg?logo=pypi&labelColor=555555&style=for-the-badge)](https://pypi.org/project/yt-dlp)
[![Source Tarball](https://img.shields.io/badge/-Source_tar-green.svg?style=for-the-badge)](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.tar.gz)
[![Other variants](https://img.shields.io/badge/-Other-grey.svg?style=for-the-badge)](#%E5%8F%91%E5%B8%83%E6%96%87%E4%BB%B6)
[![All versions](https://img.shields.io/badge/-All_Versions-lightgrey.svg?style=for-the-badge)](https://github.com/yt-dlp/yt-dlp/releases)
<!-- MANPAGE: END EXCLUDED SECTION -->

你可以使用 [二进制文件](#%E5%8F%91%E5%B8%83%E6%96%87%E4%BB%B6)、[pip](https://pypi.org/project/yt-dlp) 或其他第三方包管理器来安装 yt-dlp。详细说明请参考 [wiki](https://github.com/yt-dlp/yt-dlp/wiki/Installation)。


<!-- MANPAGE: BEGIN EXCLUDED SECTION -->
## 发布文件

#### 推荐项

文件|说明
:---|:---
[yt-dlp](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp)|跨平台的 [zipimport](https://docs.python.org/3/library/zipimport.html) 二进制文件。需要 Python 环境（推荐用于 **Linux/BSD**）
[yt-dlp.exe](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe)|Windows (Win8+) 独立 x64 二进制文件（推荐用于 **Windows**）
[yt-dlp_macos](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos)|Universal MacOS (10.15+) 独立可执行文件（推荐用于 **MacOS**）

#### 其他选择

文件|说明
:---|:---
[yt-dlp_linux](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux)|Linux (glibc 2.17+) 独立 x86_64 二进制文件
[yt-dlp_linux.zip](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux.zip)|未打包的 Linux (glibc 2.17+) x86_64 可执行文件（无自动更新）
[yt-dlp_linux_aarch64](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux_aarch64)|Linux (glibc 2.17+) 独立 aarch64 二进制文件
[yt-dlp_linux_aarch64.zip](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux_aarch64.zip)|未打包的 Linux (glibc 2.17+) aarch64 可执行文件（无自动更新）
[yt-dlp_linux_armv7l.zip](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux_armv7l.zip)|未打包的 Linux (glibc 2.31+) armv7l 可执行文件（无自动更新）
[yt-dlp_musllinux](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_musllinux)|Linux (musl 1.2+) 独立 x86_64 二进制文件
[yt-dlp_musllinux.zip](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_musllinux.zip)|未打包的 Linux (musl 1.2+) x86_64 可执行文件（无自动更新）
[yt-dlp_musllinux_aarch64](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_musllinux_aarch64)|Linux (musl 1.2+) 独立 aarch64 二进制文件
[yt-dlp_musllinux_aarch64.zip](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_musllinux_aarch64.zip)|未打包的 Linux (musl 1.2+) aarch64 可执行文件（无自动更新）
[yt-dlp_x86.exe](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_x86.exe)|Windows (Win8+) 独立 x86 (32位) 二进制文件
[yt-dlp_win_x86.zip](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_win_x86.zip)|未打包的 Windows (Win8+) x86 (32位) 可执行文件（无自动更新）
[yt-dlp_arm64.exe](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_arm64.exe)|Windows (Win10+) 独立 ARM64 二进制文件
[yt-dlp_win_arm64.zip](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_win_arm64.zip)|未打包的 Windows (Win10+) ARM64 可执行文件（无自动更新）
[yt-dlp_win.zip](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_win.zip)|未打包的 Windows (Win8+) x64 可执行文件（无自动更新）
[yt-dlp_macos.zip](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos.zip)|未打包的 MacOS (10.15+) 可执行文件（无自动更新）

#### 杂项

文件|说明
:---|:---
[yt-dlp.tar.gz](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.tar.gz)|源代码压缩包
[SHA2-512SUMS](https://github.com/yt-dlp/yt-dlp/releases/latest/download/SHA2-512SUMS)|GNU 风格的 SHA512 校验和
[SHA2-512SUMS.sig](https://github.com/yt-dlp/yt-dlp/releases/latest/download/SHA2-512SUMS.sig)|SHA512 校验和的 GPG 签名文件
[SHA2-256SUMS](https://github.com/yt-dlp/yt-dlp/releases/latest/download/SHA2-256SUMS)|GNU 风格的 SHA256 校验和
[SHA2-256SUMS.sig](https://github.com/yt-dlp/yt-dlp/releases/latest/download/SHA2-256SUMS.sig)|SHA256 校验和的 GPG 签名文件

可用于验证 GPG 签名的公钥[可在此处获取](https://github.com/yt-dlp/yt-dlp/blob/master/public.key)
用法示例：
```
curl -L https://github.com/yt-dlp/yt-dlp/raw/master/public.key | gpg --import
gpg --verify SHA2-256SUMS.sig SHA2-256SUMS
gpg --verify SHA2-512SUMS.sig SHA2-512SUMS
```

#### 许可证信息

虽然 yt-dlp 采用 [Unlicense](LICENSE) 许可证，但许多发布文件中包含了来自其他拥有不同许可证的项目的代码。

最显著的是，由 PyInstaller 打包的可执行文件中包含了基于 GPLv3+ 许可的代码，因此组合后的作品受 [GPLv3+](https://www.gnu.org/licenses/gpl-3.0.html) 许可。

zipimport Unix 可执行文件 (`yt-dlp`) 包含了来自 [`meriyah`](https://github.com/meriyah/meriyah) 的 [ISC](https://github.com/meriyah/meriyah/blob/main/LICENSE.md) 许可代码，以及来自 [`astring`](https://github.com/davidbonnet/astring) 的 [MIT](https://github.com/davidbonnet/astring/blob/main/LICENSE) 许可代码。

更多详情请参考 [THIRD_PARTY_LICENSES.txt](THIRD_PARTY_LICENSES.txt)。

git 仓库、源代码压缩包 (`yt-dlp.tar.gz`)、PyPI 源码分发包及 PyPI 构建分发包 (wheel) 仅包含受 [Unlicense](LICENSE) 许可的代码。

<!-- MANPAGE: END EXCLUDED SECTION -->

**注意**：man 帮助手册、shell 补全（自动补全）文件等都包含在 [源代码压缩包](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.tar.gz) 之中。


## 更新
如果你使用的是[发布版本的二进制文件](#%E5%8F%91%E5%B8%83%E6%96%87%E4%BB%B6)，可以使用 `yt-dlp -U` 命令来进行更新。

如果你是[通过 pip 安装的](https://github.com/yt-dlp/yt-dlp/wiki/Installation#with-pip)，只需重新运行安装程序时使用的相同命令即可。

对于其他第三方包管理器，请参阅 [wiki](https://github.com/yt-dlp/yt-dlp/wiki/Installation#third-party-package-managers) 或参考它们的文档。

<a id="update-channels"></a>

目前二进制文件有三个发布渠道 (release channels)：`stable`（稳定版）、`nightly`（每日构建版）和 `master`（主分支版）。

* `stable` 是默认渠道，通常以月度为周期发布。虽然名为 `stable`（因为很多修改已在 `nightly` 或 `master` 渠道的用户中测试过），但最新的 `stable` 版本通常比较“陈旧”，容易受到外部破坏（即网站更新导致 yt-dlp 失效）。
* `nightly` 渠道会在代码库发生变更的当晚午夜 (UTC) 之前发布。该渠道相当于项目开发快照，**推荐普通用户** 使用此渠道。`nightly` 版本可从 [yt-dlp/yt-dlp-nightly-builds](https://github.com/yt-dlp/yt-dlp-nightly-builds/releases) 获取，或者作为 `yt-dlp` PyPI 包的开发版本安装（使用 pip 的 `--pre` 参数）。
* `master` 渠道在每次向 master 分支推送代码后发布“金丝雀(canary)”版本。此渠道将始终提供最新的修复和功能，但也可能存在 bug 或退化问题。`master` 版本可从 [yt-dlp/yt-dlp-master-builds](https://github.com/yt-dlp/yt-dlp-master-builds/releases) 获取。

使用 `--update`/`-U` 时，发布版的二进制文件仅会在其当前渠道内更新。
当有新版本时，可以使用 `--update-to CHANNEL` 切换到其他渠道。`--update-to [CHANNEL@]TAG` 也可以用来升级或降级到某个渠道的特定标签版本。

你也可以使用 `--update-to <repository>` (`<owner>/<repository>`) 更新到一个完全不同仓库中的渠道。不过请谨慎操作，因为跨仓库更新的二进制文件不会进行任何验证。

用法示例：

* `yt-dlp --update-to master` 切换到 `master` 渠道并更新至其最新版本
* `yt-dlp --update-to stable@2023.07.06` 升级/降级到 `stable` 渠道的 `2023.07.06` 标签版本
* `yt-dlp --update-to 2023.10.07` 若当前渠道存在，则升级/降级至 `2023.10.07` 标签版本
* `yt-dlp --update-to example/yt-dlp@2023.09.24` 升级/降级至 `example/yt-dlp` 仓库的 `2023.09.24` 标签版本

**重要**：任何在使用 `stable` 发布版本时遇到问题的用户，在提交错误报告之前，都应该先安装或更新到 `nightly` 版本：
```
# 从 stable 可执行文件/二进制文件更新到 nightly 版本：
yt-dlp --update-to nightly

# 使用 pip 安装 nightly 版本：
python -m pip install -U --pre "yt-dlp[default]"
```

如果运行的 yt-dlp 版本距离现在超过 90 天，你会看到一条建议更新到最新版本的警告消息。
你可以在命令或配置文件中添加 `--no-update` 来屏蔽此警告。

## 依赖项
支持 Python 3.10+ (CPython) 和 3.11+ (PyPy)。其他版本和实现可能无法正常工作。

<!-- Python 3.5+ uses VC++14 and it is already embedded in the binary created
<!x-- https://www.microsoft.com/en-us/download/details.aspx?id=26999 --x>
在 Windows 上，还需要 [Microsoft Visual C++ 2010 SP1 Redistributable Package (x86)](https://download.microsoft.com/download/1/6/5/165255E7-1014-4D0A-B094-B6A430A6BFFC/vcredist_x86.exe) 才能运行 yt-dlp。通常系统已自带，但如果因缺少 `MSVCR100.dll` 报错，你需要手动安装它。
-->

虽然所有其他依赖项都是可选的，但极力推荐安装 `ffmpeg`、`ffprobe`、`yt-dlp-ejs` 和受支持的 JavaScript 运行时/引擎。

### 强烈推荐

* [**ffmpeg** 和 **ffprobe**](https://www.ffmpeg.org) - [合并单独音视频文件](#%E6%A0%BC%E5%BC%8F%E9%80%89%E6%8B%A9) 及执行各类[后期处理](#%E5%90%8E%E6%9C%9F%E5%A4%84%E7%90%86%E9%80%89%E9%A1%B9)任务所必需。许可证[取决于构建版本](https://www.ffmpeg.org/legal.html)

    由于 ffmpeg 是如此重要，我们在 [yt-dlp/FFmpeg-Builds](https://github.com/yt-dlp/FFmpeg-Builds) 提供我们自己的构建版。过去我们曾打补丁修复 yt-dlp 用户常见的问题，但目前的构建版本等同于上游的 ffmpeg。详情见 [说明文档](https://github.com/yt-dlp/FFmpeg-Builds#patches-applied)

    **重要**：你需要的是 ffmpeg *二进制文件*，**而不是** [同名的 Python 包](https://pypi.org/project/ffmpeg)

* [**yt-dlp-ejs**](https://github.com/yt-dlp/ejs) - 完整支持 YouTube 所必需。遵循 [Unlicense](https://github.com/yt-dlp/ejs/blob/main/LICENSE) 许可证，捆绑了 [MIT](https://github.com/davidbonnet/astring/blob/main/LICENSE) 和 [ISC](https://github.com/meriyah/meriyah/blob/main/LICENSE.md) 组件。

    运行 yt-dlp-ejs 还需要 JavaScript 运行时/引擎，如 [**deno**](https://deno.land) (推荐)、[**node.js**](https://nodejs.org)、[**bun**](https://bun.sh) 或 [**QuickJS**](https://bellard.org/quickjs/)。详见 [wiki](https://github.com/yt-dlp/yt-dlp/wiki/EJS)。

### 网络选项
* [**certifi**](https://github.com/certifi/python-certifi)\* - 提供 Mozilla 根证书包。遵循 [MPLv2](https://github.com/certifi/python-certifi/blob/master/LICENSE) 许可
* [**brotli**](https://github.com/google/brotli)\* 或 [**brotlicffi**](https://github.com/python-hyper/brotlicffi) - 支持 [Brotli](https://en.wikipedia.org/wiki/Brotli) 内容编码。两者均遵循 MIT 许可 <sup>[1](https://github.com/google/brotli/blob/master/LICENSE) [2](https://github.com/python-hyper/brotlicffi/blob/master/LICENSE) </sup>
* [**websockets**](https://github.com/aaugustin/websockets)\* - 用于 websocket 下载。遵循 [BSD-3-Clause](https://github.com/aaugustin/websockets/blob/main/LICENSE) 许可
* [**requests**](https://github.com/psf/requests)\* - HTTP 库。用于 HTTPS 代理和持久连接。遵循 [Apache-2.0](https://github.com/psf/requests/blob/main/LICENSE) 许可

#### 伪装 (Impersonation)

提供伪装浏览器请求支持。对某些采用 TLS 指纹识别的网站而言可能是必需的。

* [**curl_cffi**](https://github.com/lexiforest/curl_cffi) (推荐) - [curl-impersonate](https://github.com/lexiforest/curl-impersonate) 的 Python 绑定。提供对 Chrome、Edge 和 Safari 的伪装。遵循 [MIT](https://github.com/lexiforest/curl_cffi/blob/main/LICENSE) 许可
  * 可通过 `curl-cffi` 扩展安装，如 `pip install "yt-dlp[default,curl-cffi]"`
  * 目前已包含在多数构建版本中，*除了* `yt-dlp` (Unix zipimport 二进制文件) 和 `yt-dlp_x86` (Windows 32位)


### 元数据

* [**mutagen**](https://github.com/quodlibet/mutagen)\* - 用于在特定格式下使用 `--embed-thumbnail`。遵循 [GPLv2+](https://github.com/quodlibet/mutagen/blob/master/COPYING) 许可
* [**AtomicParsley**](https://github.com/wez/atomicparsley) - 当 `mutagen`/`ffmpeg` 无法工作时，用于在 `mp4`/`m4a` 中写入 `--embed-thumbnail`。遵循 [GPLv2+](https://github.com/wez/atomicparsley/blob/master/COPYING) 许可
* [**xattr**](https://github.com/xattr/xattr)、[**pyxattr**](https://github.com/iustin/pyxattr) 或 [**setfattr**](http://savannah.nongnu.org/projects/attr) - 用于在 **Mac** 和 **BSD** 上写入 xattr 元数据 (`--xattrs`)。分别遵循 [MIT](https://github.com/xattr/xattr/blob/master/LICENSE.txt)、[LGPL2.1](https://github.com/iustin/pyxattr/blob/master/COPYING) 和 [GPLv2+](http://git.savannah.nongnu.org/cgit/attr.git/tree/doc/COPYING) 许可

### 杂项

* [**pycryptodomex**](https://github.com/Legrandin/pycryptodome)\* - 用于解密 AES-128 HLS 流以及各类其他数据。遵循 [BSD-2-Clause](https://github.com/Legrandin/pycryptodome/blob/master/LICENSE.rst) 许可
* [**phantomjs**](https://github.com/ariya/phantomjs) - 在一些需要运行 JS 的提取器中使用。现已不再用于 YouTube，未来将被弃用。遵循 [BSD-3-Clause](https://github.com/ariya/phantomjs/blob/master/LICENSE.BSD) 许可
* [**secretstorage**](https://github.com/mitya57/secretstorage)\* - 使用 `--cookies-from-browser` 在 **Linux** 下解密 **Chromium** 系浏览器 cookie 时访问 **Gnome** 密钥环。遵循 [BSD-3-Clause](https://github.com/mitya57/secretstorage/blob/master/LICENSE) 许可
* 任何你希望配合 `--downloader` 使用的外部下载器

### 已弃用

* [**rtmpdump**](http://rtmpdump.mplayerhq.hu) - 用于下载 `rtmp` 流。可由 `--downloader ffmpeg` 替代。遵循 [GPLv2+](http://rtmpdump.mplayerhq.hu)
* [**mplayer**](http://mplayerhq.hu/design7/info.html) 或 [**mpv**](https://mpv.io) - 用于下载 `rstp`/`mms` 流。可由 `--downloader ffmpeg` 替代。遵循 [GPLv2+](https://github.com/mpv-player/mpv/blob/master/Copyright)

如需使用或重新分发上述依赖项，你必须同意它们各自的许可条款。

独立的发布二进制文件在构建时已包含 Python 解释器和标有 **\*** 的包。

如果你尝试执行某项任务但缺少必要依赖项时，yt-dlp 会发出警告。通过 `--verbose` 输出内容的顶部，可以查看所有当前可用的依赖项。


## 编译

### 独立的 PyInstaller 构建
要构建独立可执行文件，你必须安装 Python 和 `pyinstaller` (以及任何 yt-dlp 需要的 [可选依赖项](#%E4%BE%9D%E8%B5%96%E9%A1%B9))。生成的可执行文件其 CPU 架构将与所用 Python 相同。

你可以运行以下命令：

```
python devscripts/install_deps.py --include-group pyinstaller
python devscripts/make_lazy_extractors.py
python -m bundle.pyinstaller
```

在某些系统上，你可能需要使用 `py` 或 `python3` 代替 `python`。

`python -m bundle.pyinstaller` 接受传递给 `pyinstaller` 的任意参数，例如 `--onefile/-F` 或 `--onedir/-D`，相关[文档详见此处](https://pyinstaller.org/en/stable/usage.html#what-to-generate)。

**注意**：4.4 以下版本的 Pyinstaller [不支持](https://github.com/pyinstaller/pyinstaller#requirements-and-tested-platforms) 未使用虚拟环境、由 Windows 商店安装的 Python。

**重要**：直接运行 `pyinstaller` **而不是** 使用 `python -m bundle.pyinstaller` 是 **不** 受官方支持的。这可能导致无法正常工作。

### 跨平台二进制文件 (UNIX)
你需要编译工具 `python` (3.10+)、`zip`、`make` (GNU)、`pandoc`\* 和 `pytest`\*。

安装上述工具后，直接运行 `make` 即可。

或者你可以运行 `make yt-dlp` 仅编译二进制文件，而不更新任何附加文件。(这种情况下无需带有 **\*** 标记的构建工具)

### 相关脚本

* **`devscripts/install_deps.py`** - 为 yt-dlp 安装依赖。
* **`devscripts/update-version.py`** - 根据当前日期更新版本号。
* **`devscripts/set-variant.py`** - 设置可执行文件的构建变体 (variant)。
* **`devscripts/make_changelog.py`** - 使用简短的提交信息创建 markdown 格式的更新日志，并更新 `CONTRIBUTORS` 文件。
* **`devscripts/make_lazy_extractors.py`** - 创建懒加载提取器。在编译任何变体二进制文件前运行此命令可改善其启动性能。可设置环境变量 `YTDLP_NO_LAZY_EXTRACTORS` (赋以非空值) 来强制禁用懒加载。

注意：查看它们的 `--help` 获取更多信息。

### 派生项目 (Forking)
如果你在 GitHub 上复刻了该项目，你可以运行自己分叉的 [build 工作流](.github/workflows/build.yml) 自动将所选版本构建为工件 (artifacts)。或者你也可以运行 [release 工作流](.github/workflows/release.yml) 或启用 [nightly 工作流](.github/workflows/release-nightly.yml) 来创建完整的 (预) 发布版。
# 用法与选项

```
用法: yt-dlp [选项] URL [URL...]
```

## 通用选项:
    -h, --help                      打印此帮助文本并退出
    --version                       打印程序版本并退出
    -U, --update                    将此程序更新至最新版本
    --no-update                     不检查更新（默认）
    --update-to [CHANNEL]@[TAG]     升级/降级至特定渠道（及其特定标签）的
                                    版本（例如 "master@2023.09.01"）。
                                    如果未指定渠道，默认使用当前渠道。
                                    如果未指定标签，默认使用最新版本。
    -i, --ignore-errors             出现下载错误时继续处理，
                                    例如跳过播放列表中无法访问的视频（默认）
                                    （别名: --no-abort-on-error）
    --abort-on-error                当出现任何错误时终止下载
                                    （别名: --no-ignore-errors）
    --dump-user-agent               打印当前使用的自定义 User-Agent 并退出
    --list-extractors               列出所有支持的提取器并退出
    --extractor-descriptions        输出所有支持的提取器的描述信息并退出
    --use-extractors NAMES          要使用的提取器名称，用逗号分隔。
                                    你也可以使用正则表达式、"all"（全部）、"default"（默认）
                                    和 "end"（结束 URL 匹配）；例如：--ies
                                    "holodex.*,end,youtube"。在名称前加上
                                    "-" 表示排除它，例如 --ies
                                    default,-generic。使用 --list-extractors
                                    可获取提取器名称列表。（别名: --ies）
    --default-search PREFIX         为不合格的 URL 使用此前缀搜索。例如：
                                    "gvsearch2:python" 会在 Google Videos 中
                                    下载关于搜索词 "python" 的前两个视频。
                                    使用值 "auto" 让 yt-dlp 自动猜测
                                    （"auto_warning" 则在猜测时发出警告）。
                                    "error" 会直接抛出错误。默认值
                                    "fixup_error" 会修复损坏的 URL，但如果不
                                    可能修复，它会报错而不是去搜索
    --ignore-config                 除了由 --config-locations 给定的配置外，
                                    不加载任何其他的配置文件。
                                    为了向后兼容，如果此选项出现在系统配置文件中，
                                    则不会加载用户配置文件。
                                    （别名: --no-config）
    --no-config-locations           不加载任何自定义配置文件（默认）。
                                    当此选项出现在配置文件内部时，将忽略
                                    当前文件中定义的之前所有 --config-locations
    --config-locations PATH         主配置文件的位置；
                                    可以是配置文件的路径，或者它所在的
                                    目录（"-" 代表从 stdin 读取）。此选项可以
                                    被多次使用，也可以在其他配置文件内使用
    --plugin-dirs DIR               额外搜索插件的目录路径。
                                    可多次使用以添加多个目录。
                                    使用 "default" 搜索默认插件目录（默认行为）
    --no-plugin-dirs                清除要搜索的插件目录，
                                    包括默认目录和之前通过 --plugin-dirs
                                    提供的目录
    --js-runtimes RUNTIME[:PATH]    启用的额外 JavaScript 运行时环境，
                                    可选择提供该运行时的位置
                                    （可以是二进制文件的路径或其所在目录）。
                                    可多次使用以启用多个运行时环境。
                                    受支持的运行时环境按优先级从高到低排列为：
                                    deno, node, quickjs, bun。默认仅启用了 "deno"。
                                    将使用既已启用又可被访问的优先级最高的运行时。
                                    若要在 "deno" 可用时强制使用优先级较低的运行时，
                                    需在启用其他运行时之前传递 --no-js-runtimes
    --no-js-runtimes                清除要启用的 JavaScript 运行时环境，
                                    包括默认项及之前通过 --js-runtimes 提供的环境
    --remote-components COMPONENT   允许 yt-dlp 在需要时获取的远程组件。
                                    目前如果你使用的是官方可执行文件或已安装适当
                                    版本的 yt-dlp-ejs 包，通常不需要此选项。
                                    可多次使用以允许获取多个组件。
                                    受支持的值包括：ejs:npm（从 npm 获取外部 JS 组件），
                                    ejs:github（从 yt-dlp-ejs GitHub 获取外部 JS 组件）。
                                    默认情况下不允许任何远程组件
    --no-remote-components          不允许获取所有远程组件，
                                    包括之前通过 --remote-components 允许或默认的组件
    --flat-playlist                 不提取播放列表中的结果条目的 URL；
                                    某些条目的元数据可能会丢失，且可能会跳过下载
    --no-flat-playlist              完整提取播放列表中的视频（默认）
    --live-from-start               从头开始下载直播流。
                                    目前为实验性功能，仅支持 YouTube, Twitch, 和 TVer
    --no-live-from-start            从当前时间开始下载直播流（默认）
    --wait-for-video MIN[-MAX]      等待计划好的流变为可用。
                                    传入两次重试之间等待的最短秒数（或时间范围）
    --no-wait-for-video             不等待计划好的流（默认）
    --mark-watched                  标记视频为已观看（即使使用 --simulate 也会标记）
    --no-mark-watched               不标记视频为已观看（默认）
    --color [STREAM:]POLICY         是否在输出中使用颜色代码，可选择
                                    加上 STREAM 前缀 (stdout 或 stderr) 来指定应用的目标。
                                    可取值： "always", "auto" (默认), "never",
                                    或 "no_color" (使用无颜色终端序列)。
                                    使用 "auto-tty" 或 "no_color-tty" 仅根据终端
                                    支持情况决定。此选项可以被多次使用
    --compat-options OPTS           兼容选项，帮助维持与 youtube-dl 或
                                    youtube-dlc 配置的兼容性，它会恢复 yt-dlp 
                                    所做的一些变更。详情请见“默认行为的区别”
    --alias ALIASES OPTIONS         为某段选项字符串创建别名。除非别名
                                    以连字符 "-" 开头，否则会自动添加 "--" 前缀。
                                    参数的解析遵循 Python 字符串格式化规范。
                                    例如 --alias get-audio,-X "-S aext:{0},abr -x --audio-format {0}"
                                    创建了两个选项 "--get-audio" 和 "-X"，它们接收一个
                                    参数 (ARG0) 并展开为 "-S aext:ARG0,abr -x --audio-format ARG0"。
                                    所有定义的别名都会在 --help 输出中列出。
                                    别名选项可以触发更多别名；因此请注意避免
                                    定义循环嵌套选项。作为一种安全措施，每个
                                    别名最多可被触发 100 次。此选项可以被多次使用
    -t, --preset-alias PRESET       应用一组预定义的选项。例如：
                                    --preset-alias mp3。以下预设可用：
                                    mp3, aac, mp4, mkv, sleep。更多信息请参见
                                    文档末尾的“预设别名”部分。此选项可以多次使用

## 网络选项:
    --proxy URL                     使用指定的 HTTP/HTTPS/SOCKS 代理。要启用
                                    SOCKS 代理，请指定合适的协议头，例如
                                    socks5://user:pass@127.0.0.1:1080/。
                                    传入空字符串 (--proxy "") 来使用直连
    --socket-timeout SECONDS        放弃前等待的时间（以秒为单位）
    --source-address IP             要绑定的客户端 IP 地址
    --impersonate CLIENT[:OS]       模拟进行请求的客户端。例如：
                                    chrome, chrome-110, chrome:windows-10。传递
                                    --impersonate="" 可模拟任何客户端。
                                    请注意，强行为所有请求模拟客户端
                                    可能会对下载速度和稳定性产生不利影响
    --list-impersonate-targets      列出可供模拟的客户端
    -4, --force-ipv4                强制所有连接通过 IPv4
    -6, --force-ipv6                强制所有连接通过 IPv6
    --enable-file-urls              启用 file:// URLs。出于安全考虑默认禁用。

## 地理限制:
    --geo-verification-proxy URL    使用此代理来验证受地理限制网站的
                                    IP 地址。由 --proxy 指定的默认代理
                                    （如果未指定，则无）用于实际下载
    --xff VALUE                     如何伪造 X-Forwarded-For HTTP 头部
                                    以尝试绕过地理限制。可以设置为 "default"
                                    （仅当已知有效时伪造），"never"，CIDR 形式的
                                    IP 块，或两个字母的 ISO 3166-2 国家代码

## 视频选择:
    -I, --playlist-items ITEM_SPEC  要下载的条目的逗号分隔播放列表索引 (playlist_index)。
                                    你可以使用 "[START]:[STOP][:STEP]" 来指定范围。
                                    为后向兼容，也支持 START-STOP。
                                    使用负索引可以从右向左计数，负 STEP 
                                    可以反向下载。例如在包含 15 个项目的
                                    播放列表上使用 "-I 1:3,7,-5::2" 
                                    将下载索引为 1,2,3,7,11,13,15 的条目
    --min-filesize SIZE             如果文件小于 SIZE (如 50k 或 44.6M)，则终止下载
    --max-filesize SIZE             如果文件大于 SIZE (如 50k 或 44.6M)，则终止下载
    --date DATE                     仅下载在此时上传的视频。
                                    日期格式可以是 "YYYYMMDD" 或是
                                    [now|today|yesterday][-N[day|week|month|year]]。
                                    例如 "--date today-2weeks" 仅下载
                                    两周前的同一天上传的视频
    --datebefore DATE               仅下载在此时或更早上传的视频。
                                    日期格式与 --date 相同
    --dateafter DATE                仅下载在此时或更晚上传的视频。
                                    日期格式与 --date 相同
    --match-filters FILTER          通用视频过滤器。任何 "输出模板" 的
                                    字段都可以通过 "过滤格式" 规定的运算符
                                    与数字或字符串进行比较。你也可以简单地指定
                                    要匹配的字段是否存在，使用 "!field" 检查该
                                    字段是否不存在，并使用 "&" 来检查多个条件。
                                    如果需要，可使用 "\" 来转义 "&" 或引号。
                                    如果多次使用，只要至少满足一个条件，该过滤
                                    规则即匹配。例如： --match-filters !is_live
                                    --match-filters "like_count>?100 & description~='(?i)\bcats \& dogs\b'"
                                    将仅匹配非直播的视频，或者点赞数超过 100（或
                                    没有点赞数字段）且描述中包含短语 "cats & dogs"
                                    (不区分大小写) 的视频。使用 "--match-filters -" 
                                    可交互式询问是否下载每个视频
    --no-match-filters              不使用任何 --match-filters（默认）
    --break-match-filters FILTER    与 "--match-filters" 相同，但在有视频被拒绝时停止下载过程
    --no-break-match-filters        不使用任何 --break-match-filters（默认）
    --no-playlist                   如果 URL 既指向视频又指向播放列表，仅下载该视频
    --yes-playlist                  如果 URL 既指向视频又指向播放列表，下载该播放列表
    --age-limit YEARS               仅下载适合指定年龄的视频
    --download-archive FILE         仅下载未在此存档文件中列出的视频。
                                    将所有已下载视频的 ID 记录到其中
    --no-download-archive           不使用存档文件（默认）
    --max-downloads NUMBER          在下载 NUMBER 个文件后停止
    --break-on-existing             当遇到已存在于 --download-archive 提供的
                                    存档中的文件时，停止下载过程
    --no-break-on-existing          当遇到已存在于存档中的文件时，
                                    不要停止下载过程（默认）
    --break-per-input               更改 --max-downloads, --break-on-existing,
                                    --break-match-filters 和 autonumber 的行为，
                                    使它们按每个输入 URL 单独重置状态
    --no-break-per-input            --break-on-existing 和类似的选项
                                    将终止整个下载队列
    --skip-playlist-after-errors N  允许失败的次数，超过次数后将跳过剩余播放列表

## 下载选项:
    -N, --concurrent-fragments N    可同时下载的 dash/hlsnative
                                    视频片段数量 (默认值为 1)
    -r, --limit-rate RATE           最大下载速率，单位：字节每秒 (如 50K 或 4.2M)
    --throttled-rate RATE           最小下载速率，单位：字节每秒，低于此速率
                                    则认为受到限速，并将重新提取视频数据 (如 100K)
    -R, --retries RETRIES           重试次数 (默认值为 10)，或 "infinite" (无限)
    --file-access-retries RETRIES   遇到文件访问错误时的重试次数
                                    (默认值为 3)，或 "infinite" (无限)
    --fragment-retries RETRIES      某一个片段的重试次数 (默认值为 10)，
                                    或 "infinite" (无限) (仅适用于 DASH、hlsnative 和 ISM)
    --retry-sleep [TYPE:]EXPR       重试之间的休眠时间 (以秒为单位)
                                    (可选) 可加上重试类型前缀 (http (默认),
                                    fragment, file_access, extractor) 来指定休眠对象。
                                    EXPR 可以是数字，或 linear=START[:END[:STEP=1]]，或
                                    exp=START[:END[:BASE=2]]。此选项可以
                                    多次使用为不同的重试类型设置休眠时间，
                                    例如 --retry-sleep linear=1::2 --retry-sleep fragment:exp=1:20
    --skip-unavailable-fragments    在下载 DASH、hlsnative 和 ISM 时跳过不可用的
                                    片段（默认）(别名: --no-abort-on-unavailable-fragments)
    --abort-on-unavailable-fragments
                                    当片段不可用时中止下载
                                    (别名: --no-skip-unavailable-fragments)
    --keep-fragments                下载完成后在硬盘上保留已下载的片段
    --no-keep-fragments             下载完成后删除已下载的片段（默认）
    --buffer-size SIZE              下载缓冲区大小，如 1024 或 16K（默认值为 1024）
    --resize-buffer                 缓冲区大小将自动调整，
                                    以 --buffer-size 为初始值（默认）
    --no-resize-buffer              不自动调整缓冲区大小
    --http-chunk-size SIZE          分块 HTTP 下载的分块大小，如 10485760 
                                    或 10M（默认禁用）。这在绕过网络服务器
                                    施加的带宽限制时可能有用（实验性）
    --playlist-random               以随机顺序下载播放列表中的视频
    --lazy-playlist                 在接收到播放列表条目时立刻处理它们。
                                    这将禁用 n_entries, --playlist-random 
                                    和 --playlist-reverse
    --no-lazy-playlist              只有在解析完整个播放列表后才处理视频（默认）
    --hls-use-mpegts                为 HLS 视频使用 mpegts 容器；这允许某些
                                    播放器在下载时播放视频，并降低下载中断时
                                    文件损坏的可能性。对于直播流此选项默认启用
    --no-hls-use-mpegts             不为 HLS 视频使用 mpegts 容器。
                                    非直播流下载时的默认行为
    --download-sections REGEX       仅下载匹配指定正则表达式的章节。
                                    带有 "*" 前缀表示时间范围而非章节。
                                    负时间戳从末尾开始计算。"*from-url"
                                    可用于下载从 URL 提取的 "start_time" 和
                                    "end_time" 之间的内容。需要 ffmpeg。
                                    此选项可多次使用以跨章节下载，
                                    例如：--download-sections "*10:15-inf"
                                    --download-sections "intro"
    --downloader [PROTO:]NAME       要使用的外部下载器的名称或路径。
                                    （可选）可以加上协议前缀（http, ftp, m3u8, 
                                    dash, rstp, rtmp, mms）来指定适用于哪种协议。
                                    目前支持 native, aria2c, axel, curl, ffmpeg, 
                                    httpie, wget。你可以多次使用此选项
                                    为不同的协议设置不同的下载器。例如：
                                    --downloader aria2c --downloader "dash,m3u8:native"
                                    将对 http/ftp 下载使用 aria2c，并对 
                                    dash/m3u8 使用内置 (native) 下载器
                                    (别名: --external-downloader)
    --downloader-args NAME:ARGS     将这些参数传递给外部下载器。指定下载器名称
                                    和用冒号 ":" 分隔的参数。对于 ffmpeg，
                                    可以使用与 --postprocessor-args 相同的语法
                                    将参数传递到不同的位置。你可以多次使用此选项
                                    将不同的参数传递给不同的下载器 
                                    (别名: --external-downloader-args)

## 文件系统选项:
    -a, --batch-file FILE           包含要下载的 URL 的文件（"-" 表示
                                    stdin），每行一个 URL。以 "#", ";" 或 "]" 
                                    开头的行被视为注释并被忽略
    --no-batch-file                 不从批处理文件中读取 URL（默认）
    -P, --paths [TYPES:]PATH        文件下载的存放路径。指定文件类型和
                                    路径，用冒号 ":" 分隔。支持与 --output
                                    中所有的 TYPES 相同的类型。
                                    此外，你还可以提供 "home"（默认）和 "temp" 
                                    (临时) 路径。所有中间文件首先下载到 temp 路径，
                                    下载完成后，最终文件被移动到 home 路径。
                                    如果 --output 是绝对路径，则忽略此选项
    -o, --output [TYPES:]TEMPLATE   输出文件名的模板；详细信息见“输出模板”
    --output-na-placeholder TEXT    用于替换 --output 中不可用字段的占位符（默认："NA"）
    --restrict-filenames            将文件名限制为仅包含 ASCII 字符，
                                    并避免在文件名中使用 "&" 和空格
    --no-restrict-filenames         允许在文件名中使用 Unicode 字符、"&" 和空格（默认）
    --windows-filenames             强制文件名与 Windows 兼容
    --no-windows-filenames          只进行最少的文件名净化
    --trim-filenames LENGTH         限制文件名的长度（不包含扩展名）
                                    为指定的字符数
    -w, --no-overwrites             不覆盖任何文件
    --force-overwrites              覆盖所有视频和元数据文件。
                                    此选项隐含 --no-continue
    --no-force-overwrites           不覆盖视频，但覆盖相关的元数据文件（默认）
    -c, --continue                  恢复部分下载的文件/片段（默认）
    --no-continue                   不恢复部分下载的片段。如果文件未被分片，
                                    则重新开始下载整个文件
    --part                          使用 .part 文件而不是直接写入
                                    输出文件（默认）
    --no-part                       不使用 .part 文件 - 直接写入输出文件
    --mtime                         使用 Last-modified 响应头来设置文件的
                                    修改时间
    --no-mtime                      不使用 Last-modified 响应头来设置
                                    文件的修改时间（默认）
    --write-description             将视频描述写入 .description 文件
    --no-write-description          不写入视频描述（默认）
    --write-info-json               将视频元数据写入 .info.json 文件
                                    （可能包含个人信息）
    --no-write-info-json            不写入视频元数据（默认）
    --write-playlist-metafiles      当使用 --write-info-json、--write-description 等时，
                                    除视频元数据外，同时写入播放列表元数据（默认）
    --no-write-playlist-metafiles   当使用 --write-info-json、--write-description 等时，
                                    不写入播放列表元数据
    --clean-info-json               从 infojson 中移除一些内部元数据，
                                    例如文件名（默认）
    --no-clean-info-json            将所有字段写入 infojson
    --write-comments                提取视频评论并放置在 infojson 中。
                                    如果已知提取速度很快，即使没有此选项也会抓取评论
                                    (别名: --get-comments)
    --no-write-comments             除非已知提取速度快，否则不提取视频评论
                                    (别名: --no-get-comments)
    --load-info-json FILE           包含视频信息的 JSON 文件
                                    （使用 "--write-info-json" 选项创建的）
    --cookies FILE                  从中读取 cookie 并写入 cookie jar 的
                                    Netscape 格式的文件
    --no-cookies                    不从/向文件读取/写入 cookie（默认）
    --cookies-from-browser BROWSER[+KEYRING][:PROFILE][::CONTAINER]
                                    从中加载 cookie 的浏览器名称。目前
                                    支持的浏览器有：brave, chrome, chromium, edge, 
                                    firefox, opera, safari, vivaldi, whale。你可以选择
                                    使用各自的分隔符提供用于在 Linux 上解密 Chromium cookie 的 KEYRING、
                                    加载 cookie 的 PROFILE 名称/路径、以及
                                    CONTAINER 名称 (如果是 Firefox) ("none" 表示无容器)。
                                    默认情况下，使用最近访问的 profile 下的
                                    所有容器。目前支持的密钥环有：
                                    basictext, gnomekeyring, kwallet, kwallet5, kwallet6
    --no-cookies-from-browser       不从浏览器加载 cookie（默认）
    --cache-dir DIR                 文件系统中 yt-dlp 可以永久存储一些下载
                                    信息（如客户端 id 和签名）的位置。
                                    默认值为 ${XDG_CACHE_HOME}/yt-dlp
    --no-cache-dir                  禁用文件系统缓存
    --rm-cache-dir                  删除所有文件系统缓存文件

## 缩略图选项:
    --write-thumbnail               将缩略图图像写入磁盘
    --no-write-thumbnail            不将缩略图图像写入磁盘（默认）
    --write-all-thumbnails          将所有缩略图图像格式写入磁盘
    --list-thumbnails               列出每个视频的可用缩略图。
                                    模拟执行，除非使用了 --no-simulate

## 快捷方式选项:
    --write-link                    根据当前平台写入 Internet 快捷方式文件
                                    (.url, .webloc 或 .desktop)。URL 可能被操作系统缓存
    --write-url-link                写入 .url 的 Windows 快捷方式。
                                    操作系统根据文件路径缓存 URL
    --write-webloc-link             写入 .webloc 的 macOS 快捷方式
    --write-desktop-link            写入 .desktop 的 Linux 快捷方式

## 详细输出与模拟选项:
    -q, --quiet                     激活安静模式。如果与 --verbose 一起使用，
                                    则将日志打印到 stderr
    --no-quiet                      停用安静模式。(默认)
    --no-warnings                   忽略警告信息
    -s, --simulate                  不下载视频，也不向磁盘写入任何内容
    --no-simulate                   即使使用了打印/列出选项，也下载视频
    --ignore-no-formats-error       忽略“没有视频格式 (No video formats)”错误。
                                    即使视频实际上无法下载，对于提取元数据也非常有用
                                    （实验性）
    --no-ignore-no-formats-error    找不到可下载的视频格式时报错（默认）
    --skip-download                 不下载视频但写入所有相关文件
                                    (别名: --no-download)
    -O, --print [WHEN:]TEMPLATE     要打印到屏幕上的字段名或输出模板，
                                    可以加上打印时间前缀 WHEN 并用 ":" 分隔。
                                    WHEN 支持的值与 --use-postprocessor 的相同
                                    （默认: video）。隐含 --quiet。
                                    隐含 --simulate，除非使用了 --no-simulate 
                                    或使用了 WHEN 的较后阶段。此选项可多次使用
    --print-to-file [WHEN:]TEMPLATE FILE
                                    将给定的模板追加到文件中。WHEN 和 
                                    TEMPLATE 的值与 --print 的相同。
                                    FILE 使用与输出模板相同的语法。此选项可多次使用
    -j, --dump-json                 安静模式，但打印每个视频的 JSON 信息。
                                    模拟执行，除非使用了 --no-simulate。
                                    可用键说明见“输出模板”
    -J, --dump-single-json          安静模式，但为每个传入的 URL 或 infojson
                                    打印 JSON 信息。模拟执行，除非使用了 --no-simulate。
                                    如果 URL 指向一个播放列表，将在一行内
                                    打印整个播放列表信息
    --force-write-archive           只要未发生错误就强制写入下载存档条目，
                                    即使使用了 -s 或其他模拟选项 
                                    (别名: --force-download-archive)
    --newline                       将进度条输出换行
    --no-progress                   不打印进度条
    --progress                      即使在安静模式下也显示进度条
    --console-title                 在控制台标题栏中显示进度
    --progress-template [TYPES:]TEMPLATE
                                    进度输出模板，可选前缀之一："download:" (默认),
                                    "download-title:" (控制台标题),
                                    "postprocess:", 或 "postprocess-title:"。
                                    视频字段可以通过 "info" 键访问，
                                    进度属性可以通过 "progress" 键访问。
                                    例如 --console-title --progress-template 
                                    "download-title:%(info.id)s-%(progress.eta)s"
    --progress-delta SECONDS        进度输出之间的时间间隔（默认：0）
    -v, --verbose                   打印各种调试信息
    --dump-pages                    打印使用 base64 编码的下载页面以调试问题
                                    （极度详细）
    --write-pages                   将下载的中间页面写入当前目录的文件中
                                    以调试问题
    --print-traffic                 显示发送和读取的 HTTP 流量

## 权变措施 (Workarounds):
    --encoding ENCODING             强制使用指定编码（实验性）
    --legacy-server-connect         明确允许 HTTPS 连接到不支持 RFC 5746 
                                    安全重协商的服务器
    --no-check-certificates         禁止 HTTPS 证书验证
    --prefer-insecure               使用未加密的连接来检索有关视频的信息
    --add-headers FIELD:VALUE       指定自定义 HTTP 头及其值，用冒号 ":" 分隔。
                                    你可以多次使用此选项
    --bidi-workaround               修复缺乏双向文本支持的终端问题。
                                    需要 PATH 中有 bidiv 或 fribidi 可执行文件
    --sleep-requests SECONDS        数据提取期间每次请求之间休眠的秒数
    --sleep-interval SECONDS        每次下载前休眠的秒数。与 --max-sleep-interval
                                    一起使用时，这是最小休眠时间
                                    (别名: --min-sleep-interval)
    --max-sleep-interval SECONDS    最大休眠秒数。只能与 --min-sleep-interval 一起使用
    --sleep-subtitles SECONDS       每次字幕下载前休眠的秒数

## 视频格式选项:
    -f, --format FORMAT             视频格式代码，详细信息见“格式选择”
    -S, --format-sort SORTORDER     按给定字段对格式进行排序，
                                    详细信息见“排序格式”
    --format-sort-reset             忽略之前用户指定的排序顺序并重置为默认值
    --format-sort-force             强制用户指定的排序顺序优先于所有字段，
                                    详细信息见“排序格式”(别名: --S-force)
    --no-format-sort-force          某些字段优先于用户指定的排序顺序（默认）
    --video-multistreams            允许多个视频流合并为一个文件
    --no-video-multistreams         每个输出文件仅下载一个视频流（默认）
    --audio-multistreams            允许多个音频流合并为一个文件
    --no-audio-multistreams         每个输出文件仅下载一个音频流（默认）
    --prefer-free-formats           在相同质量下优先选择具有免费容器的视频格式
                                    而非非免费容器。与 "-S ext" 一起使用可严格
                                    优先免费容器，而不考虑质量
    --no-prefer-free-formats        不给予免费容器任何特殊偏好（默认）
    --check-formats                 确保仅从实际可下载的格式中进行选择
    --check-all-formats             检查所有格式是否实际可下载
    --no-check-formats              不检查格式是否实际可下载
    -F, --list-formats              列出每个视频的可用格式。
                                    模拟执行，除非使用了 --no-simulate
    --merge-output-format FORMAT    合并格式时可能使用的容器，用 "/" 分隔，
                                    例如 "mp4/mkv"。如果不需要合并则被忽略。
                                    （当前支持：avi, flv, mkv, mov, mp4, webm）

## 字幕选项:
    --write-subs                    写入字幕文件
    --no-write-subs                 不写入字幕文件（默认）
    --write-auto-subs               写入自动生成的字幕文件
                                    (别名: --write-automatic-subs)
    --no-write-auto-subs            不写入自动生成的字幕（默认）
                                    (别名: --no-write-automatic-subs)
    --list-subs                     列出每个视频的可用字幕。
                                    模拟执行，除非使用了 --no-simulate
    --sub-format FORMAT             字幕格式；接受格式偏好设置
                                    用 "/" 分隔，例如 "srt" 或 "ass/srt/best"
    --sub-langs LANGS               要下载的字幕语言（可以是正则表达式）或 "all"，用
                                    逗号分隔，例如 --sub-langs "en.*,ja" (其中 "en.*" 
                                    是匹配 "en" 后跟零或多个任意字符的正则表达式)。
                                    你可以在语言代码前加上 "-" 来将其从请求的
                                    语言中排除，例如 --sub-langs all,-live_chat。
                                    使用 --list-subs 获取可用的语言标签列表

## 认证选项:
    -u, --username USERNAME         使用此账户 ID 登录
    -p, --password PASSWORD         账户密码。如果未提供此选项，yt-dlp 
                                    会交互式地询问
    -2, --twofactor TWOFACTOR       双因素认证代码
    -n, --netrc                     使用 .netrc 认证数据
    --netrc-location PATH           .netrc 认证数据的位置；
                                    可以是路径或包含它的目录。默认为 ~/.netrc
    --netrc-cmd NETRC_CMD           要执行以获取提取器凭据的命令。
    --video-password PASSWORD       视频的特定密码
    --ap-mso MSO                    Adobe Pass 多系统操作商（电视提供商）标识符，
                                    使用 --ap-list-mso 获取可用 MSO 的列表
    --ap-username USERNAME          多系统操作商的账号登录名
    --ap-password PASSWORD          多系统操作商的账号密码。如果未提供此选项，
                                    yt-dlp 将会交互式地询问
    --ap-list-mso                   列出所有支持的多系统操作商
    --client-certificate CERTFILE   PEM 格式客户端证书文件的路径。可能包含私钥
    --client-certificate-key KEYFILE
                                    客户端证书私钥文件的路径
    --client-certificate-password PASSWORD
                                    客户端证书私钥的密码（如果已加密）。
                                    如果未提供且私钥已加密，yt-dlp 将交互式地询问

## 后期处理选项:
    -x, --extract-audio             将视频文件转换为纯音频文件
                                    （需要 ffmpeg 和 ffprobe）
    --audio-format FORMAT           使用 -x 时将音频转换为的格式。
                                    （当前支持：best (默认), aac, alac, flac, 
                                    m4a, mp3, opus, vorbis, wav）。你可以
                                    使用类似于 --remux-video 的语法指定多个规则
    --audio-quality QUALITY         指定使用 -x 转换音频时 ffmpeg 使用的音频质量。
                                    对于 VBR，插入介于 0 (最好) 到 10 (最差) 
                                    之间的值，或指定的比特率（如 128K） (默认值: 5)
    --remux-video FORMAT            如果需要，将视频重新封装 (remux) 为另一种容器
                                    （当前支持：avi, flv, gif, mkv, mov, mp4, webm, 
                                    aac, aiff, alac, flac, m4a, mka, mp3, ogg, opus, 
                                    vorbis, wav）。如果目标容器不支持原视频/音频编解码器，
                                    重新封装将失败。你可以指定多条规则；例如
                                    "aac>m4a/mov>mp4/mkv" 会将 aac 转为 m4a，mov
                                    转为 mp4，其他的全部转为 mkv
    --recode-video FORMAT           如果需要，将视频重新编码为另一种格式。
                                    语法和支持的格式与 --remux-video 相同
    --postprocessor-args NAME:ARGS  将这些参数传递给后期处理器 (postprocessor)。
                                    指定后期处理器/可执行文件名称以及通过冒号 ":"
                                    分隔的参数，将参数传递给特定的后期处理器/可执行文件。
                                    支持的 PP 有：Merger, ModifyChapters, SplitChapters,
                                    ExtractAudio, VideoRemuxer, VideoConvertor,
                                    Metadata, EmbedSubtitle, EmbedThumbnail,
                                    SubtitlesConvertor, ThumbnailsConvertor,
                                    FixupStretched, FixupM4a, FixupM3u8,
                                    FixupTimestamp 和 FixupDuration。
                                    受支持的可执行文件有：AtomicParsley, FFmpeg 
                                    和 FFprobe。你也可以指定 "PP+EXE:ARGS" 以仅在
                                    指定的后期处理器使用指定的执行文件时，才将
                                    参数传递给它。此外，对于 ffmpeg/ffprobe，
                                    可以在前缀后追加 "_i"/"_o"，可选地跟上一个数字，
                                    以在指定的输入/输出文件之前传递参数。
                                    例如 --ppa "Merger+ffmpeg_i1:-v quiet"。
                                    你可以多次使用此选项为不同的后期处理器
                                    传递不同的参数。(别名: --ppa)
    -k, --keep-video                在后期处理完成后在磁盘上保留中间视频文件
    --no-keep-video                 在后期处理完成后删除中间视频文件（默认）
    --post-overwrites               覆盖经过后期处理的文件（默认）
    --no-post-overwrites            不覆盖经过后期处理的文件
    --embed-subs                    在视频中嵌入字幕（仅适用于 mp4, webm 和 mkv 视频）
    --no-embed-subs                 不嵌入字幕（默认）
    --embed-thumbnail               在视频中嵌入缩略图作为封面（艺术图）
    --no-embed-thumbnail            不嵌入缩略图（默认）
    --embed-metadata                将元数据嵌入到视频文件中。如果不使用
                                    --no-embed-chapters/--no-embed-info-json，
                                    也会一并嵌入存在的章节/infojson 
                                    (别名: --add-metadata)
    --no-embed-metadata             不将元数据添加到文件中（默认）
                                    (别名: --no-add-metadata)
    --embed-chapters                将章节标记添加到视频文件中
                                    (别名: --add-chapters)
    --no-embed-chapters             不添加章节标记（默认）(别名: --no-add-chapters)
    --embed-info-json               将 infojson 作为附件嵌入到 mkv/mka 视频文件中
    --no-embed-info-json            不将 infojson 作为附件嵌入到视频文件中
    --parse-metadata [WHEN:]FROM:TO
                                    从其他字段中解析诸如 标题/艺术家 等额外元数据；
                                    有关详细信息请参阅“修改元数据”。"WHEN" 的
                                    支持值与 --use-postprocessor 相同
                                    （默认: pre_process）
    --replace-in-metadata [WHEN:]FIELDS REGEX REPLACE
                                    使用给定正则表达式替换元数据字段中的文本。
                                    此选项可多次使用。"WHEN" 的支持值与
                                    --use-postprocessor 相同（默认: pre_process）
    --xattrs                        将元数据写入视频文件的 xattrs 扩展属性中
                                    （使用 Dublin Core 和 XDG 标准）
    --concat-playlist POLICY        连接播放列表中的视频。选项有 "never", 
                                    "always", 或 "multi_video"（默认值；仅当所有
                                    视频组成一个单集节目时才连接）。所有视频文件
                                    必须具有相同的编解码器和流数量才可被连接。
                                    可以将 "pl_video:" 前缀与 "--paths" 和 "--output" 
                                    配合使用，为合并后的文件设置输出文件名。
                                    详情见“输出模板”
    --fixup POLICY                  自动修复文件的已知缺陷。可选值：
                                    never (什么都不做), warn (仅发出警告), 
                                    detect_or_warn (默认值；尽可能修复，否则警告), 
                                    force (即使文件已存在也尝试修复)
    --ffmpeg-location PATH          ffmpeg 二进制文件的位置；
                                    可以是二进制文件的路径，也可以是其所在目录
    --exec [WHEN:]CMD               执行一个命令，可选择以 "WHEN:" 作为前缀指定执行时机。
                                    "WHEN" 支持的值与 --use-postprocessor 相同
                                    (默认: after_move)。可以使用与输出模板相同的语法
                                    将任何字段作为参数传递给命令；但出于安全原因，
                                    允许的格式化转换仅有："i"/"d" (带符号的十进制整数)，
                                    "f" (十进制浮点数) 和 "q" (被 shell 引号包裹的)。
                                    如果未传递任何字段，命令末尾将自动附加
                                    %(filepath,_filename|)q。此选项可被多次使用
    --no-exec                       移除之前定义的任何 --exec
    --convert-subs FORMAT           将字幕转换为另一种格式（目前支持：
                                    ass, lrc, srt, vtt）。使用 "--convert-subs none"
                                    禁用转换（默认） (别名: --convert-subtitles)
    --convert-thumbnails FORMAT     将缩略图转换为另一种格式（目前支持：
                                    jpg, png, webp）。你可以使用类似 "--remux-video" 
                                    的语法来指定多条规则。使用 "--convert-thumbnails none"
                                    禁用转换（默认）
    --split-chapters                根据内部章节将视频拆分为多个文件。
                                    可以将 "chapter:" 前缀与 "--paths" 和 "--output" 
                                    配合使用，为分割出的文件设置输出文件名。
                                    详情见“输出模板”
    --no-split-chapters             不根据章节拆分视频（默认）
    --remove-chapters REGEX         移除标题匹配给定正则表达式的章节。
                                    语法与 --download-sections 相同。
                                    此选项可被多次使用
    --no-remove-chapters            不从文件中移除任何章节（默认）
    --force-keyframes-at-cuts       下载/拆分/移除部分章节时强制在切割处生成关键帧。
                                    这需要重新编码因而速度较慢，
                                    但输出视频在切割处周围可能会有较少的伪影
    --no-force-keyframes-at-cuts    在切割/拆分时不强制在章节周围生成关键帧（默认）
    --use-postprocessor NAME[:ARGS]
                                    要启用的插件后期处理器的 (区分大小写) 名称，
                                    并（可选）传递给它的参数，用冒号 ":" 分隔。
                                    ARGS 是一个由分号 ";" 分隔的 NAME=VALUE 列表。
                                    "when" 参数决定了调用该后期处理器的时机。
                                    可以是： "pre_process" (提取视频后), 
                                    "after_filter" (视频通过过滤后), "video" (执行 --format 后；
                                    但在 --print/--output 之前), "before_dl" (每个视频下载前), 
                                    "post_process" (每个视频下载后；默认), "after_move" 
                                    (视频文件移动到最终位置后), "after_video" (下载并
                                    处理某视频的所有格式后), 或 "playlist" (在播放列表末尾)。
                                    此选项可被多次使用以添加不同的后期处理器

## SponsorBlock 选项:
使用 [SponsorBlock API](https://sponsor.ajay.app) 为下载的 YouTube 视频
创建章节，或者从中移除各类分段（赞助、开头等）

    --sponsorblock-mark CATS        创建对应章节的 SponsorBlock 类别，用逗号分隔。
                                    可用的类别有 sponsor, intro, outro, selfpromo, preview, 
                                    filler, interaction, music_offtopic, hook, poi_highlight, 
                                    chapter, all 和 default (=all)。
                                    可以在类别前加 "-" 排除该类别。
                                    各类别的详细描述请参阅 [1]。例如：
                                    --sponsorblock-mark all,-preview
                                    [1] https://wiki.sponsor.ajay.app/w/Segment_Categories
    --sponsorblock-remove CATS      要从视频文件中移除的 SponsorBlock 类别，用逗号分隔。
                                    如果一个类别同时出现在 mark 和 remove 中，
                                    则优先执行 remove。语法和可用的类别
                                    与 --sponsorblock-mark 相同，除了
                                    "default" 指代的是 "all,-filler"，且
                                    poi_highlight, chapter 不可用
    --sponsorblock-chapter-title TEMPLATE
                                    为通过 --sponsorblock-mark 创建的 SponsorBlock 
                                    章节的标题指定一个输出模板。
                                    可用的字段仅有 start_time, end_time, category, 
                                    categories, name, category_names。默认值为
                                    "[SponsorBlock]: %(category_names)l"
    --no-sponsorblock               同时禁用 --sponsorblock-mark 和 --sponsorblock-remove
    --sponsorblock-api URL          SponsorBlock API 的位置，默认值为
                                    https://sponsor.ajay.app

## 提取器选项:
    --extractor-retries RETRIES     已知提取器错误的重试次数（默认值为 3），
                                    或 "infinite" (无限重试)
    --allow-dynamic-mpd             处理动态 DASH 清单 (manifest)（默认）
                                    (别名: --no-ignore-dynamic-mpd)
    --ignore-dynamic-mpd            不处理动态 DASH 清单
                                    (别名: --no-allow-dynamic-mpd)
    --hls-split-discontinuity       在广告休息等不连续点将 HLS 播放列表拆分为不同的格式
    --no-hls-split-discontinuity    不在广告休息等不连续点拆分 HLS 播放列表（默认）
    --extractor-args IE_KEY:ARGS    将 ARGS 参数传递给键名为 IE_KEY 的提取器。
                                    详细信息请参阅“提取器参数”。你可以多次
                                    使用此选项为不同提取器提供参数

## 预设别名:
为了方便和易用而预定义的别名。请注意，yt-dlp 未来的版本
可能会添加或调整预设内容，但现有的预设名称不会被更改或移除

    -t mp3                          -f 'ba[acodec^=mp3]/ba/b' -x --audio-format mp3

    -t aac                          -f 'ba[acodec^=aac]/ba[acodec^=mp4a.40.]/ba/b' 
                                    -x --audio-format aac

    -t mp4                          --merge-output-format mp4 --remux-video mp4 
                                    -S vcodec:h264,lang,quality,res,fps,hdr:12,acodec:aac

    -t mkv                          --merge-output-format mkv --remux-video mkv

    -t sleep                        --sleep-subtitles 5 --sleep-requests 0.75 
                                    --sleep-interval 10 --max-sleep-interval 20

# 配置

你可以通过在配置文件中放置任何受支持的命令行选项来配置 yt-dlp。配置文件会从以下位置加载：

1. **主配置 (Main Configuration)**:
    * 由 `--config-locations` 指定的文件
1. **便携配置 (Portable Configuration)**: (推荐用于便携式安装)
    * 如果使用二进制文件，则为与二进制文件同目录下的 `yt-dlp.conf`
    * 如果从源码运行，则为 `yt_dlp` 上级目录中的 `yt-dlp.conf`
1. **主目录配置 (Home Configuration)**:
    * 由 `-P` 给定的 home 路径中的 `yt-dlp.conf`
    * 如果未给出 `-P`，则会在当前目录下寻找
1. **用户配置 (User Configuration)**:
    * `${XDG_CONFIG_HOME}/yt-dlp.conf`
    * `${XDG_CONFIG_HOME}/yt-dlp/config` (推荐用于 Linux/macOS)
    * `${XDG_CONFIG_HOME}/yt-dlp/config.txt`
    * `${APPDATA}/yt-dlp.conf`
    * `${APPDATA}/yt-dlp/config` (Windows 下推荐)
    * `${APPDATA}/yt-dlp/config.txt`
    * `~/yt-dlp.conf`
    * `~/yt-dlp.conf.txt`
    * `~/.yt-dlp/config`
    * `~/.yt-dlp/config.txt`

    另见: [关于环境变量的说明](#%E5%85%B3%E4%BA%8E%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E7%9A%84%E8%AF%B4%E6%98%8E)
1. **系统配置 (System Configuration)**:
    * `/etc/yt-dlp.conf`
    * `/etc/yt-dlp/config`
    * `/etc/yt-dlp/config.txt`

例如，使用以下配置文件，yt-dlp 每次都会提取音频、复制 mtime、使用指定的代理，并将所有视频保存在你主目录下的 `YouTube` 文件夹中：
```
# 以 # 开头的行是注释

# 总是提取音频
-x

# 复制文件的 mtime
--mtime

# 使用此代理
--proxy 127.0.0.1:3128

# 将所有视频保存在主目录下的 YouTube 文件夹中
-o ~/YouTube/%(title)s.%(ext)s
```

**注意**: 配置文件中的选项与普通命令行调用中使用的选项（也就是开关）完全相同；因此在 `-` 或 `--` 之后**不能有空格**，例如应该是 `-o` 或 `--proxy`，而不能是 `- o` 或 `-- proxy`。在必要时（就像在 UNIX shell 中那样），还需要为参数加上引号。

如果你希望在某次运行 yt-dlp 时禁用所有配置文件，可以使用 `--ignore-config`。如果在任何配置文件中找到了 `--ignore-config`，则不会继续加载后续的任何配置。例如，如果将其放在“便携配置文件”中，它就会阻止加载主目录、用户和系统配置文件。另外（为了向后兼容），如果系统配置文件中出现了 `--ignore-config`，则不会加载用户配置。

### 配置文件编码

配置文件在有 UTF BOM 时根据 BOM 解码，否则根据系统的区域 (locale) 编码进行解码。

如果你希望文件被不同地解码，在文件的开头添加 `# coding: ENCODING`（例如 `# coding: shift-jis`）。在此之前不能有任何字符，甚至不能有空格或 BOM。

### 使用 netrc 认证

你可能还希望自动为支持认证的提取器（通过 `--username` 和 `--password` 提供登录信息和密码）配置凭据存储，这样就不必在每次运行 yt-dlp 时作为命令行参数传入凭据，也可以避免在 shell 历史记录中追踪到明文密码。你可以针对各个提取器使用 [`.netrc` 文件](https://stackoverflow.com/tags/.netrc/info)来实现此目的。为此，你需要在 `--netrc-location` 目录下创建一个 `.netrc` 文件，并将其读写权限限制为仅自己可用：
```
touch ${HOME}/.netrc
chmod a-rwx,u+rw ${HOME}/.netrc
```
然后，你可以按以下格式为提取器添加凭据（其中 *extractor* 是提取器的小写名称）：
```
machine <extractor> login <username> password <password>
```
例如：
```
machine youtube login myaccount@gmail.com password my_youtube_password
machine twitch login my_twitch_account_name password my_twitch_password
```
要激活使用 `.netrc` 文件的认证，你应该将 `--netrc` 参数传递给 yt-dlp，或者将其放在[配置文件](#%E9%85%8D%E7%BD%AE)中。

.netrc 文件的默认位置是 `~` (见下文)。

使用 `.netrc` 文件的缺点是密码保存在纯文本文件中。作为替代方案，你可以配置自定义 shell 命令来为提取器提供凭据。这可以通过提供 `--netrc-cmd` 参数来完成，该命令必须以 netrc 格式输出凭据并在成功时返回 `0`，其他任何返回值都会被视为错误。命令中的 `{}` 将被替换为提取器的名称，这使得为特定的提取器选择对应凭据成为可能。

例如：要使用加密存放的 `.authinfo.gpg` 作为 `.netrc` 文件：
```
yt-dlp --netrc-cmd 'gpg --decrypt ~/.authinfo.gpg' 'https://www.youtube.com/watch?v=BaW_jenozKc'
```


### 关于环境变量的说明
* 在 UNIX 上，环境变量通常表示为 `${VARIABLE}`/`$VARIABLE`，在 Windows 上表示为 `%VARIABLE%`；但在本文档中始终显示为 `${VARIABLE}`
* 对于类似路径的选项（如 `--output`, `--config-locations`），yt-dlp 也允许在 Windows 上使用 UNIX 风格的变量
* 如果未设置，`${XDG_CONFIG_HOME}` 默认指向 `~/.config`，`${XDG_CACHE_HOME}` 默认指向 `~/.cache`
* 在 Windows 上，如果存在，`~` 指向 `${HOME}`；否则指向 `${USERPROFILE}` 或 `${HOMEDRIVE}${HOMEPATH}`
* 在 Windows 上，`${USERPROFILE}` 通常指向 `C:\Users\<user name>`，`${APPDATA}` 通常指向 `${USERPROFILE}\AppData\Roaming`

# 输出模板

`-o` 选项用于指定输出文件名的模板，而 `-P` 选项则用于指定各类文件的保存路径。

<!-- MANPAGE: BEGIN EXCLUDED SECTION -->
**简而言之:** [带我去看示例](#%E8%BE%93%E5%87%BA%E6%A8%A1%E6%9D%BF%E7%A4%BA%E4%BE%8B)。
<!-- MANPAGE: END EXCLUDED SECTION -->

当下载单个文件时，`-o` 最简单的用法是不设置任何模板参数，就像 `yt-dlp -o funny_video.flv "https://some/video"`（**不建议**这样硬编码文件扩展名，因为可能会破坏某些后期处理功能）。

不过，它也可以包含某些特殊序列（占位符），在下载每个视频时它们会被替换成相应的信息。特殊序列可按照 [Python 字符串格式化操作](https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting)进行格式化，例如 `%(NAME)s` 或 `%(NAME)05d`。说明一下，它由一个百分号开头，后面是用括号括起来的名称，然后再跟着格式化操作符。

字段名称本身（括号内的部分）也可以具有一些特殊的格式化操作：

1. **对象遍历 (Object traversal)**: 在元数据中可用的字典和列表可以通过点 `.` 作为分隔符进行遍历；例如 `%(tags.0)s`, `%(subtitles.en.-1.ext)s`。你可以使用冒号 `:` 进行 Python 切片；例如 `%(id.3:7)s`, `%(id.6:2:-1)s`, `%(formats.:.format_id)s`。可以使用大括号 `{}` 构建仅包含特定键的字典；例如 `%(formats.:.{format_id,height})#j`。空的字段名 `%()s` 代表整个信息字典 (infodict)；例如 `%(.{id,title})s`。注意，并非所有使用此方法可以获取的字段都在下方列出。请使用 `-j` 查看可以获取哪些字段。

1. **算术运算 (Arithmetic)**: 可以使用 `+`, `-` 和 `*` 对数字字段进行简单的算术运算。例如 `%(playlist_index+10)03d`, `%(n_entries+1-playlist_index)d`

1. **日期/时间格式化 (Date/time Formatting)**: 日期/时间字段可以使用 [strftime 格式](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)进行格式化，用 `>` 与字段名分隔。例如 `%(duration>%H-%M-%S)s`, `%(upload_date>%Y-%m-%d)s`, `%(epoch-3600>%H-%M-%S)s`

1. **备选字段 (Alternatives)**: 可以使用 `,` 分隔指定备用的字段。例如 `%(release_date>%Y,upload_date>%Y|Unknown)s`

1. **替换值 (Replacement)**: 可以使用 `&` 作为分隔符，并根据 [`str.format` 微语言规范](https://docs.python.org/3/library/string.html#format-specification-mini-language)来指定替换值。如果字段**不为**空，那么将使用此替换值来代替字段的实际内容。此判断会在处理完“备选字段”之后进行；因此，只要*任何一个*备选字段**不为**空，就会采用此替换值。例如 `%(chapters&has chapters|no chapters)s`, `%(title&TITLE={:>20}|NO TITLE)s`

1. **默认值 (Default)**: 可以使用 `|` 作为分隔符为字段为空时指定一个字面的默认值。这将覆盖 `--output-na-placeholder` 的设置。例如 `%(uploader|Unknown)s`

1. **更多转换 (More Conversions)**: 除了常见的格式类型 `diouxXeEfFgGcrs` 之外，yt-dlp 额外支持转换为 `B` = 字节数 (**B**ytes), `j` = **j**son (附加 `#` 用于美化打印, `+` 用于 Unicode 编码), `h` = HTML 转义输出, `l` = 逗号分隔的列表 (**l**ist) (附加 `#` 则用 `\n` 换行分隔), `q` = 转为用于终端的 shell 引号包含的字符串 (**q**uoted) (附加 `#` 以将列表分割为不同参数), `D` = 添加十进制后缀 (**D**ecimal suffixes) (例如 10M) (附加 `#` 则使用 1024 作为倍数), 以及 `S` = 净化为安全的文件名 (**S**anitize as filename) (附加 `#` 则为受限模式)

1. **Unicode 规范化 (Unicode normalization)**: 格式类型 `U` 可用于 NFC [Unicode 规范化](https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize)。附加交替形式标志 (`#`) 则转为 NFD 规范化，转换标志 `+` 可用于 NFKC/NFKD 兼容性等价规范化。例如 `%(title)+.100U` 为 NFKC

综上所述，字段的通用语法为：
```
%(name[.keys][addition][>strf][,alternate][&replacement][|default])[flags][width][.precision][length]type
```

此外，你还可以独立于主输出模板，通过“文件类型加上冒号 `:` 分隔”的方式，为各类元数据文件分别设置输出模板。支持的文件类型包括：`subtitle`, `thumbnail`, `description`, `annotation` (已弃用), `infojson`, `link`, `pl_thumbnail`, `pl_description`, `pl_infojson`, `chapter`, `pl_video`。例如：`-o "%(title)s.%(ext)s" -o "thumbnail:%(title)s\%(title)s.%(ext)s"` 会将缩略图存放在与视频同名的文件夹内。如果某个类型的模板为空，则将不会写入该类型的文件。例如：`--write-thumbnail -o "thumbnail:"` 将仅为播放列表写入缩略图，不为视频写入缩略图。

<a id="outtmpl-postprocess-note"></a>

**注意**: 由于后期处理 (例如音视频合并等)，实际输出的文件名可能会有所不同。使用 `--print after_move:filepath` 可以获取所有后期处理完成后的实际文件名。

可用的字段包括：

 - `id` (字符串): 视频标识符
 - `title` (字符串): 视频标题
 - `fulltitle` (字符串): 忽略直播时间戳和通用标题的视频标题
 - `ext` (字符串): 视频文件名扩展名
 - `alt_title` (字符串): 视频的副标题
 - `description` (字符串): 视频的描述
 - `display_id` (字符串): 视频的替代标识符
 - `uploader` (字符串): 视频上传者的全名
 - `uploader_id` (字符串): 视频上传者的昵称或 ID
 - `uploader_url` (字符串): 指向视频上传者个人资料的 URL
 - `license` (字符串): 视频使用的许可证名称
 - `creators` (列表): 视频的创作者们
 - `creator` (字符串): 视频的创作者们；逗号分隔
 - `timestamp` (数字): 视频变为可用的 UNIX 时间戳
 - `upload_date` (字符串): 视频的上传日期 (UTC时间，格式 YYYYMMDD)
 - `release_timestamp` (数字): 视频发布时刻的 UNIX 时间戳
 - `release_date` (字符串): 视频发布日期 (UTC时间，格式 YYYYMMDD)
 - `release_year` (数字): 视频或专辑发布的年份 (YYYY)
 - `modified_timestamp` (数字): 视频最后一次修改时刻的 UNIX 时间戳
 - `modified_date` (字符串): 视频最后一次修改的日期 (UTC时间，格式 YYYYMMDD)
 - `channel` (字符串): 上传该视频的频道的全名
 - `channel_id` (字符串): 频道的 Id
 - `channel_url` (字符串): 频道的 URL
 - `channel_follower_count` (数字): 频道的关注者人数
 - `channel_is_verified` (布尔值): 频道在平台上是否通过了认证
 - `location` (字符串): 拍摄视频的物理地点
 - `duration` (数字): 视频的时长 (秒)
 - `duration_string` (字符串): 视频的时长 (HH:mm:ss 格式)
 - `view_count` (数字): 该视频在平台上的观看次数
 - `concurrent_view_count` (数字): 目前在平台上正观看该视频的人数
 - `like_count` (数字): 视频收到的正面评价（点赞）数量
 - `dislike_count` (数字): 视频收到的负面评价（点踩）数量
 - `repost_count` (数字): 视频的转发次数
 - `average_rating` (数字): 用户给出的平均评分，所用比例取决于原网页
 - `comment_count` (数字): 视频上的评论数量 (对于部分提取器，评论仅在最后才被下载，因此可能无法使用此字段)
 - `save_count` (数字): 视频被保存或添加书签的次数
 - `age_limit` (数字): 视频的年龄限制 (岁)
 - `live_status` (字符串): 以下值之一："not_live", "is_live", "is_upcoming", "was_live", "post_live" (曾经直播过，但 VOD 回放仍在处理中)
 - `is_live` (布尔值): 此视频当前是否是一个直播流
 - `was_live` (布尔值): 此视频最初是否是一个直播流
 - `playable_in_embed` (字符串): 此视频是否允许在其他站点的内嵌播放器中播放
 - `availability` (字符串): 视频的可用性状态："private" (私享), "premium_only" (仅高级会员), "subscriber_only" (仅订阅者), "needs_auth" (需要认证), "unlisted" (不公开) 或 "public" (公开)
 - `media_type` (字符串): 站点对媒体分类的类型，如 "episode" (剧集), "clip" (剪辑), "trailer" (预告片)
 - `start_time` (数字): URL 中指定的应开始播放的时间(秒)
 - `end_time` (数字): URL 中指定的应结束播放的时间(秒)
 - `extractor` (字符串): 提取器的名称
 - `extractor_key` (字符串): 提取器的键名
 - `epoch` (数字): 信息提取完成时刻的 Unix 纪元时间戳
 - `autonumber` (数字): 从 `--autonumber-start` 开始随每次下载递增的数字，前面会补零至5位
 - `video_autonumber` (数字): 随每个视频递增的数字
 - `n_entries` (数字): 播放列表中提取出的条目总数
 - `playlist_id` (字符串): 包含该视频的播放列表标识符
 - `playlist_title` (字符串): 包含该视频的播放列表的名称
 - `playlist` (字符串): 可用时为 `playlist_title`，否则为 `playlist_id`
 - `playlist_count` (数字): 播放列表中的条目总数。如果未能提取整个列表，此值可能未知
 - `playlist_index` (数字): 视频在播放列表中的索引，根据列表的最终索引在其前面补零
 - `playlist_autonumber` (数字): 视频在播放列表下载队列中的位置，根据播放列表的总长度在前面补零
 - `playlist_uploader` (字符串): 播放列表上传者的全名
 - `playlist_uploader_id` (字符串): 播放列表上传者的昵称或 ID
 - `playlist_channel` (字符串): 上传播放列表的频道的显示名称
 - `playlist_channel_id` (字符串): 上传播放列表的频道标识符
 - `playlist_webpage_url` (字符串): 播放列表网页的 URL
 - `webpage_url` (字符串): 视频网页的 URL（如果把它传给 yt-dlp，应该能再次产生相同的提取结果）
 - `webpage_url_basename` (字符串): 网页 URL 的基本名称 (basename)
 - `webpage_url_domain` (字符串): 网页 URL 的域名
 - `original_url` (字符串): 用户输入的原始 URL（或者如果是播放列表条目则等同于 `webpage_url`）
 - `categories` (列表): 该视频所属的分类列表
 - `tags` (列表): 分配给该视频的标签列表
 - `cast` (列表): 演职员名单列表

所有在 [过滤格式](#%E8%BF%87%E6%BB%A4%E6%A0%BC%E5%BC%8F) 中的字段也都可用。

针对属于某个逻辑章节或分段的视频的可用字段：

 - `chapter` (字符串): 该视频所属章节的名称或标题
 - `chapter_number` (数字): 该视频所属章节的编号
 - `chapter_id` (字符串): 该视频所属章节的 Id

针对属于某系列或节目中单集的视频的可用字段：

 - `series` (字符串): 视频所在系列或节目的标题
 - `series_id` (字符串): 视频所在系列或节目的 Id
 - `season` (字符串): 视频所属季的标题
 - `season_number` (数字): 视频所属季的编号
 - `season_id` (字符串): 视频所属季的 Id
 - `episode` (字符串): 视频单集的标题
 - `episode_number` (数字): 视频单集在季内的编号
 - `episode_id` (字符串): 视频单集的 Id

针对属于音乐专辑中某音轨的可用字段：

 - `track` (字符串): 音轨标题
 - `track_number` (数字): 音轨在整张专辑或碟片中的编号
 - `track_id` (字符串): 音轨 Id
 - `artists` (列表): 音轨的艺术家
 - `artist` (字符串): 音轨的艺术家；逗号分隔
 - `genres` (列表): 音轨的流派
 - `genre` (字符串): 音轨的流派；逗号分隔
 - `composers` (列表): 曲目的作曲家
 - `composer` (字符串): 曲目的作曲家；逗号分隔
 - `album` (字符串): 音轨所属的专辑标题
 - `album_type` (字符串): 专辑的类型
 - `album_artists` (列表): 专辑中的所有艺术家
 - `album_artist` (字符串): 专辑中的所有艺术家；逗号分隔
 - `disc_number` (数字): 音轨所属的碟片或其他物理介质编号

仅在使用 `--download-sections`，以及带内部章节的视频使用 `--split-chapters` 的 `chapter:` 前缀时可用的字段：

 - `section_title` (字符串): 章节的标题
 - `section_number` (数字): 章节在文件内的编号
 - `section_start` (数字): 章节开始时间 (秒)
 - `section_end` (数字): 章节结束时间 (秒)

仅在与 `--print` 一起使用时可用的字段：

 - `urls` (字符串): 所有请求格式的 URL，每行一个
 - `filename` (字符串): 视频文件的名称。注意：[实际文件名可能会有差异](#outtmpl-postprocess-note)
 - `formats_table` (表格): 由 `--list-formats` 打印的视频格式表
 - `thumbnails_table` (表格): 由 `--list-thumbnails` 打印的缩略图格式表
 - `subtitles_table` (表格): 由 `--list-subs` 打印的字幕格式表
 - `automatic_captions_table` (表格): 由 `--list-subs` 打印的自动字幕格式表

 仅在视频下载完成之后可用的字段 (`post_process`/`after_move` 阶段)：

 - `filepath`: 下载后视频文件的实际路径

仅在 `--sponsorblock-chapter-title` 中可用的字段：

 - `start_time` (数字): 章节开始时间 (秒)
 - `end_time` (数字): 章节结束时间 (秒)
 - `categories` (列表): 该章节所属的 [SponsorBlock 类别列表](https://wiki.sponsor.ajay.app/w/Types#Category)
 - `category` (字符串): 该章节所属的最细分 SponsorBlock 类别
 - `category_names` (列表): 类别的友好可读名称
 - `name` (字符串): 最细分类别的友好名称
 - `type` (字符串): 章节的 [SponsorBlock 动作类型](https://wiki.sponsor.ajay.app/w/Types#Action_Type)

输出模板中引用的每个上述序列（占位符）都会被替换为其对应的实际值。例如：使用 `-o %(title)s-%(id)s.%(ext)s` 下载标题为 `yt-dlp test video` 且 id 为 `BaW_jenozKc` 的 mp4 视频时，将在当前目录下创建一个名为 `yt-dlp test video-BaW_jenozKc.mp4` 的文件。

**注意**: 这些序列并不保证一定存在，因为它们取决于由特定提取器收集的元数据。当信息不存在时，这些序列将被替换为 `--output-na-placeholder` 提供的占位值 (默认为 `NA`)。

**提示**: 你可以查看 `-j` (JSON) 输出的内容，来确认当前某个 URL 可提取出哪些字段。

对于数字序列，你可以使用 [数字相关格式化操作](https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting)；例如：`%(view_count)05d` 会使播放量的字符串向左用零填充至 5 个字符，就像 `00042`。

输出模板还可以包含任意的层级路径，例如 `-o "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s"`，这将使每个视频下载至对应这套路径模板的目录中。缺失的目录会自动为你创建。

若要在输出模板中使用百分号字面量，请使用 `%%`。若要输出到标准输出 (stdout)，请使用 `-o -`。

当前的默认输出模板是 `%(title)s [%(id)s].%(ext)s`。

某些情况下，你不希望文件名中包含诸如中文字符、空格或 `&` 之类的特殊字符，比如当你准备将下载的文件传送到 Windows 系统，或是通过不兼容 8-bit 的通道传输文件名时。在这种情况下，可以加上 `--restrict-filenames` 标志来获取安全 (较短) 的文件名。

#### 输出模板示例

```bash
$ yt-dlp --print filename -o "test video.%(ext)s" BaW_jenozKc
test video.webm    # 具有正确后缀的字面名称

$ yt-dlp --print filename -o "%(title)s.%(ext)s" BaW_jenozKc
youtube-dl test video ''_ä↭𝕐.webm    # 各种奇怪的字符

$ yt-dlp --print filename -o "%(title)s.%(ext)s" BaW_jenozKc --restrict-filenames
youtube-dl_test_video_.webm    # 经过限制的（安全的）文件名

# 在单独的目录中下载 YouTube 播放列表视频，按其在列表中的顺序编号
$ yt-dlp -o "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s" "https://www.youtube.com/playlist?list=PLwiyx1dc3P2JR9N8gQaQN_BCvlSlap7re"

# 在单独的目录中下载 YouTube 播放列表视频，按照其上传年份进行归类
$ yt-dlp -o "%(upload_date>%Y)s/%(title)s.%(ext)s" "https://www.youtube.com/playlist?list=PLwiyx1dc3P2JR9N8gQaQN_BCvlSlap7re"

# 如果播放列表索引存在的话，在前面加上 " - " 分隔符
$ yt-dlp -o "%(playlist_index&{} - |)s%(title)s.%(ext)s" BaW_jenozKc "https://www.youtube.com/user/TheLinuxFoundation/playlists"

# 下载某个 YouTube 频道/用户所有的播放列表，并将每个播放列表分别存放在各自的目录中：
$ yt-dlp -o "%(uploader)s/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s" "https://www.youtube.com/user/TheLinuxFoundation/playlists"

# 下载 Udemy 课程，并将每一章存放在主目录的 MyVideos 文件夹下的单独目录中
$ yt-dlp -u user -p password -P "~/MyVideos" -o "%(playlist)s/%(chapter_number)s - %(chapter)s/%(title)s.%(ext)s" "https://www.udemy.com/java-tutorial"

# 下载整部剧集，将该剧及其每一季分别存放在 C:/MyVideos 下的单独目录中
$ yt-dlp -P "C:/MyVideos" -o "%(series)s/%(season_number)s - %(season)s/%(episode_number)s - %(episode)s.%(ext)s" "https://videomore.ru/kino_v_detalayah/5_sezon/367617"

# 将视频下载为 "C:\MyVideos\uploader\title.ext"，字幕下载为 "C:\MyVideos\subs\uploader\title.ext"
# 并将所有临时文件存放在 "C:\MyVideos\tmp"
$ yt-dlp -P "C:/MyVideos" -P "temp:tmp" -P "subtitle:subs" -o "%(uploader)s/%(title)s.%(ext)s" BaW_jenozKc --write-subs

# 将视频下载为 "C:\MyVideos\uploader\title.ext"，字幕下载为 "C:\MyVideos\uploader\subs\title.ext"
$ yt-dlp -P "C:/MyVideos" -o "%(uploader)s/%(title)s.%(ext)s" -o "subtitle:%(uploader)s/subs/%(title)s.%(ext)s" BaW_jenozKc --write-subs

# 将正在下载的视频直接流式传输到 stdout (标准输出)
$ yt-dlp -o - BaW_jenozKc
```

# 格式选择

默认情况下，如果你**不**传递任何选项，yt-dlp 会尝试下载可用的最佳质量。
这通常等同于使用 `-f bestvideo*+bestaudio/best`。然而，如果启用了多音频流 (`--audio-multistreams`)，默认格式将变为 `-f bestvideo+bestaudio/best`。类似地，如果 ffmpeg 不可用，或者你使用 yt-dlp 流式传输到 `stdout` (`-o -`)，默认设置将变为 `-f best/bestvideo+bestaudio`。

**弃用警告**: 最新版本的 yt-dlp 已经可以使用 ffmpeg 同时将多种格式流式传输到 stdout。因此，在未来的版本中，此默认设置将变为与正常下载类似的 `-f bv*+ba/b`。如果你希望保留 `-f b/bv+ba` 的设置，建议在配置选项中明确指定。

格式选择的一般语法是 `-f FORMAT` (或 `--format FORMAT`)，其中 `FORMAT` 是一个*选择器表达式*，即描述你希望下载的一种或多种格式的表达式。

<!-- MANPAGE: BEGIN EXCLUDED SECTION -->
**简而言之:** [带我去看示例](#%E6%A0%BC%E5%BC%8F%E9%80%89%E6%8B%A9%E7%A4%BA%E4%BE%8B)。
<!-- MANPAGE: END EXCLUDED SECTION -->

最简单的情况是请求特定的格式；例如通过 `-f 22`，你可以下载格式代码 (format code) 为 22 的格式。你可以使用 `--list-formats` 或 `-F` 来获取特定视频的可用格式代码列表。注意，这些格式代码是特定于某个提取器的。

你也可以使用文件扩展名（目前支持 `3gp`, `aac`, `flv`, `m4a`, `mp3`, `mp4`, `ogg`, `wav`, `webm`）来下载特定文件扩展名中作为单一文件提供的最佳质量格式，例如 `-f webm` 将下载作为单一文件提供的、扩展名为 `webm` 的最佳质量格式。

你可以使用 `-f -` 为*每个视频*交互式地提供格式选择器。

你也可以使用特殊名称来选择特定的边缘格式：

 - `all`: 分别选择**所有格式**
 - `mergeall`: 选择并**合并所有格式**（必须与 `--audio-multistreams`、`--video-multistreams` 之一或两者同时使用）
 - `b*`, `best*`: 选择**包含视频或音频或两者兼有**的最佳质量格式 (即 `vcodec!=none or acodec!=none`)
 - `b`, `best`: 选择**同时包含**视频和音频的最佳质量格式。等同于 `best*[vcodec!=none][acodec!=none]`
 - `bv`, `bestvideo`: 选择最佳质量的**纯视频**格式。等同于 `best*[acodec=none]`
 - `bv*`, `bestvideo*`: 选择**包含视频**的最佳质量格式。它可能也包含音频。等同于 `best*[vcodec!=none]`
 - `ba`, `bestaudio`: 选择最佳质量的**纯音频**格式。等同于 `best*[vcodec=none]`
 - `ba*`, `bestaudio*`: 选择**包含音频**的最佳质量格式。它可能也包含视频。等同于 `best*[acodec!=none]`（[不建议使用！](https://github.com/yt-dlp/yt-dlp/issues/979#issuecomment-919629354)）
 - `w*`, `worst*`: 选择包含视频或音频的最差质量格式
 - `w`, `worst`: 选择同时包含视频和音频的最差质量格式。等同于 `worst*[vcodec!=none][acodec!=none]`
 - `wv`, `worstvideo`: 选择最差质量的纯视频格式。等同于 `worst*[acodec=none]`
 - `wv*`, `worstvideo*`: 选择包含视频的最差质量格式。它可能也包含音频。等同于 `worst*[vcodec!=none]`
 - `wa`, `worstaudio`: 选择最差质量的纯音频格式。等同于 `worst*[vcodec=none]`
 - `wa*`, `worstaudio*`: 选择包含音频的最差质量格式。它可能也包含视频。等同于 `worst*[acodec!=none]`

例如，要下载最差质量的纯视频格式，你可以使用 `-f worstvideo`。然而，通常建议不要使用 `worst` 及相关选项。当你的格式选择器为 `worst` 时，被选择的将是各方面都最差的格式。而在大多数情况下，你实际想要的往往是文件体积最小的视频。因此，使用 `-S +size` 或更严谨的 `-S +size,+br,+res,+fps` 通常比使用 `-f worst` 更好。详情参见[排序格式](#%E6%8E%92%E5%BA%8F%E6%A0%BC%E5%BC%8F)。

你可以通过 `best<type>.<n>` 选择某种类型中第 n 好的格式。例如，`best.2` 将选择第二好的组合格式。同理，`bv*.3` 将选择包含视频流的第三好格式。

如果你希望下载多个视频，且它们并没有提供相同的格式，你可以使用斜杠 `/` 来指定首选顺序。请注意，左侧的格式具有更高的优先级；例如 `-f 22/17/18` 会在格式 22 可用时下载格式 22，否则在 17 可用时下载 17，否则在 18 可用时下载 18，如果都不可用，则会提示没有合适的格式可供下载。

如果你希望下载同一个视频的多个格式，请使用逗号 `,` 分隔，例如 `-f 22,17,18` 将下载所有这三种格式（当然前提是它们都可用）。这里有一个结合了优先级特性的更复杂的例子：`-f 136/137/mp4/bestvideo,140/m4a/bestaudio`。

你可以使用 `-f <format1>+<format2>+...` 将多个格式的音视频流合并到一个文件中（需要安装 ffmpeg）；例如 `-f bestvideo+bestaudio` 将下载最佳的纯视频格式和最佳的纯音频格式，并使用 ffmpeg 将它们混流 (mux) 在一起。

**弃用警告**: 因为*下述*的行为既复杂又有违直觉，在未来版本中这将被移除，并且将默认启用多流下载 (multistreams)。将会添加一个新的运算符来限制仅下载单一音频/视频。

除非使用了 `--video-multistreams`，否则具有视频流的格式中，只有第一个将被采用，其余的都会被忽略。类似地，除非使用了 `--audio-multistreams`，否则所有具备音频流的格式中也只采用第一个。例如 `-f bestvideo+best+bestaudio --video-multistreams --audio-multistreams` 将会下载并合并所有 3 个给定的格式。生成的文件将包含 2 条视频流和 2 条音频流。但是 `-f bestvideo+best+bestaudio --no-video-multistreams` 将仅下载并合并 `bestvideo` 和 `bestaudio`。此时 `best` 被忽略，因为之前已经选择了一个包含视频流的格式 (`bestvideo`)。因此，格式指定的顺序非常重要。`-f best+bestaudio --no-audio-multistreams` 将只下载 `best`，而 `-f bestaudio+best --no-audio-multistreams` 将忽略 `best` 并只下载 `bestaudio`。

## 过滤格式

你也可以通过在方括号中添加条件来过滤视频格式，例如 `-f "best[height=720]"` (或 `-f "[filesize>10M]"`，因为没有指定选择器的过滤器会被默认解释为 `best`)。

下列数值元数据字段可以与比较运算符 `<`, `<=`, `>`, `>=`, `=` (等于), `!=` (不等于) 一同使用：

 - `filesize`: 字节数 (如果预先已知)
 - `filesize_approx`: 估计的字节数
 - `width`: 视频的宽度 (如果已知)
 - `height`: 视频的高度 (如果已知)
 - `aspect_ratio`: 视频的宽高比 (如果已知)
 - `tbr`: 音视频总平均比特率，单位为 [kbps](## "1000 bits/sec")
 - `abr`: 平均音频比特率，单位为 [kbps](## "1000 bits/sec")
 - `vbr`: 平均视频比特率，单位为 [kbps](## "1000 bits/sec")
 - `asr`: 音频采样率，单位赫兹 (Hertz)
 - `fps`: 帧率
 - `audio_channels`: 音频声道数
 - `stretched_ratio`: 视频像素的 `width:height` 比例（如果像素非正方形）

过滤也可用于比较操作 `=` (等于), `^=` (以...开头), `$=` (以...结尾), `*=` (包含), `~=` (匹配正则) 以及下列字符串元数据字段：

 - `url`: 视频 URL
 - `ext`: 文件扩展名
 - `acodec`: 使用的音频编解码器名称
 - `vcodec`: 使用的视频编解码器名称
 - `container`: 容器格式名称
 - `protocol`: 将用于实际下载的协议，小写 (`http`, `https`, `rtsp`, `rtmp`, `rtmpe`, `mms`, `f4m`, `ism`, `http_dash_segments`, `m3u8`, 或 `m3u8_native`)
 - `language`: 语言代码
 - `dynamic_range`: 视频的动态范围 (如 HDR/SDR)
 - `format_id`: 格式的简短描述
 - `format`: 格式的人类可读描述
 - `format_note`: 格式的附加信息
 - `resolution`: 宽度和高度的文本描述

任何字符串比较都可以在前面加上否定前缀 `!` 以产生相反的比较结果，例如 `!*=` (不包含)。如果字符串比较的运算元包含空格或除 `._-` 以外的特殊字符，则需要用双引号或单引号括起来。

**注意**: 这些元数据字段并不能保证一定存在，因为这完全取决于特定提取器（即网站提供的元数据）所收集到的信息。提取器提供的任何其他字段也都可以用于过滤。

如果不加上问号 (`?`) ，那么值未知的格式将被排除在外。你可以组合格式过滤器，例如 `-f "bv[height<=?720][tbr>500]"` 会选择比特率至少为 500 kbps 的，最高为 720p 的视频 (或是未知高度的视频)。你也可以将过滤器与 `all` 一起使用以下载所有满足条件的格式，例如 `-f "all[vcodec=none]"` 选择所有的纯音频格式。

格式选择器也可以使用括号进行分组；例如 `-f "(mp4,webm)[height<480]"` 将下载高度小于 480 的、最佳的预合并 (pre-merged) mp4 和 webm 格式。

## 排序格式

你可以使用 `-S` (`--format-sort`) 更改评判为 `best` (最佳) 的标准。它的通用格式为 `--format-sort field1,field2...`。

可用的字段包括：

 - `hasvid`: 优先考虑带有视频流的格式
 - `hasaud`: 优先考虑带有音频流的格式
 - `ie_pref`: 提取器偏好设置
 - `lang`: 根据提取器确定的语言偏好 (例如：原声语言优于音频描述)
 - `quality`: 格式的质量
 - `source`: 来源的偏好
 - `proto`: 下载使用的协议 (`https`/`ftps` > `http`/`ftp` > `m3u8_native`/`m3u8` > `http_dash_segments`> `websocket_frag` > `mms`/`rtsp` > `f4f`/`f4m`)
 - `vcodec`: 视频编解码器 (`av01` > `vp9.2` > `vp9` > `h265` > `h264` > `vp8` > `h263` > `theora` > 其他)
 - `acodec`: 音频编解码器 (`flac`/`alac` > `wav`/`aiff` > `opus` > `vorbis` > `aac` > `mp4a` > `mp3` > `ac4` > `eac3` > `ac3` > `dts` > 其他)
 - `codec`: 等同于 `vcodec,acodec`
 - `vext`: 视频扩展名 (`mp4` > `mov` > `webm` > `flv` > 其他)。如果使用了 `--prefer-free-formats`，则优先选择 `webm`。
 - `aext`: 音频扩展名 (`m4a` > `aac` > `mp3` > `ogg` > `opus` > `webm` > 其他)。如果使用了 `--prefer-free-formats`，则顺序变为 `ogg` > `opus` > `webm` > `mp3` > `m4a` > `aac`
 - `ext`: 等同于 `vext,aext`
 - `filesize`: 确切的文件大小 (如果预先已知)
 - `fs_approx`: 估计的文件大小
 - `size`: 如果可用，则为确切的文件大小；否则为估计的文件大小
 - `height`: 视频高度
 - `width`: 视频宽度
 - `res`: 视频分辨率，通过最小尺寸计算得出。
 - `fps`: 视频帧率
 - `hdr`: 视频的动态范围 (`DV` > `HDR12` > `HDR10+` > `HDR10` > `HLG` > `SDR`)
 - `channels`: 音频声道数
 - `tbr`: 总平均比特率 (单位: [kbps](## "1000 bits/sec"))
 - `vbr`: 平均视频比特率 (单位: [kbps](## "1000 bits/sec"))
 - `abr`: 平均音频比特率 (单位: [kbps](## "1000 bits/sec"))
 - `br`: 平均比特率 (单位: [kbps](## "1000 bits/sec")), `tbr`/`vbr`/`abr`
 - `asr`: 音频采样率 (单位: Hz)

**弃用警告**: 其中许多字段具有 (目前未记录在案的) 别名，这些别名可能会在未来版本中被移除。建议仅使用文档记录的字段名称。

所有的字段，除非另有说明，都是按降序排列的。要反转该顺序，请在字段前加上 `+`。例如 `+res` 会优先选择分辨率最小的格式。此外，你可以为这些字段加上一个带冒号 `:` 前缀的偏好值。例如 `res:720` 优先选择较大的视频，但最大不超过 720p，如果没有小于 720p 的视频，则选择最小的视频。对于 `codec` 和 `ext`，你可以提供两个偏好值，第一个针对视频，第二个针对音频。例如 `+codec:avc:m4a` (等同于 `+vcodec:avc,+acodec:m4a`) 将视频编解码器偏好设置为 `h264` > `h265` > `vp9` > `vp9.2` > `av01` > `vp8` > `h263` > `theora`，并将音频编解码器偏好设置为 `mp4a` > `aac` > `vorbis` > `opus` > `mp3` > `ac3` > `dts`。你还可以使用 `~` 作为分隔符，使排序优先考虑最接近给定值的项。例如 `filesize~1G` 会优先选择文件大小最接近 1 GiB 的格式。

无论用户如何定义顺序，`hasvid` 和 `ie_pref` 字段在排序时总是被赋予最高优先级。可以通过使用 `--format-sort-force` 改变这一行为。除此之外，默认使用的顺序为：`lang,quality,res,fps,hdr:12,vcodec,channels,acodec,size,br,asr,proto,ext,hasaud,source,id`。提取器可能会覆盖此默认顺序，但它们不能覆盖用户提供的排序顺序。

请注意，hdr 的默认值是 `hdr:12`；即默认不优先考虑 Dolby Vision (DV)。做出此选择是因为 DV 格式目前尚未完全兼容大多数设备。这可能会在未来改变。

如果你的格式选择器是 `worst`，则会在排序后选择最后一项。这意味着它会选择各方面都最差的格式。大部分时间，你其实想要的是体积最小的视频。因此通常最好使用 `-f best -S +size,+br,+res,+fps`。

如果你多次使用 `-S`/`--format-sort` 选项，每次后续传入的排序参数都会追加到上一个之前，并且对于任何重复字段，只保留最高优先级的条目。例如 `-S proto -S res` 等同于 `-S res,proto`；而 `-S res:720,fps -S vcodec,res:1080` 等同于 `-S vcodec,res:1080,fps`。你可以使用 `--format-sort-reset` 来忽略之前传入的任何 `-S`/`--format-sort` 参数，并重置回默认顺序。

**提示**: 你可以使用 `-v -F` 来查看格式的排序情况（从最差到最好）。

## 格式选择示例

```bash
# 下载最佳的纯视频格式和最佳的纯音频格式并将它们合并，
# 如果没有纯视频格式，则下载最佳组合格式
$ yt-dlp -f "bv+ba/b"

# 下载包含视频的最佳格式，
# 如果它还没有音频流，则将它与最佳纯音频格式合并
$ yt-dlp -f "bv*+ba/b"

# 同上
$ yt-dlp

# 下载最佳的纯视频格式和最佳的纯音频格式而不合并它们
# 在这种情况下，应使用输出模板，因为
# 默认情况下，bestvideo 和 bestaudio 会得到相同的文件名。
$ yt-dlp -f "bv,ba" -o "%(title)s.f%(format_id)s.%(ext)s"

# 下载并合并具有视频流的最佳格式，
# 并将所有纯音频格式合并到一个文件中
$ yt-dlp -f "bv*+mergeall[vcodec=none]" --audio-multistreams

# 下载并合并具有视频流的最佳格式，
# 以及最好的 2 个纯音频格式合并到一个文件中
$ yt-dlp -f "bv*+ba+ba.2" --audio-multistreams


# 以下示例展示了旧的格式选择方法 (不使用 -S) 
# 以及如何使用 -S 来实现类似但（通常）更好的结果

# 下载可用的最差视频 (旧方法)
$ yt-dlp -f "wv*+wa/w"

# 下载可用视频中分辨率最小的最佳视频
$ yt-dlp -S "+res"

# 下载体积最小的视频
$ yt-dlp -S "+size,+br"



# 下载最佳的 mp4 视频，如果不可用则下载其它格式的最佳视频
$ yt-dlp -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b"

# 下载具有最佳扩展名的最佳视频
# (对于视频，mp4 > mov > webm > flv。对于音频，m4a > aac > mp3 ...)
$ yt-dlp -S "ext"



# 下载最佳视频，但分辨率不超过 480p，
# 如果没有低于 480p 的视频，则下载最差的视频
$ yt-dlp -f "bv*[height<=480]+ba/b[height<=480] / wv*+ba/w"

# 下载分辨率最高但不超过 480p 的最佳视频，
# 如果没有低于 480p 的视频，则下载分辨率最小的最佳视频
$ yt-dlp -S "height:480"

# 下载分辨率最高但不超过 480p 的最佳视频，
# 如果没有低于 480p 的视频，则下载分辨率最小的最佳视频
# 分辨率通过计算最小维度得出，因此这同样适用于竖屏视频
$ yt-dlp -S "res:480"



# 下载带音频的最佳视频，体积不超过 50 MB，
# 如果没有小于 50 MB 的，则下载最差视频
$ yt-dlp -f "b[filesize<50M] / w"

# 下载体积最大但不超过 50 MB 的带音频的最佳视频，
# 如果没有小于 50 MB 的，则下载体积最小的带音频视频
$ yt-dlp -f "b" -S "filesize:50M"

# 下载体积最接近 50 MB 的带音频的最佳视频
$ yt-dlp -f "b" -S "filesize~50M"



# 通过 HTTP/HTTPS 协议直接下载的最佳视频，
# 如果没有此类视频，则通过任何协议下载可用的最佳视频
$ yt-dlp -f "(bv*+ba/b)[protocol^=http][protocol!*=dash] / (bv*+ba/b)"

# 通过最佳协议下载最佳视频
# (https/ftps > http/ftp > m3u8_native > m3u8 > http_dash_segments ...)
$ yt-dlp -S "proto"



# 下载采用 h264 或 h265 编码的最佳视频，
# 如果没有此类视频，则下载最佳视频
$ yt-dlp -f "(bv*[vcodec~='^((he|a)vc|h26[45])']+ba) / (bv*+ba/b)"

# 下载采用最佳编码 (但不超过 h264) 的最佳视频，
# 如果没有此类视频，则下载采用最差编码的最佳视频
$ yt-dlp -S "codec:h264"

# 下载采用最差编码 (但好于 h264) 的最佳视频，
# 如果没有此类视频，则下载采用最佳编码的最佳视频
$ yt-dlp -S "+codec:h264"



# 更复杂的示例

# 下载分辨率不超过 720p 的最佳视频，优先选择帧率大于 30 的，
# 如果没有此类视频，则下载最差视频（仍然优先选择帧率大于 30）
$ yt-dlp -f "((bv*[fps>30]/bv*)[height<=720]/(wv*[fps>30]/wv*)) + ba / (b[fps>30]/b)[height<=720]/(w[fps>30]/w)"

# 下载分辨率最大但不超过 720p 的视频，
# 如果没有此类视频，则下载最小分辨率的视频，
# 在分辨率相同的情况下优先选择具有较大帧率的格式
$ yt-dlp -S "res:720,fps"



# 下载分辨率最小但不低于 480p 的视频，
# 如果没有此类视频，则下载最大分辨率的视频，
# 在分辨率相同的情况下优先选择更好的编解码器，然后是较大的总比特率
$ yt-dlp -S "+res:480,codec,br"
```

# 修改元数据 (MODIFYING METADATA)

可以通过使用 `--parse-metadata` 和 `--replace-in-metadata` 来修改提取器收集到的元数据。

`--replace-in-metadata FIELDS REGEX REPLACE` 用于使用 [Python 正则表达式](https://docs.python.org/3/library/re.html#regular-expression-syntax)替换任何元数据字段中的文本。对于高级用法，可以在替换字符串中使用 [后向引用 (Backreferences)](https://docs.python.org/3/library/re.html?highlight=backreferences#re.sub)。

`--parse-metadata FROM:TO` 的通用语法是提供要从中提取数据的字段名或[输出模板](#%E8%BE%93%E5%87%BA%E6%A8%A1%E6%9D%BF)，以及用于解释它的格式，两者由冒号 `:` 分隔。对于 `TO`，可以使用带有命名捕获组的 [Python 正则表达式](https://docs.python.org/3/library/re.html#regular-expression-syntax)、单个字段名、或类似于[输出模板](#%E8%BE%93%E5%87%BA%E6%A8%A1%E6%9D%BF)的语法（仅支持 `%(field)s` 格式）。此选项可以被多次使用以解析和修改各个字段。

注意，这些选项会保留它们的相对顺序，允许在解析后的字段中进行替换，反之亦然。而且，以此创建的任何字段不仅可以在[输出模板](#%E8%BE%93%E5%87%BA%E6%A8%A1%E6%9D%BF)中使用，也会影响使用 `--embed-metadata` 添加到媒体文件中的元数据。

此选项还有一些特殊的用途：

* 你可以根据当前下载视频的元数据下载一个额外的 URL。为此，请将字段 `additional_urls` 设置为你希望下载的 URL。例如：`--parse-metadata "description:(?P<additional_urls>https?://www\.vimeo\.com/\d+)"` 会下载从描述中找到的第一个 Vimeo 视频。

* 你可以用它来改变嵌入媒体文件中的元数据。为此，需设置具有 `meta_` 前缀的对应字段的值。例如，你对 `meta_description` 字段设置的任何值，都会被写入到文件中的 `description` 字段 —— 你可以用它为“描述(description)”和“大纲(synopsis)”设置不同的值。若要修改单条流的元数据，请使用 `meta<n>_` 前缀 (例如 `meta1_language`)。对 `meta_` 字段设置的任何值都会覆盖所有的默认值。

**注意**: 元数据的修改发生格式选择、提取后等一系列操作之前。有些字段可能在这些阶段期间被添加或更改，从而覆盖掉你的修改。

作为参考，以下是 yt-dlp 默认写入到文件元数据中的字段：

元数据字段            | 来源 (From)
:--------------------------|:------------------------------------------------
`title`                    | `track` 或 `title`
`date`                     | `upload_date`
`description`, `synopsis`  | `description`
`purl`, `comment`          | `webpage_url`
`track`                    | `track_number`
`artist`                   | `artist`, `artists`, `creator`, `creators`, `uploader` 或 `uploader_id`
`composer`                 | `composer` 或 `composers`
`genre`                    | `genre`, `genres`, `categories` 或 `tags`
`album`                    | `album` 或 `series`
`album_artist`             | `album_artist` 或 `album_artists`
`disc`                     | `disc_number`
`show`                     | `series`
`season_number`            | `season_number`
`episode_id`               | `episode` 或 `episode_id`
`episode_sort`             | `episode_number`
各条流的 `language`        | 该格式的 `language`

**注意**: 你所选的文件格式可能并不支持其中某些字段。


## 修改元数据的示例

```bash
# 将标题解析为 "艺术家 - 标题" 的形式
$ yt-dlp --parse-metadata "title:%(artist)s - %(title)s"

# 正则表达式示例
$ yt-dlp --parse-metadata "description:Artist - (?P<artist>.+)"

# 将 episode 字段复制到 title 字段中 (此时 FROM 和 TO 皆为单独字段)
$ yt-dlp --parse-metadata "episode:title"

# 将标题设置为 "系列名称 S01E05" 这种格式
$ yt-dlp --parse-metadata "%(series)s S%(season_number)02dE%(episode_number)02d:%(title)s"

# 在视频元数据中优先将 uploader (上传者) 作为 "artist" (艺术家) 字段
$ yt-dlp --parse-metadata "%(uploader|)s:%(meta_artist)s" --embed-metadata

# 在视频元数据中，使用视频描述而非 webpage_url 来填充 "comment" 字段，
# 并且能够正确处理多行文本
$ yt-dlp --parse-metadata "description:(?s)(?P<meta_comment>.+)" --embed-metadata

# 不要在视频元数据中设置任何 "synopsis" (大纲) 字段
$ yt-dlp --parse-metadata ":(?P<meta_synopsis>)"

# 将 "formats" 字段从 infojson 中移除 (将其设置为空字符串)
$ yt-dlp --parse-metadata "video::(?P<formats>)" --write-info-json

# 将标题和上传者中的所有空格及 "_" 替换为 "-"
$ yt-dlp --replace-in-metadata "title,uploader" "[ _]" "-"

```

# 提取器参数 (EXTRACTOR ARGUMENTS)

一些提取器接受额外的参数，可以通过 `--extractor-args KEY:ARGS` 来传递。`ARGS` 是一个以分号 `;` 分隔的字符串，形如 `ARG=VAL1,VAL2`。例如 `--extractor-args "youtube:player-client=tv,mweb;formats=incomplete" --extractor-args "twitter:api=syndication"`

注意：在 CLI 命令行中，`ARG` 可以使用 `-` 替代 `_`；例如 `youtube:player-client"` 会变成 `youtube:player_client"`。

以下提取器使用了此功能：

#### youtube
* `lang`: 偏好此语言代码（区分大小写）的翻译后元数据（`title`，`description` 等）。默认情况下，优先使用视频的主要语言元数据，回退项则为翻译后的 `en` (英语)。支持的内容语言代码列表请参阅 [youtube/_base.py](https://github.com/yt-dlp/yt-dlp/blob/415b4c9f955b1a0391204bd24a7132590e7b3bdb/yt_dlp/extractor/youtube/_base.py#L402-L409)。
* `skip`: `hls`, `dash` 或 `translated_subs` 之一或多个组合，分别用于跳过 m3u8 manifest、dash manifest 和[自动翻译字幕](https://github.com/yt-dlp/yt-dlp/issues/4090#issuecomment-1158102032)的提取。
* `player_client`: 用于提取视频数据的客户端。目前可用的客户端有 `web`, `web_safari`, `web_embedded`, `web_music`, `web_creator`, `mweb`, `ios`, `android`, `android_vr`, `tv`, `tv_downgraded`, 和 `tv_simply`。默认情况下使用 `android_vr,web_safari`。如果没有可用的 JavaScript 运行时/引擎，则仅使用 `android_vr`。如果向 yt-dlp 传递了已登录的 cookies，则对于免费帐户使用 `tv_downgraded,web_safari`，对于高级账户 (premium) 使用 `tv_downgraded,web_creator`。当使用登录 cookies 访问 `music.youtube.com` URL 时，会添加 `web_music` 客户端。`web_embedded` 客户端用于年龄限制视频，但仅在某些情况下成功绕过限制（例如如果视频允许内嵌播放），并且当 `android_vr` 无法访问视频时可作为回退项添加。如果帐户需要年龄验证，则会针对年龄限制视频添加 `web_creator` 客户端。有些客户端（如 `web_creator` 和 `web_music`）的格式需要 `po_token` 才可下载。有些客户端（如 `web_creator`）仅在登录认证后才能工作。并非所有客户端都支持 cookie 认证。你可以使用 `default` 表示默认客户端集合，或使用 `all` 表示所有客户端（不推荐）。你可以在客户端前加 `-` 将其排除，例如 `youtube:player_client=default,-web_safari`
* `player_skip`: 跳过对于稳健提取通常必需的某些网络请求。可以是 `configs` (跳过客户端配置)、`webpage` (跳过初始网页)、`js` (跳过 js 播放器)、`initial_data` (跳过初始数据/下一集请求) 之一或组合。虽然这些选项可以减少请求数量或避免部分速率限制，但它们可能会导致诸如格式或元数据缺失等问题。更多详情请参见 [#860](https://github.com/yt-dlp/yt-dlp/pull/860) 和 [#12826](https://github.com/yt-dlp/yt-dlp/issues/12826)
* `webpage_skip`: 跳过提取内嵌的网页数据。可以是 `player_response`, `initial_data` 之一或两者兼有。这些选项用于测试目的，并不会跳过任何网络请求。默认不跳过任何一项；然而，如果使用并非为 `actual` 的 `player_js_version`，那么将隐式开启 `webpage_skip=player_response`
* `webpage_client`: 用于视频网页请求的客户端。选项为 `web` 或 `web_safari`（默认）
* `player_params`: 用于播放器请求的 YouTube 播放器参数。将覆盖由 yt-dlp 设置的任何默认参数。
* `player_js_variant`: 用于 n/sig 解密的播放器 javascript 变体。已知的变体有：`main`, `tcc`, `tce`, `es5`, `es6`, `es6_tcc`, `es6_tce`, `tv`, `tv_es6`, `phone`, `house`。默认值为 `main`，其余用于调试目的。你可以使用 `actual` 来采用站点实际规定的版本。
* `player_js_version`: 用于 n/sig 解密的播放器 javascript 版本，格式为 `signature_timestamp@hash`（例如 `20348@0004de42`）。默认使用站点规定的版本，并且可以通过 `actual` 进行选择。使用任何其他值将隐式开启 `webpage_skip=player_response`
* `comment_sort`: `top` 或 `new` (默认) - 选择（YouTube 端的）评论排序模式
* `max_comments`: 限制收集的评论数量。由逗号分隔的整数列表，分别代表 `max-comments,max-parents,max-replies,max-replies-per-thread,max-depth`。默认为 `all,all,all,all,all`
    * `max-depth` 值为 `1` 会舍弃所有的回复评论，无论为 `max-replies` 或 `max-replies-per-thread` 给出了何值
    * 例如 `all,all,1000,10,2` 会获得总计最多 1000 条回复，每个评论串下最多 10 条回复，并且仅提取到第 2 深度层级（即顶级评论及其直接回复）。`1000,all,100` 会获得最多总计 1000 条评论，及总计最多 100 条回复。
* `formats`: 改变返回的格式类型。`dashy` (将 HTTP 转为 DASH), `duplicate` (内容相同但 URL 或协议不同；包括 `dashy`), `incomplete` (无法完整下载 - 实时 dash、实时自适应 https 以及回放 m3u8), `missing_pot` (包括需要 PO Token 但缺少该 token 的格式)
* `innertube_host`: 用于所有 API 请求的 Innertube API 主机；例如 `studio.youtube.com`, `youtubei.googleapis.com`。注意：从某个子域名导出的 cookie 在其他子域名上无法工作
* `innertube_key`: 用于所有 API 请求的 Innertube API 密钥。默认不使用 API 密钥
* `raise_incomplete_data`: 当收到不完整数据 (`Incomplete Data Received`) 时抛出错误，而不是报告警告
* `data_sync_id`: 覆盖在 Innertube API 请求中使用的账户 Data Sync ID。如果你在使用带有 `youtube:player_skip=webpage,configs` 或 `youtubetab:skip=webpage` 的帐户，可能需要此项
* `visitor_data`: 覆盖在 Innertube API 请求中使用的 Visitor Data。应与 `player_skip=webpage,configs` 配合并在无 cookies 的情况下使用。注意：使用不当可能会产生不利影响。如果你需要来自浏览器的会话状态，应该传递包含 Visitor ID 的 cookies 
* `po_token`: 要使用的 Proof of Origin (PO) 令牌。以逗号分隔的 PO Token 列表，格式为 `CLIENT.CONTEXT+PO_TOKEN`，例如 `youtube:po_token=web.gvs+XXX,web.player=XXX,web_safari.gvs+YYY`。上下文 (Context) 可以是 `gvs` (Google Video Server URL), `player` (Innertube 播放器请求) 或 `subs` (字幕)
* `pot_trace`: 为获取 PO Token 启用调试日志。`true` 或 `false` (默认)
* `fetch_pot`: 从提供者处获取 PO Token 所使用的策略。可选项有 `always` (不论特定客户端对特定上下文是否需要，总是尝试获取 PO Token)，`never` (从不获取 PO Token)，或 `auto` (默认；仅当客户端对特定上下文需要时获取)
* `jsc_trace`: 为获取 JS Challenge 启用调试日志。`true` 或 `false` (默认)
* `use_ad_playback_context`: 跳过前贴片广告以消除下载前强制的等待时间。给 yt-dlp 传递 Premium 账户 cookies 时**不要使用**此项，因为这会导致丢失 Premium 高级格式。仅在播放器客户端为 `mweb` 或 `web_music` 时有效。`true` 或 `false` (默认)

#### youtube-ejs
* `jitless`: 在无 JIT 的模式下运行受支持的 JavaScript 引擎。支持的运行时有 `deno`, `node` 和 `bun`。它牺牲了一定的性能/速度来提供更好的安全性。请注意 `node` 和 `bun` 仍被认为是不安全的。`true` 或 `false` (默认)

#### youtubepot-webpo
* `bind_to_visitor_id`: 缓存 WebPO 令牌时，是否使用 Visitor ID 而非 Visitor Data。`true` (默认) 或 `false`

#### youtubetab (YouTube 播放列表, 频道, feeds 等)
* `skip`: 包含以下之一或多个选项：`webpage` (跳过下载初始网页), `authcheck` (在未下载初始网页的情况下，允许下载需要认证的播放列表。这可能会导致不良后果，详情参见 [#1122](https://github.com/yt-dlp/yt-dlp/pull/1122))
* `approximate_date`: 在 flat-playlist 中提取粗略的 `upload_date` 和 `timestamp`。这可能会导致基于日期的过滤稍有偏差。

#### generic (通用)
* `fragment_query`: 如果没有提供值，将 mpd/m3u8 manifest URL 中的任何 query 参数透传给它们的片段，否则将按 `fragment_query=VALUE` 给定的查询字符串应用到分片上。注意，如果流具有 HLS AES-128 密钥，那么查询参数也会被传递到密钥 URI，除非传递了 `key_query` 提取器参数，或者通过 `hls_key` 提取器参数提供了外部密钥 URI。这对于 ffmpeg 下载器无效
* `variant_query`: 如果没有提供值，将主 m3u8 URL 的 query 透传给其变体播放列表的 URL，否则将应用由 `variant_query=VALUE` 给定的查询字符串
* `key_query`: 如果没有提供值，将主 m3u8 URL 的 query 透传给其 HLS AES-128 解密密钥 URI，否则将应用由 `key_query=VALUE` 给定的查询字符串。注意如果已通过 `hls_key` 提取器参数提供了密钥 URI，此项将无效。对 ffmpeg 下载器无效
* `hls_key`: HLS AES-128 密钥 URI **或** 密钥本身（十六进制），以及可选的 IV（十六进制），格式为 `(URI|KEY)[,IV]`；例如 `generic:hls_key=ABCDEF1234567980,0xFEDCBA0987654321`。传递这些值中的任何一个将强制使用本地 HLS 下载器，并覆盖在 m3u8 播放列表中找到的相应值
* `is_live`: 绕过实时的 HLS 检测并手动设置 `live_status` - 值为 `false` 会将其设为 `not_live`，任何其他值（或不设值）则会设为 `is_live`
* `impersonate`: 在初始网页请求时尝试伪装的目标客户端；例如 `generic:impersonate=safari,chrome-110`。使用 `generic:impersonate` 来伪装为任何可用的目标，使用 `generic:impersonate=false` 可禁用伪装（默认）

#### vikichannel
* `video_types`: 要下载的视频类型 - `episodes` (剧集), `movies` (电影), `clips` (片段), `trailers` (预告片) 中的一项或多项

#### youtubewebarchive
* `check_all`: 以发出更多网络请求为代价进行更多检查。`thumbnails`, `captures` 中的一项或多项

#### gamejolt
* `comment_sort`: `hot` (最热，默认), `you` (需要 cookies), `top` (置顶), `new` (最新) - 选择 (GameJolt 端的) 评论排序模式

#### hotstar
* `res`: 要忽略的分辨率 - `sd`, `hd`, `fhd` 之一或多个组合
* `vcodec`: 要忽略的视频编解码器 - `h264`, `h265`, `dvh265` 之一或多个组合
* `dr`: 要忽略的动态范围 - `sdr`, `hdr10`, `dv` 之一或多个组合

#### instagram
* `app_id`: 用于 API 请求的 `X-IG-App-ID` 头部的值。默认为网页应用程序 ID，即 `936619743392459`

#### niconicochannelplus
* `max_comments`: 要提取的最大评论数量 - 默认值为 `120`

#### tiktok
* `api_hostname`: 用于移动 API 调用的主机名，例如 `api22-normal-c-alisg.tiktokv.com`
* `app_name`: 用于移动 API 调用的默认应用名称，例如 `trill`
* `app_version`: 用于移动 API 调用的默认应用版本 - 应与 `manifest_app_version` 一起设置，例如 `34.1.2`
* `manifest_app_version`: 用于移动 API 调用的默认数字应用版本，例如 `2023401020`
* `aid`: 用于移动 API 调用的默认应用 ID，例如 `1180`
* `app_info`: 通过提供一个或多个格式为 `<iid>/[app_name]/[app_version]/[manifest_app_version]/[aid]` 的应用信息字符串来启用移动 API 提取，其中 `iid` 是唯一的应用安装 ID。`iid` 是唯一必填的值；所有其他值及其 `/` 分隔符均可省略，例如 `tiktok:app_info=1234567890123456789` 或 `tiktok:app_info=123,456/trill///1180,789//34.0.1/340001`
* `device_id`: 使用真实的设备 ID 启用移动 API 提取，用于移动 API 调用。默认为一个随机的 19 位数字符串

#### rokfinchannel
* `tab`: 要下载哪个标签页的内容 - `new`, `top`, `videos`, `podcasts`, `streams`, `stacks` 之一

#### twitter
* `api`: 选择提取推文所用的 API，可以是 `graphql` (默认), `legacy` 或 `syndication`。如果已登录则此项无效

#### stacommu, wrestleuniverse
* `device_id`: 由网站分配的、用于执行付费直播内容设备限制的 UUID 值。可以在浏览器本地存储中找到

#### twitch
* `client_id`: 将随 GraphQL 请求发送的 Client ID 值，例如 `twitch:client_id=kimne78kx3ncx6brgo4mv6wki5h1ko`

#### nhkradirulive (NHK らじる★らじる LIVE)
* `area`: 提取哪个地区的变体。有效的地区为：`sapporo`, `sendai`, `tokyo`, `nagoya`, `osaka`, `hiroshima`, `matsuyama`, `fukuoka`。默认为 `tokyo`

#### nflplusreplay
* `type`: 要提取的比赛重播类型。有效类型包括：`full_game`, `full_game_spanish`, `condensed_game` 和 `all_22`。你可以使用 `all` 提取所有可用的重播类型（这是默认行为）

#### jiocinema
* `refresh_token`: 位于浏览器本地存储中的 `refreshToken` UUID，可以通过传递该值，在使用 `token` 作为用户名、浏览器本地存储的 `accessToken` 作为密码登录时，延长登录会话的有效期。

#### jiosaavn
* `bitrate`: 要请求的音频比特率。`16`, `32`, `64`, `128`, `320` 之一或多个组合。默认为 `128,320`

#### afreecatvlive
* `cdn`: 通过请求获取流 URL 时，所用的一个或多个 CDN ID，例如 `gcp_cdn`, `gs_cdn_pc_app`, `gs_cdn_mobile_web`, `gs_cdn_pc_web`

#### soundcloud
* `formats`: 从 API 请求的格式。请求值应采用 `{protocol}_{codec}` 的格式，例如 `hls_opus,http_aac`。字符 `*` 可以作为通配符，例如 `*_mp3`，若直接传递 `*` 则请求全部格式。已知的协议包括 `http`, `hls` 和 `hls-aes`；已知的编码包括 `aac`, `opus` 和 `mp3`。原始的 `download` (下载)格式总是会被提取。默认值为 `http_aac,hls_aac,http_opus,hls_opus,http_mp3,hls_mp3`

#### orfon (orf:on)
* `prefer_segments_playlist`: 当有提供节目各片段的播放列表时，优先选择该列表而非单一完整视频。如果需要单独的各个分段，请使用 `--concat-playlist never --extractor-args "orfon:prefer_segments_playlist"`

#### bilibili
* `prefer_multi_flv`: 对于仍然提供旧格式的旧视频，倾向于提取 flv 格式而不是 mp4

#### sonylivseries
* `sort_order`: 系列视频提取的剧集排序顺序 - `asc` (升序，最老的排在最前面) 或 `desc` (降序，最新的排在最前面)。默认为 `asc`

#### tver
* `backend`: 提取用的后端 API - 可以是 `streaks` (默认) 或 `brightcove` (已弃用)

#### vimeo
* `client`: 用于提取视频数据的客户端。当前可用的客户端有 `android`, `ios`, `macos` 和 `web`。一次只能使用一个客户端。默认使用 `macos` 客户端，但在登录时使用 `web` 客户端。`web` 客户端仅在具备帐户 cookie 或登录凭据时才工作。`android` 和 `ios` 客户端仅在拥有以前缓存的 OAuth 令牌时才工作
* `original_format_policy`: 关于何时尝试提取原始格式的策略。可以是 `always` (总是), `never` (从不), 或 `auto` (自动)。默认的 `auto` 策略通过仅在 Vimeo 公开视频的下载能力时发出额外请求，以避免超过 web 客户端 API 的速率限制。

**注意**: 在不考虑后向兼容性的情况下，这些选项可能会在未来被更改或移除

<!-- MANPAGE: MOVE "INSTALLATION" SECTION HERE -->


# 插件 (PLUGINS)

请注意，**所有**插件都会被导入（即使未被显式调用），并且系统对插件代码**不执行任何检查**。**只有当你信任相关代码时才自行承担风险使用插件！**

插件可以分为两种类型：提取器 (`extractor`) 或后期处理器 (`postprocessor`)。
- 提取器插件无需通过 CLI 启用，并在输入 URL 匹配其适用范围时会被自动调用。
- 提取器插件优先于内置提取器。
- 后期处理器插件可以通过使用 `--use-postprocessor NAME` 来调用。


插件是从命名空间包 `yt_dlp_plugins.extractor` 和 `yt_dlp_plugins.postprocessor` 中加载的。

换言之，其磁盘上的文件结构大致如下：

        yt_dlp_plugins/
            extractor/
                myplugin.py
            postprocessor/
                myplugin.py

yt-dlp 会在许多位置查找这些 `yt_dlp_plugins` 命名空间文件夹（见下文），并从**所有**这些位置加载插件。
将环境变量 `YTDLP_NO_PLUGINS` 设置为非空值即可完全禁用插件的加载。

请参阅 [wiki 获取一些已知的插件](https://github.com/yt-dlp/yt-dlp/wiki/Plugins)

## 安装插件

可以使用各种方法将插件安装到指定位置。

1. **配置目录 (Configuration directories)**:
   插件包（即包含 `yt_dlp_plugins` 命名空间文件夹的包）可以直接丢入以下标准[配置位置](#%E9%85%8D%E7%BD%AE)中：
    * **用户插件 (User Plugins)**
      * `${XDG_CONFIG_HOME}/yt-dlp/plugins/<package name>/yt_dlp_plugins/` (Linux/macOS 推荐)
      * `${XDG_CONFIG_HOME}/yt-dlp-plugins/<package name>/yt_dlp_plugins/`
      * `${APPDATA}/yt-dlp/plugins/<package name>/yt_dlp_plugins/` (Windows 推荐)
      * `${APPDATA}/yt-dlp-plugins/<package name>/yt_dlp_plugins/`
      * `~/.yt-dlp/plugins/<package name>/yt_dlp_plugins/`
      * `~/yt-dlp-plugins/<package name>/yt_dlp_plugins/`
    * **系统插件 (System Plugins)**
      * `/etc/yt-dlp/plugins/<package name>/yt_dlp_plugins/`
      * `/etc/yt-dlp-plugins/<package name>/yt_dlp_plugins/`
2. **可执行文件位置 (Executable location)**: 插件包也可以类似地安装在与可执行文件同级的 `yt-dlp-plugins` 目录中（推荐用于便携式安装）：
    * 对于二进制文件环境: 当存在 `<root-dir>/yt-dlp.exe` 时，放入 `<root-dir>/yt-dlp-plugins/<package name>/yt_dlp_plugins/`
    * 对于源代码环境: 当存在 `<root-dir>/yt_dlp/__main__.py` 时，放入 `<root-dir>/yt-dlp-plugins/<package name>/yt_dlp_plugins/`

3. **pip 和存在于 `PYTHONPATH` 中的其他位置**
    * 可以使用 `pip` 来安装和管理插件包。有关示例请参阅 [yt-dlp-sample-plugins](https://github.com/yt-dlp/yt-dlp-sample-plugins)。
      * 注意：通过 pip 安装的不同插件包中的插件文件必须具有唯一的文件名。
    * 系统将在 `PYTHONPATH` 的所有路径中搜索 `yt_dlp_plugins` 命名空间文件夹。
      * 注意：这不适用于通过 Pyinstaller 构建的版本。


此外也支持将根目录下包含 `yt_dlp_plugins` 命名空间文件夹的 `.zip`, `.egg` 和 `.whl` 压缩包作为插件包。

* 例如：使用 `${XDG_CONFIG_HOME}/yt-dlp/plugins/mypluginpkg.zip`，且 `mypluginpkg.zip` 内包含有 `yt_dlp_plugins/<type>/myplugin.py`。

通过带有 `--verbose` 选项运行 yt-dlp 可以检查插件是否已被成功加载。

## 开发插件

参阅 [yt-dlp-sample-plugins](https://github.com/yt-dlp/yt-dlp-sample-plugins) 仓库获取插件包的模板，并参阅 wiki 的 [插件开发 (Plugin Development)](https://github.com/yt-dlp/yt-dlp/wiki/Plugin-Development) 部分来查看插件开发指南。

各个提取器和后期处理器的公共类（名称分别以 `IE`/`PP` 结尾的类）都将从对应的文件中被导入。这个过程遵守下划线前缀规则（例如 `_MyBasePluginIE` 被认为是私有类）及 `__all__` 规则。同理，为模块名称加下划线前缀（如 `_myplugin.py`）也可防止该模块被导入。

要通过你自己的子类替换现有的提取器，需要设置 `plugin_name` 类的关键字参数（例如：`class MyPluginIE(ABuiltInIE, plugin_name='myplugin')` 将用 `MyPluginIE` 替换 `ABuiltInIE`）。由于提取器会替换父类，所以你应该使用上述描述的方法之一将其设为私有，以排除子类提取器被单独导入。

如果你是一名插件作者，请为你的仓库添加 [yt-dlp-plugins](https://github.com/topics/yt-dlp-plugins) 标签以便被发现。

参阅 [开发者说明 (Developer Instructions)](https://github.com/yt-dlp/yt-dlp/blob/master/CONTRIBUTING.md#developer-instructions) 来了解如何编写和测试提取器。

# 嵌入 YT-DLP (EMBEDDING YT-DLP)

yt-dlp 尽力做好一款命令行程序，因而它应该能够被任何编程语言所调用。

你的程序应该避免解析常规的标准输出 (stdout)，因为它们可能在将来的版本中改变。取而代之的是，程序应当使用例如 `-J`, `--print`, `--progress-template`, `--exec` 等选项来创建能够可靠重现与解析的控制台输出。

如果是 Python 程序，你可以使用更加强大且灵活的方式嵌入 yt-dlp：

```python
from yt_dlp import YoutubeDL

URLS = ['https://www.youtube.com/watch?v=BaW_jenozKc']
with YoutubeDL() as ydl:
    ydl.download(URLS)
```

极大可能你还会希望利用各种配置选项。若要获取可用的选项列表，请查阅 [`yt_dlp/YoutubeDL.py`](yt_dlp/YoutubeDL.py#L183) 或在 Python shell 中执行 `help(yt_dlp.YoutubeDL)`。如果你对 CLI (命令行界面) 已经很熟悉了，你可以使用 [`devscripts/cli_to_api.py`](https://github.com/yt-dlp/yt-dlp/blob/master/devscripts/cli_to_api.py) 将任何 CLI 参数选项转换为对应的 `YoutubeDL` 参数。

**提示**: 如果你是把代码从 youtube-dl 移植到 yt-dlp，请务必注意一个重要区别：我们并不保证 `YoutubeDL.extract_info` 的返回值绝对可以被 JSON 序列化，或者一定是一个字典 (dictionary)。它的结构会“类似于字典”，但如果你想确保它是一个可以被序列化的字典，请通过 `YoutubeDL.sanitize_info` 方法对它进行处理，详见[下方的示例](#%E6%8F%90%E5%8F%96%E4%BF%A1%E6%81%AF)。

## 嵌入示例

#### 提取信息

```python
import json
import yt_dlp

URL = 'https://www.youtube.com/watch?v=BaW_jenozKc'

# ℹ️ 执行 help(yt_dlp.YoutubeDL) 来查看可用的选项和公共函数列表
ydl_opts = {}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(URL, download=False)

    # ℹ️ ydl.sanitize_info 可使 info 对象能够被 json 序列化
    print(json.dumps(ydl.sanitize_info(info)))
```
#### 使用 info-json 下载

```python
import yt_dlp

INFO_FILE = 'path/to/video.info.json'

with yt_dlp.YoutubeDL() as ydl:
    error_code = ydl.download_with_info_file(INFO_FILE)

print('有部分视频下载失败' if error_code
      else '所有视频均已成功下载')
```

#### 提取音频

```python
import yt_dlp

URLS = ['https://www.youtube.com/watch?v=BaW_jenozKc']

ydl_opts = {
    'format': 'm4a/bestaudio/best',
    # ℹ️ 执行 help(yt_dlp.postprocessor) 来查看可用的后期处理器及其参数的列表
    'postprocessors': [{  # 使用 ffmpeg 提取音频
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'm4a',
    }]
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    error_code = ydl.download(URLS)
```

#### 过滤视频

```python
import yt_dlp

URLS = ['https://www.youtube.com/watch?v=BaW_jenozKc']

def longer_than_a_minute(info, *, incomplete):
    """仅下载长于一分钟（或持续时间未知）的视频"""
    duration = info.get('duration')
    if duration and duration < 60:
        return 'The video is too short'

ydl_opts = {
    'match_filter': longer_than_a_minute,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    error_code = ydl.download(URLS)
```

#### 添加日志记录器和进度回调钩子 (progress hook)

```python
import yt_dlp

URLS = ['https://www.youtube.com/watch?v=BaW_jenozKc']

class MyLogger:
    def debug(self, msg):
        # 为了兼容 youtube-dl，debug 和 info 信息都会传递给 debug 方法
        # 你可以通过前缀 '[debug] ' 将它们区分开
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


# ℹ️ 参阅 help(yt_dlp.YoutubeDL) 中的 "progress_hooks"
def my_hook(d):
    if d['status'] == 'finished':
        print('下载完成，现在进行后期处理...')


ydl_opts = {
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(URLS)
```

#### 添加自定义的后期处理器 (PostProcessor)

```python
import yt_dlp

URLS = ['https://www.youtube.com/watch?v=BaW_jenozKc']

# ℹ️ 参阅 help(yt_dlp.postprocessor.PostProcessor)
class MyCustomPP(yt_dlp.postprocessor.PostProcessor):
    def run(self, info):
        self.to_screen('Doing stuff')
        return [], info


with yt_dlp.YoutubeDL() as ydl:
    # ℹ️ "when" 参数可取 yt_dlp.utils.POSTPROCESS_WHEN 中的任何值
    ydl.add_post_processor(MyCustomPP(), when='pre_process')
    ydl.download(URLS)
```


#### 使用自定义的格式选择器

```python
import yt_dlp

URLS = ['https://www.youtube.com/watch?v=BaW_jenozKc']

def format_selector(ctx):
    """ 选择不会生成 mkv 文件的最佳视频和最佳音频。
    注意: 这仅是一个示例，并不处理所有情况 """

    # formats 已经被按从最差到最佳进行了排序
    formats = ctx.get('formats')[::-1]

    # acodec='none' 意味着没有音频
    best_video = next(f for f in formats
                      if f['vcodec'] != 'none' and f['acodec'] == 'none')

    # 寻找兼容的音频扩展名
    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
    # vcodec='none' 意味着没有视频
    best_audio = next(f for f in formats if (
        f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

    # 对于合并的格式，这些是最少必须要求的字段
    yield {
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        # 必须是由 + 分隔的协议列表
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }


ydl_opts = {
    'format': format_selector,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(URLS)
```


# 与 YOUTUBE-DL 的区别 (CHANGES FROM YOUTUBE-DL)

### 新功能

* 这是从 [**yt-dlc@f9401f2**](https://github.com/blackjack4494/yt-dlc/commit/f9401f2a91987068139c5f757b12fc711d4c0cee) fork 出来的一个分支，并且与 [**youtube-dl@a08f2b7**](https://github.com/ytdl-org/youtube-dl/commit/a08f2b7e4567cdc50c0614ee0a4ffdff49b8b6e6) 进行了合并 ([排除项](https://github.com/yt-dlp/yt-dlp/issues/21))。

* **[SponsorBlock 整合](#sponsorblock-%E9%80%89%E9%A1%B9)**: 你可以利用 [SponsorBlock](https://sponsor.ajay.app) API 来标记或移除 YouTube 视频中的赞助片段。

* **[格式排序](#%E6%8E%92%E5%BA%8F%E6%A0%BC%E5%BC%8F)**: 默认的格式排序选项已被更改，如今会优先选择更高分辨率和更好的编解码器，而不仅仅是比特率较高的。此外，你现在可以使用 `-S` 指定排序顺序。这使得格式选择变得比仅使用 `--format` 简单得多 ([示例](#%E6%A0%BC%E5%BC%8F%E9%80%89%E6%8B%A9%E7%A4%BA%E4%BE%8B))。

* **与 animelover1984/youtube-dl 合并**: 你能获得来自 [animelover1984/youtube-dl](https://github.com/animelover1984/youtube-dl) 的大部分功能和改进，包括 `--write-comments` (写入评论), `BiliBiliSearch` (B站搜索), `BilibiliChannel` (B站频道), 将缩略图嵌入 mp4/ogg/opus 中, 播放列表的 infojson 等等。详见 [#31](https://github.com/yt-dlp/yt-dlp/pull/31)。

* **YouTube 的各项改进**:
    * 支持片段 (Clips), 快拍 (Stories) (`ytstories:<channel UCID>`), 搜索（包含过滤器）**\***, YouTube Music 搜索, 频道内搜索, 搜索前缀 (`ytsearch:`)**\***, Mixes(混音列表), 以及各种 Feeds (`:ytfav`, `:ytwatchlater`, `:ytsubs`, `:ythistory`, `:ytrec`, `:ytnotif`)
    * 修复了[基于 n-sig 的限速问题](https://github.com/ytdl-org/youtube-dl/issues/29326) **\***
    * 使用 `--live-from-start` 可以从头开始下载正在进行的直播流 (*实验性功能*)
    * YouTube 频道 URL 现在能下载该频道的所有上传内容，包括短视频 (shorts) 和直播录像 (live)

* **来自浏览器的 Cookies**: 可以使用 `--cookies-from-browser BROWSER[+KEYRING][:PROFILE][::CONTAINER]` 自动从所有主流网络浏览器提取 Cookies。

* **时间范围下载**: 可以使用 `--download-sections` 基于时间戳或章节片段部分地下载视频。

* **按章节拆分视频**: 可以使用 `--split-chapters` 基于章节将视频拆分为多个文件。

* **多线程下载视频片段**: 并行下载 m3u8/mpd 视频的多个片段。使用 `--concurrent-fragments` (`-N`) 选项可设置使用的线程数。

* **全新及被修复的提取器**: 增加了许多新的提取器，也修复了大量现有的提取器。请参阅[更新日志](Changelog.md)或[支持站点列表](supportedsites.md)。

* **新增的有线电视提供商 (MSOs)**: Philo, Spectrum, SlingTV, Cablevision, RCN 等。

* **从清单 (manifest) 提取字幕**: 可以从流媒体的清单文件中提取字幕。详见 [commit/be6202f](https://github.com/yt-dlp/yt-dlp/commit/be6202f12b97858b9d716e608394b51065d0419f)。

* **多个路径和输出模板**: 你可以为不同类型的文件给出不同的[输出模板](#%E8%BE%93%E5%87%BA%E6%A8%A1%E6%9D%BF)和下载路径。你还可以使用 `--paths` (`-P`) 设置保存中间下载文件的临时路径。

* **便携配置**: 将自动从主目录和根目录加载配置文件。有关详细信息，请参阅[配置](#%E9%85%8D%E7%BD%AE)。

* **输出模板的改进**: 输出模板现在可以进行日期时间格式化、数值偏移、对象遍历等操作。有关详细信息，请参阅[输出模板](#%E8%BE%93%E5%87%BA%E6%A8%A1%E6%9D%BF)。甚至可以借助 `--parse-metadata` 和 `--replace-in-metadata` 执行更高级的操作。

* **其他新选项**: 添加了许多新选项，例如 `--alias`, `--print`, `--concat-playlist`, `--wait-for-video`, `--retry-sleep`, `--sleep-requests`, `--convert-thumbnails`, `--force-download-archive`, `--force-overwrites`, `--break-match-filters` 等等。

* **各项改进**: `--format`/`--match-filters` 中加入了正则表达式和其他运算符，支持多个 `--postprocessor-args` 和 `--downloader-args`，更快的归档 (archive) 检查，更多[格式选择选项](#%E6%A0%BC%E5%BC%8F%E9%80%89%E6%8B%A9)，合并多条视频/音频流，多个 `--config-locations`，在不同阶段执行 `--exec` 等。

* **插件**: 可以从外部文件加载提取器和后期处理器。详情见[插件](#%E6%8F%92%E4%BB%B6)。

* **自我更新器**: 可以使用 `yt-dlp -U` 更新程序发布版本，需要的话也能用 `--update-to` 降级。

* **自动构建**: 通过 `--update-to nightly` 和 `--update-to master` 可使用 [Nightly(每日)/master(主分支) 构建版](#update-channels)。

有关所有变更的完整列表，请参阅[更新日志](Changelog.md)或[提交记录](https://github.com/yt-dlp/yt-dlp/commits)。

带有 **\*** 标记的功能已被向后移植 (back-ported) 到 youtube-dl 中。

### 默认行为的区别

yt-dlp 的某些默认选项不同于 youtube-dl 和 youtube-dlc：

* yt-dlp 目前仅支持 [Python 3.10+](## "Windows 8")，并且随着更低版本 Python [进入 EOL 阶段](https://devguide.python.org/versions/#python-release-cycle) 将移除对它们的支持；而 [youtube-dl 仍支持 Python 2.6+ 和 3.2+](https://github.com/ytdl-org/youtube-dl/issues/30568#issue-1118238743)。
* 选项 `--auto-number` (`-A`)、`--title` (`-t`) 和 `--literal` (`-l`) 已不再生效。详见[已移除选项](#%E5%B7%B2%E7%A7%BB%E9%99%A4)。
* 不再支持 `avconv` 作为 `ffmpeg` 的替代品。
* yt-dlp 存储配置文件的位置与 youtube-dl 略有不同。正确位置的列表见[配置](#%E9%85%8D%E7%BD%AE)。
* 默认的[输出模板](#%E8%BE%93%E5%87%BA%E6%A8%A1%E6%9D%BF)现在是 `%(title)s [%(id)s].%(ext)s`。这一改变并没有任何特别原因，且早在 yt-dlp 公开之前就已更改，目前没有计划改回 `%(title)s-%(id)s.%(ext)s`。如果你需要，可以使用 `--compat-options filename`。
* 默认的[格式排序](#%E6%8E%92%E5%BA%8F%E6%A0%BC%E5%BC%8F)与 youtube-dl 不同，其优先考虑更高的分辨率和更好的编解码器，而不是单纯的更高比特率。你可以使用 `--format-sort` 选项更改为你偏好的任何顺序，或者使用 `--compat-options format-sort` 恢复 youtube-dl 的排序顺序。早期版本的 yt-dlp 由于兼容性广泛而优先考虑 VP9；你可以使用 `--compat-options prefer-vp9-sort` 恢复这种偏好。这两个兼容选项不能同时使用。
* 默认格式选择器为 `bv*+ba/b`。这意味着如果发现某个结合了音视频的单一文件其画质优于最佳的纯视频格式，那么将优先选用该单一文件格式。使用 `-f bv+ba/b` 或 `--compat-options format-spec` 可将其恢复。
* 与 youtube-dlc 不同，yt-dlp 默认不允许将多条音频/视频流合并到一个文件中（因为这与使用 `-f bv*+ba` 冲突）。如果需要此功能，必须通过 `--audio-multistreams` 和 `--video-multistreams` 启用。你也可以使用 `--compat-options multistreams` 来同时启用它们。
* 默认启用了 `--no-abort-on-error` (不遇到错误就中止)。使用 `--abort-on-error` 或 `--compat-options abort-on-error` 可以在遇到错误时中止。
* 当写入诸如缩略图、描述或 infojson 等元数据文件时，播放列表也会写入相同的信息（如果可用）。使用 `--no-write-playlist-metafiles` 或 `--compat-options no-playlist-metafiles` 来阻止写入这些文件。
* 当与 `--write-info-json` 一起使用时，`--add-metadata` 会除了将元数据写入外，还会把 `infojson` 附加到 `mkv` 文件。使用 `--no-embed-info-json` 或 `--compat-options no-attach-info-json` 还原这一行为。
* 与 youtube-dl 相比，使用 `--add-metadata` 时有些元数据会被嵌入不同的字段中。最明显的是，`comment` 字段会包含 `webpage_url`，而 `synopsis` 则包含 `description`。你可以[使用 `--parse-metadata`](#%E4%BF%AE%E6%94%B9%E5%85%83%E6%95%B0%E6%8D%AE) 按你喜欢的模式修改，或者使用 `--compat-options embed-metadata` 还原。
* `playlist_index` 与诸如 `--playlist-reverse` 和 `--playlist-items` 等选项同时使用时，其行为有所不同。详情见 [#302](https://github.com/yt-dlp/yt-dlp/issues/302)。如果你希望保留以前的行为，可以使用 `--compat-options playlist-index`。
* `-F` 的输出现在以新的格式列出。使用 `--compat-options list-formats` 还原。
* 如果有的话，实时聊天(Live chats, 弹幕)也会被视作字幕。使用 `--sub-langs all,-live_chat` 可以下载除实时聊天之外的所有字幕。你也可以使用 `--compat-options no-live-chat` 来阻止下载任何实时聊天/弹幕。
* YouTube 频道 URL 现在会下载该频道的所有上传视频。若只下载特定选项卡 (tab) 中的视频，请传递该选项卡的 URL。如果频道没有提供所请求的选项卡，将会抛出错误。另外，如果没有处于直播中的视频，`/live` URL 将会报错，而不是静默下载整个频道的视频。你可以使用 `--compat-options no-youtube-channel-redirect` 还原所有这些重定向。
* YouTube 播放列表现在也会列出不可用的视频。使用 `--compat-options no-youtube-unavailable-videos` 移除它们。
* 从 YouTube 提取的上传日期现在基于 UTC。
* 如果使用了 `ffmpeg` 作为下载器，并且条件允许，下载和合并格式的动作将在同一操作中一步完成。使用 `--compat-options no-direct-merge` 还原。
* 只要可能，将缩略图嵌入到 `mp4` 中会由 mutagen 完成。使用 `--compat-options embed-thumbnail-atomicparsley` 可强制使用 AtomicParsley。
* 某些内部元数据（例如文件名）现在默认会从 infojson 中移除。使用 `--no-clean-infojson` 或 `--compat-options no-clean-infojson` 还原。
* 当同时使用 `--embed-subs` 和 `--write-subs` 时，字幕会被写入到磁盘，同时也会嵌入媒体文件中。你只需使用 `--embed-subs` 即可嵌入字幕并自动删除独立存放的字幕文件。详情见 [#630 (comment)](https://github.com/yt-dlp/yt-dlp/issues/630#issuecomment-893659460)。可以使用 `--compat-options no-keep-subs` 还原。
* 若已安装 `certifi`，则将其用于 SSL 根证书。如果你想使用系统证书（例如自签名的证书），使用 `--compat-options no-certifi`。
* yt-dlp 清理文件名中无效字符的方式不同于且优于 youtube-dl。你可以使用 `--compat-options filename-sanitization` 还原回 youtube-dl 的行为。
* (目前尚未实现) ~~yt-dlp 在可能的情况下会尝试将外部下载器的输出解析为标准进度输出。你可以使用 `--compat-options no-external-downloader-progress` 原样保留下载器的原始输出。~~
* yt-dlp 在 2021.09.01 到 2022.11.11（含）期间的版本，会将 `--match-filters` 运用到嵌套的播放列表中。这是 [8f18ac](https://github.com/yt-dlp/yt-dlp/commit/8f18aca8717bb0dd49054555af8d386e5eda3a88) 所引起的一个无意副作用，并于 [d7b460](https://github.com/yt-dlp/yt-dlp/commit/d7b460d0e5fc710950582baed2e3fc616ed98a80) 得到修复。使用 `--compat-options playlist-match-filter` 可还原。
* yt-dlp 在 2021.11.10 到 2023.06.21（含）期间的版本，会针对片段化/清单(manifest)格式估计 `filesize_approx` 的值。为了方便起见，这在 [f2fe69](https://github.com/yt-dlp/yt-dlp/commit/f2fe69c7b0d208bdb1f6292b4ae92bc1e1a7444a) 被加入，但是由于估算出的值可能极端不准确，在 [0dff8e](https://github.com/yt-dlp/yt-dlp/commit/0dff8e4d1e6e9fb938f4256ea9af7d81f42fd54f) 又被回滚了。使用 `--compat-options manifest-filesize-approx` 可以保留提取该估算值的行为。
* yt-dlp 采用更为现代的 http 客户端后端（例如 `requests`）。使用 `--compat-options prefer-legacy-http-handler` 以偏好使用旧版的 http 处理器 (`urllib`) 执行标准 http 请求。
* 子模块 `swfinterp`, `casefold` 已被移除。
* 传递 `--simulate` (或以 `download=False` 参数调用 `extract_info`) 不再会更改默认格式选择。详情请见 [#9843](https://github.com/yt-dlp/yt-dlp/issues/9843)。
* yt-dlp 默认不再将服务器的修改时间应用到下载的文件上。使用 `--mtime` 或 `--compat-options mtime-by-default` 还原。

为了方便起见，可以使用一些兼容选项的别名：

* `--compat-options all`: 使用所有的兼容选项（**切勿使用这个！**）
* `--compat-options youtube-dl`: 等同于 `--compat-options all,-multistreams,-playlist-match-filter,-manifest-filesize-approx,-allow-unsafe-ext,-prefer-vp9-sort,-allow-unsafe-exec-expansion`
* `--compat-options youtube-dlc`: 等同于 `--compat-options all,-no-live-chat,-no-youtube-channel-redirect,-playlist-match-filter,-manifest-filesize-approx,-allow-unsafe-ext,-prefer-vp9-sort,-allow-unsafe-exec-expansion`
* `--compat-options 2021`: 等同于 `--compat-options 2022,no-certifi,filename-sanitization`
* `--compat-options 2022`: 等同于 `--compat-options 2023,playlist-match-filter,no-external-downloader-progress,prefer-legacy-http-handler,manifest-filesize-approx`
* `--compat-options 2023`: 等同于 `--compat-options 2024,prefer-vp9-sort`
* `--compat-options 2024`: 等同于 `--compat-options 2025,mtime-by-default`
* `--compat-options 2025`: 目前不作任何操作。可使用它来启用所有的未来兼容选项。

使用上面某一年的兼容选项别名，将会把 yt-dlp 的默认行为锚定 (pin) 为对应年份*年底*的状态。

以下兼容选项会恢复到应用安全补丁之前存在漏洞的旧有行为：

* `--compat-options allow-unsafe-ext`: 允许下载带有任何扩展名的文件（包括不安全的文件） ([GHSA-79w7-vh3h-8g4j](<https://github.com/yt-dlp/yt-dlp/security/advisories/GHSA-79w7-vh3h-8g4j>))

    > :warning: 只有当确定一个有效的文件下载是因为其扩展名被检测为不常见而被拒绝时，才可使用。
    >
    > **此选项可能会启用远程代码执行！** 请考虑改为[提交一个 Issue](<https://github.com/yt-dlp/yt-dlp/issues/new/choose>)！

* `--compat-options allow-unsafe-exec-expansion`: `--exec` 选项允许在其命令中使用输出模板语法；然而，为了安全考量，可以使用的转换被限制在 `i`/`d` (带符号的十进制整数)，`f` (十进制浮点数) 及 `q` (经过 shell 转义的内容)。yt-dlp 在 2021.04.11 到 2026.03.17（含）期间的版本并未应用这一限制。本选项可用于取消此限制

    > :warning: **此选项可能会启用远程代码执行！** 考虑在你的 exec 命令模板中，将 `%()q` 转换应用于任何字符串值。


### 已弃用的选项

这些都是已被弃用的选项，以及用来达到相同效果的现有替代方案。

#### 几乎冗余的选项
虽然这些选项与其新的对应部分几乎相同，但某些差异使得它们并非完全多余

    -j, --dump-json                  --print "%()j"
    -F, --list-formats               --print formats_table
    --list-thumbnails                --print thumbnails_table --print playlist:thumbnails_table
    --list-subs                      --print automatic_captions_table --print subtitles_table

#### 冗余选项
虽然这些选项确实是多余的，但由于其易用性，仍期望保留它们

    --get-description                --print description
    --get-duration                   --print duration_string
    --get-filename                   --print filename
    --get-format                     --print format
    --get-id                         --print id
    --get-thumbnail                  --print thumbnail
    -e, --get-title                  --print title
    -g, --get-url                    --print urls
    --match-title REGEX              --match-filters "title ~= (?i)REGEX"
    --reject-title REGEX             --match-filters "title !~= (?i)REGEX"
    --min-views COUNT                --match-filters "view_count >=? COUNT"
    --max-views COUNT                --match-filters "view_count <=? COUNT"
    --break-on-reject                使用 --break-match-filters
    --user-agent UA                  --add-headers "User-Agent:UA"
    --referer URL                    --add-headers "Referer:URL"
    --playlist-start NUMBER          -I NUMBER:
    --playlist-end NUMBER            -I :NUMBER
    --playlist-reverse               -I ::-1
    --no-playlist-reverse            默认值
    --no-colors                      --color no_color

#### 不推荐的选项
虽然这些选项仍然有效，但不推荐使用它们，因为已经有了实现相同目标的其它替代选项

    --force-generic-extractor        --ies generic,default
    --exec-before-download CMD       --exec "before_dl:CMD"
    --no-exec-before-download        --no-exec
    --all-formats                    -f all
    --all-subs                       --sub-langs all --write-subs
    --print-json                     -j --no-simulate
    --autonumber-size NUMBER         使用字符串格式化，例如 %(autonumber)03d
    --autonumber-start NUMBER        使用内部字段格式化，例如 %(autonumber+NUMBER)s
    --id                             -o "%(id)s.%(ext)s"
    --metadata-from-title FORMAT     --parse-metadata "%(title)s:FORMAT"
    --hls-prefer-native              --downloader "m3u8:native"
    --hls-prefer-ffmpeg              --downloader "m3u8:ffmpeg"
    --list-formats-old               --compat-options list-formats (别名: --no-list-formats-as-table)
    --list-formats-as-table          --compat-options -list-formats [默认值]
    --geo-bypass                     --xff "default"
    --no-geo-bypass                  --xff "never"
    --geo-bypass-country CODE        --xff CODE
    --geo-bypass-ip-block IP_BLOCK   --xff IP_BLOCK

#### 开发者选项
这些选项不意在供最终用户使用

    --test                           仅下载视频的一部分以测试提取器
    --load-pages                     加载由 --write-pages 转储生成的页面
    --allow-unplayable-formats       同时列出不可播放的格式
    --no-allow-unplayable-formats    默认行为

#### 曾用别名
以下是由于各种原因不再记录在文档中的别名

    --clean-infojson                 --clean-info-json
    --force-write-download-archive   --force-write-archive
    --no-clean-infojson              --no-clean-info-json
    --no-split-tracks                --no-split-chapters
    --no-write-srt                   --no-write-subs
    --prefer-unsecure                --prefer-insecure
    --rate-limit RATE                --limit-rate RATE
    --split-tracks                   --split-chapters
    --srt-lang LANGS                 --sub-langs LANGS
    --trim-file-names LENGTH         --trim-filenames LENGTH
    --write-srt                      --write-subs
    --yes-overwrites                 --force-overwrites

#### Sponskrub 选项
为了使用 `--sponsorblock` 选项，对 [SponSkrub](https://github.com/faissaloo/SponSkrub) 的支持已被移除

    --sponskrub                      --sponsorblock-mark all
    --no-sponskrub                   --no-sponsorblock
    --sponskrub-cut                  --sponsorblock-remove all
    --no-sponskrub-cut               --sponsorblock-remove -all
    --sponskrub-force                不适用
    --no-sponskrub-force             不适用
    --sponskrub-location             不适用
    --sponskrub-args                 不适用

#### 不再受支持的选项
这些选项可能不再按预期运行

    --prefer-avconv                  yt-dlp 已不再官方支持 avconv (别名: --no-prefer-ffmpeg)
    --prefer-ffmpeg                  默认行为 (别名: --no-prefer-avconv)
    -C, --call-home                  尚未实现
    --no-call-home                   默认行为
    --include-ads                    不再受支持
    --no-include-ads                 默认行为
    --write-annotations              如今已没有任何受支持的网站保留标注 (annotations) 功能了
    --no-write-annotations           默认行为
    --avconv-location                此 --ffmpeg-location 别名已被移除
    --cn-verification-proxy URL      此 --geo-verification-proxy URL 别名已被移除
    --dump-headers                   此 --print-traffic 别名已被移除
    --dump-intermediate-pages        此 --dump-pages 别名已被移除
    --youtube-skip-dash-manifest     此 --extractor-args "youtube:skip=dash" 的别名已被移除 (别名: --no-youtube-include-dash-manifest)
    --youtube-skip-hls-manifest      此 --extractor-args "youtube:skip=hls" 的别名已被移除 (别名: --no-youtube-include-hls-manifest)
    --youtube-include-dash-manifest  默认行为 (别名: --no-youtube-skip-dash-manifest)
    --youtube-include-hls-manifest   默认行为 (别名: --no-youtube-skip-hls-manifest)
    --youtube-print-sig-code         移除了此项用于测试的功能
    --dump-user-agent                不再受支持
    --xattr-set-filesize             不再受支持
    --compat-options seperate-video-versions  已不再需要
    --compat-options no-youtube-prefer-utc-upload-date  不再受支持

#### 已移除选项
这些选项自 2014 年起就被弃用，现在已被完全移除

    -A, --auto-number                -o "%(autonumber)s-%(id)s.%(ext)s"
    -t, -l, --title, --literal       -o "%(title)s-%(id)s.%(ext)s"


# 参与贡献 (CONTRIBUTING)
有关如何[提交问题 (Opening an Issue)](CONTRIBUTING.md#opening-an-issue)以及向项目[贡献代码](CONTRIBUTING.md#developer-instructions)的说明，请参阅 [CONTRIBUTING.md](CONTRIBUTING.md#contributing-to-yt-dlp)。

# WIKI
有关更多信息，请参阅本项目的 [Wiki](https://github.com/yt-dlp/yt-dlp/wiki) 页面。
