#build by Piyushimp
import cv2
import sys
import time
from camera import CameraFeed
from hand_tracking import HandTracker
from grid_world import GridWorld
from hologram_renderer import HologramRenderer

class IronManARBuilder:
    """
    Main application class that orchestrates all modules.
    """
    
    def __init__(self):
        """Initialize all system components."""
        print("="*60)
        print("BlocksByPi")
        print("="*60)
        
        # Initialize camera
        print("\n[1/4] Initializing camera...")
        self.camera = CameraFeed(camera_id=0, width=1280, height=720)
        self.camera.start()
        time.sleep(1)  # Wait for camera to warm up
        
        # Initialize hand tracking
        print("[2/4] Loading hand tracking model...")
        self.hand_tracker = HandTracker(max_hands=1)
        
        # Initialize grid world
        print("[3/4] Creating 3D grid world...")
        self.grid_world = GridWorld(grid_size=20, block_size=0.5)
        
        # Initialize renderer
        print("[4/4] Setting up hologram renderer...")
        width, height = self.camera.get_dimensions()
        self.renderer = HologramRenderer(width, height)
        
        print("\n✓ System ready!\n")
        
        # State variables
        self.running = False
        self.last_gesture = None
        self.gesture_cooldown = 0
        self.fps_counter = FPSCounter()
        
    def run(self):
        """Main application loop."""
        self.running = True
        
        print("Starting AR Builder...")
        print("\nControls:")
        print("  ESC - Exit")
        print("  R - Reset world")
        print("  G - Toggle grid")
        print("  H - Toggle HUD")
        print("  Q/E - Move cursor up/down\n")
        
        try:
            while self.running:
                # Get camera frame
                frame = self.camera.read()
                if frame is None:
                    continue
                
                # Process hand tracking
                frame = self.hand_tracker.process_frame(frame)
                
                # Update cursor based on hand position
                hand_pos = self.hand_tracker.get_hand_position()
                if hand_pos:
                    self.grid_world.update_cursor(hand_pos[0], hand_pos[1], 
                                                  frame.shape[1], frame.shape[0])
                
                # Handle gestures
                self._handle_gestures()
                
                # Render holograms
                output = self.renderer.render_frame(frame, self.grid_world, self.hand_tracker)
                
                # Add FPS counter
                fps = self.fps_counter.update()
                cv2.putText(output, f"FPS: {fps:.1f}", (10, self.renderer.frame_height - 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Display
                cv2.imshow('Iron Man AR Builder', output)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if not self._handle_keyboard(key):
                    break
                
                # Gesture cooldown
                if self.gesture_cooldown > 0:
                    self.gesture_cooldown -= 1
                    
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def _handle_gestures(self):
        """Process hand gestures for block building."""
        gesture = self.hand_tracker.get_gesture()
        
        # Only process new gestures after cooldown
        if gesture and gesture != self.last_gesture and self.gesture_cooldown == 0:
            cursor = self.grid_world.get_cursor_position()
            
            if gesture == 'place':
                # Place block at cursor
                if self.grid_world.place_block(*cursor):
                    print(f"Block placed at {cursor}")
                    self.gesture_cooldown = 15  # Prevent spam
                    
            elif gesture == 'delete':
                # Remove block at cursor
                if self.grid_world.remove_block(*cursor):
                    print(f"Block removed from {cursor}")
                    self.gesture_cooldown = 15
                    
            elif gesture == 'change_color':
                # Cycle color palette
                self.grid_world.cycle_color()
                self.gesture_cooldown = 30  # Longer cooldown for color change
            
            self.last_gesture = gesture
        
        # Reset last gesture if hand is idle
        if gesture is None:
            self.last_gesture = None
    
    def _handle_keyboard(self, key):
        """Handle keyboard input.
        
        Returns:
            False to exit, True to continue
        """
        if key == 27:  # ESC
            return False
            
        elif key == ord('r') or key == ord('R'):
            # Reset world
            self.grid_world.clear_world()
            
        elif key == ord('g') or key == ord('G'):
            # Toggle grid
            self.renderer.toggle_grid()
            
        elif key == ord('h') or key == ord('H'):
            # Toggle HUD
            self.renderer.toggle_hud()
            
        elif key == ord('q') or key == ord('Q'):
            # Move cursor down
            self.grid_world.move_cursor_down()
            
        elif key == ord('e') or key == ord('E'):
            # Move cursor up
            self.grid_world.move_cursor_up()
        
        return True
    
    def cleanup(self):
        """Clean up resources."""
        print("\nShutting down...")
        self.running = False
        self.camera.stop()
        self.hand_tracker.close()
        cv2.destroyAllWindows()
        print("Goodbye!")

class FPSCounter:
    """Simple FPS counter for performance monitoring."""
    
    def __init__(self, smoothing=0.9):
        self.fps = 0
        self.last_time = time.time()
        self.smoothing = smoothing
    
    def update(self):
        current_time = time.time()
        elapsed = current_time - self.last_time
        self.last_time = current_time
        
        if elapsed > 0:
            instant_fps = 1.0 / elapsed
            self.fps = self.smoothing * self.fps + (1 - self.smoothing) * instant_fps
        
        return self.fps

def main():
    """Entry point of the application."""
    try:
        app = IronManARBuilder()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

