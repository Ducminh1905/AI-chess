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
    def __init__(self, width, height, player_color=chess.WHITE):
        self.width = width
        self.height = height
        self.tile_width = width // 8
        self.tile_height = height // 8
        self.selected_piece = None
        self.turn = chess.WHITE
        self.player_color = player_color  # NEW: Store player color
        self.flipped = (player_color == chess.BLACK)  # NEW: Flip board if player is black
        
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
        
        # Animation variables
        self.animating_piece = None
        self.animating_piece_img = None
        self.animation_start_pos = None
        self.animation_target_pos = None
        self.animation_progress = 0.0
        self.animation_speed = 0.15
        self.is_animating = False
        self.animation_source_square = None
        
        # Last move highlighting
        self.last_move_source = None
        self.last_move_target = None
        
        # Enhanced features
        self.transposition_table = TranspositionTable()
        self.move_history = MoveHistory()
        self.evaluation_history = []
        
        # Undo functionality - SIMPLIFIED
        self.board_states = []
        self.gui_states = []
        self.max_undo_states = 100  # Cho phép undo tối đa 50 lần
        
        # Time management
        self.time_white = 300.0
        self.time_black = 300.0
        self.increment = 3.0

    def flip_board(self):
        """Flip the board view"""
        self.flipped = not self.flipped
        self.update_gui_from_chess_board()
        print(f"Board flipped: {self.flipped}")

    def set_player_color(self, color):
        """Set player color and adjust board orientation"""
        self.player_color = color
        self.flipped = (color == chess.BLACK)
        self.update_gui_from_chess_board()
        print(f"Player color set to: {'BLACK' if color == chess.BLACK else 'WHITE'}")
        print(f"Board flipped: {self.flipped}")

    def get_display_position(self, chess_pos):
        """Convert chess position to display position based on board orientation"""
        x, y = chess_pos
        if self.flipped:
            return (7 - x, 7 - y)
        return (x, y)

    def get_chess_position(self, display_pos):
        """Convert display position to chess position based on board orientation"""
        x, y = display_pos
        if self.flipped:
            return (7 - x, 7 - y)
        return (x, y)

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
                    # Get display position (may be flipped)
                    display_pos = self.get_display_position((x, y))
                    square = self.get_square_from_pos(display_pos)
                    
                    # Set occupying piece in square based on config
                    if piece[1] == 'R':
                        square.occupying_piece = Piece(display_pos, chess.ROOK, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
                    elif piece[1] == 'N':
                        square.occupying_piece = Piece(display_pos, chess.KNIGHT, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
                    elif piece[1] == 'B':
                        square.occupying_piece = Piece(display_pos, chess.BISHOP, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
                    elif piece[1] == 'Q':
                        square.occupying_piece = Piece(display_pos, chess.QUEEN, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
                    elif piece[1] == 'K':
                        square.occupying_piece = Piece(display_pos, chess.KING, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
                    elif piece[1] == 'P':
                        square.occupying_piece = Piece(display_pos, chess.PAWN, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
    
    def update_gui_from_chess_board(self):
        """Update GUI pieces to match chess board state with proper board orientation"""
        # Clear all pieces first
        for square in self.squares:
            square.occupying_piece = None
        
        # Set pieces based on chess board
        for square in chess.SQUARES:
            piece = self.chess_board.piece_at(square)
            if piece:
                file = chess.square_file(square)
                rank = chess.square_rank(square)
                chess_pos = (file, 7 - rank)  # Convert to chess coordinates
                
                # Convert to display coordinates (may be flipped)
                display_pos = self.get_display_position(chess_pos)
                gui_square = self.get_square_from_pos(display_pos)
                
                if gui_square:
                    gui_square.occupying_piece = Piece(display_pos, piece.piece_type, piece.color, self)
    
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
    
    def set_last_move_highlight(self, source_pos, target_pos):
        """Set highlighting for the last move"""
        # Clear previous last move highlights
        for square in self.squares:
            square.last_move = False
        
        # Set new last move highlights
        if source_pos:
            # Convert chess position to display position
            display_source = self.get_display_position(source_pos)
            source_square = self.get_square_from_pos(display_source)
            if source_square:
                source_square.last_move = True
                self.last_move_source = source_square
                print(f"Highlighting last move source: {source_pos} -> display: {display_source}")
        
        if target_pos:
            # Convert chess position to display position
            display_target = self.get_display_position(target_pos)
            target_square = self.get_square_from_pos(display_target)
            if target_square:
                target_square.last_move = True
                self.last_move_target = target_square
                print(f"Highlighting last move target: {target_pos} -> display: {display_target}")
    
    def clear_last_move_highlight(self):
        """Clear all last move highlights"""
        for square in self.squares:
            square.last_move = False
        self.last_move_source = None
        self.last_move_target = None

    def save_board_state(self):
        """Save current board state - SIMPLIFIED VERSION"""
        try:
            board_state = {
                'fen': self.chess_board.fen(),
                'turn': self.turn,
                'last_move_source': self.last_move_source.pos if self.last_move_source else None,
                'last_move_target': self.last_move_target.pos if self.last_move_target else None
            }
            
            # Save GUI state (đơn giản hóa)
            gui_state = {}
            for square in self.squares:
                if square.occupying_piece:
                    gui_state[square.pos] = {
                        'type': square.occupying_piece.piece_type,
                        'color': square.occupying_piece.color
                    }
            
            self.board_states.append(board_state)
            self.gui_states.append(gui_state)
            
            # Keep reasonable number of states (tăng lên để cho phép undo nhiều)
            max_states = 100  # Cho phép undo tối đa 50 lần (100 states / 2)
            if len(self.board_states) > max_states:
                self.board_states.pop(0)
                self.gui_states.pop(0)
            
            print(f"SAVE DEBUG: Saved state. Total states: {len(self.board_states)}")
            
        except Exception as e:
            print(f"SAVE ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    def undo_last_move(self):
        """
        Undo 2 moves gần nhất (1 của player + 1 của AI)
        SIMPLIFIED VERSION - Chỉ cần hoạt động đúng
        """
        print(f"UNDO DEBUG: Starting undo...")
        print(f"UNDO DEBUG: Current board states available: {len(self.board_states)}")
        print(f"UNDO DEBUG: Current FEN: {self.chess_board.fen()}")
        print(f"UNDO DEBUG: Current turn: {'WHITE' if self.turn == chess.WHITE else 'BLACK'}")
        
        # Cần ít nhất 2 moves để undo
        if len(self.board_states) < 2:
            print("UNDO ERROR: Cần ít nhất 2 moves để undo")
            return None
        
        try:
            # Lấy state từ 2 moves trước (index -2)
            target_state = self.board_states[-2]
            target_gui_state = self.gui_states[-2]
            
            print(f"UNDO DEBUG: Target FEN: {target_state['fen']}")
            print(f"UNDO DEBUG: Target turn: {'WHITE' if target_state['turn'] == chess.WHITE else 'BLACK'}")
            
            # Xóa 2 states cuối (current + previous)
            self.board_states = self.board_states[:-2]
            self.gui_states = self.gui_states[:-2]
            
            print(f"UNDO DEBUG: Removed 2 states, remaining: {len(self.board_states)}")
            
            # Restore chess board từ FEN
            self.chess_board = chess.Board(target_state['fen'])
            self.turn = target_state['turn']
            
            print(f"UNDO DEBUG: Restored chess board, turn = {'WHITE' if self.turn == chess.WHITE else 'BLACK'}")
            
            # CRITICAL FIX: Clear transposition table after undo
            self.transposition_table.clear()
            print("UNDO DEBUG: Cleared transposition table to avoid stale cache")
            
            # Clear tất cả GUI pieces
            for square in self.squares:
                square.occupying_piece = None
                square.highlight = False
                square.check = False
                square.checkmate = False
                square.last_move = False
                if hasattr(square, 'is_move_indicator'):
                    delattr(square, 'is_move_indicator')
            
            # Restore pieces từ chess board với board orientation
            pieces_restored = 0
            for chess_square in chess.SQUARES:
                piece = self.chess_board.piece_at(chess_square)
                if piece:
                    file = chess.square_file(chess_square)
                    rank = chess.square_rank(chess_square)
                    chess_pos = (file, 7 - rank)  # Convert to chess coordinates
                    
                    # Convert to display coordinates (may be flipped)
                    display_pos = self.get_display_position(chess_pos)
                    gui_square = self.get_square_from_pos(display_pos)
                    
                    if gui_square:
                        new_piece = Piece(display_pos, piece.piece_type, piece.color, self)
                        gui_square.occupying_piece = new_piece
                        pieces_restored += 1
            
            print(f"UNDO DEBUG: Restored {pieces_restored} pieces")
            
            # Restore last move highlighting nếu có
            if target_state.get('last_move_source') and target_state.get('last_move_target'):
                # Convert stored positions back to chess coordinates for highlighting
                chess_source = self.get_chess_position(target_state['last_move_source'])
                chess_target = self.get_chess_position(target_state['last_move_target'])
                self.set_last_move_highlight(chess_source, chess_target)
            else:
                self.clear_last_move_highlight()
            
            # Reset interactive state
            self.selected_piece = None
            self.is_animating = False
            self.animating_piece = None
            self.animating_piece_img = None
            self.animation_source_square = None
            self.animation_progress = 0.0
            
            # Verify board state
            legal_moves = list(self.chess_board.legal_moves)
            print(f"UNDO DEBUG: Legal moves available: {len(legal_moves)}")
            
            if len(legal_moves) == 0:
                print("UNDO ERROR: No legal moves available after undo!")
                return None
            
            print(f"UNDO DEBUG: Final FEN: {self.chess_board.fen()}")
            print(f"UNDO DEBUG: Final turn: {'WHITE' if self.turn == chess.WHITE else 'BLACK'}")
            print("UNDO DEBUG: Undo completed successfully")
            
            return 2  # Successfully undid 2 moves
            
        except Exception as e:
            print(f"UNDO ERROR: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
        """Start animation for piece movement"""
        print(f"Starting animation: {piece} from {start_pos} to {target_pos}")
        
        # Store animation data
        self.animating_piece = piece
        self.animating_piece_img = piece.img.copy()
        self.animation_start_pos = start_pos
        self.animation_target_pos = target_pos
        self.animation_progress = 0.0
        self.is_animating = True
        
        # Store source square to prevent piece disappearing
        self.animation_source_square = self.get_square_from_pos(start_pos)
    
    def update_animation(self):
        """Update animation progress"""
        if self.is_animating:
            self.animation_progress += self.animation_speed
            
            if self.animation_progress >= 1.0:
                self.animation_progress = 1.0
                self.is_animating = False
                
                # Clear animation data
                self.animating_piece = None
                self.animating_piece_img = None
                self.animation_source_square = None
                
                print("Animation completed and cleared")
    
    def get_animated_position(self):
        """Get current animated position using smooth easing"""
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
        
        # Simple gradient background for border
        for y in range(border_surface.get_height()):
            ratio = y / border_surface.get_height()
            r = int(139 + (101 - 139) * ratio)
            g = int(116 + (67 - 116) * ratio)
            b = int(78 + (33 - 78) * ratio)
            pygame.draw.line(border_surface, (r, g, b), (0, y), (border_surface.get_width(), y))
        
        # Simple border layers
        colors = [(101, 67, 33), (139, 116, 78), (160, 140, 100)]
        widths = [6, 3, 1]
        for color, width in zip(colors, widths):
            pygame.draw.rect(border_surface, color, 
                           (border_width - width*3, border_width - width*3, 
                            self.width + width*6, self.height + width*6), width)
        
        return border_surface
    
    def draw_coordinates(self, surface, font, border_width):
        """Draw elegant coordinate labels with proper orientation"""
        text_color = (101, 67, 33)
        
        if self.flipped:
            # Files (h-a) and ranks (1-8) when flipped for black player
            files = 'hgfedcba'
            ranks = [str(i) for i in range(1, 9)]
        else:
            # Files (a-h) and ranks (8-1) for white player
            files = 'abcdefgh'
            ranks = [str(i) for i in range(8, 0, -1)]
        
        # Files - bottom
        for i, letter in enumerate(files):
            text = font.render(letter, True, text_color)
            x = border_width + i * self.tile_width + self.tile_width // 2 - text.get_width() // 2
            y = self.height + border_width + 5
            surface.blit(text, (x, y))
        
        # Ranks - left side
        for i, number in enumerate(ranks):
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
        
        # Draw squares and pieces
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
            
            # During animation, don't draw piece at source position
            should_draw_piece = True
            
            if (self.is_animating and 
                self.animation_source_square is not None and
                square.pos == self.animation_source_square.pos):
                should_draw_piece = False
                print(f"Animation active - hiding piece at {square.pos}")
            
            # Draw the square
            square.draw(main_surface, should_draw_piece)
        
        # Draw animated piece
        if self.is_animating and self.animating_piece and self.animating_piece_img:
            animated_pos = self.get_animated_position()
            if animated_pos:
                piece_rect = self.animating_piece_img.get_rect()
                piece_rect.center = animated_pos
                
                # Draw animated piece without shadows
                main_surface.blit(self.animating_piece_img, piece_rect.topleft)
                print(f"Drawing animated piece at: {animated_pos}")
        
        # Update animation
        self.update_animation()
        
        # Blit main surface to board surface
        board_surface.blit(main_surface, (border_width, border_width))
        
        # Draw coordinates with proper orientation
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
        self.x = self.pos[0]
        self.y = self.pos[1]
        self.gui_board = board
        self.img = self.get_img()
        self.move_count = 0  # Track number of moves for this piece
        
        # Calculate coordinate based on board orientation
        self.update_coord()
    
    def update_coord(self):
        """Update coordinate based on current board orientation"""
        # Convert display position to chess position
        chess_pos = self.gui_board.get_chess_position(self.pos)
        self.coord = get_coord_from_pos(*chess_pos)
    
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
            target_coord = move[2:4]
            chess_pos = get_pos_from_coord(target_coord)
            # Convert chess position to display position
            display_pos = self.gui_board.get_display_position(chess_pos)
            square = self.gui_board.get_square_from_pos(display_pos)
            if square:
                output.add(square)
        return output

    def move(self, square, force=False):
        # Clear highlights
        for i in self.gui_board.squares:
            i.highlight = False
        
        # Convert square position back to chess coordinates for move validation
        chess_pos = self.gui_board.get_chess_position(square.pos)
        target_coord = get_coord_from_pos(*chess_pos)
        
        mark_castling = False
        mark_en_passant = False
        
        # Check for castling (using chess coordinates)
        current_chess_pos = self.gui_board.get_chess_position(self.pos)
        if (self.piece_type == chess.KING and 
            abs(chess_pos[0] - current_chess_pos[0]) == 2 and 
            self.gui_board.chess_board.has_castling_rights(self.gui_board.turn)):
            mark_castling = True
            side = 'KING_SIDE' if chess_pos[0] > current_chess_pos[0] else 'QUEEN_SIDE'
        
        # Check for en passant (using chess coordinates) 
        if (self.piece_type == chess.PAWN and 
            abs(current_chess_pos[0] - chess_pos[0]) == 1 and 
            abs(current_chess_pos[1] - chess_pos[1]) == 1 and 
            square.occupying_piece == None):
            mark_en_passant = True
        
        if square in self.get_valid_moves() or force:
            print(f"MOVE DEBUG: Making move from {self.coord} to {target_coord}")
            print(f"MOVE DEBUG: Force = {force}")
            print(f"MOVE DEBUG: Current turn before move: {'WHITE' if self.gui_board.turn == chess.WHITE else 'BLACK'}")
            
            # Save state before making move (for undo) - FOR BOTH PLAYER AND AI
            try:
                self.gui_board.save_board_state()
                print("MOVE DEBUG: Board state saved successfully")
            except Exception as e:
                print(f"MOVE DEBUG: Error saving board state: {e}")
            
            prev_square = self.gui_board.get_square_from_pos(self.pos)
            move_cur = self.coord
            
            # Store positions for last move highlighting (in chess coordinates)
            source_chess_pos = self.gui_board.get_chess_position(self.pos)
            target_chess_pos = self.gui_board.get_chess_position(square.pos)
            
            # Different approach for player vs bot moves
            if not force:
                print(f"Player move with animation: {self.coord} -> {target_coord}")
                
                # Start animation BEFORE any position updates
                self.gui_board.start_animation(self, self.pos, square.pos)
                
            # Update piece position (same for both player and bot)
            self.pos, self.x, self.y = square.pos, square.x, square.y
            self.update_coord()  # Update coordinate based on new position
            
            # Update board state (same for both player and bot)
            prev_square.occupying_piece = None
            square.occupying_piece = self
            
            # Set last move highlighting using chess coordinates
            self.gui_board.set_last_move_highlight(source_chess_pos, target_chess_pos)
            
            self.gui_board.selected_piece = None
            move_new = target_coord
            self.move_count += 1
            
            # Handle pawn promotion
            if self.piece_type == chess.PAWN:
                if (self.color == chess.WHITE and move_new[1] == '8') or (self.color == chess.BLACK and move_new[1] == '1'):
                    move_new += 'q'
                    self.piece_type = chess.QUEEN
                    self.img = self.get_img()
            
            # Update chess board
            if not force:
                try:
                    print(f"MOVE DEBUG: Pushing move to chess board: {move_cur + move_new}")
                    self.gui_board.chess_board.push_san(move_cur + move_new)
                    print("MOVE DEBUG: Chess board updated successfully")
                except Exception as e:
                    print(f"MOVE DEBUG: Error updating chess board: {e}")
            
            # Handle special moves
            if mark_en_passant:
                # Convert captured pawn position to display coordinates
                captured_chess_pos = (chess_pos[0], current_chess_pos[1])
                captured_display_pos = self.gui_board.get_display_position(captured_chess_pos)
                captured_pawn_square = self.gui_board.get_square_from_pos(captured_display_pos)
                if captured_pawn_square:
                    captured_pawn_square.occupying_piece = None
            
            if mark_castling:
                # Handle castling rook movement with board orientation
                if self.gui_board.turn == chess.WHITE:
                    if side == 'KING_SIDE':
                        rook_chess_cur = (7, 7)
                        rook_chess_new = (5, 7)
                    else:  # QUEEN_SIDE
                        rook_chess_cur = (0, 7)
                        rook_chess_new = (3, 7)
                elif self.gui_board.turn == chess.BLACK:
                    if side == 'KING_SIDE':
                        rook_chess_cur = (7, 0)
                        rook_chess_new = (5, 0)
                    else:  # QUEEN_SIDE
                        rook_chess_cur = (0, 0)
                        rook_chess_new = (3, 0)
                
                # Convert to display coordinates
                rook_display_cur = self.gui_board.get_display_position(rook_chess_cur)
                rook_display_new = self.gui_board.get_display_position(rook_chess_new)
                
                rook = self.gui_board.get_piece_from_pos(rook_display_cur)
                if rook:
                    target_square = self.gui_board.get_square_from_pos(rook_display_new)
                    if target_square:
                        rook.move(target_square, force=True)
            
            # Switch turns
            if not force:
                old_turn = self.gui_board.turn
                self.gui_board.turn = chess.WHITE if self.gui_board.turn == chess.BLACK else chess.BLACK
                print(f"MOVE DEBUG: Turn switched from {'WHITE' if old_turn == chess.WHITE else 'BLACK'} to {'WHITE' if self.gui_board.turn == chess.WHITE else 'BLACK'}")
            
            print(f"MOVE DEBUG: Move completed: {move_cur + move_new}")
            return move_cur + move_new
        
        else:
            self.gui_board.selected_piece = None
            print(f"MOVE DEBUG: Invalid move attempted from {self.coord} to {target_coord}")
            return None