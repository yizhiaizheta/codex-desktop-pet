# Linux 安装与本次修改

本仓库基于 [bailong-desktop-pet](https://github.com/jingh12312-rgb/bailong-desktop-pet) 的 v0.5.1 源码（b102e73）整理，保留上游说明与素材约束。

## 安装（Ubuntu / X11）

```bash
sudo apt install python3-venv ffmpeg libxcb-cursor0
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

动画素材不纳入Git。请从[上游 v0.5.1 发布包](https://github.com/jingh12312-rgb/bailong-desktop-pet/releases/tag/v0.5.1)提取整个 `outputs` 文件夹放到本仓库根目录，保留35段透明WebM及素材清单。Linux使用系统FFmpeg，不要复制发布包中的Windows工具。素材权利说明见 [ASSETS.md](ASSETS.md)。

```bash
./启动白龙桌宠.sh
```

单击互动、按住拖动、双击查询Codex额度、右键设置。通过本机已有Codex登录使用额度/对话功能。程序优先使用`BAILONG_CODEX`环境变量或本机`/usr/lib/chatgpt/resources/codex`。没有附带账号或登录状态。

## 修复内容

- 修复中文多行气泡裁切，按照实际宽度计算布局高度。
- 任务消息取消内嵌滚动条，文字增加时聊天气泡自动增高，缩短时也能回缩。
- 默认轻度清理动画透明边缘，减少外围杂点，保留高不透明度发丝和翼缘；RGB和原始视频不改变。
- 缓存记录透明清理模式，避免读取旧缓存。

退出桌宠后使用 `BAILONG_ALPHA_CLEANUP=0 ./启动白龙桌宠.sh` 可以临时关闭边缘清理。设置和日志在被Git忽略的`linux-state/`目录。

## 验证和限制

```bash
cd app
QT_QPA_PLATFORM=offscreen ../.venv/bin/python -m unittest test_bubble_layout test_video_alpha_cleanup test_task_notifications -v
```

新增气泡及透明度测试已在Qt 6.9.2 / FFmpeg 4.4环境通过。透明处理还完成35段原始动画、4426帧对比：RGB及高不透明度区域保持一致。

Linux尚未实现Windows音效、全屏检测及自动启动。上游完整测试中的`test_sound_mute_and_menu_options`依赖Windows的winsound，`test_click_disambiguation`受Qt粗粒度定时器影响；不是本次新增功能的通过声明。
