import cv2
import numpy as np
import math

class HologramRenderer:
    """
    Renders futuristic hologram blocks and Iron Man HUD on camera feed.
    Uses OpenCV for 2D overlay rendering with glow effects.
    """
    
    def __init__(self, frame_width, frame_height):
        """
        Initialize the hologram renderer.
        
        Args:
            frame_width: Width of camera frame
            frame_height: Height of camera frame
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Rendering settings
        self.show_grid = True
        self.show_hud = True
        self.glow_intensity = 30
        
        # Animation frame counter
        self.frame_count = 0
        
    def render_frame(self, frame, grid_world, hand_tracker):
        """
        Render hologram blocks and HUD on frame.
        
        Args:
            frame: Camera frame to render on
            grid_world: GridWorld instance with blocks
            hand_tracker: HandTracker instance
            
        Returns:
            Rendered frame with holograms
        """
        self.frame_count += 1
        output = frame.copy()
        
        # Create overlay for transparency
        overlay = output.copy()
        
        # Render grid (if enabled)
        if self.show_grid:
            self._render_grid(overlay, grid_world)
        
        # Render cursor
        self._render_cursor(overlay, grid_world)
        
        # Render all blocks
        self._render_blocks(overlay, grid_world)
        
        # Blend overlay with original frame (alpha blending)
        cv2.addWeighted(overlay, 0.7, output, 0.3, 0, output)
        
        # Render HUD around hand (if hand detected)
        if self.show_hud and hand_tracker.get_hand_position():
            self._render_hud(output, hand_tracker)
        
        # Render UI info
        self._render_ui_info(output, grid_world, hand_tracker)
        
        return output
    
    def _render_grid(self, frame, grid_world):
        """Render futuristic grid ground."""
        grid_color = (0, 100, 150)
        grid_spacing = self.frame_width // 15
        
        # Vertical lines
        for i in range(0, self.frame_width, grid_spacing):
            cv2.line(frame, (i, 0), (i, self.frame_height), grid_color, 1)
        
        # Horizontal lines
        for i in range(0, self.frame_height, grid_spacing):
            cv2.line(frame, (0, i), (self.frame_width, i), grid_color, 1)
    
    def _render_cursor(self, frame, grid_world):
        """Render placement cursor."""
        cursor_pos = grid_world.get_cursor_position()
        
        # Map grid position to screen position
        screen_x = int((cursor_pos[0] / grid_world.grid_size) * self.frame_width)
        screen_y = int((cursor_pos[2] / grid_world.grid_size) * self.frame_height)
        
        # Pulsing animation
        pulse = int(20 + 15 * math.sin(self.frame_count * 0.15))
        
        # Draw cursor as crosshair
        color = (0, 255, 255)  # Cyan
        cv2.circle(frame, (screen_x, screen_y), pulse, color, 2)
        cv2.line(frame, (screen_x - 20, screen_y), (screen_x + 20, screen_y), color, 2)
        cv2.line(frame, (screen_x, screen_y - 20), (screen_x, screen_y + 20), color, 2)
        
        # Cursor coordinates text
        cv2.putText(frame, f"({cursor_pos[0]}, {cursor_pos[1]}, {cursor_pos[2]})",
                   (screen_x + 30, screen_y - 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.5, color, 1)
    
    def _render_blocks(self, frame, grid_world):
        """Render all hologram blocks."""
        for (gx, gy, gz), color in grid_world.get_all_blocks():
            self._render_block(frame, gx, gy, gz, color, grid_world)
    
    def _render_block(self, frame, gx, gy, gz, color, grid_world):
        """Render a single hologram block."""
        # Map grid to screen coordinates
        screen_x = int((gx / grid_world.grid_size) * self.frame_width)
        screen_y = int((gz / grid_world.grid_size) * self.frame_height)
        
        # Block size varies with Y position (height)
        base_size = 40
        size_scale = 1.0 + (gy * 0.1)  # Blocks higher up appear larger
        block_size = int(base_size * size_scale)
        
        # Convert color to BGR (0-255)
        bgr_color = (int(color[2] * 255), int(color[1] * 255), int(color[0] * 255))
        
        # Draw block as rectangle with glow
        top_left = (screen_x - block_size // 2, screen_y - block_size // 2)
        bottom_right = (screen_x + block_size // 2, screen_y + block_size // 2)
        
        # Glow effect (multiple rectangles with decreasing alpha)
        for i in range(3, 0, -1):
            glow_size = block_size + i * 5
            glow_top_left = (screen_x - glow_size // 2, screen_y - glow_size // 2)
            glow_bottom_right = (screen_x + glow_size // 2, screen_y + glow_size // 2)
            cv2.rectangle(frame, glow_top_left, glow_bottom_right, bgr_color, -1)
        
        # Main block
        cv2.rectangle(frame, top_left, bottom_right, bgr_color, -1)
        
        # Border
        cv2.rectangle(frame, top_left, bottom_right, (255, 255, 255), 2)
        
        # Height indicator line
        if gy > 0:
            line_y = screen_y + block_size // 2
            cv2.line(frame, (screen_x, line_y), (screen_x, line_y + gy * 15), bgr_color, 2)
    
    def _render_hud(self, frame, hand_tracker):
        """Render Iron Man style HUD around hand."""
        hand_pos = hand_tracker.get_hand_position()
        if not hand_pos:
            return
        
        hx, hy = int(hand_pos[0]), int(hand_pos[1])
        
        # Rotating rings animation
        angle = (self.frame_count * 3) % 360
        
        # Outer ring
        radius1 = 80
        self._draw_arc(frame, hx, hy, radius1, angle, 180, (0, 200, 255), 2)
        
        # Middle ring
        radius2 = 60
        self._draw_arc(frame, hx, hy, radius2, -angle, 120, (0, 255, 200), 2)
        
        # Inner ring
        radius3 = 40
        self._draw_arc(frame, hx, hy, radius3, angle * 2, 90, (0, 255, 255), 2)
        
        # Corner brackets
        bracket_size = 15
        self._draw_brackets(frame, hx, hy, 100, bracket_size, (0, 255, 255))
        
        # Center reticle
        cv2.circle(frame, (hx, hy), 5, (0, 255, 255), 2)
        cv2.circle(frame, (hx, hy), 3, (0, 255, 255), -1)
        
        # Gesture indicator
        gesture = hand_tracker.get_gesture()
        if gesture:
            gesture_text = gesture.upper().replace('_', ' ')
            cv2.putText(frame, gesture_text, (hx + 110, hy), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    def _draw_arc(self, frame, cx, cy, radius, start_angle, arc_length, color, thickness):
        """Draw a circular arc."""
        axes = (radius, radius)
        cv2.ellipse(frame, (cx, cy), axes, 0, start_angle, start_angle + arc_length, color, thickness)
    
    def _draw_brackets(self, frame, cx, cy, size, bracket_len, color):
        """Draw corner brackets around a point."""
        # Top-left
        cv2.line(frame, (cx - size, cy - size), (cx - size + bracket_len, cy - size), color, 2)
        cv2.line(frame, (cx - size, cy - size), (cx - size, cy - size + bracket_len), color, 2)
        
        # Top-right
        cv2.line(frame, (cx + size, cy - size), (cx + size - bracket_len, cy - size), color, 2)
        cv2.line(frame, (cx + size, cy - size), (cx + size, cy - size + bracket_len), color, 2)
        
        # Bottom-left
        cv2.line(frame, (cx - size, cy + size), (cx - size + bracket_len, cy + size), color, 2)
        cv2.line(frame, (cx - size, cy + size), (cx - size, cy + size - bracket_len), color, 2)
        
        # Bottom-right
        cv2.line(frame, (cx + size, cy + size), (cx + size - bracket_len, cy + size), color, 2)
        cv2.line(frame, (cx + size, cy + size), (cx + size, cy + size - bracket_len), color, 2)
    
    def _render_ui_info(self, frame, grid_world, hand_tracker):
        """Render UI information overlay."""
        # Background panel
        cv2.rectangle(frame, (10, 10), (300, 150), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (300, 150), (0, 200, 255), 2)
        
        # Title
        cv2.putText(frame, "BlocksByPi", (20, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Info text
        y_offset = 60
        info_texts = [
            f"Blocks: {grid_world.get_block_count()}",
            f"Cursor: {grid_world.get_cursor_position()}",
            f"Color: RGB{grid_world.get_current_color()}"
        ]
        
        for text in info_texts:
            cv2.putText(frame, text, (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += 25
        
        # Controls hint
        cv2.rectangle(frame, (10, self.frame_height - 100), (350, self.frame_height - 10), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, self.frame_height - 100), (350, self.frame_height - 10), (0, 200, 255), 2)
        
        controls = [
            "ESC: Exit | R: Reset | G: Grid | H: HUD",
            "Open Palm: Place | Fist: Delete",
            "Index: Move | Thumb Up: Color"
        ]
        
        y_offset = self.frame_height - 80
        for text in controls:
            cv2.putText(frame, text, (15, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            y_offset += 20
    
    def toggle_grid(self):
        """Toggle grid visibility."""
        self.show_grid = not self.show_grid
        print(f"Grid: {'ON' if self.show_grid else 'OFF'}")
    
    def toggle_hud(self):
        """Toggle HUD visibility."""
        self.show_hud = not self.show_hud
        print(f"HUD: {'ON' if self.show_hud else 'OFF'}")


