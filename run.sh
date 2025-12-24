#!/usr/bin/with-contenv bashio

# Print banner
echo "========================================"
echo "  Good-GYM Exercise Tracker v2.0"
echo "  Starting addon..."
echo "========================================"

# Read configuration from Home Assistant
export RTSP_URL=$(bashio::config 'rtsp_url')
export MQTT_HOST=$(bashio::config 'mqtt_host')
export MQTT_PORT=$(bashio::config 'mqtt_port')
export MQTT_USER=$(bashio::config 'mqtt_user')
export MQTT_PASSWORD=$(bashio::config 'mqtt_password')
export MQTT_TOPIC_PREFIX=$(bashio::config 'mqtt_topic_prefix')
export EXERCISE_TYPE=$(bashio::config 'exercise_type')
export DETECTION_INTERVAL=$(bashio::config 'detection_interval')
export RTMPOSE_MODE=$(bashio::config 'rtmpose_mode')
export FRAME_SKIP=$(bashio::config 'frame_skip')
export RECONNECT_INTERVAL=$(bashio::config 'reconnect_interval')
export ENABLE_DEBUG=$(bashio::config 'enable_debug')
export ENABLE_MQTT_DISCOVERY=$(bashio::config 'enable_mqtt_discovery')

# Log configuration (without sensitive data)
bashio::log.info "RTSP URL: ${RTSP_URL}"
bashio::log.info "MQTT Host: ${MQTT_HOST}:${MQTT_PORT}"
bashio::log.info "Exercise Type: ${EXERCISE_TYPE}"
bashio::log.info "RTMPose Mode: ${RTMPOSE_MODE}"

# Change to app directory
cd /app

# Start the Python service
bashio::log.info "Starting Good-GYM service..."
python -u main.py
