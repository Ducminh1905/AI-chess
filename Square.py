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
        
        # Enhanced luxury wood-like colors with golden accents
        self.draw_color = (248, 225, 188) if self.color == 'light' else (171, 122, 87)  # Premium wood colors
        self.highlight_color = (255, 215, 0) if self.color == 'light' else (255, 165, 0)  # Gold highlight
        self.check_color = (255, 99, 99)  # Light red for check
        self.checkmate_color = (255, 0, 0)  # Bright red for checkmate
        
        # Enhanced move indicator colors
        self.valid_move_color = (50, 205, 50, 180)  # Enhanced green with transparency
        self.capture_color = (220, 20, 60, 180)  # Enhanced red with transparency
        
        self.occupying_piece = None
        self.coord = self.get_coord()
        self.highlight = False
        self.check = False
        self.checkmate = False
        self.rect = pygame.Rect(
            self.abs_x, self.abs_y,
            self.width, self.height
        )

    # Get the formal notation of the tile
    def get_coord(self):
        columns = 'abcdefgh'
        return columns[self.x] + str(self.y + 1)

    def draw_luxury_wood_texture(self, display, base_color):
        """Draw a luxurious wood texture with golden accents"""
        # Base color with gradient effect
        for i in range(self.height):
            gradient_factor = 1.0 - (i / self.height) * 0.15
            current_color = tuple(int(c * gradient_factor) for c in base_color)
            pygame.draw.line(display, current_color, 
                           (self.abs_x, self.abs_y + i), 
                           (self.abs_x + self.width, self.abs_y + i))
        
        # Add wood grain texture
        grain_color = tuple(max(0, c - 20) for c in base_color)
        accent_color = tuple(min(255, c + 15) for c in base_color)
        
        # Horizontal grain lines with varying opacity
        for i in range(3, self.height - 3, 12):
            start_y = self.abs_y + i
            pygame.draw.line(display, grain_color, 
                           (self.abs_x + 8, start_y), 
                           (self.abs_x + self.width - 8, start_y), 2)
            # Add highlight line
            pygame.draw.line(display, accent_color, 
                           (self.abs_x + 8, start_y + 1), 
                           (self.abs_x + self.width - 12, start_y + 1), 1)
        
        # Enhanced border with multiple layers
        border_dark = tuple(max(0, c - 40) for c in base_color)
        border_light = tuple(min(255, c + 25) for c in base_color)
        
        # Outer darker border
        pygame.draw.rect(display, border_dark, self.rect, 2)
        # Inner lighter accent
        inner_rect = pygame.Rect(self.abs_x + 1, self.abs_y + 1, 
                                self.width - 2, self.height - 2)
        pygame.draw.rect(display, border_light, inner_rect, 1)

    def draw_enhanced_move_indicator(self, display):
        """Draw enhanced move indicators with glow effects"""
        center_x = self.abs_x + self.width // 2
        center_y = self.abs_y + self.height // 2
        
        if self.occupying_piece is not None:
            # Draw glowing ring for capture moves
            for radius in range(self.width // 3 + 5, self.width // 3 - 1, -1):
                alpha = 60 - (radius - self.width // 3 + 5) * 10
                color = (*self.capture_color[:3], max(0, alpha))
                
                # Create a surface for the alpha circle
                circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(circle_surface, color, (radius, radius), radius, 3)
                display.blit(circle_surface, (center_x - radius, center_y - radius))
        else:
            # Draw glowing filled circle for regular moves
            for radius in range(self.width // 6 + 3, self.width // 6 - 1, -1):
                alpha = 120 - (radius - self.width // 6 + 3) * 20
                color = (*self.valid_move_color[:3], max(0, alpha))
                
                circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(circle_surface, color, (radius, radius), radius)
                display.blit(circle_surface, (center_x - radius, center_y - radius))

    def draw(self, display, draw_piece=True):
        # Determine the color to use
        if self.checkmate:
            color = self.checkmate_color
        elif self.check:
            color = self.check_color
        elif self.highlight and not hasattr(self, 'is_move_indicator'):
            color = self.highlight_color
        else:
            color = self.draw_color
        
        # Draw the square with luxury wood texture
        self.draw_luxury_wood_texture(display, color)
        
        # Draw enhanced move indicators if this square is highlighted as a valid move
        if self.highlight and hasattr(self, 'is_move_indicator'):
            self.draw_enhanced_move_indicator(display)
        
        # Adds the chess piece icons with enhanced shadow
        if self.occupying_piece is not None and draw_piece:
            centering_rect = self.occupying_piece.img.get_rect()
            centering_rect.center = self.rect.center
            
            # Enhanced shadow effect with multiple layers
            shadow_offsets = [(3, 3), (2, 2), (1, 1)]
            shadow_alphas = [30, 40, 50]
            
            for offset, alpha in zip(shadow_offsets, shadow_alphas):
                shadow_surface = pygame.Surface((centering_rect.width, centering_rect.height), pygame.SRCALPHA)
                shadow_surface.fill((0, 0, 0, alpha))
                display.blit(shadow_surface, (centering_rect.topleft[0] + offset[0], 
                                            centering_rect.topleft[1] + offset[1]))
            
            # Draw the piece
            display.blit(self.occupying_piece.img, centering_rect.topleft)