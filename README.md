# AIChat - AI 聊天助手

一个简单易用的基于 DeepSeek API 的 AI 聊天助手，支持对话历史管理和记忆压缩归档。

## ✨ 功能特点

- 🤖 基于 DeepSeek API 的智能对话
- 💾 本地保存对话历史，支持历史回顾
- 📦 智能记忆压缩，避免历史无限增长
- 🔄 自动归档和二次总结，提升效率
- 👤 自定义用户和AI名字，更个性化

## 🚀 快速开始

### 一键启动（推荐）

直接双击 `start.bat` 文件即可启动，首次运行会自动安装依赖。

### 手动启动

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python aichat.py
```

### 配置 API Key

1. 在 `.env` 中填入你的 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=你的API密钥
DEEPSEEK_MODEL=deepseek-v4-pro
```

你可以从 [DeepSeek 开放平台](https://platform.deepseek.com/) 获取 API 密钥。

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `aichat.py` | 主程序文件 |
| `chat_history.json` | 对话历史文件 |
| `chat_archive.json` | 归档总结文件 |
| `user.json` | 用户配置文件 |
| `.env` | 环境配置文件 |

## 🎯 记忆机制

- **主历史**：最多保留 20 条消息
- **归档区**：超出部分会自动归档
- **智能总结**：归档满 10 条原始消息后进行总结
- **二次压缩**：归档满 10 条总结后进行二次总结

## 🔧 自定义配置

在 `aichat.py` 和 `.env` 中可以修改：

```python
MAX_MESSAGES = 20  # 主历史最多消息数
ARCHIVE_MAX_SUMMARIES = 10  # 归档总结数
```

在 `.env` 中可以配置：

```env
DEEPSEEK_API_KEY=你的API密钥
DEEPSEEK_MODEL=deepseek-v4-pro  # 可选：deepseek-v4-pro, deepseek-v4-flash
```

你也可以修改 `system_message` 来改变 AI 的性格和说话风格。

## 📄 许可证

本项目采用 **MIT 许可证** - 详见 [LICENSE](./LICENSE) 文件。

## 📝 更新日志

详见 [CHANGELOG.md](./CHANGELOG.md)

## 💡 常见问题

**Q: API调用失败？**
A: 检查 `.env` 文件中的 API Key 是否正确配置。

**Q: 历史记录丢失？**
A: 不要手动删除 `chat_history.json` 和 `chat_archive.json` 文件。

**Q: 可以修改AI名字吗？**
A: 可以删除 `user.json` 重新运行程序，或者手动编辑该文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

享受与 AI 聊天吧！✨
