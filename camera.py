import cv2
import threading
import numpy as np

class CameraFeed:
    """
    Manages webcam feed capture with threading for smooth performance.
    Provides frame access to other modules.
    """
    
    def __init__(self, camera_id=0, width=1280, height=720):
        """
        Initialize camera feed.
        
        Args:
            camera_id: Webcam device ID (default 0)
            width: Frame width in pixels
            height: Frame height in pixels
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap = None
        self.frame = None
        self.running = False
        self.lock = threading.Lock()
        
    def start(self):
        """Start the camera feed in a separate thread."""
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        if not self.cap.isOpened():
            raise Exception("Could not open camera. Check camera permissions and availability.")
        
        self.running = True
        self.thread = threading.Thread(target=self._update_frame, daemon=True)
        self.thread.start()
        print(f"Camera started: {self.width}x{self.height}")
        
    def _update_frame(self):
        """Internal method to continuously capture frames."""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame
    
    def read(self):
        """Get the latest frame from camera."""
        with self.lock:
            if self.frame is None:
                return None
            return self.frame.copy()
    
    def get_dimensions(self):
        """Return camera frame dimensions."""
        return self.width, self.height
    
    def stop(self):
        """Stop the camera feed and release resources."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
        print("Camera stopped")
    
    def is_running(self):
        """Check if camera is running."""
        return self.running and self.cap is not None and self.cap.isOpened()


