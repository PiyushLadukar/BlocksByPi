import numpy as np

class GridWorld:
    """
    3D voxel grid system for Minecraft-style block placement.
    Manages block coordinates, colors, and world state.
    """
    
    def __init__(self, grid_size=20, block_size=0.5):
        """
        Initialize the 3D grid world.
        
        Args:
            grid_size: Number of blocks per dimension
            block_size: Size of each block in world units
        """
        self.grid_size = grid_size
        self.block_size = block_size
        self.blocks = {}  # Dictionary: (x, y, z) -> color
        
        # Block color palette (RGB values 0-1)
        self.color_palette = [
            (0.0, 0.8, 1.0),   # Neon blue (default)
            (0.0, 1.0, 0.8),   # Cyan
            (0.8, 0.0, 1.0),   # Purple
            (0.0, 1.0, 0.3),   # Green
            (1.0, 0.5, 0.0),   # Orange
        ]
        self.current_color_index = 0
        
        # Cursor position for block placement
        self.cursor_pos = [grid_size // 2, 0, grid_size // 2]
        
    def world_to_grid(self, x, y, z):
        """
        Convert world coordinates to grid coordinates.
        
        Args:
            x, y, z: World coordinates
            
        Returns:
            Grid coordinates (snapped to grid)
        """
        gx = int(np.round(x / self.block_size))
        gy = int(np.round(y / self.block_size))
        gz = int(np.round(z / self.block_size))
        
        # Clamp to grid bounds
        gx = max(0, min(self.grid_size - 1, gx))
        gy = max(0, min(self.grid_size - 1, gy))
        gz = max(0, min(self.grid_size - 1, gz))
        
        return (gx, gy, gz)
    
    def grid_to_world(self, gx, gy, gz):
        """
        Convert grid coordinates to world coordinates.
        
        Args:
            gx, gy, gz: Grid coordinates
            
        Returns:
            World coordinates (center of block)
        """
        x = gx * self.block_size
        y = gy * self.block_size
        z = gz * self.block_size
        return (x, y, z)
    
    def place_block(self, gx, gy, gz, color=None):
        """
        Place a block at grid coordinates.
        
        Args:
            gx, gy, gz: Grid coordinates
            color: RGB color tuple (or None for current color)
        """
        if 0 <= gx < self.grid_size and 0 <= gy < self.grid_size and 0 <= gz < self.grid_size:
            if color is None:
                color = self.color_palette[self.current_color_index]
            self.blocks[(gx, gy, gz)] = color
            return True
        return False
    
    def remove_block(self, gx, gy, gz):
        """
        Remove a block from grid coordinates.
        
        Args:
            gx, gy, gz: Grid coordinates
        """
        if (gx, gy, gz) in self.blocks:
            del self.blocks[(gx, gy, gz)]
            return True
        return False
    
    def has_block(self, gx, gy, gz):
        """Check if a block exists at grid coordinates."""
        return (gx, gy, gz) in self.blocks
    
    def get_block_color(self, gx, gy, gz):
        """Get the color of a block at grid coordinates."""
        return self.blocks.get((gx, gy, gz))
    
    def get_all_blocks(self):
        """Get all blocks in the world."""
        return self.blocks.items()
    
    def clear_world(self):
        """Remove all blocks from the world."""
        self.blocks.clear()
        print("World cleared")
    
    def update_cursor(self, hand_x, hand_y, frame_width, frame_height):
        """
        Update cursor position based on hand position.
        
        Args:
            hand_x, hand_y: Hand position in screen coordinates
            frame_width, frame_height: Camera frame dimensions
        """
        # Map hand position to grid coordinates
        # X axis: left-right on screen
        # Y axis: depth (hand distance simulated)
        # Z axis: up-down on screen
        
        norm_x = hand_x / frame_width
        norm_y = hand_y / frame_height
        
        self.cursor_pos[0] = int(norm_x * self.grid_size)
        self.cursor_pos[2] = int(norm_y * self.grid_size)
        
        # Clamp cursor
        self.cursor_pos[0] = max(0, min(self.grid_size - 1, self.cursor_pos[0]))
        self.cursor_pos[2] = max(0, min(self.grid_size - 1, self.cursor_pos[2]))
    
    def move_cursor_up(self):
        """Move cursor up (Y axis)."""
        if self.cursor_pos[1] < self.grid_size - 1:
            self.cursor_pos[1] += 1
    
    def move_cursor_down(self):
        """Move cursor down (Y axis)."""
        if self.cursor_pos[1] > 0:
            self.cursor_pos[1] -= 1
    
    def get_cursor_position(self):
        """Get current cursor grid position."""
        return tuple(self.cursor_pos)
    
    def cycle_color(self):
        """Switch to next color in palette."""
        self.current_color_index = (self.current_color_index + 1) % len(self.color_palette)
        print(f"Color changed to: {self.color_palette[self.current_color_index]}")
    
    def get_current_color(self):
        """Get current selected color."""
        return self.color_palette[self.current_color_index]
    
    def get_block_count(self):
        """Get total number of blocks in world."""
        return len(self.blocks)
