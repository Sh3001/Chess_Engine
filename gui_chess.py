import pygame
import sys
from board import Board
from engine import Engine
from evaluation import evaluate_board

pygame.init()

WIDTH, HEIGHT = 720, 640
BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8
EVAL_BAR_WIDTH = WIDTH - BOARD_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shivam's Chess Engine")

LIGHT = (238, 238, 210)
DARK = (118, 150, 86)
HIGHLIGHT = (246, 246, 105)
BLACK_BAR = (40, 40, 40)
WHITE_BAR = (220, 220, 220)

# Map pieces to asset filenames (adjust to your assets naming)
piece_map = {
    'P': 'wP', 'N': 'wN', 'B': 'wB', 'R': 'wR', 'Q': 'wQ', 'K': 'wK',
    'p': 'p', 'n': 'n', 'b': 'b', 'r': 'r', 'q': 'q', 'k': 'k'
}

pieces = {}
for name in set(piece_map.values()):
    try:
        img = pygame.image.load(f"assets/{name}.svg")
        pieces[name] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
    except Exception as e:
        surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        surf.fill((200, 200, 200))
        pieces[name] = surf


def draw_board(board, selected=None, moves=[]):
    for r in range(8):
        for c in range(8):
            color = LIGHT if (r + c) % 2 == 0 else DARK
            pygame.draw.rect(screen, color, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            # highlight selected square
            if selected == (r, c):
                pygame.draw.rect(screen, HIGHLIGHT, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)

            # draw move hints
            for m in moves:
                if m.end == (r, c):
                    pygame.draw.circle(screen, (180, 180, 80),
                                       (c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2), 10)

            # draw pieces
            piece = board.board[r][c]
            if piece != '.':
                img_key = piece_map.get(piece)
                if img_key and img_key in pieces:
                    screen.blit(pieces[img_key], (c * SQUARE_SIZE, r * SQUARE_SIZE))
                else:
                    rect = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                    rect.fill((150, 0, 0) if piece.isupper() else (0, 0, 150))
                    screen.blit(rect, (c * SQUARE_SIZE, r * SQUARE_SIZE))


def draw_eval_bar(score):
    pygame.draw.rect(screen, BLACK_BAR, (BOARD_SIZE, 0, EVAL_BAR_WIDTH, HEIGHT))
    normalized = max(min(score / 2000.0, 1), -1)
    bar_height = int((HEIGHT / 2) * (1 - normalized))
    pygame.draw.rect(screen, WHITE_BAR, (BOARD_SIZE, bar_height, EVAL_BAR_WIDTH, HEIGHT - bar_height))


def get_square_under_mouse():
    x, y = pygame.mouse.get_pos()
    if x >= BOARD_SIZE:
        return None
    return (y // SQUARE_SIZE, x // SQUARE_SIZE)


def main():
    board = Board()
    engine = Engine(depth=3)  # 3 = strong, 2 = medium, 1 = easy
    selected = None
    move_hints = []
    move_history = []

    running = True
    clock = pygame.time.Clock()

    while running:
        eval_score = evaluate_board(board)
        draw_board(board, selected, move_hints)
        draw_eval_bar(eval_score)
        pygame.display.flip()

        # Engine plays as Black
        if not board.white_to_move:
            move = engine.find_best_move(board)
            if move:
                board.make_move(move)
                move_history.append(str(move))
            else:
                print("Game Over (No legal moves).")
                running = False
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = get_square_under_mouse()
                if not clicked:
                    continue

                if selected is None:
                    piece = board.board[clicked[0]][clicked[1]]
                    if piece != '.' and piece.isupper() == board.white_to_move:
                        selected = clicked
                        move_hints = [m for m in board.generate_legal_moves() if m.start == clicked]
                else:
                    chosen = [m for m in move_hints if m.end == clicked]
                    if chosen:
                        board.make_move(chosen[0])
                        move_history.append(str(chosen[0]))
                    selected = None
                    move_hints = []

        pygame.display.update()
        clock.tick(30)


if __name__ == "__main__":
    main()
