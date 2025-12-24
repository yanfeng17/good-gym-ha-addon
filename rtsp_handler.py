"""
RTSP Stream Handler for Good-GYM Home Assistant Addon
Manages RTSP camera connection and frame capture
"""
import cv2
import time
import threading
from typing import Optional, Callable
import numpy as np


class RTSPHandler:
    """Handle RTSP stream connection and frame capture with automatic reconnection"""
    
    def __init__(self, rtsp_url: str, reconnect_interval: int = 5):
        """
        Initialize RTSP handler
        
        Args:
            rtsp_url: RTSP camera URL
            reconnect_interval: Seconds to wait before reconnecting on failure
        """
        self.rtsp_url = rtsp_url
        self.reconnect_interval = reconnect_interval
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_connected = False
        self.is_running = False
        self.last_frame: Optional[np.ndarray] = None
        self.frame_count = 0
        self.error_count = 0
        
        # Threading
        self.lock = threading.Lock()
        self.capture_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.on_frame_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
    
    def connect(self) -> bool:
        """
        Connect to RTSP stream
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            print(f"🎥 Connecting to RTSP stream: {self.rtsp_url}")
            
            # Release existing connection if any
            if self.cap is not None:
                self.cap.release()
            
            # Create new connection with optimized settings
            self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
            
            # Force TCP transport (fixes "406 Not Acceptable" errors)
            # CAP_PROP_RTSP_TRANSPORT: 0 = UDP, 1 = TCP, 2 = HTTP
            self.cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 10000)  # 10 second timeout
            self.cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 10000)  # 10 second read timeout
            
            # Configure capture settings for better performance
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize latency
            self.cap.set(cv2.CAP_PROP_FPS, 30)  # Target frame rate
            
            # Try to enable TCP transport (may not work on all OpenCV builds)
            try:
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))
            except:
                pass  # Ignore if not supported
            
            # Test connection
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.is_connected = True
                self.error_count = 0
                
                # Get stream info
                width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = self.cap.get(cv2.CAP_PROP_FPS)
                
                print(f"✓ Connected to RTSP stream")
                print(f"  Resolution: {width}x{height}")
                print(f"  FPS: {fps}")
                
                return True
            else:
                print(f"✗ Failed to read frame from RTSP stream")
                self.is_connected = False
                return False
                
        except Exception as e:
            print(f"✗ RTSP connection error: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from RTSP stream"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_connected = False
        print("📴 Disconnected from RTSP stream")
    
    def start_capture(self, on_frame: Optional[Callable] = None):
        """
        Start capturing frames in a separate thread
        
        Args:
            on_frame: Callback function called for each frame (frame, frame_count)
        """
        if self.is_running:
            print("⚠ Capture already running")
            return
        
        self.on_frame_callback = on_frame
        self.is_running = True
        
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        print("▶ Started frame capture thread")
    
    def stop_capture(self):
        """Stop capturing frames"""
        self.is_running = False
        if self.capture_thread is not None:
            self.capture_thread.join(timeout=5)
        print("⏹ Stopped frame capture")
    
    def _capture_loop(self):
        """Main capture loop (runs in separate thread)"""
        reconnect_attempts = 0
        max_reconnect_attempts = 10
        
        while self.is_running:
            # Connect if not connected
            if not self.is_connected:
                if reconnect_attempts < max_reconnect_attempts:
                    print(f"🔄 Attempting to reconnect... (attempt {reconnect_attempts + 1}/{max_reconnect_attempts})")
                    if self.connect():
                        reconnect_attempts = 0
                    else:
                        reconnect_attempts += 1
                        time.sleep(self.reconnect_interval)
                        continue
                else:
                    print(f"✗ Max reconnection attempts reached. Stopping.")
                    if self.on_error_callback:
                        self.on_error_callback("Max reconnection attempts reached")
                    break
            
            # Read frame
            try:
                ret, frame = self.cap.read()
                
                if ret and frame is not None:
                    self.frame_count += 1
                    
                    # Store frame (thread-safe)
                    with self.lock:
                        self.last_frame = frame.copy()
                    
                    # Call callback if provided
                    if self.on_frame_callback:
                        self.on_frame_callback(frame, self.frame_count)
                    
                    # Reset error count on successful read
                    self.error_count = 0
                    
                else:
                    # Frame read failed
                    self.error_count += 1
                    print(f"⚠ Failed to read frame (error count: {self.error_count})")
                    
                    # Reconnect after multiple errors
                    if self.error_count > 10:
                        print("🔄 Too many errors, reconnecting...")
                        self.is_connected = False
                        self.disconnect()
                        time.sleep(1)
                    
            except Exception as e:
                print(f"✗ Error in capture loop: {e}")
                self.is_connected = False
                self.disconnect()
                time.sleep(self.reconnect_interval)
        
        # Cleanup
        self.disconnect()
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """
        Get the latest captured frame (thread-safe)
        
        Returns:
            Latest frame or None if not available
        """
        with self.lock:
            return self.last_frame.copy() if self.last_frame is not None else None
    
    def get_stats(self) -> dict:
        """Get capture statistics"""
        return {
            'is_connected': self.is_connected,
            'frame_count': self.frame_count,
            'error_count': self.error_count,
        }
    
    def __del__(self):
        """Cleanup on deletion"""
        self.stop_capture()
        self.disconnect()


if __name__ == "__main__":
    # Test RTSP handler
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python rtsp_handler.py <rtsp_url>")
        sys.exit(1)
    
    rtsp_url = sys.argv[1]
    
    def on_frame(frame, count):
        if count % 30 == 0:  # Print every 30 frames
            print(f"📸 Frame {count}: {frame.shape}")
    
    handler = RTSPHandler(rtsp_url)
    handler.start_capture(on_frame=on_frame)
    
    try:
        # Run for 30 seconds
        time.sleep(30)
    except KeyboardInterrupt:
        print("\n⏹ Interrupted by user")
    finally:
        handler.stop_capture()
        print(f"\n📊 Stats: {handler.get_stats()}")
