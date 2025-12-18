# DeskPet 桌面宠物

一个基于 Python3.9 和 PySide6 的桌面宠物应用，支持 AI 对话功能。

## 功能特性

- **桌面宠物** - 透明无边框窗口，可拖拽移动
- **AI 对话** - 支持接入大语言模型 API（OpenAI 兼容格式）
- **双模式对话**
  - 对话框模式：传统聊天窗口
  - 字幕模式：宠物旁边显示气泡字幕，更沉浸
- **系统托盘** - 最小化到托盘，随时唤出
- **个性化设置** - 自定义宠物名字、图片、模型配置

## 安装使用

### 1. 克隆项目

```bash
git clone https://github.com/chen6-gif/DeskPet.git
cd DeskPet
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行程序

```bash
python app.py
```

## 配置说明

首次运行后，右键托盘图标 → 设置，配置以下内容：

| 配置项 | 说明 |
|--------|------|
| 宠物名字 | 显示在对话中的名称 |
| 宠物图片 | 支持 PNG 透明图片 |
| API URL | LLM API 地址（OpenAI 兼容格式） |
| API Key | 你的 API 密钥 |
| 模型 | 模型名称 |

### 支持的 API

支持所有 OpenAI 兼容格式的 API：

- 腾讯混元：`https://api.hunyuan.cloud.tencent.com/v1`
- DeepSeek：`https://api.deepseek.com/v1`
- 智谱 AI：`https://open.bigmodel.cn/api/paas/v4`
- 各种中转 API

## 使用方法

| 操作 | 功能 |
|------|------|
| 双击宠物 | 打开对话 |
| 右键宠物 | 显示菜单 |
| 拖拽宠物 | 移动位置 |
| 右键托盘 | 显示/隐藏/设置/退出 |

## 后续计划

- [ ] 动画系统（多帧动画、状态切换）
- [ ] 插件系统（计时器、闹钟、天气等）
- [ ] 语音合成（TTS）
- [ ] 更多交互动作

## 技术栈

- Python 3.8+
- PySide6（Qt for Python）
- Requests（HTTP 请求）

## 许可证

MIT License
