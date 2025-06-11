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

def draw_button(display, rect, text, font, is_hovered=False, is_disabled=False):
    """Draw a styled button"""
    if is_disabled:
        bg_color = (120, 120, 120)
        text_color = (80, 80, 80)
        border_color = (100, 100, 100)
    elif is_hovered:
        bg_color = (180, 150, 120)
        text_color = (50, 30, 10)
        border_color = (139, 116, 78)
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

def draw_move_history_panel(display, move_history, font, panel_rect):
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
    title = font.render("History of Move", True, (101, 67, 33))
    title_rect = title.get_rect(centerx=panel_rect.width // 2, y=10)
    panel_surface.blit(title, title_rect)
    
    # Divider line
    pygame.draw.line(panel_surface, (101, 67, 33), 
                    (10, 40), (panel_rect.width - 10, 40), 2)
    
    # Move history
    y_offset = 50
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
    """Draw control buttons in the panel - FIXED layout with Undo button"""
    button_width = 70  # Reduced width to fit better
    button_height = 28
    button_spacing = 8
    
    # Calculate positions for 5 buttons in 3 rows to fit properly
    # Row 1: Reset, Surrender
    reset_rect = pygame.Rect(
        panel_rect.x + 10,
        panel_rect.y + panel_rect.height - 130,
        button_width,
        button_height
    )
    
    surrender_rect = pygame.Rect(
        panel_rect.x + 10 + button_width + button_spacing,
        panel_rect.y + panel_rect.height - 130,
        button_width,
        button_height
    )
    
    # Row 2: Undo (centered)
    undo_rect = pygame.Rect(
        panel_rect.x + 10 + (panel_rect.width - 20 - button_width) // 2,
        panel_rect.y + panel_rect.height - 95,
        button_width,
        button_height
    )
    
    # Row 3: Save, Load
    save_rect = pygame.Rect(
        panel_rect.x + 10,
        panel_rect.y + panel_rect.height - 60,
        button_width,
        button_height
    )
    
    load_rect = pygame.Rect(
        panel_rect.x + 10 + button_width + button_spacing,
        panel_rect.y + panel_rect.height - 60,
        button_width,
        button_height
    )
    
    # Check if undo should be disabled (need at least 2 moves in history)
    undo_disabled = len(button_states.get('move_history', [])) < 2
    
    # Draw buttons
    draw_button(display, reset_rect, "Reset", font, button_states.get('reset_hover', False))
    draw_button(display, surrender_rect, "Surrender", font, button_states.get('surrender_hover', False))
    draw_button(display, undo_rect, "Undo", font, button_states.get('undo_hover', False), undo_disabled)
    draw_button(display, save_rect, "Save", font, button_states.get('save_hover', False))
    draw_button(display, load_rect, "Load", font, button_states.get('load_hover', False))
    
    return {
        'reset': reset_rect,
        'surrender': surrender_rect,
        'undo': undo_rect,
        'save': save_rect,
        'load': load_rect
    }

def save_game_state(board, move_history, sequence):
    """Save current game state to file"""
    game_state = {
        'board_fen': board.chess_board.fen(),
        'move_history': move_history,
        'sequence': sequence,
        'turn': board.turn
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

def show_game_over_dialog(display, font, result_text):
    """Show game over dialog"""
    dialog_width = 300
    dialog_height = 150
    dialog_x = (TOTAL_WIDTH - dialog_width) // 2
    dialog_y = (TOTAL_HEIGHT - dialog_height) // 2
    
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    
    # Draw dialog background
    pygame.draw.rect(display, (240, 230, 200), dialog_rect)
    pygame.draw.rect(display, (101, 67, 33), dialog_rect, 3)
    
    # Draw text
    lines = result_text.split('\n')
    y_offset = dialog_y + 20
    for line in lines:
        text_surface = font.render(line, True, (101, 67, 33))
        text_rect = text_surface.get_rect(centerx=dialog_x + dialog_width // 2, y=y_offset)
        display.blit(text_surface, text_rect)
        y_offset += 30

def draw(display, board, move_history, font, button_states):
    # Create a beautiful gradient background
    draw_gradient_background(display, TOTAL_WIDTH, TOTAL_HEIGHT)
    
    # Draw the chess board (offset by border)
    board.draw(display)
    
    # Draw move history panel
    panel_rect = pygame.Rect(BOARD_WIDTH + BORDER_WIDTH + 10, BORDER_WIDTH, 
                           PANEL_WIDTH - 20, BOARD_HEIGHT)
    draw_move_history_panel(display, move_history, font, panel_rect)
    
    # Pass move history info to button drawing for undo state
    button_states['move_history'] = move_history
    
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
        
        # Handle bot moves
        if not game_over and board.turn == chess.BLACK and not board.is_animating:
            print("Board value after player has moved:", Bot.get_board_val(board.chess_board))
            move_made = None
            if opening and len(sequence) < 6:
                move_made = Bot.opening_search(board, sequence)
            
            if move_made is None:
                move_made = Bot.minimax_search(board, 3, board.turn == chess.WHITE)
                opening = False

            status = (move_made is not None)
            if opening and move_made:
                sequence.append(move_made)
            
            # Add bot move to history
            if move_made:
                move_history.append(move_made)
                
            print("Board value after bot has moved:", Bot.get_board_val(board.chess_board))
            print("--------------------------------------")

            if not status:
                game_result = board.is_end_game()
                game_over = True
        
        # Check for game end
        if not game_over:
            end_result = board.is_end_game()
            if end_result is not False:
                game_result = end_result
                game_over = True
                if not trained_this_game:
                # Train AI from this game
                    print("AI is training before reset...")
                    try:
                        game_data = {
                        'move_history': move_history,
                        'result': game_result,
                        'fen': board.chess_board.fen()
                        }
                        Bot.train_from_game(game_data)
                        Bot.save_model("model.pkl")
                        Bot.save_game_analysis(board, game_result)
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
                            'fen': board.chess_board.fen()
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
                                    'fen': board.chess_board.fen()
                                }
                                Bot.train_from_game(game_data)
                                Bot.save_model("model.pkl")
                                Bot.save_game_analysis(board, "Player reset mid-game")
                                print("AI trained and saved before reset.")
                            except Exception as e:
                                print(f"Error training AI before reset: {e}")

                        # Reset game
                        board = GUI_Board(*BOARD_SIZE)
                        sequence = []
                        move_history = []
                        opening = True
                        game_over = False
                        game_result = ""
                        print("Game reset!")
                        trained_this_game = False

                        
                    elif clicked_button == 'surrender':
                        if not game_over:
                            game_result = "You surrendered! Black wins!"
                            game_over = True
                            print("Player surrendered!")

                        try:
                            print(" AI is training after surrender...")
                            game_data = {
                                'move_history': move_history,
                                'result': "Player surrendered",
                                'fen': board.chess_board.fen()
                            }
                            Bot.train_from_game(game_data)
                            Bot.save_model("model.pkl")
                            Bot.save_game_analysis(board, "Player surrendered")
                            print("AI trained and saved after surrender.")
                        except Exception as e:
                            print(f"Error training AI after surrender: {e}")

                    # NEW: Handle Undo button click - IMPROVED VERSION
                    elif clicked_button == 'undo':
                        if not game_over and not board.is_animating and len(move_history) >= 2:
                            print("UNDO: Attempting to undo last 2 moves...")
                            print(f"UNDO: Move history before: {move_history}")
                            print(f"UNDO: Current turn before undo: {'White' if board.turn == chess.WHITE else 'Black'}")
                            
                            # Remove last 2 moves from move_history FIRST
                            undone_moves = move_history[-2:]  # Store for debugging
                            move_history = move_history[:-2]
                            
                            # Update sequence if we're still in opening
                            if opening and len(sequence) >= 2:
                                sequence = sequence[:-2]
                            
                            # Call the undo function from Board.py
                            undo_result = board.undo_last_move()
                            
                            if undo_result == 2:  # Successfully undid 2 moves
                                print(f"UNDO: Successfully undid moves: {undone_moves}")
                                print(f"UNDO: Move history after: {move_history}")
                                print(f"UNDO: Opening sequence after: {sequence}")
                                
                                # Reset game over state if it was set
                                if game_over:
                                    game_over = False
                                    game_result = ""
                                    print("UNDO: Game over state reset")
                                
                                # Clear any selection state
                                board.selected_piece = None
                                
                                # Verify the board state
                                print(f"UNDO: Current turn after undo: {'White' if board.turn == chess.WHITE else 'Black'}")
                                print(f"UNDO: Legal moves available: {len(list(board.chess_board.legal_moves))}")
                                
                                # Check if we're back to opening
                                if len(sequence) < 6:
                                    opening = True
                                    print("UNDO: Back to opening phase")
                                
                            else:
                                # If undo failed, restore the move history
                                move_history.extend(undone_moves)
                                if opening:
                                    sequence.extend(undone_moves)
                                print("UNDO: Failed to undo, move history restored")
                        else:
                            if len(move_history) < 2:
                                print("UNDO: Not enough moves to undo (need at least 2)")
                            elif game_over:
                                print("UNDO: Cannot undo when game is over")
                            elif board.is_animating:
                                print("UNDO: Cannot undo during animation")

                            
                    elif clicked_button == 'save':
                        if save_game_state(board, move_history, sequence):
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
                                opening = len(sequence) < 6
                                game_over = False
                                game_result = ""
                                
                                # Update GUI board state to match chess board
                                board.update_gui_from_chess_board()
                                print("Game loaded successfully!")
                            except Exception as e:
                                print(f"Failed to load game: {e}")
                        else:
                            print("No saved game found!")
                    
                    # Handle board clicks only if not clicking buttons and game not over
                    elif not game_over and not board.is_animating:
                        # Check if click is within board area
                        board_rect = pygame.Rect(BORDER_WIDTH, BORDER_WIDTH, BOARD_WIDTH, BOARD_HEIGHT)
                        if board_rect.collidepoint(mx, my):
                            # Adjust mouse coordinates for border offset
                            adjusted_mx = mx - BORDER_WIDTH
                            adjusted_my = my - BORDER_WIDTH
                            move_made = board.handle_click(adjusted_mx, adjusted_my)
                            if move_made is not None:
                                if opening: 
                                    sequence.append(move_made)
                                # Add player move to history
                                move_history.append(move_made)
        
        # Draw everything
        button_rects = draw(screen, board, move_history, font, button_states)
        
        # Show game over dialog
        if game_over and game_result:
            show_game_over_dialog(screen, font, game_result)
            pygame.display.update()
        
        # Control frame rate for smooth animation
        clock.tick(60)  # 60 FPS for smooth animation