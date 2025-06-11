import pygame

class Square:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        # x, y: Position of tile on board, e.g. 1d <-> 1, 4
        self.width = width
        self.height = height
        # width, height: size of tile to be drawn(shown)
        self.abs_x = x * width
        self.abs_y = y * height
        self.abs_pos = (self.abs_x, self.abs_y)
        self.pos = (x, y)
        
        self.color = 'light' if (x + y) % 2 == 0 else 'dark'
        
        # Clean, elegant colors without shadows
        self.draw_color = (248, 225, 188) if self.color == 'light' else (171, 122, 87)  # Premium wood colors
        self.highlight_color = (255, 215, 0) if self.color == 'light' else (255, 165, 0)  # Gold highlight
        self.check_color = (255, 99, 99)  # Light red for check
        self.checkmate_color = (255, 0, 0)  # Bright red for checkmate
        
        # NEW: Last move highlight color - Xanh nước biển
        self.last_move_color = (70, 130, 180) if self.color == 'light' else (25, 95, 145)  # Steel blue
        
        # Clean move indicator colors
        self.valid_move_color = (50, 205, 50)  # Clean green
        self.capture_color = (220, 20, 60)  # Clean red
        
        self.occupying_piece = None
        self.coord = self.get_coord()
        self.highlight = False
        self.check = False
        self.checkmate = False
        self.last_move = False  # NEW: Track if this square is part of last move
        self.rect = pygame.Rect(
            self.abs_x, self.abs_y,
            self.width, self.height
        )

    # Get the formal notation of the tile
    def get_coord(self):
        columns = 'abcdefgh'
        return columns[self.x] + str(self.y + 1)

    def draw_clean_square(self, display, base_color):
        """Draw a clean, elegant square without shadows"""
        # Fill with base color
        pygame.draw.rect(display, base_color, self.rect)
        
        # Simple, clean border
        border_color = tuple(max(0, c - 30) for c in base_color)
        pygame.draw.rect(display, border_color, self.rect, 1)

    def draw_clean_move_indicator(self, display):
        """Draw clean move indicators without glow effects"""
        center_x = self.abs_x + self.width // 2
        center_y = self.abs_y + self.height // 2
        
        if self.occupying_piece is not None:
            # Draw simple ring for capture moves
            pygame.draw.circle(display, self.capture_color, (center_x, center_y), 
                             self.width // 3, 3)
        else:
            # Draw simple filled circle for regular moves
            pygame.draw.circle(display, self.valid_move_color, (center_x, center_y), 
                             self.width // 6)

    def draw(self, display, draw_piece=True):
        # Determine the color to use - UPDATED PRIORITY
        if self.checkmate:
            color = self.checkmate_color
        elif self.check:
            color = self.check_color
        elif self.last_move:  # NEW: Last move highlighting has priority over normal highlight
            color = self.last_move_color
        elif self.highlight and not hasattr(self, 'is_move_indicator'):
            color = self.highlight_color
        else:
            color = self.draw_color
        
        # Draw the square with clean appearance
        self.draw_clean_square(display, color)
        
        # Draw clean move indicators if this square is highlighted as a valid move
        if self.highlight and hasattr(self, 'is_move_indicator'):
            self.draw_clean_move_indicator(display)
        
        # Draw chess piece without shadow effects
        if self.occupying_piece is not None and draw_piece:
            centering_rect = self.occupying_piece.img.get_rect()
            centering_rect.center = self.rect.center
            
            # Simply draw the piece without any shadow
            display.blit(self.occupying_piece.img, centering_rect.topleft)