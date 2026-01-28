<img width="1002" height="954" alt="image" src="https://github.com/user-attachments/assets/e460c9bb-6d7e-4260-b13e-bda3d65ce935" />

# Rclone-Smart-Helper 🚀

**一个专为 Windows 环境优化的轻量级 Rclone 智能图形化管理助手。**

---

## 🌟 项目简介

本项目是一个基于 Python Tkinter 开发的 Rclone GUI 助手。

### 为什么需要它？
在 Windows 环境下，直接使用 Rclone 命令行对新手不友好，且市面上现有的 GUI 工具往往体积庞大或兼容性欠佳。本助手针对以下痛点设计：
- **极简兼容性**：专为 **Windows 10 x64** 环境下的 **32 位 Python** 兼容性优化，不依赖复杂的主题库，确保 100% 启动。
- **参数解耦**：解决了初学者容易混淆“挂载参数”与“同步参数”的互斥报错问题。
- **安全第一**：为所有危险指令增加了物理层面的保护锁。

---

## ✨ 核心特性

- **🧠 智能参数过滤**
  自动识别指令逻辑。例如：在执行 `Sync` 或 `Lsf` 时，程序会自动剔除不兼容的挂载参数（如 `--vfs-cache-mode`），避免内核由于 `unknown flag` 报错退出。

- **🛡️ 危险指令锁**
  针对 `Purge`（粉碎）、`Delete`（删除）、`Dedupe`（去重）及 `Move`（移动）等高危指令，内置二次确认确认机制，降低误操作风险。

- **🚥 多任务并行架构**
  - **即时任务**（同步、列表、校验、树状结构）：在助手内置日志框中实时滚动显示进度。
  - **持久服务**（挂载 Z 盘、WebDav/HTTP 服务）：一键唤起独立后台窗口，确保助手主程序关闭后，挂载服务依然在线。

- **⚡ 进程强杀**
  支持一键终止当前运行的任务进程树，快速响应，无残留进程。

---

## 🚀 快速开始

### 1. 准备环境
- 下载并安装 [Rclone 内核](https://rclone.org/downloads/)（推荐 `rclone-win7-64.exe`）。
- 确保您的 Windows 环境已安装 Python (若直接运行生成的 `.exe` 则无需安装)。

### 2. 部署运行
1. 将本助手的 `rc.py`（或打包后的 `Rclone助手.exe`）放入 Rclone 内核所在的文件夹。
2. 双击运行程序。
3. 在界面中配置您的 **Source** (源) 和 **Dest** (目的) 路径。
4. 点击对应的功能按钮即可开始执行。

> **目录结构示例：**
> ```text
> 📂 Rclone-Tools
>  ┣ 📜 rclone-win7-64.exe  (内核)
>  ┗ 📜 Rclone助手.exe      (本项目助手)
> ```

---

## 📦 打包指南

如果您修改了代码并希望重新生成 `.exe` 文件，请使用 PyInstaller：

```bash
# 安装打包工具
pip install pyinstaller

# 执行打包命令 (隐藏控制台窗口)
pyinstaller -F -w --clean --name "Rclone助手" rc.py
