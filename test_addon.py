#!/usr/bin/env python3
"""
Test script for Good-GYM Home Assistant Addon
Tests the service locally without Docker/Home Assistant
"""
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_banner():
    print("\n" + "="*60)
    print("  Good-GYM Addon Local Test Script")
    print("="*60 + "\n")

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_modules = [
        'cv2',
        'numpy',
        'paho.mqtt.client',
        'rtmlib',
    ]
    
    missing = []
    for module_name in required_modules:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name}")
        except ImportError:
            print(f"  ✗ {module_name} (missing)")
            missing.append(module_name)
    
    if missing:
        print(f"\n⚠ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r homeassistant/requirements.txt")
        return False
    
    print("✓ All dependencies installed\n")
    return True

def test_config_manager():
    """Test configuration manager"""
    print("🔧 Testing ConfigManager...")
    
    try:
        from homeassistant.config_manager import ConfigManager
        
        # This will use environment variables
        config = ConfigManager()
        config.print_config()
        
        print("✓ ConfigManager working\n")
        return config
    except Exception as e:
        print(f"✗ ConfigManager error: {e}\n")
        return None

def test_rtsp_handler(rtsp_url):
    """Test RTSP handler"""
    print(f"🎥 Testing RTSP connection to: {rtsp_url}")
    
    try:
        from homeassistant.rtsp_handler import RTSPHandler
        
        handler = RTSPHandler(rtsp_url)
        
        if handler.connect():
            print("✓ RTSP connection successful")
            
            # Test capturing a few frames
            print("  Capturing test frames...")
            frame_count = 0
            
            def on_frame(frame, count):
                nonlocal frame_count
                frame_count = count
                if count <= 5:
                    print(f"  📸 Frame {count}: {frame.shape}")
            
            handler.start_capture(on_frame=on_frame)
            time.sleep(3)
            handler.stop_capture()
            
            print(f"✓ Captured {frame_count} frames\n")
            return True
        else:
            print("✗ RTSP connection failed\n")
            return False
            
    except Exception as e:
        print(f"✗ RTSP error: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_mqtt_publisher(mqtt_config):
    """Test MQTT publisher"""
    print(f"📡 Testing MQTT connection to: {mqtt_config['host']}:{mqtt_config['port']}")
    
    try:
        from homeassistant.mqtt_publisher import MQTTPublisher
        
        publisher = MQTTPublisher(mqtt_config, 'test')
        
        if publisher.connect():
            print("✓ MQTT connection successful")
            
            # Publish test message
            print("  Publishing test message...")
            publisher.publish_state(
                count=10,
                stage='up',
                angle=160.0,
                test=True
            )
            
            time.sleep(1)
            publisher.disconnect()
            
            print("✓ MQTT test completed\n")
            return True
        else:
            print("✗ MQTT connection failed\n")
            return False
            
    except Exception as e:
        print(f"✗ MQTT error: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_rtmpose():
    """Test RTMPose processor"""
    print("🧠 Testing RTMPose processor...")
    
    try:
        from exercise_counters import ExerciseCounter
        from core.rtmpose_processor import RTMPoseProcessor
        import numpy as np
        
        counter = ExerciseCounter()
        processor = RTMPoseProcessor(counter, mode='balanced')
        
        # Create a dummy frame
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Process frame (will likely not detect anything)
        result = processor.process_frame(dummy_frame, 'squat')
        
        print("✓ RTMPose processor initialized\n")
        return True
        
    except Exception as e:
        print(f"✗ RTMPose error: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def main():
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing packages.\n")
        return 1
    
    # Test configuration
    config = test_config_manager()
    if not config:
        print("\n❌ Configuration test failed\n")
        return 1
    
    # Test RTMPose
    if not test_rtmpose():
        print("\n⚠ RTMPose test failed (this might be expected without models)\n")
    
    # Test MQTT
    mqtt_config = config.get_mqtt_config()
    mqtt_ok = test_mqtt_publisher(mqtt_config)
    
    # Test RTSP (optional - might not have camera)
    rtsp_config = config.get_rtsp_config()
    print(f"ℹ RTSP URL: {rtsp_config['url']}")
    response = input("Do you want to test RTSP connection? (y/n): ")
    
    if response.lower() == 'y':
        rtsp_ok = test_rtsp_handler(rtsp_config['url'])
    else:
        print("⏭ Skipping RTSP test\n")
        rtsp_ok = None
    
    # Summary
    print("="*60)
    print("  Test Summary")
    print("="*60)
    print(f"  Dependencies: ✓")
    print(f"  Configuration: ✓")
    print(f"  RTMPose: {'✓' if test_rtmpose else '⚠'}")
    print(f"  MQTT: {'✓' if mqtt_ok else '✗'}")
    if rtsp_ok is not None:
        print(f"  RTSP: {'✓' if rtsp_ok else '✗'}")
    else:
        print(f"  RTSP: (skipped)")
    print("="*60 + "\n")
    
    if mqtt_ok:
        print("✅ Core components are working!\n")
        print("Next steps:")
        print("1. Set up a real RTSP camera")
        print("2. Run: python homeassistant/main.py")
        print("3. Or build Docker: docker build -f homeassistant/Dockerfile .\n")
        return 0
    else:
        print("❌ Some components failed. Check MQTT broker.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
