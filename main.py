import pygame
import chess
from time import sleep
from Board import GUI_Board
import Bot
import json
import os

def draw_gradient_background(display, width, height):
    """Draw simple background without heavy gradient"""
    # Màu nền đơn giản thay vì gradient phức tạp
    background_color = (120, 90, 60)  # Màu nâu đơn giản
    display.fill(background_color)

def draw_button(display, rect, text, font, is_hovered=False, is_disabled=False):
    """Draw a clean button without gradients"""
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
    
    # Draw button background đơn giản
    pygame.draw.rect(display, bg_color, rect)
    
    # Draw border
    pygame.draw.rect(display, border_color, rect, 2)
    
    # Draw text
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    display.blit(text_surface, text_rect)

def draw_move_history_panel(display, move_history, font, panel_rect):
    """Draw move history panel without gradient"""
    # Panel background đơn giản
    panel_surface = pygame.Surface((panel_rect.width, panel_rect.height))
    panel_surface.fill((240, 230, 200))  # Màu đơn thay vì gradient
    
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
            
            if move_text and y_offset < panel_rect.height - 120:  # Leave space for buttons
                # Highlight the latest move
                text_color = (200, 0, 0) if i >= len(move_history) - 2 else (101, 67, 33)
                move_surface = font.render(move_text, True, text_color)
                panel_surface.blit(move_surface, (15, y_offset))
                y_offset += line_height
    
    display.blit(panel_surface, panel_rect.topleft)

def draw_control_buttons(display, panel_rect, font, button_states):
    """Draw control buttons in the panel"""
    button_width = 80
    button_height = 30
    button_spacing = 10
    
    # Reset button
    reset_rect = pygame.Rect(
        panel_rect.x + 10,
        panel_rect.y + panel_rect.height - 115,  # Moved up for new button
        button_width,
        button_height
    )
    
    # Surrender button  
    surrender_rect = pygame.Rect(
        panel_rect.x + button_width + 20,
        panel_rect.y + panel_rect.height - 115,  # Moved up for new button
        button_width,
        button_height
    )
    
    # NEW: Undo button
    undo_rect = pygame.Rect(
        panel_rect.x + 10,
        panel_rect.y + panel_rect.height - 80,
        button_width,
        button_height
    )
    
    # Save button (moved down)
    save_rect = pygame.Rect(
        panel_rect.x + button_width + 20,
        panel_rect.y + panel_rect.height - 80,
        button_width,
        button_height
    )
    
    # Load button (moved down)
    load_rect = pygame.Rect(
        panel_rect.x + 10,
        panel_rect.y + panel_rect.height - 45,
        button_width,
        button_height
    )
    
    # Draw buttons
    draw_button(display, reset_rect, "Reset", font, button_states.get('reset_hover', False))
    draw_button(display, surrender_rect, "Surrender", font, button_states.get('surrender_hover', False))
    draw_button(display, undo_rect, "Undo", font, button_states.get('undo_hover', False), 
                button_states.get('undo_disabled', False))  # Can be disabled
    draw_button(display, save_rect, "Save", font, button_states.get('save_hover', False))
    draw_button(display, load_rect, "Load", font, button_states.get('load_hover', False))
    
    return {
        'reset': reset_rect,
        'surrender': surrender_rect,
        'undo': undo_rect,  # NEW
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
    """Show clean game over dialog without shadows"""
    dialog_width = 300
    dialog_height = 150
    dialog_x = (TOTAL_WIDTH - dialog_width) // 2
    dialog_y = (TOTAL_HEIGHT - dialog_height) // 2
    
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    
    # Draw clean dialog background
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
    # Create a simple background
    draw_gradient_background(display, TOTAL_WIDTH, TOTAL_HEIGHT)
    
    # Draw the chess board (offset by border)
    board.draw(display)
    
    # Draw move history panel
    panel_rect = pygame.Rect(BOARD_WIDTH + BORDER_WIDTH + 10, BORDER_WIDTH, 
                           PANEL_WIDTH - 20, BOARD_HEIGHT)
    draw_move_history_panel(display, move_history, font, panel_rect)
    
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
        
        # Check if undo should be disabled (remove game_over restriction temporarily)
        button_states['undo_disabled'] = len(move_history) < 2  # Only need 2+ moves
        
        # Handle bot moves
        if not game_over and board.turn == chess.BLACK and not board.is_animating:
            print("MAIN DEBUG: Bot turn starting...")
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
                print(f"MAIN DEBUG: Bot made move: {move_made}")
                
            print("Board value after bot has moved:", Bot.get_board_val(board.chess_board))
            print("--------------------------------------")

            if not status:
                game_result = board.is_end_game()
                game_over = True
                print(f"MAIN DEBUG: Game ended with result: {game_result}")
        
        # Check for game end
        if not game_over:
            end_result = board.is_end_game()
            if end_result is not False:
                game_result = end_result
                game_over = True
                print(f"MAIN DEBUG: Game ended in main loop: {game_result}")
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
                        print("AI trained and model saved after the game.")
                        trained_this_game = True
                    except Exception as e:
                        print(f"Error during post-game training: {e}")

     
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
                                print("AI is training on early reset...")
                                game_data = {
                                    'move_history': move_history,
                                    'result': "Reset early",  # Hoặc để "" nếu bạn muốn
                                    'fen': board.chess_board.fen()
                                }
                                Bot.train_from_game(game_data)
                                Bot.save_model("model.pkl")
                                print("AI trained and model saved before reset.")
                                trained_this_game = True
                            except Exception as e:
                                print(f"Error training AI before reset: {e}")

                        # Reset game
                        board = GUI_Board(*BOARD_SIZE)
                        sequence = []
                        move_history = []
                        opening = True
                        game_over = False
                        game_result = ""
                        trained_this_game = False
                        print("Game reset!")

                        
                    elif clicked_button == 'undo':
                        print(f"MAIN DEBUG: Undo clicked. Move history length: {len(move_history)}")
                        print(f"MAIN DEBUG: Game over: {game_over}")
                        print(f"MAIN DEBUG: Current board turn: {'White' if board.turn == chess.WHITE else 'Black'}")
                        
                        if len(move_history) >= 2:  # Remove game_over check temporarily
                            try:
                                # Always undo both AI move and player move to get back to player's turn
                                moves_undone = board.undo_last_move()
                                print(f"MAIN DEBUG: Undo returned: {moves_undone}")
                                
                                if moves_undone:
                                    # Remove corresponding moves from history
                                    for i in range(moves_undone):
                                        if len(move_history) > 0:
                                            removed_move = move_history.pop()
                                            print(f"MAIN DEBUG: Removed move from history: {removed_move}")
                                    
                                    # If we're in opening, also remove from sequence
                                    if opening:
                                        for i in range(moves_undone):
                                            if len(sequence) > 0:
                                                removed_seq = sequence.pop()
                                                print(f"MAIN DEBUG: Removed from sequence: {removed_seq}")
                                    
                                    # Reset game state flags
                                    opening = len(sequence) < 6
                                    game_over = False  # FORCE reset game over flag
                                    game_result = ""   # Clear game result
                                    
                                    print(f"MAIN DEBUG: After undo - Move history: {move_history}")
                                    print(f"MAIN DEBUG: After undo - Board turn: {'White' if board.turn == chess.WHITE else 'Black'}")
                                    print(f"MAIN DEBUG: After undo - Opening: {opening}")
                                    print(f"MAIN DEBUG: After undo - Game over: {game_over}")
                                    print(f"MAIN DEBUG: After undo - Can undo again: {len(move_history) >= 2}")
                                else:
                                    print("MAIN DEBUG: Undo failed!")
                            except Exception as e:
                                print(f"MAIN DEBUG: Error during undo: {e}")
                                import traceback
                                traceback.print_exc()
                        else:
                            print("MAIN DEBUG: Cannot undo - insufficient moves or game over!")
                            
                    elif clicked_button == 'surrender':
                        if not game_over:
                            game_result = "You surrendered! Black wins!"
                            game_over = True
                            print("Player surrendered!")

                            try:
                                Bot.save_game_analysis(board, game_result)
                            except Exception as e:
                                print(f"Error saving analysis: {e}")


                            
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