import chess
import random as rd
import Board
import json
import numpy as np
from datetime import datetime
import os

squares = {
    chess.A8:(0,0), chess.B8:(0,1), chess.C8:(0,2), chess.D8:(0,3), chess.E8:(0,4), chess.F8:(0,5), chess.G8:(0,6), chess.H8:(0,7),
    chess.A7:(1,0), chess.B7:(1,1), chess.C7:(1,2), chess.D7:(1,3), chess.E7:(1,4), chess.F7:(1,5), chess.G7:(1,6), chess.H7:(1,7),
    chess.A6:(2,0), chess.B6:(2,1), chess.C6:(2,2), chess.D6:(2,3), chess.E6:(2,4), chess.F6:(2,5), chess.G6:(2,6), chess.H6:(2,7),
    chess.A5:(3,0), chess.B5:(3,1), chess.C5:(3,2), chess.D5:(3,3), chess.E5:(3,4), chess.F5:(3,5), chess.G5:(3,6), chess.H5:(3,7),
    chess.A4:(4,0), chess.B4:(4,1), chess.C4:(4,2), chess.D4:(4,3), chess.E4:(4,4), chess.F4:(4,5), chess.G4:(4,6), chess.H4:(4,7),
    chess.A3:(5,0), chess.B3:(5,1), chess.C3:(5,2), chess.D3:(5,3), chess.E3:(5,4), chess.F3:(5,5), chess.G3:(5,6), chess.H3:(5,7),
    chess.A2:(6,0), chess.B2:(6,1), chess.C2:(6,2), chess.D2:(6,3), chess.E2:(6,4), chess.F2:(6,5), chess.G2:(6,6), chess.H2:(6,7),
    chess.A1:(7,0), chess.B1:(7,1), chess.C1:(7,2), chess.D1:(7,3), chess.E1:(7,4), chess.F1:(7,5), chess.G1:(7,6), chess.H1:(7,7)
}

piece_values = {chess.PAWN:100, chess.KNIGHT:320, chess.BISHOP:330, chess.ROOK:500, chess.QUEEN:900, chess.KING:20000}

# Enhanced piece-square tables with game phase adjustments
board_values_opening = {
    chess.PAWN: [
        [  0,   0,   0,   0,   0,   0,   0,   0],
        [ 50,  50,  50,  50,  50,  50,  50,  50],
        [ 10,  10,  20,  30,  30,  20,  10,  10],
        [  5,   5,  10,  27,  27,  10,   5,   5],
        [  0,   0,   0,  25,  25,   0,   0,   0],
        [  5,  -5, -10,   0,   0, -10,  -5,   5],
        [  5,  10,  10, -25, -25,  10,  10,   5],
        [  0,   0,   0,   0,   0,   0,   0,   0]
    ],
    chess.KNIGHT: [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20,   0,   0,   0,   0, -20, -40],
        [-30,   0,  10,  15,  15,  10,   0, -30],
        [-30,   5,  15,  20,  20,  15,   5, -30],
        [-30,   0,  15,  20,  20,  15,   0, -30],
        [-30,   5,  10,  15,  15,  10,   5, -30],
        [-40, -20,   0,   5,   5,   0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50]
    ],
    chess.BISHOP: [
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10,   0,   0,   0,   0,   0,   0, -10],
        [-10,   0,   5,  10,  10,   5,   0, -10],
        [-10,   5,   5,  10,  10,   5,   5, -10],
        [-10,   0,  10,  10,  10,  10,   0, -10],
        [-10,  10,  10,  10,  10,  10,  10, -10],
        [-10,   5,   0,   0,   0,   0,   5, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20]
    ],
    chess.ROOK: [
        [  0,   0,   0,   0,   0,   0,   0,   0],
        [  5,  10,  10,  10,  10,  10,  10,   5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [ -5,   0,   0,   0,   0,   0,   0,  -5],
        [  0,   0,   0,   5,   5,   0,   0,   0]
    ],
    chess.QUEEN: [
        [-20, -10, -10,  -5,  -5, -10, -10, -20],
        [-10,   0,   0,   0,   0,   0,   0, -10],
        [-10,   0,   5,   5,   5,   5,   0, -10],
        [ -5,   0,   5,   5,   5,   5,   0,  -5],
        [  0,   0,   5,   5,   5,   5,   0,  -5],
        [-10,   5,   5,   5,   5,   5,   0, -10],
        [-10,   0,   5,   0,   0,   0,   0, -10],
        [-20, -10, -10,  -5,  -5, -10, -10, -20]
    ],
    chess.KING: [
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [ 20,  20,   0,   0,   0,   0,  20,  20],
        [ 20,  30,  10,   0,   0,  10,  30,  20]
    ]
}

# Endgame piece-square tables
board_values_endgame = {
    chess.PAWN: [
        [  0,   0,   0,   0,   0,   0,   0,   0],
        [ 80,  80,  80,  80,  80,  80,  80,  80],
        [ 50,  50,  50,  50,  50,  50,  50,  50],
        [ 30,  30,  30,  30,  30,  30,  30,  30],
        [ 20,  20,  20,  20,  20,  20,  20,  20],
        [ 10,  10,  10,  10,  10,  10,  10,  10],
        [ 10,  10,  10,  10,  10,  10,  10,  10],
        [  0,   0,   0,   0,   0,   0,   0,   0]
    ],
    chess.KING: [
        [-50, -40, -30, -20, -20, -30, -40, -50],
        [-30, -20, -10,   0,   0, -10, -20, -30],
        [-30, -10,  20,  30,  30,  20, -10, -30],
        [-30, -10,  30,  40,  40,  30, -10, -30],
        [-30, -10,  30,  40,  40,  30, -10, -30],
        [-30, -10,  20,  30,  30,  20, -10, -30],
        [-30, -30,   0,   0,   0,   0, -30, -30],
        [-50, -30, -30, -30, -30, -30, -30, -50]
    ]
}

# Global variables
d = 0
best_moves = []
nodes_count = 0
openings = []
INFINITY = 960240

# Neural Network simulation (placeholder for real implementation)
class SimpleNeuralNetwork:
    def __init__(self):
        self.weights = {}
        self.training_data = []
        self.load_weights()
    
    def load_weights(self):
        """Load pre-trained weights or initialize random ones"""
        try:
            with open('data/nn_weights.json', 'r') as f:
                self.weights = json.load(f)
        except FileNotFoundError:
            # Initialize with random weights
            self.weights = {
                'piece_activity': rd.uniform(0.8, 1.2),
                'king_safety': rd.uniform(0.9, 1.1),
                'pawn_structure': rd.uniform(0.7, 1.3),
                'center_control': rd.uniform(0.6, 1.4)
            }
            self.save_weights()
    
    def save_weights(self):
        """Save current weights to file"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/nn_weights.json', 'w') as f:
                json.dump(self.weights, f)
        except Exception as e:
            print(f"Error saving game analysis: {e}")

def load_and_analyze_games():
    """Load previous games for learning"""
    analysis_files = []
    if os.path.exists('data'):
        for filename in os.listdir('data'):
            if filename.startswith('game_analysis_') and filename.endswith('.json'):
                analysis_files.append(os.path.join('data', filename))
    
    games_data = []
    for filepath in analysis_files:
        try:
            with open(filepath, 'r') as f:
                game_data = json.load(f)
                games_data.append(game_data)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    
    print(f"Loaded {len(games_data)} previous games for analysis")
    return games_data

def get_difficulty_adjusted_depth(difficulty="medium"):
    """Get search depth based on difficulty level"""
    depth_map = {
        "easy": 2,
        "medium": 4,
        "hard": 6,
        "expert": 8
    }
    return depth_map.get(difficulty, 4)

def adaptive_depth_search(board, base_depth=4, time_limit=5.0):
    """Adaptive depth search based on position complexity"""
    import time
    
    start_time = time.time()
    legal_moves = len(list(board.chess_board.legal_moves))
    
    # Adjust depth based on position complexity
    if legal_moves < 10:  # Simple position
        depth = base_depth + 1
    elif legal_moves > 30:  # Complex position
        depth = max(2, base_depth - 1)
    else:
        depth = base_depth
    
    # Iterative deepening
    best_result = None
    for current_depth in range(1, depth + 1):
        if time.time() - start_time > time_limit:
            break
        
        try:
            result = minimax_search(board, current_depth, board.turn == chess.WHITE)
            if result:
                best_result = result
            print(f"Completed depth {current_depth} in {time.time() - start_time:.2f}s")
        except Exception as e:
            print(f"Error at depth {current_depth}: {e}")
            break
    
    return best_result

# Advanced features for tournament play
class TimeManager:
    def __init__(self, initial_time=300, increment=3):
        self.white_time = initial_time
        self.black_time = initial_time
        self.increment = increment
        self.move_times = []
    
    def allocate_time(self, color, moves_made, position_complexity=1.0):
        """Allocate thinking time based on remaining time and position"""
        current_time = self.white_time if color == chess.WHITE else self.black_time
        
        # Basic time allocation strategy
        if moves_made < 10:  # Opening
            allocated_time = min(current_time * 0.05, 10.0)
        elif moves_made < 30:  # Middlegame
            allocated_time = min(current_time * 0.08 * position_complexity, 30.0)
        else:  # Endgame
            allocated_time = min(current_time * 0.15, 60.0)
        
        return max(1.0, allocated_time)
    
    def update_time(self, color, time_used):
        """Update remaining time after a move"""
        if color == chess.WHITE:
            self.white_time = max(0, self.white_time - time_used + self.increment)
        else:
            self.black_time = max(0, self.black_time - time_used + self.increment)
        
        self.move_times.append((color, time_used))

# Initialize components on module load
time_manager = TimeManager()

# Auto-learning from previous games on startup
try:
    previous_games = load_and_analyze_games()
    if previous_games:
        print(f"Learning from {len(previous_games)} previous games...")
        for game in previous_games[-10:]:  # Learn from last 10 games
            neural_net.learn_from_game(game)
except Exception as e:
    print(f"Error during initial learning: {e}")

print("Enhanced Chess AI initialized with Machine Learning support!") saving weights: {e}")
    
def evaluate_position(self, board_features):
        """Neural network position evaluation"""
        # Simplified neural network evaluation
        score = 0
        
        # Piece activity evaluation
        try:
            mobility = len(list(chess.Board(board_features['fen']).legal_moves))
            score += mobility * self.weights.get('piece_activity', 1.0) * 2
        except:
            score += 0
        
        # King safety (simplified)
        king_safety_score = rd.uniform(-50, 50)  # Placeholder
        score += king_safety_score * self.weights.get('king_safety', 1.0)
        
        # Pawn structure
        pawn_score = rd.uniform(-30, 30)  # Placeholder
        score += pawn_score * self.weights.get('pawn_structure', 1.0)
        
        # Center control
        center_score = rd.uniform(-20, 20)  # Placeholder
        score += center_score * self.weights.get('center_control', 1.0)
        
        return score
    
def learn_from_game(self, game_data):
        """Simple learning from game results"""
        # Very simplified learning
        result = game_data.get('result', 0)  # 1 for win, 0 for draw, -1 for loss
        
        # Adjust weights slightly based on result
        adjustment = 0.01 * result
        for key in self.weights:
            self.weights[key] += adjustment * rd.uniform(-1, 1)
            # Keep weights in reasonable bounds
            self.weights[key] = max(0.1, min(2.0, self.weights[key]))
        
        self.save_weights()

# Initialize neural network
neural_net = SimpleNeuralNetwork()

def evaluate_mobility(board: chess.Board):
    """Evaluate piece mobility - FIXED VERSION"""
    try:
        # Count legal moves for current player
        current_player_mobility = len(list(board.legal_moves))
        
        # Create a copy to count opponent mobility
        board_copy = board.copy()
        
        # Switch turns to count opponent mobility
        board_copy.turn = not board_copy.turn
        opponent_mobility = len(list(board_copy.legal_moves))
        
        # Calculate mobility difference
        if board.turn == chess.WHITE:
            mobility_score = (current_player_mobility - opponent_mobility) * 2
        else:
            mobility_score = (opponent_mobility - current_player_mobility) * 2
        
        return mobility_score
        
    except Exception as e:
        print(f"Error in evaluate_mobility: {e}")
        return 0

def evaluate_king_safety_advanced(board: chess.Board):
    """Advanced king safety evaluation - FIXED VERSION"""
    try:
        safety_score = 0
        
        for color in [chess.WHITE, chess.BLACK]:
            king_square = board.king(color)
            if king_square is not None:
                # Check for castling rights
                if board.has_castling_rights(color):
                    safety_score += 30 if color == chess.WHITE else -30
                
                # Penalize exposed king
                king_file = chess.square_file(king_square)
                
                # Central king penalty in opening/middlegame
                if len(board.piece_map()) > 12:  # Not endgame
                    if 2 <= king_file <= 5:  # King in center files
                        safety_score += -20 if color == chess.WHITE else 20
        
        return safety_score
        
    except Exception as e:
        print(f"Error in evaluate_king_safety_advanced: {e}")
        return 0

def evaluate_pawn_structure_advanced(board: chess.Board):
    """Advanced pawn structure evaluation - FIXED VERSION"""
    try:
        pawn_score = 0
        
        white_pawns = board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = board.pieces(chess.PAWN, chess.BLACK)
        
        # Count doubled pawns
        for file in range(8):
            white_pawns_in_file = len([p for p in white_pawns if chess.square_file(p) == file])
            black_pawns_in_file = len([p for p in black_pawns if chess.square_file(p) == file])
            
            if white_pawns_in_file > 1:
                pawn_score -= 20 * (white_pawns_in_file - 1)
            if black_pawns_in_file > 1:
                pawn_score += 20 * (black_pawns_in_file - 1)
        
        # Isolated pawns penalty
        for pawn in white_pawns:
            if is_isolated_pawn(pawn, white_pawns):
                pawn_score -= 15
        
        for pawn in black_pawns:
            if is_isolated_pawn(pawn, black_pawns):
                pawn_score += 15
        
        return pawn_score
        
    except Exception as e:
        print(f"Error in evaluate_pawn_structure_advanced: {e}")
        return 0

def is_isolated_pawn(pawn_square, friendly_pawns):
    """Check if a pawn is isolated - SAFE VERSION"""
    try:
        pawn_file = chess.square_file(pawn_square)
        adjacent_files = [pawn_file - 1, pawn_file + 1]
        
        for adjacent_file in adjacent_files:
            if 0 <= adjacent_file <= 7:
                for pawn in friendly_pawns:
                    if chess.square_file(pawn) == adjacent_file:
                        return False
        return True
    except Exception as e:
        print(f"Error in is_isolated_pawn: {e}")
        return False

def get_board_val(board: chess.Board, use_neural_net=False):
    """Enhanced board evaluation with neural network support - FIXED VERSION"""
    try:
        if is_draw(board):
            return 0
        if board.is_checkmate():
            return 99999 if board.outcome().winner == chess.WHITE else -99999
        
        # Get game phase
        piece_count = len(board.piece_map())
        is_endgame = piece_count <= 12
        
        # Choose appropriate piece-square tables
        current_board_values = board_values_endgame if is_endgame else board_values_opening
        
        val = 0
        
        # Traditional evaluation
        for square in squares:
            tmp_piece = board.piece_at(square)
            if tmp_piece is not None:
                tmp_color = tmp_piece.color
                tmp_type = tmp_piece.piece_type
                tmp_pos = squares[square]
                
                piece_val = piece_values[tmp_type]
                
                # Use appropriate piece-square table
                if tmp_type in current_board_values:
                    if tmp_color == chess.WHITE:
                        positional_val = current_board_values[tmp_type][tmp_pos[0]][tmp_pos[1]]
                    else:
                        positional_val = current_board_values[tmp_type][7-tmp_pos[0]][tmp_pos[1]]
                else:
                    # Fall back to opening values for pieces not in endgame tables
                    if tmp_color == chess.WHITE:
                        positional_val = board_values_opening[tmp_type][tmp_pos[0]][tmp_pos[1]]
                    else:
                        positional_val = board_values_opening[tmp_type][7-tmp_pos[0]][tmp_pos[1]]
                
                total_piece_val = piece_val + positional_val
                
                if tmp_color == chess.WHITE:
                    val += total_piece_val
                else:
                    val -= total_piece_val
        
        # Add neural network evaluation if enabled
        if use_neural_net:
            try:
                features = {
                    'fen': board.fen(),
                    'piece_count': piece_count,
                    'is_endgame': is_endgame
                }
                nn_eval = neural_net.evaluate_position(features)
                val += int(nn_eval * 0.3)  # Weight neural network contribution
            except Exception as e:
                print(f"Neural network evaluation error: {e}")
        
        # Additional positional factors with error handling
        try:
            val += evaluate_mobility(board)
        except Exception as e:
            print(f"Mobility evaluation error: {e}")
        
        try:
            val += evaluate_king_safety_advanced(board)
        except Exception as e:
            print(f"King safety evaluation error: {e}")
        
        try:
            val += evaluate_pawn_structure_advanced(board)
        except Exception as e:
            print(f"Pawn structure evaluation error: {e}")
        
        return val
        
    except Exception as e:
        print(f"Critical error in get_board_val: {e}")
        # Return basic material evaluation as fallback
        material_val = 0
        try:
            for square in squares:
                piece = board.piece_at(square)
                if piece:
                    val = piece_values.get(piece.piece_type, 0)
                    material_val += val if piece.color == chess.WHITE else -val
        except:
            pass
        return material_val

def is_draw(board: chess.Board):
    return board.is_stalemate() or board.is_seventyfive_moves() or board.is_fivefold_repetition() or board.is_insufficient_material()

def minimax_search(board, depth=5, maximizing=False, use_neural_net=False):
    """Enhanced minimax search with neural network support"""
    global d, best_moves, nodes_count
    d = depth
    best_moves.clear()
    nodes_count = 0

    if board.chess_board.is_game_over():
        return None

    tmp_board = board.chess_board.fen()
    
    # Check transposition table
    try:
        board_hash = hash(tmp_board)
        cached_result = board.transposition_table.get(board_hash)
        if cached_result and cached_result['depth'] >= depth:
            print(f"Using cached evaluation: {cached_result['evaluation']}")
    except:
        pass
    
    best_value = alpha_beta(tmp_board, depth, -INFINITY, INFINITY, maximizing, use_neural_net, getattr(board, 'transposition_table', None))
    
    # Store in transposition table
    try:
        board.transposition_table.store(board_hash, best_value, depth)
    except:
        pass
    
    if not best_moves:
        return None
        
    chosen_move = best_moves[rd.randint(0, len(best_moves) - 1)]

    # Make the move
    best_piece = board.get_piece_from_pos(Board.get_pos_from_coord(chosen_move[0:2]))
    dst_sq = board.get_square_from_pos(Board.get_pos_from_coord(chosen_move[2:4]))
    best_piece.move(dst_sq)

    # Store evaluation in history
    try:
        board.evaluation_history.append(best_value)
    except:
        pass

    # Print information
    print("Nodes visited:", nodes_count)
    print("Best move value found:", best_value)
    print("Best moves found:", *best_moves)
    print("Chosen move:", chosen_move)
    if use_neural_net:
        print("Neural network evaluation enabled")
    
    return chosen_move

def get_move_value(move, board_fen, use_neural_net=False):
    """Enhanced move evaluation"""
    tmp_board = chess.Board(board_fen)
    tmp_board.push_san(move)
    return get_board_val(tmp_board, use_neural_net)

def alpha_beta(board_fen, depth, a, b, maximizing, use_neural_net=False, transposition_table=None):
    """Enhanced alpha-beta with transposition table support"""
    global best_moves, nodes_count, d

    tmp_board = chess.Board(board_fen)
    
    # Check transposition table
    if transposition_table:
        try:
            board_hash = hash(board_fen)
            cached_result = transposition_table.get(board_hash)
            if cached_result and cached_result['depth'] >= depth:
                return cached_result['evaluation']
        except:
            pass
    
    if (depth <= 0) or (tmp_board.is_game_over()):
        evaluation = get_board_val(tmp_board, use_neural_net)
        if transposition_table:
            try:
                transposition_table.store(hash(board_fen), evaluation, depth)
            except:
                pass
        return evaluation

    moves = [move.uci() for move in tmp_board.generate_legal_moves()]
    
    # Enhanced move ordering
    if depth >= 2:
        try:
            move_scores = []
            for move in moves:
                score = get_move_value(move, board_fen, use_neural_net)
                move_scores.append((move, score))
            
            if maximizing:
                move_scores.sort(key=lambda x: x[1], reverse=True)
            else:
                move_scores.sort(key=lambda x: x[1])
            
            moves = [move for move, score in move_scores]
        except:
            pass  # Use original move order if sorting fails
    
    if maximizing:
        value_max = -INFINITY
        for move in moves:
            nodes_count += 1
            tmp_board.push_san(move)
            value = alpha_beta(tmp_board.fen(), depth - 1, a, b, False, use_neural_net, transposition_table)
            tmp_board.pop()
            
            if depth == d:  # Record the best moves at root level
                if value > value_max:
                    value_max = value
                    best_moves.clear()
                    best_moves.append(move)
                elif value == value_max:
                    best_moves.append(move)
            else:
                value_max = max(value, value_max)
            
            a = max(a, value_max)
            if a >= b:
                break  # Beta cutoff
        
        if transposition_table:
            try:
                transposition_table.store(hash(board_fen), value_max, depth)
            except:
                pass
        return value_max
    
    else:
        value_min = INFINITY
        for move in moves:
            nodes_count += 1
            tmp_board.push_san(move)
            value = alpha_beta(tmp_board.fen(), depth - 1, a, b, True, use_neural_net, transposition_table)
            tmp_board.pop()
            
            if depth == d:  # Record the best moves at root level
                if value < value_min:
                    value_min = value
                    best_moves.clear()
                    best_moves.append(move)
                elif value == value_min:
                    best_moves.append(move)
            else:
                value_min = min(value, value_min)
            
            b = min(b, value_min)
            if b <= a:
                break  # Alpha cutoff
        
        if transposition_table:
            try:
                transposition_table.store(hash(board_fen), value_min, depth)
            except:
                pass
        return value_min

def initialize_openings():
    """Initialize opening book"""
    global openings
    try:
        with open('openings.txt') as open_sequences:
            while True:
                sequence = open_sequences.readline().split()
                if len(sequence) == 0:
                    break
                openings.append(sequence)
        print(f"Loaded {len(openings)} opening lines")
    except FileNotFoundError:
        try:
            with open('data/openings.txt') as open_sequences:
                while True:
                    sequence = open_sequences.readline().split()
                    if len(sequence) == 0:
                        break
                    openings.append(sequence)
            print(f"Loaded {len(openings)} opening lines from data folder")
        except FileNotFoundError:
            print("Warning: openings.txt not found. Creating basic openings...")
            # Create basic openings if file doesn't exist
            basic_openings = [
                ['e2e4', 'e7e5', 'g1f3', 'b8c6', 'f1b5'],
                ['d2d4', 'd7d5', 'c2c4', 'e7e6', 'b1c3'],
                ['g1f3', 'g8f6', 'c2c4', 'g7g6', 'b1c3'],
                ['e2e4', 'c7c5', 'g1f3', 'd7d6', 'd2d4'],
                ['d2d4', 'g8f6', 'c2c4', 'e7e6', 'b1c3']
            ]
            openings = basic_openings
            print(f"Created {len(openings)} basic opening lines")

def opening_search(board, sequence: list):
    """Enhanced opening search with learning"""
    global best_moves, openings
    best_moves.clear()

    matching_lines = []
    for line in openings[:]:  # Use slice to avoid modification during iteration
        if len(sequence) < len(line) and sequence == line[0:len(sequence)]:
            next_move = line[len(sequence)]
            if next_move != 'None':
                matching_lines.append((line, next_move))
        elif sequence != line[0:len(sequence)]:
            # Remove lines that don't match current sequence
            if line in openings:
                openings.remove(line)

    if matching_lines:
        # Choose move from matching lines
        best_moves = [move for line, move in matching_lines]
        chosen_move = best_moves[rd.randint(0, len(best_moves) - 1)]
        
        best_piece = board.get_piece_from_pos(Board.get_pos_from_coord(chosen_move[0:2]))
        dst_sq = board.get_square_from_pos(Board.get_pos_from_coord(chosen_move[2:4]))
        best_piece.move(dst_sq)

        print("Book moves found:", best_moves)
        print("Chosen move:", chosen_move)
        return chosen_move
    else:
        return None

def save_game_analysis(board, result, filename=None):
    """Save game analysis for machine learning"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/game_analysis_{timestamp}.json"
    
    try:
        analysis_data = {
            'timestamp': datetime.now().isoformat(),
            'final_fen': board.chess_board.fen(),
            'move_history': getattr(board.move_history, 'moves', []),
            'evaluation_history': getattr(board, 'evaluation_history', []),
            'result': result,  # 1 for AI win, 0 for draw, -1 for AI loss
            'game_length': len(getattr(board.move_history, 'moves', [])),
            'opening_used': len([m for m in getattr(board.move_history, 'moves', [])[:6]]),
            'final_evaluation': getattr(board, 'evaluation_history', [0])[-1] if hasattr(board, 'evaluation_history') and board.evaluation_history else 0
        }
        
        os.makedirs('data', exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        print(f"Game analysis saved to {filename}")
        
        # Learn from this game
        neural_net.learn_from_game(analysis_data)
        
    except Exception as e:
        print(f"Error")