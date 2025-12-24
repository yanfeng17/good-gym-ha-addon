# Good-GYM Home Assistant Addon - 快速开始指南

## 🎯 5分钟快速上手

### 前置条件

```bash
# 1. 确保已安装 Python 3.9+
python --version

# 2. 确保有 MQTT broker (本地测试可用 Mosquitto)
# 3. 准备一个 RTSP 摄像头 URL (或使用测试视频)
```

### 本地测试 (推荐新手)

#### 步骤 1: 安装依赖

```bash
cd Good-GYM
pip install -r homeassistant/requirements.txt
```

#### 步骤 2: 配置环境变量

Windows (PowerShell):
```powershell
$env:RTSP_URL="rtsp://192.168.1.100:554/stream"
$env:MQTT_HOST="localhost"
$env:MQTT_PORT="1883"
$env:EXERCISE_TYPE="squat"
$env:RTMPOSE_MODE="balanced"
```

Linux/Mac (Bash):
```bash
export RTSP_URL="rtsp://192.168.1.100:554/stream"
export MQTT_HOST="localhost"
export MQTT_PORT="1883"
export EXERCISE_TYPE="squat"
export RTMPOSE_MODE="balanced"
```

#### 步骤 3: 运行测试

```bash
# 测试各组件
python homeassistant/test_addon.py

# 如果测试通过,运行完整服务
python homeassistant/main.py
```

#### 步骤 4: 验证 MQTT 消息

在另一个终端窗口:
```bash
# 订阅 MQTT 主题
mosquitto_sub -h localhost -t "homeassistant/sensor/good_gym/#" -v
```

---

## 🐳 Docker 测试

### 单独构建测试

```bash
cd Good-GYM

# 构建镜像
docker build -f homeassistant/Dockerfile -t good-gym-addon .

# 运行容器
docker run --rm \
  -e RTSP_URL="rtsp://192.168.1.100:554/stream" \
  -e MQTT_HOST="host.docker.internal" \
  -e MQTT_PORT="1883" \
  -e EXERCISE_TYPE="squat" \
  -e ENABLE_DEBUG="true" \
  good-gym-addon
```

---

## 🏠 Home Assistant 部署

### 方法 1: 本地 Addon (开发)

1. **创建 addons 目录结构**
```bash
# 在 Home Assistant 配置目录
mkdir -p addons/good-gym
cp -r homeassistant/* addons/good-gym/
cp -r core addons/good-gym/
cp -r data addons/good-gym/
cp -r models addons/good-gym/
cp exercise_counters.py addons/good-gym/
```

2. **重启 Supervisor**
```bash
ha supervisor reload
```

3. **安装 Addon**
- Supervisor > Add-on Store
- 刷新页面
- 找到 "Good-GYM Exercise Tracker (Local)"
- 点击安装

### 方法 2: GitHub 仓库 (生产)

1. **准备 GitHub 仓库**
```bash
# 创建新的 addon 仓库
mkdir good-gym-addon
cd good-gym-addon

# 复制文件
cp -r ../Good-GYM/homeassistant/* .
mkdir -p core data models
cp -r ../Good-GYM/core/* core/
cp -r ../Good-GYM/data/* data/
cp -r ../Good-GYM/models/* models/
cp ../Good-GYM/exercise_counters.py .

# 初始化 Git
git init
git add .
git commit -m "Initial commit"
git push origin main
```

2. **添加到 Home Assistant**
- Supervisor > Add-on Store > ⋮ > Repositories
- 添加: `https://github.com/your-username/good-gym-addon`
- 刷新并安装

---

## 📱 使用手机作为摄像头

### Android - IP Webcam

1. 安装 "IP Webcam" APP
2. 启动服务器
3. 记下 IP 地址,例如: `http://192.168.1.50:8080`
4. RTSP URL: `rtsp://192.168.1.50:8080/h264_ulaw.sdp`

### iOS - EpocCam

1. 安装 EpocCam APP 和桌面驱动
2. 启动 APP
3. 使用第三方工具转换为 RTSP (或使用 HA Camera 集成)

---

## 🧪 测试场景

### 测试 1: MQTT 连接

```python
# test_mqtt.py
from homeassistant.mqtt_publisher import MQTTPublisher

config = {
    'host': 'localhost',
    'port': 1883,
    'username': '',
    'password': '',
    'topic_prefix': 'test/good_gym'
}

pub = MQTTPublisher(config, 'squat')
if pub.connect():
    print("✓ MQTT OK")
    pub.publish_state(count=1, stage='up', angle=160.0)
    pub.disconnect()
```

### 测试 2: RTSP 连接

```python
# test_rtsp.py
from homeassistant.rtsp_handler import RTSPHandler
import time

handler = RTSPHandler("rtsp://your_camera_url")
if handler.connect():
    print("✓ RTSP OK")
    handler.start_capture()
    time.sleep(5)
    stats = handler.get_stats()
    print(f"捕获 {stats['frame_count']} 帧")
    handler.stop_capture()
```

### 测试 3: 完整流程 (使用测试视频)

```bash
# 1. 准备测试视频 (下载一个深蹲视频)
ffmpeg -i squat_video.mp4 -c copy -f rtsp rtsp://localhost:8554/test

# 2. 配置环境变量指向测试流
export RTSP_URL="rtsp://localhost:8554/test"

# 3. 运行服务
python homeassistant/main.py
```

---

## 🎮 Home Assistant 配置示例

### 仪表板卡片

```yaml
# configuration.yaml 或 dashboard YAML

# 简单数字显示
type: entities
entities:
  - entity: sensor.good_gym_squat_counter
    name: 深蹲次数

# 进度条
type: gauge
entity: sensor.good_gym_squat_counter
min: 0
max: 50
name: 今日目标
needle: true

# 统计卡片
type: statistic
entity: sensor.good_gym_squat_counter
stat_type: mean
period:
  calendar:
    period: week
```

### 自动化示例

```yaml
# automations.yaml

# 达到目标时通知
- id: exercise_goal_reached
  alias: 健身目标达成
  trigger:
    - platform: numeric_state
      entity_id: sensor.good_gym_squat_counter
      above: 30
  action:
    - service: notify.mobile_app_your_phone
      data:
        title: "🎉 目标达成!"
        message: "完成 {{ states('sensor.good_gym_squat_counter') }} 个深蹲"
        data:
          push:
            sound: success

# 每次计数时播放提示音
- id: exercise_count_sound
  alias: 运动计数提示
  trigger:
    - platform: state
      entity_id: sensor.good_gym_squat_counter
  condition:
    - condition: template
      value_template: "{{ trigger.to_state.state | int > trigger.from_state.state | int }}"
  action:
    - service: media_player.play_media
      target:
        entity_id: media_player.echo_dot
      data:
        media_content_id: "media-source://media_source/local/sounds/beep.mp3"
        media_content_type: "music"

# 游戏化: 完成动作时灯光闪烁
- id: exercise_light_flash
  alias: 运动灯光效果
  trigger:
    - platform: state
      entity_id: sensor.good_gym_squat_counter
  action:
    - service: light.turn_on
      target:
        entity_id: light.living_room
      data:
        flash: short
        rgb_color: [0, 255, 0]
```

---

## 🔧 常见问题快速解决

### 问题 1: RTSP 连接失败

```bash
# 测试 RTSP URL
ffplay rtsp://your_camera_url

# 或
vlc rtsp://your_camera_url

# 检查防火墙
sudo ufw allow 554/tcp
```

### 问题 2: MQTT 连接失败

```bash
# 测试 MQTT broker
mosquitto_sub -h localhost -t "test" -v

# 检查 Mosquitto 状态 (Home Assistant)
ha addons info core_mosquitto
```

### 问题 3: CPU 占用过高

修改配置:
```yaml
frame_skip: 3          # 每3帧处理一次
rtmpose_mode: performance  # 快速模式
```

### 问题 4: RTMPose 模型下载失败

手动下载模型并放置到 `models/` 目录。

### 问题 5: 权限问题 (Docker)

```bash
# 给予执行权限
chmod +x homeassistant/run.sh
```

---

## 📊 性能优化建议

### CPU 优化

```yaml
# config.yaml
options:
  frame_skip: 2              # 降低处理频率
  rtmpose_mode: performance  # 快速模式
  detection_interval: 0.2    # 降低检测频率
```

### 网络优化

1. **使用有线连接** (摄像头和 HA 服务器)
2. **降低 RTSP 流分辨率** (640x480 或 1280x720)
3. **本地 MQTT broker** (不要用云端)

### 摄像头设置

- 分辨率: 1280x720 (推荐)
- 帧率: 15-30 FPS
- 编码: H.264
- 比特率: 2-4 Mbps

---

## 🚀 下一步

1. ✅ **完成本地测试**
2. ✅ **验证 MQTT 消息**
3. ✅ **部署到 Home Assistant**
4. 🎯 **创建仪表板**
5. 🎯 **设置自动化**
6. 🎯 **分享到社区**

---

## 📚 更多资源

- [完整文档](DOCS.md)
- [用户手册](README.md)
- [项目 Walkthrough](../../.gemini/antigravity/brain/*/walkthrough.md)
- [原项目 GitHub](https://github.com/yo-WASSUP/Good-GYM)

## 💡 提示

- 确保摄像头能看到全身
- 光线充足效果更好
- 背景简单有助于检测
- 首次使用建议用 `balanced` 模式

---

**祝您使用愉快! 🏋️‍♂️**
