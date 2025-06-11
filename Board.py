import pygame
import chess
import math
from Square import Square
import json

columns = 'abcdefgh'

def get_pos_from_coord(coord:str):
    for i in range(8):
        if columns[i] == coord[0]:
            res = (i, 8 - int(coord[1]))
            break
    return res

def get_coord_from_pos(x, y):
    return columns[x] + str(8-y)

class TranspositionTable:
    """Transposition table for caching board evaluations"""
    def __init__(self, max_size=100000):
        self.table = {}
        self.max_size = max_size
        
    def get(self, board_hash):
        return self.table.get(board_hash)
    
    def store(self, board_hash, evaluation, depth):
        if len(self.table) >= self.max_size:
            # Remove oldest entries (simple FIFO)
            oldest_key = next(iter(self.table))
            del self.table[oldest_key]
        
        self.table[board_hash] = {
            'evaluation': evaluation,
            'depth': depth
        }
    
    def clear(self):
        self.table.clear()

class MoveHistory:
    """Enhanced move history with position tracking for threefold repetition"""
    def __init__(self):
        self.moves = []
        self.positions = {}  # FEN -> count
        
    def add_move(self, move, fen):
        self.moves.append(move)
        self.positions[fen] = self.positions.get(fen, 0) + 1
        
    def is_threefold_repetition(self):
        return any(count >= 3 for count in self.positions.values())
    
    def get_last_moves(self, n):
        return self.moves[-n:] if len(self.moves) >= n else self.moves
    
    def clear(self):
        self.moves.clear()
        self.positions.clear()

class GUI_Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tile_width = width // 8
        self.tile_height = height // 8
        self.selected_piece = None
        self.turn = chess.WHITE
        self.config = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]
        self.chess_board = chess.Board()
        self.squares = self.generate_squares()
        self.setup_board()
        
        # Animation variables - FIXED
        self.animating_piece = None
        self.animating_piece_img = None
        self.animation_start_pos = None
        self.animation_target_pos = None
        self.animation_progress = 0.0
        self.animation_speed = 0.15  # Slightly faster
        self.is_animating = False
        self.animation_source_square = None  # Track source square
        
        # Enhanced features
        self.transposition_table = TranspositionTable()
        self.move_history = MoveHistory()
        self.evaluation_history = []
        
        # Time management
        self.time_white = 300.0  # 5 minutes
        self.time_black = 300.0  # 5 minutes
        self.increment = 3.0     # 3 seconds per move

    def generate_squares(self):
        output = set()
        for y in range(8):
            for x in range(8):
                output.add(Square(x, y, self.tile_width, self.tile_height))
        return output

    def get_square_from_pos(self, pos):
        for square in self.squares:
            if (square.x, square.y) == (pos[0], pos[1]):
                return square

    def get_piece_from_pos(self, pos):
        return self.get_square_from_pos(pos).occupying_piece
    
    def setup_board(self):
        for y, row in enumerate(self.config):
            for x, piece in enumerate(row):
                if piece != '':
                    square = self.get_square_from_pos((x, y))
                    # Set occupying piece in square based on config
                    if piece[1] == 'R':
                        square.occupying_piece = Piece((x,y), chess.ROOK, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
                    elif piece[1] == 'N':
                        square.occupying_piece = Piece((x,y), chess.KNIGHT, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
                    elif piece[1] == 'B':
                        square.occupying_piece = Piece((x,y), chess.BISHOP, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
                    elif piece[1] == 'Q':
                        square.occupying_piece = Piece((x,y), chess.QUEEN, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
                    elif piece[1] == 'K':
                        square.occupying_piece = Piece((x,y), chess.KING, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
                    elif piece[1] == 'P':
                        square.occupying_piece = Piece((x,y), chess.PAWN, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
    
    def update_gui_from_chess_board(self):
        """Update GUI pieces to match chess board state"""
        # Clear all pieces first
        for square in self.squares:
            square.occupying_piece = None
        
        # Set pieces based on chess board
        for square in chess.SQUARES:
            piece = self.chess_board.piece_at(square)
            if piece:
                file = chess.square_file(square)
                rank = chess.square_rank(square)
                gui_pos = (file, 7 - rank)  # Convert to GUI coordinates
                gui_square = self.get_square_from_pos(gui_pos)
                if gui_square:
                    gui_square.occupying_piece = Piece(gui_pos, piece.piece_type, piece.color, self)
    
    def get_possible_moves(self):
        res = set()
        for square in self.squares:
            if square.occupying_piece is not None:
                for valid_move in square.occupying_piece.get_moves():
                    res.add(valid_move)
        return res
    
    def is_checkmate(self):
        return self.chess_board.is_checkmate()
    
    def is_draw(self):
        return (self.chess_board.is_stalemate() or 
                self.chess_board.is_seventyfive_moves() or 
                self.chess_board.is_fivefold_repetition() or 
                self.chess_board.is_insufficient_material() or
                self.move_history.is_threefold_repetition())
    
    def is_end_game(self):
        res = ''
        if self.is_checkmate():
            side = 'White' if self.turn == chess.BLACK else 'Black'
            res = side + ' wins!'
        elif self.is_draw():
            res = 'Draw!'
        if res != '':
            return res
        return False
    
    def get_game_phase(self):
        """Determine game phase for evaluation adjustments"""
        piece_count = len(self.chess_board.piece_map())
        if piece_count >= 24:
            return "opening"
        elif piece_count >= 12:
            return "middlegame"
        else:
            return "endgame"
    
    def evaluate_position_features(self):
        """Extract position features for neural network"""
        features = []
        
        # Board representation (8x8x12 for 6 piece types * 2 colors)
        board_tensor = []
        for rank in range(8):
            rank_data = []
            for file in range(8):
                square = chess.square(file, 7-rank)
                piece = self.chess_board.piece_at(square)
                piece_vector = [0] * 12  # 6 pieces * 2 colors
                if piece:
                    piece_idx = (piece.piece_type - 1) * 2 + (0 if piece.color else 1)
                    piece_vector[piece_idx] = 1
                rank_data.append(piece_vector)
            board_tensor.append(rank_data)
        
        # Additional features
        additional_features = [
            1 if self.chess_board.turn else 0,  # Turn
            1 if self.chess_board.has_kingside_castling_rights(chess.WHITE) else 0,
            1 if self.chess_board.has_queenside_castling_rights(chess.WHITE) else 0,
            1 if self.chess_board.has_kingside_castling_rights(chess.BLACK) else 0,
            1 if self.chess_board.has_queenside_castling_rights(chess.BLACK) else 0,
            self.chess_board.halfmove_clock / 100.0,  # Normalized
            len(list(self.chess_board.legal_moves)) / 40.0,  # Normalized mobility
        ]
        
        return {
            'board': board_tensor,
            'features': additional_features,
            'phase': self.get_game_phase()
        }
    
    def start_animation(self, piece, start_pos, target_pos):
        """Start animation for piece movement - FIXED"""
        print(f"Starting animation: {piece} from {start_pos} to {target_pos}")
        
        # Store animation data
        self.animating_piece = piece
        self.animating_piece_img = piece.img.copy()
        self.animation_start_pos = start_pos
        self.animation_target_pos = target_pos
        self.animation_progress = 0.0
        self.is_animating = True
        
        # IMPORTANT: Store source square to prevent piece disappearing
        self.animation_source_square = self.get_square_from_pos(start_pos)
    
    def update_animation(self):
        """Update animation progress - FIXED"""
        if self.is_animating:
            self.animation_progress += self.animation_speed
            
            if self.animation_progress >= 1.0:
                self.animation_progress = 1.0
                self.is_animating = False
                
                # CLEANUP: Clear animation data
                self.animating_piece = None
                self.animating_piece_img = None
                self.animation_source_square = None
                
                print("Animation completed")
    
    def get_animated_position(self):
        """Get current animated position using smooth easing - FIXED"""
        if not self.is_animating or self.animating_piece is None:
            return None
        
        # Enhanced smooth easing function
        t = self.animation_progress
        # Cubic easing for more natural movement
        t = t * t * (3.0 - 2.0 * t)  # Smoothstep
        
        start_x = self.animation_start_pos[0] * self.tile_width + self.tile_width // 2
        start_y = self.animation_start_pos[1] * self.tile_height + self.tile_height // 2
        target_x = self.animation_target_pos[0] * self.tile_width + self.tile_width // 2
        target_y = self.animation_target_pos[1] * self.tile_height + self.tile_height // 2
        
        current_x = start_x + (target_x - start_x) * t
        current_y = start_y + (target_y - start_y) * t
        
        return (current_x, current_y)
    
    def handle_click(self, mx, my):
        if self.is_animating:
            return None
            
        x = mx // self.tile_width
        y = my // self.tile_height
        clicked_square = self.get_square_from_pos((x, y))
        
        try:
            move_made = self.selected_piece.move(clicked_square)
        except AttributeError:
            move_made = None

        if move_made is not None:
            # Add to move history
            self.move_history.add_move(move_made, self.chess_board.fen())
            return move_made

        elif self.selected_piece is None:
            # Select a piece
            if clicked_square.occupying_piece is not None:
                if clicked_square.occupying_piece.color == self.turn:
                    self.selected_piece = clicked_square.occupying_piece

        elif clicked_square.occupying_piece is not None:
            if clicked_square.occupying_piece.color == self.turn:
                # Change selected piece
                self.selected_piece = clicked_square.occupying_piece
    
    def draw_luxury_border(self, display):
        """Draw an enhanced luxury wooden border"""
        border_width = 30
        
        # Create border surface
        border_surface = pygame.Surface((self.width + 2*border_width, self.height + 2*border_width))
        
        # Gradient background for border
        for y in range(border_surface.get_height()):
            ratio = y / border_surface.get_height()
            r = int(139 + (101 - 139) * ratio)
            g = int(116 + (67 - 116) * ratio)
            b = int(78 + (33 - 78) * ratio)
            pygame.draw.line(border_surface, (r, g, b), (0, y), (border_surface.get_width(), y))
        
        # Multiple border layers for depth
        colors = [(101, 67, 33), (139, 116, 78), (160, 140, 100)]
        widths = [6, 3, 1]
        for color, width in zip(colors, widths):
            pygame.draw.rect(border_surface, color, 
                           (border_width - width*3, border_width - width*3, 
                            self.width + width*6, self.height + width*6), width)
        
        return border_surface
    
    def draw_coordinates(self, surface, font, border_width):
        """Draw elegant coordinate labels"""
        text_color = (101, 67, 33)
        
        # Files (a-h) - bottom
        for i, letter in enumerate('abcdefgh'):
            text = font.render(letter, True, text_color)
            x = border_width + i * self.tile_width + self.tile_width // 2 - text.get_width() // 2
            y = self.height + border_width + 5
            surface.blit(text, (x, y))
        
        # Ranks (1-8) - left side
        for i in range(8):
            number = str(8 - i)
            text = font.render(number, True, text_color)
            x = border_width - 20
            y = border_width + i * self.tile_height + self.tile_height // 2 - text.get_height() // 2
            surface.blit(text, (x, y))
    
    def draw(self, display):
        # Create enhanced border surface
        border_width = 30
        board_surface = self.draw_luxury_border(display)
        
        # Create the main board surface
        main_surface = pygame.Surface((self.width, self.height))
        
        cur_turn = self.turn
        
        # Clear all highlights first
        for square in self.squares:
            square.highlight = False
            if hasattr(square, 'is_move_indicator'):
                delattr(square, 'is_move_indicator')
        
        # Set highlights for selected piece and valid moves
        if self.selected_piece is not None:
            self.get_square_from_pos(self.selected_piece.pos).highlight = True
            for square in self.selected_piece.get_valid_moves():
                square.highlight = True
                square.is_move_indicator = True
        
        # Draw squares with enhanced effects - FIXED RENDERING
        for square in self.squares:
            # Check status for kings
            if square.occupying_piece is not None:
                if square.occupying_piece.piece_type == chess.KING and square.occupying_piece.color == cur_turn:
                    if self.is_checkmate():
                        square.checkmate = True
                    elif self.chess_board.is_check():
                        square.check = True
                    else:
                        square.check = False
                        square.checkmate = False
                else:
                    square.check = square.checkmate = False
            else:
                square.check = square.checkmate = False
            
            # FIXED: Better logic for determining when to draw pieces
            draw_piece = True
            
            # Only hide piece if it's currently being animated AND it's at the source square
            if (self.is_animating and 
                self.animating_piece and 
                self.animation_source_square and
                square == self.animation_source_square):
                draw_piece = False
                print(f"Hiding piece at source square: {square.pos}")
            
            # Draw the square (with or without piece)
            square.draw(main_surface, draw_piece)
        
        # Draw animated piece with enhanced effects - FIXED
        if self.is_animating and self.animating_piece and self.animating_piece_img:
            animated_pos = self.get_animated_position()
            if animated_pos:
                # Enhanced shadow for animated piece
                piece_rect = self.animating_piece_img.get_rect()
                piece_rect.center = animated_pos
                
                # Multiple shadow layers for depth
                shadow_offsets = [(4, 4), (3, 3), (2, 2)]
                shadow_alphas = [20, 30, 40]
                for offset, alpha in zip(shadow_offsets, shadow_alphas):
                    shadow_surface = pygame.Surface((piece_rect.width, piece_rect.height), pygame.SRCALPHA)
                    shadow_surface.fill((0, 0, 0, alpha))
                    main_surface.blit(shadow_surface, (piece_rect.topleft[0] + offset[0], piece_rect.topleft[1] + offset[1]))
                
                # Draw the animated piece
                main_surface.blit(self.animating_piece_img, piece_rect.topleft)
                print(f"Drawing animated piece at: {animated_pos}")
        
        # Update animation
        self.update_animation()
        
        # Blit main surface to board surface
        board_surface.blit(main_surface, (border_width, border_width))
        
        # Draw coordinates
        try:
            font = pygame.font.Font(None, 24)
            self.draw_coordinates(board_surface, font, border_width)
        except:
            pass
        
        # Blit to main display
        display.blit(board_surface, (0, 0))


class Piece(chess.Piece):
    def __init__(self, pos, type:chess.PieceType, color:chess.Color, board:GUI_Board):
        super().__init__(type, color)
        self.pos = pos
        self.coord = get_coord_from_pos(*self.pos)
        self.x = self.pos[0]
        self.y = self.pos[1]
        self.gui_board = board
        self.img = self.get_img()
        self.move_count = 0  # Track number of moves for this piece
    
    def get_img(self):
        img_path = 'data/imgs/'
        pieces = ['_pawn.png', '_knight.png', '_bishop.png', '_rook.png', '_queen.png', '_king.png']
        if self.color == chess.WHITE:
            img_path += 'w'
        else:
            img_path += 'b'
        img_path += pieces[self.piece_type - 1]
        res = pygame.image.load(img_path)
        res = pygame.transform.scale(res, (self.gui_board.tile_width - 35, self.gui_board.tile_height - 35))
        return res
    
    def get_moves(self):
        output = set()
        available_moves = {move.uci() for move in self.gui_board.chess_board.generate_legal_moves()}
        
        for move in available_moves:
            if move[0:2] == self.coord:
                output.add(move)
        return output
    
    def get_valid_moves(self):
        output = set()
        for move in self.get_moves():
            sq_pos = get_pos_from_coord(move[2:4])
            square = self.gui_board.get_square_from_pos(sq_pos)
            output.add(square)
        return output

    def move(self, square, force=False):
        # Clear highlights
        for i in self.gui_board.squares:
            i.highlight = False
        
        mark_castling = False
        mark_en_passant = False
        if self.piece_type == chess.KING and abs(square.x - self.x) == 2 and self.gui_board.chess_board.has_castling_rights(self.gui_board.turn):
            mark_castling = True
            side = 'KING_SIDE' if square.x > self.x else 'QUEEN_SIDE'
        if self.piece_type == chess.PAWN and abs(self.x - square.x) == 1 and abs(self.y - square.y) == 1 and square.occupying_piece == None:
            mark_en_passant = True
        
        if square in self.get_valid_moves() or force:           
            prev_square = self.gui_board.get_square_from_pos(self.pos)
            move_cur = self.coord
            
            # FIXED: Start animation before updating positions
            if not force:
                print(f"Starting move animation: {self.coord} -> {get_coord_from_pos(*square.pos)}")
                self.gui_board.start_animation(self, self.pos, square.pos)
            
            # Update piece position
            self.pos, self.x, self.y = square.pos, square.x, square.y
            self.coord = get_coord_from_pos(*self.pos)
            
            # Update board state
            prev_square.occupying_piece = None
            square.occupying_piece = self
            self.gui_board.selected_piece = None
            move_new = self.coord
            self.move_count += 1
            
            # Handle pawn promotion
            if self.piece_type == chess.PAWN:
                if (self.color == chess.WHITE and move_new[1] == '8') or (self.color == chess.BLACK and move_new[1] == '1'):
                    move_new += 'q'
                    self.piece_type = chess.QUEEN
                    self.img = self.get_img()
            
            # Update chess board
            if not force:
                self.gui_board.chess_board.push_san(move_cur + move_new)
            
            # Handle special moves
            if mark_en_passant:
                captured_pawn_at = self.gui_board.get_square_from_pos((square.x, prev_square.y))
                captured_pawn_at.occupying_piece = None
            
            if mark_castling:
                if self.gui_board.turn == chess.WHITE:
                    rook_cur_pos = (7, 7) if side == 'KING_SIDE' else (0, 7)
                    rook_new_pos = (5, 7) if side == 'KING_SIDE' else (3, 7)
                elif self.gui_board.turn == chess.BLACK:
                    rook_cur_pos = (7, 0) if side == 'KING_SIDE' else (0, 0)
                    rook_new_pos = (5, 0) if side == 'KING_SIDE' else (3, 0)
                rook = self.gui_board.get_piece_from_pos(rook_cur_pos)
                rook.move(self.gui_board.get_square_from_pos(rook_new_pos), force=True)
            
            # Switch turns
            if not force:
                self.gui_board.turn = chess.WHITE if self.gui_board.turn == chess.BLACK else chess.BLACK
            
            return move_cur + move_new
        
        else:
            self.gui_board.selected_piece = None
            return None