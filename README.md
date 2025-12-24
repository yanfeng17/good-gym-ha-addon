# 🏋️ Good-GYM Home Assistant Addon

[![GitHub](https://img.shields.io/github/license/yo-WASSUP/Good-GYM)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-blue)](CHANGELOG.md)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-green)](https://www.home-assistant.io/)

**AI-powered exercise tracker with RTMPose pose detection**

Transform your Home Assistant into a smart fitness tracker using RTSP cameras and real-time pose detection!

---

## 📋 目录 Table of Contents

- [功能特点 Features](#-功能特点-features)
- [快速开始 Quick Start](#-快速开始-quick-start)
- [架构说明 Architecture](#-架构说明-architecture)
- [文件说明 Files](#-文件说明-files)
- [配置选项 Configuration](#-配置选项-configuration)
- [示例 Examples](#-示例-examples)
- [常见问题 FAQ](#-常见问题-faq)
- [贡献 Contributing](#-贡献-contributing)
- [许可证 License](#-许可证-license)

---

## ✨ 功能特点 Features

### 🎯 核心功能
- ✅ **RTSP 摄像头支持** - 接入任何网络摄像头
- ✅ **MQTT 实时推送** - 无缝集成 Home Assistant
- ✅ **RTMPose AI 检测** - 高精度姿态检测
- ✅ **10+ 运动类型** - 深蹲、俯卧撑、仰卧起坐等
- ✅ **自动发现** - MQTT Discovery 自动创建传感器
- ✅ **CPU 运行** - 无需 GPU

### 🔧 技术特性
- 🐳 Docker 容器化部署
- 🔄 自动重连机制
- 🧵 多线程视频处理
- ⚙️ 灵活配置选项
- 🌐 中英文支持
- 📊 实时状态监控

### 🏗️ 支持的架构
- `amd64` (x86_64)
- `aarch64` (ARM 64-bit, Raspberry Pi 4)

---

## 🚀 快速开始 Quick Start

### 前置要求

1. **Home Assistant** - 已安装并运行
2. **MQTT Broker** - 推荐 Mosquitto addon
3. **RTSP 摄像头** - 任何支持 RTSP 的摄像头

### 安装步骤

#### 方法 1: 通过 GitHub 仓库

```bash
# 1. 在 Home Assistant 中添加仓库
Supervisor > Add-on Store > ⋮ > Repositories
添加: https://github.com/your-username/good-gym-addon

# 2. 刷新页面并安装 Good-GYM

# 3. 配置选项
rtsp_url: "rtsp://192.168.1.100:554/stream"
mqtt_host: "core-mosquitto"
exercise_type: "squat"

# 4. 启动 Addon
```

#### 方法 2: 本地测试 (开发)

```bash
# 克隆项目
git clone https://github.com/yo-WASSUP/Good-GYM.git
cd Good-GYM

# 安装依赖
pip install -r homeassistant/requirements.txt

# 配置环境变量
export RTSP_URL="rtsp://your_camera"
export MQTT_HOST="localhost"
export EXERCISE_TYPE="squat"

# 运行测试
python homeassistant/test_addon.py

# 运行服务
python homeassistant/main.py
```

---

## 🏗️ 架构说明 Architecture

```
┌─────────────────┐
│  RTSP Camera    │
└────────┬────────┘
         │ Video Stream
         ▼
┌─────────────────────────────┐
│   Good-GYM Addon            │
│                             │
│  RTSP → RTMPose → Counter   │
│            ↓                │
│         MQTT Publish        │
└────────┬────────────────────┘
         │ MQTT Messages
         ▼
┌─────────────────────────────┐
│   Home Assistant            │
│   - Sensors                 │
│   - Automations             │
│   - Dashboard               │
└─────────────────────────────┘
```

### 数据流程

1. **视频采集**: RTSPHandler 从摄像头获取视频流
2. **姿态检测**: RTMPoseProcessor 提取人体关键点
3. **运动计数**: ExerciseCounter 计算动作次数
4. **状态推送**: MQTTPublisher 发送数据到 HA
5. **用户交互**: 通过 HA 仪表板查看和自动化

---

## 📁 文件说明 Files

### 核心模块

| 文件 | 说明 |
|------|------|
| `config_manager.py` | 配置管理器 |
| `rtsp_handler.py` | RTSP 视频流处理 |
| `mqtt_publisher.py` | MQTT 消息发布 |
| `main.py` | 主服务入口 |

### 配置文件

| 文件 | 说明 |
|------|------|
| `config.yaml` | Addon 配置定义 |
| `Dockerfile` | Docker 镜像定义 |
| `build.json` | 构建配置 |
| `run.sh` | 启动脚本 |
| `requirements.txt` | Python 依赖 |

### 文档

| 文件 | 说明 |
|------|------|
| `README.md` | 用户手册 (本文件) |
| `DOCS.md` | 技术文档 |
| `QUICKSTART.md` | 快速开始指南 |
| `CHANGELOG.md` | 版本历史 |

### 示例

| 文件 | 说明 |
|------|------|
| `examples/dashboard.yaml` | 仪表板配置示例 |
| `examples/automations.yaml` | 自动化示例 |

### 测试

| 文件 | 说明 |
|------|------|
| `test_addon.py` | 测试脚本 |
| `env.example` | 环境变量示例 |

---

## ⚙️ 配置选项 Configuration

### 基本配置

```yaml
rtsp_url: "rtsp://192.168.1.100:554/stream"  # RTSP 摄像头地址
mqtt_host: "core-mosquitto"                   # MQTT 服务器
mqtt_port: 1883                               # MQTT 端口
exercise_type: "squat"                        # 运动类型
```

### 高级配置

```yaml
rtmpose_mode: "balanced"      # performance/balanced/accuracy
frame_skip: 1                 # 跳帧处理 (1-10)
detection_interval: 0.1       # 检测间隔 (秒)
reconnect_interval: 5         # 重连间隔 (秒)
enable_debug: false           # 启用调试日志
enable_mqtt_discovery: true   # 启用自动发现
```

### 支持的运动类型

| 类型 | 中文 | 英文 |
|------|------|------|
| `squat` | 深蹲 | Squat |
| `pushup` | 俯卧撑 | Push-up |
| `situp` | 仰卧起坐 | Sit-up |
| `bicep_curl` | 弯举 | Bicep Curl |
| `lateral_raise` | 侧平举 | Lateral Raise |
| `overhead_press` | 推举 | Overhead Press |
| `leg_raise` | 抬腿 | Leg Raise |
| `knee_raise` | 抬膝 | Knee Raise |
| `knee_press` | 压膝 | Knee Press |
| `crunch` | 卷腹 | Crunch |

---

## 💡 示例 Examples

### 仪表板卡片

```yaml
type: gauge
entity: sensor.good_gym_squat_counter
min: 0
max: 50
name: 深蹲进度
needle: true
```

### 自动化 - 目标达成通知

```yaml
automation:
  - alias: "健身目标达成"
    trigger:
      - platform: numeric_state
        entity_id: sensor.good_gym_squat_counter
        above: 30
    action:
      - service: notify.mobile_app
        data:
          message: "完成30个深蹲！"
```

### 自动化 - 计数提示音

```yaml
automation:
  - alias: "运动计数提示"
    trigger:
      - platform: state
        entity_id: sensor.good_gym_squat_counter
    action:
      - service: media_player.play_media
        data:
          media_content_id: "/local/sounds/beep.mp3"
```

更多示例查看 [examples/](examples/) 目录。

---

## ❓ 常见问题 FAQ

### Q: 需要 GPU 吗?
**A:** 不需要，RTMPose 可在 CPU 上运行。

### Q: 支持哪些摄像头?
**A:** 任何支持 RTSP 协议的网络摄像头或使用 IP Webcam 等 APP 的手机。

### Q: CPU 占用太高?
**A:** 增加 `frame_skip` 或切换到 `performance` 模式。

### Q: 计数不准确?
**A:** 确保摄像头能看到全身，光线充足，背景简单。

### Q: 可以同时追踪多个摄像头吗?
**A:** 可以安装多个 addon 实例，每个实例对应一个摄像头。

---

## 🤝 贡献 Contributing

欢迎贡献代码！请遵循以下步骤:

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证 License

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](../LICENSE) 文件。

---

## 🙏 致谢 Credits

- **RTMPose**: https://github.com/Tau-J/rtmlib
- **原项目**: https://github.com/yo-WASSUP/Good-GYM
- **Home Assistant 社区**

---

## 📞 支持 Support

- 📧 [GitHub Issues](https://github.com/yo-WASSUP/Good-GYM/issues)
- 💬 [Home Assistant Community](https://community.home-assistant.io/)
- 📖 [完整文档](DOCS.md)

---

## 🗺️ 路线图 Roadmap

- [ ] REST API 接口
- [ ] 多摄像头支持
- [ ] WebRTC 实时预览
- [ ] 动作准确性评分
- [ ] 移动应用集成

查看 [CHANGELOG.md](CHANGELOG.md) 了解更多计划。

---

**Made with ❤️ for Home Assistant Community**

⭐ 如果觉得有用，请给项目点个星！
