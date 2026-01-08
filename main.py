# main.py
from board import Board
from engine import choose_move

def print_board(board):
    for row in board.board:
        print(' '.join(row))
    print()

def eval_bar(score):
    norm = max(min(score / 1000, 1), -1)
    white_fill = int((norm + 1) * 10)
    black_fill = 20 - white_fill
    return f"[{'█'*white_fill}{'░'*black_fill}] {score:.1f}"

if __name__ == "__main__":
    board = Board()
    difficulty = int(input("Select difficulty (1-4): "))

    while True:
        print_board(board)
        print("Evaluation:", eval_bar(0 if board.white_to_move else 0))
        if board.white_to_move:
            move_input = input("Enter your move (e.g., e2e4): ")
            if move_input == "quit":
                break
            try:
                start = (8 - int(move_input[1]), ord(move_input[0]) - 97)
                end = (8 - int(move_input[3]), ord(move_input[2]) - 97)
                move = (start, end)
                board.make_move(move)
            except:
                print("Invalid move format.")
        else:
            print("AI thinking...")
            best_move, score = choose_move(board, difficulty)
            if best_move is None:
                print("Game over!")
                break
            board.make_move(best_move)
            print(f"AI plays {best_move}, Eval={score}")
