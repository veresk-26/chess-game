import pygame
import sys
import time
import random
import copy
import math

pygame.init()
WIDTH, HEIGHT = 560, 660
BOARD_SIZE = 400
CELL = 50
OFFSET_X = 60
OFFSET_Y = 80

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess vs AI")

# Colors
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (50, 50, 200)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
BROWN = (139, 69, 19)
GOLD = (218, 165, 32)

# Piece values
PIECE_VALUES = {
    'P': 100, 'p': -100,
    'N': 320, 'n': -320,
    'B': 330, 'b': -330,
    'R': 500, 'r': -500,
    'Q': 900, 'q': -900,
    'K': 20000, 'k': -20000
}

def draw_antlers(surf, cx, cy, size, color=BROWN):
    """Draw deer antlers between buttons"""
    s = size / 100
    
    # Left antler
    points_left = [
        (cx - 30*s, cy + 20*s),
        (cx - 45*s, cy + 5*s),
        (cx - 55*s, cy - 15*s),
        (cx - 50*s, cy - 25*s),
        (cx - 40*s, cy - 15*s),
        (cx - 35*s, cy - 30*s),
        (cx - 25*s, cy - 25*s),
        (cx - 28*s, cy - 10*s),
        (cx - 20*s, cy + 5*s),
        (cx - 25*s, cy + 15*s),
    ]
    
    # Right antler
    points_right = [
        (cx + 30*s, cy + 20*s),
        (cx + 45*s, cy + 5*s),
        (cx + 55*s, cy - 15*s),
        (cx + 50*s, cy - 25*s),
        (cx + 40*s, cy - 15*s),
        (cx + 35*s, cy - 30*s),
        (cx + 25*s, cy - 25*s),
        (cx + 28*s, cy - 10*s),
        (cx + 20*s, cy + 5*s),
        (cx + 25*s, cy + 15*s),
    ]
    
    pygame.draw.polygon(surf, color, points_left)
    pygame.draw.polygon(surf, BLACK, points_left, 2)
    pygame.draw.polygon(surf, color, points_right)
    pygame.draw.polygon(surf, BLACK, points_right, 2)
    pygame.draw.circle(surf, color, (cx, cy + 20*s), 4*s)
    pygame.draw.circle(surf, BLACK, (cx, cy + 20*s), 4*s, 1)

def draw_king(surf, x, y, color):
    rect = pygame.Rect(x-CELL//2+5, y-CELL//2+2, CELL-10, CELL-4)
    pygame.draw.rect(surf, color, rect)
    pygame.draw.rect(surf, BLACK, rect, 2)
    for dx in [-CELL//4, 0, CELL//4]:
        pygame.draw.line(surf, YELLOW, (x+dx, y-CELL//2+2), (x+dx, y-CELL//2-6), 3)

def draw_queen(surf, x, y, color):
    rect = pygame.Rect(x-CELL//2+5, y-CELL//3+5, CELL-10, CELL//2-5)
    pygame.draw.rect(surf, color, rect)
    pygame.draw.rect(surf, BLACK, rect, 2)
    for dx in range(-2, 3):
        pygame.draw.line(surf, YELLOW, (x+dx*CELL//6, y-CELL//3+5), (x+dx*CELL//6, y-CELL//3-3), 2)

def draw_bishop(surf, x, y, color):
    oval = pygame.Rect(x-CELL//2+5, y-CELL//4, CELL-10, CELL//2-5)
    pygame.draw.ellipse(surf, color, oval)
    pygame.draw.ellipse(surf, BLACK, oval, 2)
    hole = pygame.Rect(x-CELL//6, y-CELL//6, CELL//3, CELL//3)
    bg_color = LIGHT if ((x-OFFSET_X)//CELL + (y-OFFSET_Y)//CELL)%2==0 else DARK
    pygame.draw.ellipse(surf, bg_color, hole)
    pygame.draw.ellipse(surf, BLACK, hole, 2)

def draw_pawn(surf, x, y, color):
    pygame.draw.circle(surf, color, (x, y), CELL//3)
    pygame.draw.circle(surf, BLACK, (x, y), CELL//3, 2)

def draw_knight(surf, x, y, color):
    points = [(x, y+CELL//2), (x-CELL//2, y-CELL//2), (x+CELL//2, y-CELL//2)]
    pygame.draw.polygon(surf, color, points)
    pygame.draw.polygon(surf, BLACK, points, 2)

def draw_rook(surf, x, y, color):
    rect = pygame.Rect(x-CELL//2+5, y-CELL//2+5, CELL-10, CELL-10)
    pygame.draw.rect(surf, color, rect)
    pygame.draw.rect(surf, BLACK, rect, 2)
    hole = pygame.Rect(x-CELL//4, y-CELL//4, CELL//2, CELL//2)
    bg_color = LIGHT if ((x-OFFSET_X)//CELL + (y-OFFSET_Y)//CELL)%2==0 else DARK
    pygame.draw.rect(surf, bg_color, hole)
    pygame.draw.rect(surf, BLACK, hole, 2)

PIECES = {
    'K': (draw_king, WHITE), 'k': (draw_king, BLACK),
    'Q': (draw_queen, WHITE), 'q': (draw_queen, BLACK),
    'B': (draw_bishop, WHITE), 'b': (draw_bishop, BLACK),
    'N': (draw_knight, WHITE), 'n': (draw_knight, BLACK),
    'R': (draw_rook, WHITE), 'r': (draw_rook, BLACK),
    'P': (draw_pawn, WHITE), 'p': (draw_pawn, BLACK),
}

def is_in_check(board, color):
    king = 'k' if color == 'black' else 'K'
    king_pos = None
    for r in range(8):
        for c in range(8):
            if board[r][c] == king:
                king_pos = (r, c)
                break
        if king_pos:
            break
    
    if not king_pos:
        return True
    
    enemy = 'black' if color == 'white' else 'white'
    for r in range(8):
        for c in range(8):
            if board[r][c]:
                piece_color = 'white' if board[r][c].isupper() else 'black'
                if piece_color == enemy:
                    moves = get_piece_moves(board, r, c, check_king=False)
                    if king_pos in moves:
                        return True
    return False

def get_piece_moves(board, row, col, check_king=True):
    piece = board[row][col]
    if not piece:
        return []
    
    moves = []
    color = 'white' if piece.isupper() else 'black'
    
    def in_bounds(r, c):
        return 0 <= r < 8 and 0 <= c < 8
    
    def not_friendly(r, c):
        if not board[r][c]:
            return True
        return (board[r][c].isupper() and color == 'black') or (board[r][c].islower() and color == 'white')
    
    if piece.lower() == 'p':
        direction = -1 if color == 'white' else 1
        start_row = 6 if color == 'white' else 1
        if in_bounds(row+direction, col) and not board[row+direction][col]:
            moves.append((row+direction, col))
            if row == start_row and not board[row+2*direction][col]:
                moves.append((row+2*direction, col))
        for dc in [-1, 1]:
            if in_bounds(row+direction, col+dc):
                target = board[row+direction][col+dc]
                if target and ((target.isupper() and color == 'black') or (target.islower() and color == 'white')):
                    moves.append((row+direction, col+dc))
    
    elif piece.lower() == 'n':
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            r, c = row+dr, col+dc
            if in_bounds(r, c) and not_friendly(r, c):
                moves.append((r, c))
    
    elif piece.lower() == 'b':
        for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            for i in range(1, 8):
                r, c = row+dr*i, col+dc*i
                if not in_bounds(r, c):
                    break
                if board[r][c]:
                    if not_friendly(r, c):
                        moves.append((r, c))
                    break
                moves.append((r, c))
    
    elif piece.lower() == 'r':
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            for i in range(1, 8):
                r, c = row+dr*i, col+dc*i
                if not in_bounds(r, c):
                    break
                if board[r][c]:
                    if not_friendly(r, c):
                        moves.append((r, c))
                    break
                moves.append((r, c))
    
    elif piece.lower() == 'q':
        for dr, dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            for i in range(1, 8):
                r, c = row+dr*i, col+dc*i
                if not in_bounds(r, c):
                    break
                if board[r][c]:
                    if not_friendly(r, c):
                        moves.append((r, c))
                    break
                moves.append((r, c))
    
    elif piece.lower() == 'k':
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row+dr, col+dc
                if in_bounds(r, c) and not_friendly(r, c):
                    moves.append((r, c))
    
    if check_king:
        valid_moves = []
        for move in moves:
            test_board = copy.deepcopy(board)
            test_board[move[0]][move[1]] = test_board[row][col]
            test_board[row][col] = ''
            if not is_in_check(test_board, color):
                valid_moves.append(move)
        return valid_moves
    
    return moves

def get_all_moves(board, color):
    all_moves = []
    for r in range(8):
        for c in range(8):
            if board[r][c]:
                piece_color = 'white' if board[r][c].isupper() else 'black'
                if piece_color == color:
                    moves = get_piece_moves(board, r, c)
                    for move in moves:
                        all_moves.append(((r, c), move))
    return all_moves

def get_piece_value(piece):
    if not piece:
        return 0
    return abs(PIECE_VALUES.get(piece, 0))

def get_attacked_squares(board, color):
    attacked = set()
    for r in range(8):
        for c in range(8):
            if board[r][c]:
                piece_color = 'white' if board[r][c].isupper() else 'black'
                if piece_color == color:
                    moves = get_piece_moves(board, r, c, check_king=False)
                    for move in moves:
                        attacked.add(move)
    return attacked

def get_piece_attackers(board, square, color):
    attackers = []
    for r in range(8):
        for c in range(8):
            if board[r][c]:
                piece_color = 'white' if board[r][c].isupper() else 'black'
                if piece_color == color:
                    moves = get_piece_moves(board, r, c, check_king=False)
                    if square in moves:
                        attackers.append((r, c, board[r][c]))
    return attackers

def ai_move(board, color):
    moves = get_all_moves(board, color)
    if not moves:
        return None
    
    enemy_color = 'white' if color == 'black' else 'black'
    
    best_moves = []
    best_score = -999999
    
    for (from_pos, to_pos) in moves:
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = board[from_row][from_col]
        captured = board[to_row][to_col]
        
        score = 0
        our_value = get_piece_value(piece)
        captured_value = get_piece_value(captured)
        
        test_board = copy.deepcopy(board)
        test_board[to_row][to_col] = test_board[from_row][from_col]
        test_board[from_row][from_col] = ''
        
        if is_in_check(test_board, color):
            score -= 5000
        
        enemy_attacks = get_attacked_squares(board, enemy_color)
        is_under_attack = (from_row, from_col) in enemy_attacks
        
        if is_under_attack and piece.lower() != 'k':
            if our_value >= 500:
                score += 300
            elif our_value >= 300:
                score += 200
            else:
                score += 40
        
        if captured:
            enemy_attackers = get_piece_attackers(board, to_pos, enemy_color)
            our_attackers = get_piece_attackers(board, to_pos, color)
            
            enemy_count = len(enemy_attackers)
            our_count = len(our_attackers) + 1
            
            if captured_value >= 900:
                score += captured_value * 15
            elif our_value >= 300 and captured_value <= 100:
                score -= 1000
                if (color == 'black' and to_row == 7) or (color == 'white' and to_row == 0):
                    score += 50
            elif our_value >= 500 and captured_value <= 330:
                score -= 1500
            elif enemy_count == 0:
                score += captured_value * 10
                if our_value < captured_value:
                    score += (captured_value - our_value) * 5
            elif our_count > enemy_count:
                score += captured_value * 8
                if our_value < captured_value:
                    score += (captured_value - our_value) * 4
            elif our_count == enemy_count:
                if captured_value >= our_value:
                    score += captured_value * 5
                else:
                    score -= (our_value - captured_value) * 8
            else:
                if captured_value >= 900:
                    score += captured_value * 6
                else:
                    score -= our_value * 3
        
        if our_value > 0 and not captured:
            enemy_attacks_after = get_attacked_squares(test_board, enemy_color)
            if (to_row, to_col) in enemy_attacks_after:
                enemy_attackers = get_piece_attackers(test_board, to_pos, enemy_color)
                for (ar, ac, ap) in enemy_attackers:
                    enemy_value = get_piece_value(ap)
                    if enemy_value < our_value:
                        score -= (our_value - enemy_value) * 8
                    elif enemy_value == our_value:
                        score -= 30
                    else:
                        score -= 15
                    break
        
        if piece.lower() == 'p':
            if color == 'black' and to_row == 7:
                score += 200
            if color == 'white' and to_row == 0:
                score += 200
            if color == 'black' and to_row > from_row:
                score += 5
            if color == 'white' and to_row < from_row:
                score += 5
        
        if piece.lower() == 'n' or piece.lower() == 'b':
            if (color == 'black' and from_row in [0, 7]) or (color == 'white' and from_row in [0, 7]):
                if 2 <= to_row <= 5 and 2 <= to_col <= 5:
                    score += 15
        
        if 2 <= to_row <= 5 and 2 <= to_col <= 5:
            score += 5
        
        if piece.lower() == 'k':
            pieces_count = sum(1 for r in range(8) for c in range(8) if board[r][c])
            if pieces_count <= 10:
                if 2 <= to_row <= 5 and 2 <= to_col <= 5:
                    score += 20
        
        score += random.randint(-1, 1)
        
        if score > best_score:
            best_score = score
            best_moves = [(from_pos, to_pos)]
        elif score == best_score:
            best_moves.append((from_pos, to_pos))
    
    if best_moves:
        return random.choice(best_moves)
    return None

def promote_pawn(board, row, col):
    piece = board[row][col]
    if piece == 'P' and row == 0:
        board[row][col] = 'Q'
        return True
    elif piece == 'p' and row == 7:
        board[row][col] = 'q'
        return True
    return False

def reset_game():
    return [
        ['r','n','b','q','k','b','n','r'],
        ['p','p','p','p','p','p','p','p'],
        ['','','','','','','',''],
        ['','','','','','','',''],
        ['','','','','','','',''],
        ['','','','','','','',''],
        ['P','P','P','P','P','P','P','P'],
        ['R','N','B','Q','K','B','N','R']
    ]

class Animation:
    def __init__(self, from_pos, to_pos, piece):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.piece = piece
        self.progress = 0.0
        self.speed = 0.15
        self.finished = False
        
        self.from_x = OFFSET_X + from_pos[1] * CELL + CELL//2
        self.from_y = OFFSET_Y + from_pos[0] * CELL + CELL//2
        self.to_x = OFFSET_X + to_pos[1] * CELL + CELL//2
        self.to_y = OFFSET_Y + to_pos[0] * CELL + CELL//2
    
    def update(self):
        self.progress += self.speed
        if self.progress >= 1.0:
            self.progress = 1.0
            self.finished = True
    
    def get_position(self):
        t = self.progress
        t = t * t * (3 - 2 * t)
        x = self.from_x + (self.to_x - self.from_x) * t
        y = self.from_y + (self.to_y - self.from_y) * t
        return x, y
    
    def draw(self, surf):
        x, y = self.get_position()
        draw_func, color = PIECES[self.piece]
        draw_func(surf, x, y, color)

def draw_board():
    for row in range(8):
        for col in range(8):
            x = OFFSET_X + col*CELL
            y = OFFSET_Y + row*CELL
            color = LIGHT if (row+col)%2==0 else DARK
            pygame.draw.rect(screen, color, (x, y, CELL, CELL))
            
            if selected and (row, col) == selected:
                s = pygame.Surface((CELL, CELL))
                s.set_alpha(100)
                s.fill(GREEN)
                screen.blit(s, (x, y))
            
            if (row, col) in valid_moves:
                s = pygame.Surface((CELL, CELL))
                s.set_alpha(80)
                s.fill((0, 255, 0))
                screen.blit(s, (x, y))
            
            if (row, col) in flash_cells:
                s = pygame.Surface((CELL, CELL))
                s.set_alpha(150)
                s.fill(RED)
                screen.blit(s, (x, y))
            
            if not (animation and not animation.finished and (row, col) == animation.from_pos):
                piece = board[row][col]
                if piece:
                    px = x + CELL//2
                    py = y + CELL//2
                    draw_func, piece_color = PIECES[piece]
                    draw_func(screen, px, py, piece_color)
    
    if animation and not animation.finished:
        animation.draw(screen)
    
    # Coordinates
    font = pygame.font.Font(None, 24)
    for i in range(8):
        letter = chr(ord('a') + i)
        number = str(8 - i)
        
        text = font.render(letter, True, BLACK)
        screen.blit(text, (OFFSET_X + i*CELL + CELL//2 - 6, OFFSET_Y + 8*CELL + 5))
        text = font.render(letter, True, BLACK)
        screen.blit(text, (OFFSET_X + i*CELL + CELL//2 - 6, OFFSET_Y - 22))
        
        text = font.render(number, True, BLACK)
        screen.blit(text, (OFFSET_X - 25, OFFSET_Y + i*CELL + CELL//2 - 8))
        text = font.render(number, True, BLACK)
        screen.blit(text, (OFFSET_X + 8*CELL + 8, OFFSET_Y + i*CELL + CELL//2 - 8))
    
    # Buttons aligned with board edges
    font = pygame.font.Font(None, 32)
    
    button_height = 45
    button_y = OFFSET_Y + 8*CELL + 25
    
    board_left = OFFSET_X
    board_right = OFFSET_X + 8*CELL
    board_center = (board_left + board_right) // 2
    button_width = (board_right - board_left - 60) // 2
    
    # New Game button
    new_game_rect = pygame.Rect(board_left, button_y, button_width, button_height)
    pygame.draw.rect(screen, BLUE, new_game_rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, new_game_rect, 2, border_radius=8)
    text = font.render("New Game", True, WHITE)
    text_rect = text.get_rect(center=new_game_rect.center)
    screen.blit(text, text_rect)
    
    # Antlers
    antler_center_x = board_center
    antler_center_y = button_y + button_height // 2
    draw_antlers(screen, antler_center_x, antler_center_y, 55, BROWN)
    
    # Exit button
    exit_rect = pygame.Rect(board_right - button_width, button_y, button_width, button_height)
    pygame.draw.rect(screen, RED, exit_rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, exit_rect, 2, border_radius=8)
    text = font.render("Exit", True, WHITE)
    text_rect = text.get_rect(center=exit_rect.center)
    screen.blit(text, text_rect)
    
    # Subtitle text below buttons
    font_small = pygame.font.Font(None, 24)
    subtitle = "Experimental Chess of Razor"
    text = font_small.render(subtitle, True, DARK_GRAY)
    text_rect = text.get_rect(center=(WIDTH//2, button_y + button_height + 30))
    screen.blit(text, text_rect)
    
    return new_game_rect, exit_rect

# Initialize
board = reset_game()
game_over = False
winner = None
selected = None
valid_moves = []
flash_cells = []
flash_start = 0
ai_thinking = False
turn = 'white'
ai_move_made = False
animation = None
animating = False

clock = pygame.time.Clock()
running = True

while running:
    current_time = time.time()
    
    # Update animation
    if animation and not animation.finished:
        animation.update()
        if animation.finished:
            from_pos = animation.from_pos
            to_pos = animation.to_pos
            
            board[to_pos[0]][to_pos[1]] = board[from_pos[0]][from_pos[1]]
            board[from_pos[0]][from_pos[1]] = ''
            
            promote_pawn(board, to_pos[0], to_pos[1])
            
            opponent = 'black' if turn == 'white' else 'white'
            opponent_moves = get_all_moves(board, opponent)
            
            if not opponent_moves:
                game_over = True
                if is_in_check(board, opponent):
                    winner = 'Player' if opponent == 'black' else 'AI'
                else:
                    winner = 'Draw'
            
            if not game_over:
                turn = 'white' if turn == 'black' else 'black'
            
            animation = None
            animating = False
    
    # AI turn
    if not game_over and not animating and turn == 'black' and not ai_thinking and not ai_move_made:
        ai_thinking = True
        pygame.time.wait(300)
        
        move = ai_move(board, 'black')
        if move:
            from_pos, to_pos = move
            piece = board[from_pos[0]][from_pos[1]]
            
            animation = Animation(from_pos, to_pos, piece)
            animating = True
            ai_move_made = True
        else:
            game_over = True
            if is_in_check(board, 'black'):
                winner = 'Player'
            else:
                winner = 'Draw'
            ai_move_made = True
        
        ai_thinking = False
    
    if turn == 'white':
        ai_move_made = False
    
    if not game_over and not animating and turn == 'white':
        player_moves = get_all_moves(board, 'white')
        if not player_moves:
            game_over = True
            if is_in_check(board, 'white'):
                winner = 'AI'
            else:
                winner = 'Draw'
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            new_game_rect, exit_rect = draw_board()
            if new_game_rect.collidepoint(mx, my):
                board = reset_game()
                game_over = False
                winner = None
                selected = None
                valid_moves = []
                flash_cells = []
                turn = 'white'
                ai_thinking = False
                ai_move_made = False
                animation = None
                animating = False
                continue
            elif exit_rect.collidepoint(mx, my):
                running = False
                continue
            
            if not game_over and not animating and turn == 'white' and not ai_thinking:
                col = (mx - OFFSET_X) // CELL
                row = (my - OFFSET_Y) // CELL
                
                if 0 <= row < 8 and 0 <= col < 8:
                    if selected is None:
                        if board[row][col] and board[row][col].isupper():
                            selected = (row, col)
                            valid_moves = get_piece_moves(board, row, col)
                    else:
                        if (row, col) in valid_moves:
                            piece = board[selected[0]][selected[1]]
                            
                            animation = Animation(selected, (row, col), piece)
                            animating = True
                            selected = None
                            valid_moves = []
                            flash_cells = []
                        else:
                            flash_cells = [(row, col)]
                            flash_start = current_time
                            if board[row][col] and board[row][col].isupper():
                                selected = (row, col)
                                valid_moves = get_piece_moves(board, row, col)
                            else:
                                selected = None
                                valid_moves = []
                else:
                    selected = None
                    valid_moves = []
                    flash_cells = []
    
    if flash_cells and current_time - flash_start > 0.5:
        flash_cells = []
    
    screen.fill(GRAY)
    new_game_rect, exit_rect = draw_board()
    
    if game_over:
        font = pygame.font.Font(None, 48)
        if winner == 'Player':
            text = font.render("You Win!", True, GREEN)
        elif winner == 'AI':
            text = font.render("AI Wins!", True, RED)
        else:
            text = font.render("Draw!", True, YELLOW)
        text_rect = text.get_rect(center=(WIDTH//2, OFFSET_Y + 8*CELL + 40))
        pygame.draw.rect(screen, DARK_GRAY, (WIDTH//2-100, OFFSET_Y + 8*CELL + 20, 200, 40))
        pygame.draw.rect(screen, BLACK, (WIDTH//2-100, OFFSET_Y + 8*CELL + 20, 200, 40), 2)
        screen.blit(text, text_rect)
    
    if not game_over:
        font = pygame.font.Font(None, 28)
        if turn == 'white':
            turn_text = "Your Turn"
            color = GREEN
        else:
            turn_text = "AI Thinking..."
            color = YELLOW
        text = font.render(turn_text, True, color)
        screen.blit(text, (10, OFFSET_Y + 8*CELL + 35))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()