# 英语音标学习网站

一个帮助用户学习英语音标的互动网站，支持鼠标悬停自动播放发音，双击查看详情。

## 功能特点

- 分类展示所有48个英语音标（元音和辅音）
- 鼠标悬停在音标按钮上自动播放对应的音频
- 双击音标按钮跳转到详细的音标学习页面
- 响应式设计，适配各种屏幕尺寸
- 美观的UI界面和流畅的动画效果
- 显示每个音标对应的示例单词，并支持单词发音播放

## 目录结构

```
├── index.html       # 主页面文件
├── auto_download.py # 音标音频视频自动下载脚本
├── extract_words.py # 音标对应单词提取和下载脚本
├── phonetic_words.json # 音标与单词映射关系文件
├── audio/           # 存储音标音频文件（需手动添加或使用脚本下载）
├── video/           # 存储音标视频文件（需手动添加或使用脚本下载）
├── words-voice/     # 存储单词发音文件（使用extract_words.py脚本下载）
└── .gitignore       # Git忽略文件配置
```

## 如何使用

1. 克隆或下载本项目到本地

2. 下载音标音频文件并放入`audio/`目录
   - 音频文件命名格式：`phonetic-{id}.mp3`（例如 `phonetic-1.mp3` 对应 `/i:/` 音标）
   - 您可以从 [英语音标网](https://www.yyybabc.com/) 下载相应的音频文件

3. （可选）下载音标视频文件并放入`video/`目录

4. （可选）运行单词提取脚本下载单词发音文件：
   ```bash
   python extract_words.py
   ```

5. 在浏览器中打开`index.html`文件开始使用

## 自动下载脚本说明

### 音标音视频自动下载脚本 (auto_download.py)

此脚本会自动访问英语音标网站，提取并下载所有48个音标的音频和视频文件。

使用方法：
```bash
python auto_download.py
```

脚本功能：
- 自动创建 `audio` 和 `video` 目录
- 从网站提取并下载所有48个音标的音频和视频文件
- 显示下载进度和统计信息
- 记录日志到 `download.log` 文件

### 单词提取和下载脚本 (extract_words.py)

此脚本会自动访问英语音标网站，从d1.html到d48.html提取单词信息并下载相关单词发音到words-voice目录。

使用方法：
```bash
python extract_words.py
```

脚本功能：
- 自动创建 `words-voice` 目录
- 从每个音标页面提取示例单词
- 下载单词发音文件
- 生成 phonetic_words.json 文件，用于前端显示单词信息
- 显示处理进度和统计信息
- 记录日志到 `extract_words.log` 文件

## 本地开发

您可以使用任何Web服务器来预览网站，例如使用Python的内置HTTP服务器：

```bash
python3 -m http.server 8000
```

然后在浏览器中访问 `http://localhost:8000`

## 技术栈

- HTML5
- Tailwind CSS v3
- Font Awesome
- JavaScript

## 注意事项

- 由于浏览器的自动播放政策限制，首次悬停可能需要用户交互才能播放音频
- 请确保您已正确下载并放置了所有需要的音频文件
- 如需自定义样式，可以修改index.html中的Tailwind配置

## 版权信息

本项目仅用于学习目的，音标内容版权归原网站所有。