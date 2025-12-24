# Good-GYM Home Assistant Addon Changelog

## [2.0.0] - 2025-12-24

### Added - Home Assistant Addon 首次发布
- ✨ RTSP 摄像头支持
- ✨ MQTT 实时推送到 Home Assistant
- ✨ Home Assistant MQTT Discovery 自动配置
- ✨ 无头服务模式（移除 PyQt5 GUI）
- ✨ Docker 容器化部署
- ✨ 多架构支持 (amd64, aarch64)
- ✨ 自动重连机制 (RTSP & MQTT)
- ✨ 线程化视频处理
- ✨ 配置热重载支持

### Features
- 📹 RTSP 视频流接入
- 🧠 RTMPose 姿态检测 (CPU 模式)
- 🏋️ 10 种运动类型支持
- 📡 MQTT 消息发布
- 🔄 自动重连和错误恢复
- ⚙️ 灵活的配置选项
- 📊 实时状态推送
- 🌐 中英文界面支持

### Documentation
- 📖 完整的用户手册 (README.md)
- 📚 技术文档 (DOCS.md)
- 🚀 快速开始指南 (QUICKSTART.md)
- 💡 配置示例 (dashboard.yaml, automations.yaml)
- 🧪 测试脚本 (test_addon.py)

### Performance
- ⚡ 跳帧处理选项
- 🎯 三种检测模式 (performance/balanced/accuracy)
- 💻 CPU 优化
- 🔧 可调节的检测频率

### Supported Exercises
- Squat (深蹲)
- Push-up (俯卧撑)
- Sit-up (仰卧起坐)
- Bicep Curl (弯举)
- Lateral Raise (侧平举)
- Overhead Press (推举)
- Leg Raise (抬腿)
- Knee Raise (抬膝)
- Knee Press (压膝)
- Crunch (卷腹)

---

## [1.2.0] - 2025-11-15 (Desktop App)

### Added
- 运动类型数据库功能
- `data/exercises.json` 统一配置管理
- 自定义运动类型支持

### Fixed
- 从统计界面切换回检测界面时的闪退问题

---

## [1.1.0] - 2025-11-14 (Desktop App)

### Changed
- 恢复到同步姿态检测（提高准确率）

---

## [1.0.0] - 2025-06-12 (Desktop App)

### Added
- 优化 exercise_counters.py
- 提高计数准确性
- 代码结构优化

---

## [0.9.0] - 2025-06-07 (Desktop App)

### Major Update
- 放弃 YOLO 模型和所有 GPU 支持
- 采用 RTMPose 进行姿态检测
- 支持 CPU 运行
- 简化依赖和安装

---

## Migration Notes (1.x → 2.0)

### Breaking Changes
- ❌ 移除 PyQt5 GUI (改为 Home Assistant 界面)
- ❌ 移除本地统计存储 (使用 HA 历史记录)
- ❌ 需要 MQTT broker
- ❌ 需要 RTSP 摄像头 (不再支持本地摄像头直接访问)

### Migration Steps
1. 在 Home Assistant 中安装 MQTT broker (Mosquitto)
2. 配置摄像头支持 RTSP 输出
3. 安装 Good-GYM Addon
4. 配置 RTSP URL 和 MQTT 设置
5. 在仪表板中添加传感器卡片

---

## Roadmap

### v2.1.0 (计划中)
- [ ] REST API 接口
- [ ] 多摄像头支持
- [ ] 自定义 MQTT 消息格式
- [ ] GPU 加速选项
- [ ] 录像功能

### v2.2.0 (计划中)
- [ ] WebRTC 支持
- [ ] 实时视频预览
- [ ] 动作准确性评分
- [ ] 语音反馈

### v3.0.0 (未来)
- [ ] 移动应用集成
- [ ] 云端同步
- [ ] 社交功能
- [ ] AI 教练建议

---

## Contributors
- [@yo-WASSUP](https://github.com/yo-WASSUP) - Original desktop app
- Community contributors

## License
MIT License - See LICENSE file for details
