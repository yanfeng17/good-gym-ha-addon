"""
Configuration Manager for Good-GYM Home Assistant Addon
Handles reading and validating addon configuration
"""
import json
import os
import sys
from typing import Dict, Any


class ConfigManager:
    """Manage addon configuration from Home Assistant options or environment variables"""
    
    def __init__(self, config_file: str = "/data/options.json"):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to Home Assistant options.json file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or environment variables"""
        # Try to load from Home Assistant options file
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    print(f"✓ Loaded config from {self.config_file}")
                    return config
            except Exception as e:
                print(f"⚠ Error loading config file: {e}")
        
        # Fallback to environment variables (for development/testing)
        print("ℹ Using environment variables for configuration")
        config = {
            'rtsp_url': os.getenv('RTSP_URL', 'rtsp://localhost:8554/stream'),
            'mqtt_host': os.getenv('MQTT_HOST', 'localhost'),
            'mqtt_port': int(os.getenv('MQTT_PORT', '1883')),
            'mqtt_user': os.getenv('MQTT_USER', ''),
            'mqtt_password': os.getenv('MQTT_PASSWORD', ''),
            'mqtt_topic_prefix': os.getenv('MQTT_TOPIC_PREFIX', 'homeassistant/sensor/good_gym'),
            'exercise_type': os.getenv('EXERCISE_TYPE', 'squat'),
            'detection_interval': float(os.getenv('DETECTION_INTERVAL', '0.1')),
            'enable_debug': os.getenv('ENABLE_DEBUG', 'false').lower() == 'true',
            'enable_mqtt_discovery': os.getenv('ENABLE_MQTT_DISCOVERY', 'true').lower() == 'true',
            'rtmpose_mode': os.getenv('RTMPOSE_MODE', 'lightweight'),  # lightweight, balanced, or performance
            'reconnect_interval': int(os.getenv('RECONNECT_INTERVAL', '5')),
            'frame_skip': int(os.getenv('FRAME_SKIP', '1')),  # Process every N frames
        }
        return config
    
    def _validate_config(self):
        """Validate required configuration parameters"""
        required_params = ['rtsp_url', 'mqtt_host', 'exercise_type']
        
        for param in required_params:
            if not self.config.get(param):
                raise ValueError(f"Missing required configuration parameter: {param}")
        
        # Validate exercise type
        valid_exercises = [
            'squat', 'pushup', 'situp', 'bicep_curl', 'lateral_raise',
            'overhead_press', 'leg_raise', 'knee_raise', 'knee_press', 'crunch'
        ]
        if self.config['exercise_type'] not in valid_exercises:
            raise ValueError(
                f"Invalid exercise_type: {self.config['exercise_type']}. "
                f"Valid options: {', '.join(valid_exercises)}"
            )
        
        # Validate RTMPose mode
        valid_modes = ['lightweight', 'balanced', 'performance']
        if self.config.get('rtmpose_mode', 'lightweight') not in valid_modes:
            raise ValueError(
                f"Invalid rtmpose_mode. Valid options: {', '.join(valid_modes)}"
            )
        
        print("✓ Configuration validated successfully")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self.config.get(key, default)
    
    def get_mqtt_config(self) -> Dict[str, Any]:
        """Get MQTT-specific configuration"""
        return {
            'host': self.config['mqtt_host'],
            'port': self.config['mqtt_port'],
            'username': self.config.get('mqtt_user', ''),
            'password': self.config.get('mqtt_password', ''),
            'topic_prefix': self.config.get('mqtt_topic_prefix', 'homeassistant/sensor/good_gym'),
        }
    
    def get_rtsp_config(self) -> Dict[str, Any]:
        """Get RTSP-specific configuration"""
        return {
            'url': self.config['rtsp_url'],
            'reconnect_interval': self.config.get('reconnect_interval', 5),
        }
    
    def get_detection_config(self) -> Dict[str, Any]:
        """Get detection-specific configuration"""
        return {
            'exercise_type': self.config['exercise_type'],
            'detection_interval': self.config.get('detection_interval', 0.1),
            'rtmpose_mode': self.config.get('rtmpose_mode', 'lightweight'),
            'frame_skip': self.config.get('frame_skip', 1),
            'enable_debug': self.config.get('enable_debug', False),
        }
    
    def print_config(self):
        """Print current configuration (without sensitive data)"""
        print("\n" + "="*50)
        print("Good-GYM Addon Configuration")
        print("="*50)
        
        # Safe config (hide passwords)
        safe_config = self.config.copy()
        if safe_config.get('mqtt_password'):
            safe_config['mqtt_password'] = '****'
        
        for key, value in safe_config.items():
            print(f"  {key}: {value}")
        
        print("="*50 + "\n")


if __name__ == "__main__":
    # Test configuration manager
    config = ConfigManager()
    config.print_config()
