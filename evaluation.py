PIECE_VALUES = {
    'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': -20000,
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000
}

def evaluate_board(board):
    score = 0
    for r in range(8):
        for c in range(8):
            piece = board.board[r][c]
            if piece == '.':
                continue
            score += PIECE_VALUES.get(piece, 0)
    return score if board.white_to_move else -score
