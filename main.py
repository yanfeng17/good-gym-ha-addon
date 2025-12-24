"""
Good-GYM Home Assistant Addon - Main Service
Headless exercise tracking service with RTSP input and MQTT output
"""
import sys
import os
import time
import signal
import cv2
from typing import Optional

# Configure RTMLib cache to use persistent storage BEFORE importing rtmlib
# This prevents re-downloading models on every restart
CACHE_DIR = "/data/.cache/rtmlib"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(os.path.join(CACHE_DIR, "hub", "checkpoints"), exist_ok=True)

# Set environment variables for model caching
os.environ['TORCH_HOME'] = CACHE_DIR
os.environ['HF_HOME'] = CACHE_DIR
# RTMLib uses this directory pattern
os.environ['XDG_CACHE_HOME'] = "/data/.cache"

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_manager import ConfigManager
from rtsp_handler import RTSPHandler
from mqtt_publisher import MQTTPublisher
from core.rtmpose_processor import RTMPoseProcessor
from exercise_counters import ExerciseCounter


class GoodGymService:
    """Main service class for Good-GYM Home Assistant Addon"""
    
    def __init__(self, config_file: str = "/data/options.json"):
        """
        Initialize Good-GYM service
        
        Args:
            config_file: Path to Home Assistant options.json
        """
        print("\n" + "="*60)
        print("  🏋️  Good-GYM Home Assistant Addon v2.0")
        print("  AI-Powered Exercise Tracker with RTMPose")
        print("="*60 + "\n")
        
        # Load configuration
        self.config = ConfigManager(config_file)
        self.config.print_config()
        
        # Initialize components
        self.exercise_counter: Optional[ExerciseCounter] = None
        self.rtmpose_processor: Optional[RTMPoseProcessor] = None
        self.rtsp_handler: Optional[RTSPHandler] = None
        self.mqtt_publisher: Optional[MQTTPublisher] = None
        
        # State
        self.is_running = False
        self.frame_count = 0
        self.last_count = 0
        self.last_publish_time = 0
        self.publish_interval = 0.5  # Publish every 0.5 seconds
        
        # Get configuration
        detection_config = self.config.get_detection_config()
        self.exercise_type = detection_config['exercise_type']
        self.frame_skip = detection_config['frame_skip']
        self.enable_debug = detection_config['enable_debug']
        self.max_resolution = detection_config.get('max_resolution', 640)
    
    def initialize(self) -> bool:
        """
        Initialize all components
        
        Returns:
            True if all components initialized successfully
        """
        try:
            # 1. Initialize exercise counter
            print("📊 Initializing exercise counter...")
            self.exercise_counter = ExerciseCounter(smoothing_window=5)
            print(f"✓ Exercise counter ready (type: {self.exercise_type})")
            
            # 2. Initialize RTMPose processor
            print("\n🧠 Initializing RTMPose processor...")
            detection_config = self.config.get_detection_config()
            self.rtmpose_processor = RTMPoseProcessor(
                exercise_counter=self.exercise_counter,
                mode=detection_config['rtmpose_mode'],
                backend='onnxruntime',
                device='cpu'
            )
            # Disable skeleton drawing to save CPU
            self.rtmpose_processor.set_skeleton_visibility(False)
            print("✓ RTMPose processor ready")
            
            # 3. Initialize MQTT publisher
            print("\n📡 Initializing MQTT publisher...")
            mqtt_config = self.config.get_mqtt_config()
            self.mqtt_publisher = MQTTPublisher(mqtt_config, self.exercise_type)
            
            if not self.mqtt_publisher.connect():
                print("✗ Failed to connect to MQTT broker")
                return False
            
            self.mqtt_publisher.publish_status('online', f'Tracking {self.exercise_type}')
            print("✓ MQTT publisher ready")
            
            # 4. Initialize RTSP handler
            print("\n🎥 Initializing RTSP handler...")
            rtsp_config = self.config.get_rtsp_config()
            self.rtsp_handler = RTSPHandler(
                rtsp_url=rtsp_config['url'],
                reconnect_interval=rtsp_config['reconnect_interval']
            )
            print("✓ RTSP handler ready")
            
            print("\n✅ All components initialized successfully\n")
            return True
            
        except Exception as e:
            print(f"\n✗ Initialization error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def process_frame(self, frame, frame_number: int):
        """
        Process a single frame from RTSP stream
        
        Args:
            frame: Video frame from RTSP
            frame_number: Frame number
        """
        try:
            # Skip frames if configured
            if self.frame_skip > 1 and frame_number % self.frame_skip != 0:
                return
            
            self.frame_count += 1
            
            # Resize frame if needed to reduce CPU usage
            h, w = frame.shape[:2]
            if w > self.max_resolution:
                scale = self.max_resolution / w
                new_width = int(w * scale)
                new_height = int(h * scale)
                frame = cv2.resize(frame, (new_width, new_height))
                if self.enable_debug and frame_number == 1:
                    print(f"📏 Resized frame from {w}x{h} to {new_width}x{new_height}")
            
            # Process frame with RTMPose
            processed_frame = self.rtmpose_processor.process_frame(
                frame,
                self.exercise_type
            )
            
            # Get current count and stage
            current_count = self.exercise_counter.counter
            current_stage = self.exercise_counter.stage
            
            # Get current angle (for display/logging)
            # Note: This is a simplified approach, actual angle depends on exercise type
            angle = None  # RTMPose processor would need to expose this
            
            # Publish to MQTT if count changed or enough time has passed
            current_time = time.time()
            count_changed = current_count != self.last_count
            time_to_publish = (current_time - self.last_publish_time) >= self.publish_interval
            
            if count_changed or time_to_publish:
                self.mqtt_publisher.publish_state(
                    count=current_count,
                    stage=current_stage,
                    angle=angle,
                    frame_count=self.frame_count
                )
                
                self.last_publish_time = current_time
                
                # Log count changes
                if count_changed:
                    print(f"✓ Count updated: {current_count} reps (stage: {current_stage})")
                    self.last_count = current_count
            
            # Debug output every 100 frames
            if self.enable_debug and self.frame_count % 100 == 0:
                print(f"📸 Processed {self.frame_count} frames | Count: {current_count} | Stage: {current_stage}")
        
        except Exception as e:
            print(f"✗ Error processing frame: {e}")
            if self.enable_debug:
                import traceback
                traceback.print_exc()
    
    def start(self):
        """Start the service"""
        if not self.initialize():
            print("✗ Failed to initialize service")
            return False
        
        print("▶️  Starting Good-GYM service...\n")
        print(f"   Exercise Type: {self.exercise_type}")
        print(f"   RTSP URL: {self.config.get('rtsp_url')}")
        print(f"   MQTT Topic: {self.mqtt_publisher.state_topic}")
        print(f"   Frame Skip: {self.frame_skip}")
        print("\n" + "="*60 + "\n")
        
        self.is_running = True
        
        # Start RTSP capture with frame callback
        self.rtsp_handler.start_capture(on_frame=self.process_frame)
        
        print("✅ Service started successfully!")
        print("   Press Ctrl+C to stop\n")
        
        # Keep main thread alive
        try:
            while self.is_running:
                time.sleep(1)
                
                # Periodic status check
                if self.frame_count > 0 and self.frame_count % 300 == 0:
                    stats = self.rtsp_handler.get_stats()
                    print(f"📊 Status - Frames: {self.frame_count}, Count: {self.exercise_counter.counter}, RTSP: {stats}")
        
        except KeyboardInterrupt:
            print("\n⏹️  Received stop signal...")
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the service"""
        print("\n🛑 Stopping Good-GYM service...")
        
        self.is_running = False
        
        # Stop RTSP capture
        if self.rtsp_handler:
            self.rtsp_handler.stop_capture()
        
        # Publish final state and offline status
        if self.mqtt_publisher and self.mqtt_publisher.is_connected:
            self.mqtt_publisher.publish_state(
                count=self.exercise_counter.counter if self.exercise_counter else 0,
                stage=self.exercise_counter.stage if self.exercise_counter else None,
                angle=None
            )
            self.mqtt_publisher.publish_status('offline', 'Service stopped')
            self.mqtt_publisher.disconnect()
        
        print("✅ Service stopped gracefully\n")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n⚠️  Received signal {signum}")
        self.is_running = False


def main():
    """Main entry point"""
    # Determine config file path
    config_file = "/data/options.json"  # Home Assistant default
    
    # Allow override via environment variable (for testing)
    if os.getenv('CONFIG_FILE'):
        config_file = os.getenv('CONFIG_FILE')
    
    # Create and start service
    service = GoodGymService(config_file=config_file)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, service.signal_handler)
    signal.signal(signal.SIGTERM, service.signal_handler)
    
    # Start service
    service.start()


if __name__ == "__main__":
    main()
