import pygame
import chess
from time import sleep
from Board import GUI_Board
import Bot
import json
import os

def draw_gradient_background(display, width, height):
    """Draw a beautiful gradient background"""
    for y in range(height):
        color_ratio = y / height
        # Elegant dark to light brown gradient
        r = int(101 + (139 - 101) * color_ratio)
        g = int(67 + (116 - 67) * color_ratio)
        b = int(33 + (78 - 33) * color_ratio)
        pygame.draw.line(display, (r, g, b), (0, y), (width, y))

def draw_button(display, rect, text, font, is_hovered=False, is_disabled=False, button_type="normal"):
    """Draw a styled button với màu sắc phân biệt theo loại"""
    if is_disabled:
        bg_color = (120, 120, 120)
        text_color = (80, 80, 80)
        border_color = (100, 100, 100)
    elif is_hovered:
        # Màu sắc khác nhau cho từng loại button khi hover
        if button_type == "danger":  # Surrender button
            bg_color = (220, 120, 120)
            text_color = (80, 20, 20)
            border_color = (180, 80, 80)
        elif button_type == "warning":  # Reset button
            bg_color = (220, 180, 120)
            text_color = (80, 60, 20)
            border_color = (180, 140, 80)
        elif button_type == "info":  # Undo button
            bg_color = (120, 180, 220)
            text_color = (20, 60, 80)
            border_color = (80, 140, 180)
        else:  # Save, Load buttons
            bg_color = (180, 150, 120)
            text_color = (50, 30, 10)
            border_color = (139, 116, 78)
    else:
        # Màu sắc bình thường
        if button_type == "danger":
            bg_color = (180, 100, 100)
            text_color = (60, 20, 20)
            border_color = (140, 70, 70)
        elif button_type == "warning":
            bg_color = (180, 150, 100)
            text_color = (60, 45, 20)
            border_color = (140, 115, 70)
        elif button_type == "info":
            bg_color = (100, 150, 180)
            text_color = (20, 45, 60)
            border_color = (70, 115, 140)
        else:
            bg_color = (160, 130, 100)
            text_color = (101, 67, 33)
            border_color = (101, 67, 33)
    
    # Draw button background with gradient
    for y in range(rect.height):
        ratio = y / rect.height
        r = int(bg_color[0] * (1 - ratio * 0.2))
        g = int(bg_color[1] * (1 - ratio * 0.2))
        b = int(bg_color[2] * (1 - ratio * 0.2))
        pygame.draw.line(display, (r, g, b), 
                        (rect.x, rect.y + y), 
                        (rect.x + rect.width, rect.y + y))
    
    # Draw border
    pygame.draw.rect(display, border_color, rect, 2)
    
    # Draw text
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    display.blit(text_surface, text_rect)

def show_color_selection_screen(display, font):
    """Hiển thị màn hình chọn màu quân cho người chơi"""
    clock = pygame.time.Clock()
    
    while True:
        mx, my = pygame.mouse.get_pos()
        
        # Draw background
        draw_gradient_background(display, TOTAL_WIDTH, TOTAL_HEIGHT)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Choose Your Color", True, (101, 67, 33))
        title_rect = title_text.get_rect(center=(TOTAL_WIDTH // 2, 150))
        display.blit(title_text, title_rect)
        
        subtitle_text = font.render("Select which side you want to play as:", True, (101, 67, 33))
        subtitle_rect = subtitle_text.get_rect(center=(TOTAL_WIDTH // 2, 200))
        display.blit(subtitle_text, subtitle_rect)
        
        # Button dimensions
        button_width = 150
        button_height = 60
        button_spacing = 50
        
        # White button
        white_button_rect = pygame.Rect(
            TOTAL_WIDTH // 2 - button_width - button_spacing // 2,
            TOTAL_HEIGHT // 2,
            button_width,
            button_height
        )
        
        # Black button  
        black_button_rect = pygame.Rect(
            TOTAL_WIDTH // 2 + button_spacing // 2,
            TOTAL_HEIGHT // 2,
            button_width,
            button_height
        )
        
        # Check hover states
        white_hover = white_button_rect.collidepoint(mx, my)
        black_hover = black_button_rect.collidepoint(mx, my)
        
        # Draw buttons
        draw_button(display, white_button_rect, "Play as White", font, white_hover, False, "normal")
        draw_button(display, black_button_rect, "Play as Black", font, black_hover, False, "normal")
        
        # Additional info
        info_text = font.render("White moves first, Black moves second", True, (101, 67, 33))
        info_rect = info_text.get_rect(center=(TOTAL_WIDTH // 2, TOTAL_HEIGHT // 2 + 120))
        display.blit(info_text, info_rect)
        
        pygame.display.update()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None  # Exit game
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if white_button_rect.collidepoint(mx, my):
                        return chess.WHITE  # Player chọn trắng
                    elif black_button_rect.collidepoint(mx, my):
                        return chess.BLACK  # Player chọn đen
        
        clock.tick(60)

def draw_move_history_panel(display, move_history, font, panel_rect, current_turn, player_color):
    """Draw the elegant move history panel"""
    # Panel background with gradient
    panel_surface = pygame.Surface((panel_rect.width, panel_rect.height))
    for y in range(panel_rect.height):
        ratio = y / panel_rect.height
        r = int(240 + (220 - 240) * ratio)
        g = int(230 + (210 - 230) * ratio)
        b = int(200 + (180 - 200) * ratio)
        pygame.draw.line(panel_surface, (r, g, b), (0, y), (panel_rect.width, y))
    
    # Panel border
    pygame.draw.rect(panel_surface, (101, 67, 33), (0, 0, panel_rect.width, panel_rect.height), 3)
    pygame.draw.rect(panel_surface, (139, 116, 78), (2, 2, panel_rect.width - 4, panel_rect.height - 4), 1)
    
    # Title
    title = font.render("Move History", True, (101, 67, 33))
    title_rect = title.get_rect(centerx=panel_rect.width // 2, y=10)
    panel_surface.blit(title, title_rect)
    
    # Current turn indicator
    turn_text = "Your turn" if current_turn == player_color else "AI's turn"
    turn_color = (0, 150, 0) if current_turn == player_color else (150, 0, 0)
    turn_surface = font.render(turn_text, True, turn_color)
    turn_rect = turn_surface.get_rect(centerx=panel_rect.width // 2, y=30)
    panel_surface.blit(turn_surface, turn_rect)
    
    # Divider line
    pygame.draw.line(panel_surface, (101, 67, 33), 
                    (10, 50), (panel_rect.width - 10, 50), 2)
    
    # Move history
    y_offset = 60
    moves_per_line = 2
    line_height = 25
    
    if move_history:
        for i in range(0, len(move_history), moves_per_line):
            move_text = ""
            move_number = (i // 2) + 1
            
            if i < len(move_history):
                white_move = move_history[i]
                move_text = f"{move_number}. {white_move}"
                
                if i + 1 < len(move_history):
                    black_move = move_history[i + 1]
                    move_text += f" {black_move}"
            
            if move_text and y_offset < panel_rect.height - 170:  # Leave more space for 3 rows of buttons
                # Highlight the latest move
                text_color = (200, 0, 0) if i >= len(move_history) - 2 else (101, 67, 33)
                move_surface = font.render(move_text, True, text_color)
                panel_surface.blit(move_surface, (15, y_offset))
                y_offset += line_height
    
    display.blit(panel_surface, panel_rect.topleft)

def draw_control_buttons(display, panel_rect, font, button_states):
    """Draw control buttons in the panel - NEW LAYOUT: 2-2-1"""
    button_width = 70
    button_height = 30
    button_spacing_x = 12  # Horizontal spacing between buttons
    button_spacing_y = 10  # Vertical spacing between rows
    
    # Calculate starting positions to center the layout
    total_width_per_row = 2 * button_width + button_spacing_x
    start_x = panel_rect.x + (panel_rect.width - total_width_per_row) // 2
    start_y = panel_rect.y + panel_rect.height - 140  # Start from bottom
    
    # Row 1: Reset, Save (top row)
    reset_rect = pygame.Rect(
        start_x,
        start_y,
        button_width,
        button_height
    )
    
    save_rect = pygame.Rect(
        start_x + button_width + button_spacing_x,
        start_y,
        button_width,
        button_height
    )
    
    # Row 2: Surrender, Load (middle row)
    surrender_rect = pygame.Rect(
        start_x,
        start_y + button_height + button_spacing_y,
        button_width,
        button_height
    )
    
    load_rect = pygame.Rect(
        start_x + button_width + button_spacing_x,
        start_y + button_height + button_spacing_y,
        button_width,
        button_height
    )
    
    # Row 3: Undo (bottom row, centered)
    undo_rect = pygame.Rect(
        panel_rect.x + (panel_rect.width - button_width) // 2,  # Centered horizontally
        start_y + 2 * (button_height + button_spacing_y),
        button_width,
        button_height
    )
    
    # Check if undo should be disabled (need at least 2 moves in history)
    undo_disabled = len(button_states.get('move_history', [])) < 2 or button_states.get('game_over', False)
    
    # Draw buttons with improved layout and color coding
    draw_button(display, reset_rect, "Reset", font, button_states.get('reset_hover', False), False, "warning")
    draw_button(display, save_rect, "Save", font, button_states.get('save_hover', False), False, "normal")
    draw_button(display, surrender_rect, "Surrender", font, button_states.get('surrender_hover', False), False, "danger")
    draw_button(display, load_rect, "Load", font, button_states.get('load_hover', False), False, "normal")
    draw_button(display, undo_rect, "Undo", font, button_states.get('undo_hover', False), undo_disabled, "info")
    
    return {
        'reset': reset_rect,
        'save': save_rect,
        'surrender': surrender_rect,
        'load': load_rect,
        'undo': undo_rect
    }

def save_game_state(board, move_history, sequence, player_color):
    """Save current game state to file"""
    game_state = {
        'board_fen': board.chess_board.fen(),
        'move_history': move_history,
        'sequence': sequence,
        'turn': board.turn,
        'player_color': player_color  # Lưu màu của người chơi
    }
    
    try:
        with open('saved_game.json', 'w') as f:
            json.dump(game_state, f)
        return True
    except Exception as e:
        print(f"Error saving game: {e}")
        return False

def load_game_state():
    """Load game state from file"""
    try:
        if os.path.exists('saved_game.json'):
            with open('saved_game.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading game: {e}")
    return None

def create_game_over_dialog_surface(font, result_text):
    """Tạo surface cho dialog game over - chỉ tạo một lần"""
    dialog_width = 400
    dialog_height = 200
    
    # Create dialog surface
    dialog_surface = pygame.Surface((dialog_width, dialog_height))
    
    # Draw dialog background with gradient
    for y in range(dialog_height):
        ratio = y / dialog_height
        r = int(240 + (220 - 240) * ratio)
        g = int(230 + (210 - 230) * ratio)
        b = int(200 + (180 - 200) * ratio)
        pygame.draw.line(dialog_surface, (r, g, b), (0, y), (dialog_width, y))
    
    # Draw borders
    pygame.draw.rect(dialog_surface, (101, 67, 33), (0, 0, dialog_width, dialog_height), 4)
    pygame.draw.rect(dialog_surface, (139, 116, 78), (2, 2, dialog_width - 4, dialog_height - 4), 2)
    
    # Draw title
    title_font = pygame.font.Font(None, 36)
    title_text = title_font.render("Game Over", True, (101, 67, 33))
    title_rect = title_text.get_rect(centerx=dialog_width // 2, y=20)
    dialog_surface.blit(title_text, title_rect)
    
    # Draw result text
    lines = result_text.split('\n')
    y_offset = 70
    result_font = pygame.font.Font(None, 28)
    
    for line in lines:
        if line.strip():  # Only draw non-empty lines
            text_surface = result_font.render(line, True, (101, 67, 33))
            text_rect = text_surface.get_rect(centerx=dialog_width // 2, y=y_offset)
            dialog_surface.blit(text_surface, text_rect)
            y_offset += 35
    
    # Draw instruction
    instruction_text = font.render("Click Reset to play again", True, (101, 67, 33))
    instruction_rect = instruction_text.get_rect(centerx=dialog_width // 2, y=dialog_height - 30)
    dialog_surface.blit(instruction_text, instruction_rect)
    
    return dialog_surface

def draw(display, board, move_history, font, button_states, current_turn, player_color, game_over=False):
    # Create a beautiful gradient background
    draw_gradient_background(display, TOTAL_WIDTH, TOTAL_HEIGHT)
    
    # Draw the chess board (offset by border)
    board.draw(display)
    
    # Draw move history panel with turn indicator
    panel_rect = pygame.Rect(BOARD_WIDTH + BORDER_WIDTH + 10, BORDER_WIDTH, 
                           PANEL_WIDTH - 20, BOARD_HEIGHT)
    draw_move_history_panel(display, move_history, font, panel_rect, current_turn, player_color)
    
    # Pass move history info and game over state to button drawing
    button_states['move_history'] = move_history
    button_states['game_over'] = game_over
    
    # Draw control buttons and return their rects
    button_rects = draw_control_buttons(display, panel_rect, font, button_states)
    
    pygame.display.update()
    return button_rects

# Enhanced window dimensions
BOARD_SIZE = (600, 600)
BORDER_WIDTH = 30
PANEL_WIDTH = 250
BOARD_WIDTH, BOARD_HEIGHT = BOARD_SIZE
TOTAL_WIDTH = BOARD_WIDTH + BORDER_WIDTH * 2 + PANEL_WIDTH
TOTAL_HEIGHT = BOARD_HEIGHT + BORDER_WIDTH * 2

if __name__ == '__main__':
    Bot.initialize_openings()
    pygame.init()
    
    # Initialize font
    pygame.font.init()
    font = pygame.font.Font(None, 20)
    
    # Create enhanced screen with side panel
    screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
    pygame.display.set_caption("Enhanced Luxury Chess Game with AI")
    
    # ===== CHỌN MÀU QUÂN CHO NGƯỜI CHƠI =====
    player_color = show_color_selection_screen(screen, font)
    if player_color is None:
        pygame.quit()
        exit()
    
    ai_color = chess.BLACK if player_color == chess.WHITE else chess.WHITE
    print(f"Player chọn: {'Trắng' if player_color == chess.WHITE else 'Đen'}")
    print(f"AI chơi: {'Trắng' if ai_color == chess.WHITE else 'Đen'}")
    
    # Set up the game clock for smooth animation
    clock = pygame.time.Clock()
    
    board = GUI_Board(*BOARD_SIZE)
    sequence = []
    move_history = []
    opening = True
    button_states = {}
    game_over = False
    game_result = ""
    trained_this_game = False
    show_dialog = False  # Flag để kiểm soát hiển thị dialog
    frozen_screen = None  # Cache toàn bộ màn hình game khi dialog hiện
    
    # ===== NẾUVỀ AI CHƠI TRẮNG THÌ THỰC HIỆN NƯỚC ĐI ĐẦU TIÊN =====
    if ai_color == chess.WHITE:
        print("AI (White) will make the first move...")
        # AI sẽ đi trong vòng lặp chính, không cần làm gì ở đây

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        
        # Update button hover states
        panel_rect = pygame.Rect(BOARD_WIDTH + BORDER_WIDTH + 10, BORDER_WIDTH, 
                               PANEL_WIDTH - 20, BOARD_HEIGHT)
        button_rects = draw_control_buttons(screen, panel_rect, font, button_states)
        
        # Check button hovers
        for button_name, rect in button_rects.items():
            button_states[f'{button_name}_hover'] = rect.collidepoint(mx, my)
        
        # ===== HANDLE BOT MOVES WITH FULL DEBUG - UPDATED FOR COLOR SYSTEM =====
        if not game_over and board.turn == ai_color and not board.is_animating:
            print("=== AI TURN STARTED ===")
            print(f"Game over: {game_over}")
            print(f"Board turn: {'BLACK' if board.turn == chess.BLACK else 'WHITE'}")
            print(f"AI Color: {'BLACK' if ai_color == chess.BLACK else 'WHITE'}")
            print(f"Player Color: {'BLACK' if player_color == chess.BLACK else 'WHITE'}")
            print(f"Is animating: {board.is_animating}")
            print(f"Opening: {opening}")
            print(f"Sequence: {sequence}")
            print(f"Move history: {move_history}")
            print(f"Chess board FEN: {board.chess_board.fen()}")
            print(f"Legal moves count: {len(list(board.chess_board.legal_moves))}")
            
            print("Board value after player has moved:", Bot.get_board_val(board.chess_board))
            move_made = None
            
            if opening and len(sequence) < 6:
                print("TRYING OPENING BOOK...")
                move_made = Bot.opening_search(board, sequence)
                print(f"Opening book result: {move_made}")
            
            if move_made is None:
                print("USING MINIMAX...")
                try:
                    move_made = Bot.minimax_search(board, 3, board.turn == chess.WHITE)
                    print(f"Minimax result: {move_made}")
                except Exception as e:
                    print(f"MINIMAX ERROR: {e}")
                    import traceback
                    traceback.print_exc()
                opening = False

            status = (move_made is not None)
            
            # ===== FULL DEBUG SECTION =====
            print(f"Move made: {move_made}")
            print(f"Status: {status}")
            print(f"Chess board legal moves: {[move.uci() for move in board.chess_board.legal_moves]}")
            print(f"Is checkmate: {board.chess_board.is_checkmate()}")
            print(f"Is stalemate: {board.chess_board.is_stalemate()}")
            print(f"Is check: {board.chess_board.is_check()}")
            
            if opening and move_made:
                sequence.append(move_made)
            
            # Add bot move to history
            if move_made:
                move_history.append(move_made)
                
            print("Board value after bot has moved:", Bot.get_board_val(board.chess_board))
            print("=== AI TURN ENDED ===")

            if not status:
                print("AI FAILED TO MOVE - CHECKING WHY:")
                print(f"Legal moves count: {len(list(board.chess_board.legal_moves))}")
                print(f"Game over conditions:")
                print(f"  Checkmate: {board.chess_board.is_checkmate()}")
                print(f"  Stalemate: {board.chess_board.is_stalemate()}")
                print(f"  Insufficient material: {board.chess_board.is_insufficient_material()}")
                game_result = board.is_end_game()
                game_over = True
        
        # Check for game end
        if not game_over:
            end_result = board.is_end_game()
            if end_result is not False:
                game_result = end_result
                game_over = True
                show_dialog = True  # Hiển thị dialog
                frozen_screen = None  # Reset để capture màn hình mới
                if not trained_this_game:
                # Train AI from this game
                    print("AI is training before reset...")
                    try:
                        # Xác định kết quả cho AI dựa trên ai_color và làm rõ thông báo
                        if "White wins!" in game_result:
                            ai_result = "AI Win" if ai_color == chess.WHITE else "AI Loss"
                            # Cập nhật thông báo rõ ràng hơn
                            if ai_color == chess.WHITE:
                                game_result = "Checkmate! White (AI) wins!"
                            else:
                                game_result = "Checkmate! White (You) wins!"
                        elif "Black wins!" in game_result:
                            ai_result = "AI Win" if ai_color == chess.BLACK else "AI Loss"
                            # Cập nhật thông báo rõ ràng hơn
                            if ai_color == chess.BLACK:
                                game_result = "Checkmate! Black (AI) wins!"
                            else:
                                game_result = "Checkmate! Black (You) wins!"
                        else:
                            ai_result = "Draw"
                            # Giữ nguyên thông báo draw
                        
                        game_data = {
                        'move_history': move_history,
                        'result': ai_result,
                        'fen': board.chess_board.fen(),
                        'player_color': 'White' if player_color == chess.WHITE else 'Black',
                        'ai_color': 'White' if ai_color == chess.WHITE else 'Black'
                        }
                        Bot.train_from_game(game_data)
                        Bot.save_model("model.pkl")
                        Bot.save_game_analysis(board, ai_result)
                        print("AI trained and model saved after the game.")
                        trained_this_game = True
                    except Exception as e:
                        print(f"Error during post-game training: {e}")

     
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Nếu chưa học và có dữ liệu thì học trước khi thoát
                if move_history and not trained_this_game:
                    try:
                        print(" AI is training before quit...")
                        game_data = {
                            'move_history': move_history,
                            'result': "Player quit mid-game",
                            'fen': board.chess_board.fen(),
                            'player_color': 'White' if player_color == chess.WHITE else 'Black',
                            'ai_color': 'White' if ai_color == chess.WHITE else 'Black'
                        }
                        Bot.train_from_game(game_data)
                        Bot.save_model("model.pkl")
                        Bot.save_game_analysis(board, "Player quit mid-game")
                        print("AI trained and saved before quit.")
                    except Exception as e:
                        print(f"Error training before quit: {e}")
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check button clicks
                    clicked_button = None
                    for button_name, rect in button_rects.items():
                        if rect.collidepoint(mx, my):
                            clicked_button = button_name
                            break
                    
                    if clicked_button == 'reset':
                        # Nếu đã có nước đi và chưa học thì học trước khi reset
                        if move_history and not trained_this_game:
                            try:
                                print(" AI is training before reset...")
                                game_data = {
                                    'move_history': move_history,
                                    'result': "Player reset mid-game",
                                    'fen': board.chess_board.fen(),
                                    'player_color': 'White' if player_color == chess.WHITE else 'Black',
                                    'ai_color': 'White' if ai_color == chess.WHITE else 'Black'
                                }
                                Bot.train_from_game(game_data)
                                Bot.save_model("model.pkl")
                                Bot.save_game_analysis(board, "Player reset mid-game")
                                print("AI trained and saved before reset.")
                            except Exception as e:
                                print(f"Error training AI before reset: {e}")

                        # Show color selection again
                        new_player_color = show_color_selection_screen(screen, font)
                        if new_player_color is None:
                            running = False
                            break
                        
                        # Update colors
                        player_color = new_player_color
                        ai_color = chess.BLACK if player_color == chess.WHITE else chess.WHITE
                        print(f"New game - Player: {'Trắng' if player_color == chess.WHITE else 'Đen'}, AI: {'Trắng' if ai_color == chess.WHITE else 'Đen'}")

                        # Reset game
                        board = GUI_Board(*BOARD_SIZE)
                        sequence = []
                        move_history = []
                        opening = True
                        game_over = False
                        game_result = ""
                        show_dialog = False  # Ẩn dialog
                        frozen_screen = None  # Clear frozen screen
                        print("Game reset!")
                        trained_this_game = False

                        
                    elif clicked_button == 'surrender':
                        if not game_over:
                            # Xác định thông báo surrender chính xác
                            if player_color == chess.WHITE:
                                game_result = "You surrendered! Black (AI) wins!"
                            else:
                                game_result = "You surrendered! White (AI) wins!"
                            game_over = True
                            show_dialog = True  # Hiển thị dialog surrender
                            frozen_screen = None  # Reset để capture màn hình mới
                            print("Player surrendered!")

                        try:
                            print(" AI is training after surrender...")
                            game_data = {
                                'move_history': move_history,
                                'result': "AI Win",  # AI thắng vì player surrender
                                'fen': board.chess_board.fen(),
                                'player_color': 'White' if player_color == chess.WHITE else 'Black',
                                'ai_color': 'White' if ai_color == chess.WHITE else 'Black'
                            }
                            Bot.train_from_game(game_data)
                            Bot.save_model("model.pkl")
                            Bot.save_game_analysis(board, "AI Win")
                            print("AI trained and saved after surrender.")
                            trained_this_game = True  # Đánh dấu đã train để tránh train lại
                        except Exception as e:
                            print(f"Error training AI after surrender: {e}")

                    elif clicked_button == 'undo':
                        if not game_over and not board.is_animating and len(move_history) >= 2:
                            print("UNDO: User requested undo")
                            print(f"UNDO: Move history before: {move_history}")
                            print(f"UNDO: Sequence before: {sequence}")
                            
                            # Backup current state in case undo fails
                            backup_move_history = move_history.copy()
                            backup_sequence = sequence.copy()
                            
                            # Remove last 2 moves from move history FIRST
                            move_history = move_history[:-2]
                            
                            # Remove from sequence if they were opening moves
                            moves_removed_from_sequence = 0
                            for i in range(2):  # Check last 2 moves
                                if len(sequence) > 0 and len(backup_move_history) > i:
                                    last_move = backup_move_history[-(i+1)]
                                    if len(sequence) > 0 and sequence[-1] == last_move:
                                        sequence = sequence[:-1]
                                        moves_removed_from_sequence += 1
                            
                            print(f"UNDO: Removed {moves_removed_from_sequence} moves from sequence")
                            
                            # Call undo function
                            undo_result = board.undo_last_move()
                            
                            if undo_result == 2:
                                print("UNDO: Successfully undid 2 moves")
                                print(f"UNDO: Move history after: {move_history}")
                                print(f"UNDO: Sequence after: {sequence}")
                                
                                # Reset game over state if needed
                                if game_over:
                                    game_over = False
                                    game_result = ""
                                    show_dialog = False
                                    frozen_screen = None
                                    print("UNDO: Game over state reset")
                                
                                # Clear selection
                                board.selected_piece = None
                                
                                # Check if back to opening
                                if len(move_history) < 6:
                                    opening = True
                                    print("UNDO: Back to opening phase")
                                
                            else:
                                # Undo failed, restore everything
                                print("UNDO: Failed, restoring state")
                                move_history = backup_move_history
                                sequence = backup_sequence
                                
                        else:
                            # Show why undo can't be performed
                            if len(move_history) < 2:
                                print("UNDO: Not enough moves (need at least 2)")
                            elif game_over:
                                print("UNDO: Cannot undo when game is over")
                            elif board.is_animating:
                                print("UNDO: Cannot undo during animation")
                            
                    elif clicked_button == 'save':
                        if save_game_state(board, move_history, sequence, player_color):
                            print("Game saved successfully!")
                        else:
                            print("Failed to save game!")
                            
                    elif clicked_button == 'load':
                        saved_state = load_game_state()
                        if saved_state:
                            try:
                                # Create new board and load state
                                board = GUI_Board(*BOARD_SIZE)
                                board.chess_board = chess.Board(saved_state['board_fen'])
                                board.turn = saved_state['turn']
                                move_history = saved_state['move_history']
                                sequence = saved_state['sequence']
                                
                                # Load player color if available
                                if 'player_color' in saved_state:
                                    player_color = saved_state['player_color']
                                    ai_color = chess.BLACK if player_color == chess.WHITE else chess.WHITE
                                    print(f"Loaded - Player: {'Trắng' if player_color == chess.WHITE else 'Đen'}, AI: {'Trắng' if ai_color == chess.WHITE else 'Đen'}")
                                
                                opening = len(sequence) < 6
                                game_over = False
                                game_result = ""
                                show_dialog = False  # Ẩn dialog
                                frozen_screen = None  # Clear frozen screen
                                
                                # Update GUI board state to match chess board
                                board.update_gui_from_chess_board()
                                print("Game loaded successfully!")
                            except Exception as e:
                                print(f"Failed to load game: {e}")
                        else:
                            print("No saved game found!")
                    
                    # Handle board clicks only if not clicking buttons and game not over
                    elif not game_over and not board.is_animating:
                        # Check if click is within board area AND it's player's turn
                        board_rect = pygame.Rect(BORDER_WIDTH, BORDER_WIDTH, BOARD_WIDTH, BOARD_HEIGHT)
                        if board_rect.collidepoint(mx, my) and board.turn == player_color:
                            # Adjust mouse coordinates for border offset
                            adjusted_mx = mx - BORDER_WIDTH
                            adjusted_my = my - BORDER_WIDTH
                            move_made = board.handle_click(adjusted_mx, adjusted_my)
                            if move_made is not None:
                                if opening: 
                                    sequence.append(move_made)
                                # Add player move to history
                                move_history.append(move_made)
        
        # Draw everything - COMPLETELY FIXED: Không nhấp nháy
        if game_over and game_result and show_dialog:
            if frozen_screen is None:
                # Lần đầu tiên hiển thị dialog - capture toàn bộ màn hình
                button_rects = draw(screen, board, move_history, font, button_states, board.turn, player_color, game_over)
                
                # Capture màn hình hiện tại
                frozen_screen = screen.copy()
                
                # Tạo overlay trên frozen screen
                overlay = pygame.Surface((TOTAL_WIDTH, TOTAL_HEIGHT))
                overlay.set_alpha(128)
                overlay.fill((0, 0, 0))
                frozen_screen.blit(overlay, (0, 0))
                
                # Tạo và vẽ dialog
                dialog_surf = create_game_over_dialog_surface(font, game_result)
                dialog_x = (TOTAL_WIDTH - dialog_surf.get_width()) // 2
                dialog_y = (TOTAL_HEIGHT - dialog_surf.get_height()) // 2
                frozen_screen.blit(dialog_surf, (dialog_x, dialog_y))
                
                # Update display một lần duy nhất
                screen.blit(frozen_screen, (0, 0))
                pygame.display.update()
            else:
                # Các lần sau - chỉ blit frozen screen, không vẽ gì thêm
                screen.blit(frozen_screen, (0, 0))
                # KHÔNG CALL pygame.display.update() ở đây để tránh nhấp nháy
            
            # Return button rects for event handling
            panel_rect = pygame.Rect(BOARD_WIDTH + BORDER_WIDTH + 10, BORDER_WIDTH, 
                                   PANEL_WIDTH - 20, BOARD_HEIGHT)
            total_width_per_row = 2 * 70 + 12
            start_x = panel_rect.x + (panel_rect.width - total_width_per_row) // 2
            start_y = panel_rect.y + panel_rect.height - 140
            
            button_rects = {
                'reset': pygame.Rect(start_x, start_y, 70, 30),
                'save': pygame.Rect(start_x + 82, start_y, 70, 30),
                'surrender': pygame.Rect(start_x, start_y + 40, 70, 30),
                'load': pygame.Rect(start_x + 82, start_y + 40, 70, 30),
                'undo': pygame.Rect(panel_rect.x + (panel_rect.width - 70) // 2, start_y + 80, 70, 30)
            }
        else:
            # Game bình thường
            button_rects = draw(screen, board, move_history, font, button_states, board.turn, player_color, game_over)
        
        # Control frame rate for smooth animation  
        clock.tick(60)  # 60 FPS for smooth animation