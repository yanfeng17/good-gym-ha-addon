"""
MQTT Publisher for Good-GYM Home Assistant Addon
Publishes exercise counting data to MQTT broker with Home Assistant discovery
"""
import json
import time
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt


class MQTTPublisher:
    """Publish exercise data to MQTT with Home Assistant discovery support"""
    
    def __init__(self, config: Dict[str, Any], exercise_type: str):
        """
        Initialize MQTT publisher
        
        Args:
            config: MQTT configuration dict (host, port, username, password, topic_prefix)
            exercise_type: Type of exercise being tracked
        """
        self.host = config['host']
        self.port = config['port']
        self.username = config.get('username', '')
        self.password = config.get('password', '')
        self.topic_prefix = config.get('topic_prefix', 'homeassistant/sensor/good_gym')
        self.exercise_type = exercise_type
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id=f"good_gym_{exercise_type}")
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Set credentials if provided
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        # Connection state
        self.is_connected = False
        self.session_start_time = time.time()
        
        # Topics
        self.state_topic = f"{self.topic_prefix}_{exercise_type}/state"
        self.config_topic = f"{self.topic_prefix}_{exercise_type}/config"
        self.status_topic = f"{self.topic_prefix}_status/state"
    
    def connect(self) -> bool:
        """
        Connect to MQTT broker
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            print(f"📡 Connecting to MQTT broker: {self.host}:{self.port}")
            self.client.connect(self.host, self.port, keepalive=60)
            self.client.loop_start()
            
            # Wait for connection (with timeout)
            timeout = 10
            start_time = time.time()
            while not self.is_connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.is_connected:
                print("✓ Connected to MQTT broker")
                return True
            else:
                print("✗ Failed to connect to MQTT broker (timeout)")
                return False
                
        except Exception as e:
            print(f"✗ MQTT connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
        print("📴 Disconnected from MQTT broker")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            self.is_connected = True
            print("✓ MQTT connection established")
            # Publish discovery config on connect
            self.publish_discovery()
        else:
            print(f"✗ MQTT connection failed with code: {rc}")
            self.is_connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        self.is_connected = False
        if rc != 0:
            print(f"⚠ Unexpected MQTT disconnection (code: {rc})")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        print(f"📨 Received message on {msg.topic}: {msg.payload.decode()}")
    
    def publish_discovery(self):
        """Publish Home Assistant MQTT discovery configuration"""
        # Exercise-specific exercise names
        exercise_names = {
            'squat': 'Squat',
            'pushup': 'Push-up',
            'situp': 'Sit-up',
            'bicep_curl': 'Bicep Curl',
            'lateral_raise': 'Lateral Raise',
            'overhead_press': 'Overhead Press',
            'leg_raise': 'Leg Raise',
            'knee_raise': 'Knee Raise',
            'knee_press': 'Knee Press',
            'crunch': 'Crunch',
        }
        
        exercise_name = exercise_names.get(self.exercise_type, self.exercise_type.title())
        
        # Discovery configuration for count sensor
        discovery_config = {
            "name": f"Good-GYM {exercise_name} Counter",
            "state_topic": self.state_topic,
            "value_template": "{{ value_json.count }}",
            "unit_of_measurement": "reps",
            "icon": "mdi:run",
            "json_attributes_topic": self.state_topic,
            "unique_id": f"good_gym_{self.exercise_type}_counter",
            "device": {
                "identifiers": ["good_gym_addon"],
                "name": "Good-GYM Exercise Tracker",
                "model": "RTMPose AI v2.0",
                "manufacturer": "Good-GYM",
                "sw_version": "2.0.0"
            }
        }
        
        # Publish discovery message
        self.client.publish(
            self.config_topic,
            json.dumps(discovery_config),
            qos=1,
            retain=True
        )
        
        print(f"📢 Published MQTT discovery for {exercise_name}")
    
    def publish_state(self, count: int, stage: Optional[str], angle: Optional[float], **kwargs):
        """
        Publish current exercise state
        
        Args:
            count: Current repetition count
            stage: Current stage (up/down)
            angle: Current angle measurement
            **kwargs: Additional attributes to publish
        """
        if not self.is_connected:
            print("⚠ Not connected to MQTT broker, skipping publish")
            return
        
        # Build state message
        state_data = {
            "count": count,
            "stage": stage or "unknown",
            "angle": round(angle, 2) if angle is not None else None,
            "exercise_type": self.exercise_type,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "session_start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.session_start_time)),
        }
        
        # Add additional attributes
        state_data.update(kwargs)
        
        # Publish state
        try:
            self.client.publish(
                self.state_topic,
                json.dumps(state_data),
                qos=0,
                retain=False
            )
        except Exception as e:
            print(f"✗ Error publishing state: {e}")
    
    def publish_status(self, status: str, message: str = ""):
        """
        Publish addon status
        
        Args:
            status: Status string (online, offline, error)
            message: Optional status message
        """
        if not self.is_connected:
            return
        
        status_data = {
            "status": status,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        
        try:
            self.client.publish(
                self.status_topic,
                json.dumps(status_data),
                qos=1,
                retain=True
            )
        except Exception as e:
            print(f"✗ Error publishing status: {e}")
    
    def reset_session(self):
        """Reset session start time"""
        self.session_start_time = time.time()
        print(f"🔄 Session reset at {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    # Test MQTT publisher
    import os
    
    config = {
        'host': os.getenv('MQTT_HOST', 'localhost'),
        'port': int(os.getenv('MQTT_PORT', '1883')),
        'username': os.getenv('MQTT_USER', ''),
        'password': os.getenv('MQTT_PASSWORD', ''),
        'topic_prefix': 'homeassistant/sensor/good_gym',
    }
    
    publisher = MQTTPublisher(config, 'squat')
    
    if publisher.connect():
        # Publish some test data
        for i in range(10):
            publisher.publish_state(
                count=i,
                stage='up' if i % 2 == 0 else 'down',
                angle=160.0 if i % 2 == 0 else 110.0
            )
            time.sleep(1)
        
        publisher.publish_status('online', 'Test completed')
        time.sleep(1)
        publisher.disconnect()
