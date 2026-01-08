import math
import random

# ========================== ENGINE CONFIG =============================
MAX_DEPTH = 3      # Increase to 4 or 5 for stronger play (slower)

PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
    'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': -20000
}

# ===================== PIECE-SQUARE TABLES ============================
# White tables; for black use reversed indexing
PST_PAWN = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

PST_KNIGHT = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20, 0, 5, 5, 0,-20,-40],
    [-30, 5,10,15,15,10, 5,-30],
    [-30, 0,15,20,20,15, 0,-30],
    [-30, 5,15,20,20,15, 5,-30],
    [-30, 0,10,15,15,10, 0,-30],
    [-40,-20, 0, 0, 0, 0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

PST_BISHOP = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10, 5, 0, 0, 0, 0, 5,-10],
    [-10,10,10,10,10,10,10,-10],
    [-10, 0,10,10,10,10, 0,-10],
    [-10, 5, 5,10,10, 5, 5,-10],
    [-10, 0, 5,10,10, 5, 0,-10],
    [-10, 0, 0, 0, 0, 0, 0,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

PST_ROOK = [
    [0, 0, 5,10,10, 5, 0, 0],
    [-5, 0, 0, 0, 0, 0, 0,-5],
    [-5, 0, 0, 0, 0, 0, 0,-5],
    [-5, 0, 0, 0, 0, 0, 0,-5],
    [-5, 0, 0, 0, 0, 0, 0,-5],
    [-5, 0, 0, 0, 0, 0, 0,-5],
    [5,10,10,10,10,10,10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

PST_QUEEN = [
    [-20,-10,-10,-5,-5,-10,-10,-20],
    [-10, 0, 5, 0, 0, 0, 0,-10],
    [-10, 5, 5, 5, 5, 5, 0,-10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0,-10],
    [-10, 0, 5, 0, 0, 0, 0,-10],
    [-20,-10,-10,-5,-5,-10,-10,-20]
]

PST_KING = [
    [20, 30, 10, 0, 0, 10, 30, 20],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30]
]

# ====================== ENGINE CLASS ================================

class Engine:
    def evaluate_piece(self, piece, r, c):
        """Material + position evaluation."""
        if piece == '.':
            return 0

        val = PIECE_VALUES[piece]

        # apply PST
        table = {
            'P': PST_PAWN, 'N': PST_KNIGHT, 'B': PST_BISHOP,
            'R': PST_ROOK, 'Q': PST_QUEEN, 'K': PST_KING
        }.get(piece.upper(), None)

        if table:
            if piece.isupper():  # white
                val += table[r][c]
            else:                 # black
                val -= table[7 - r][c]

        return val

    def evaluate(self, board):
        """Full board evaluation: material + PST + mobility."""
        score = 0

        # material + PST
        for r in range(8):
            for c in range(8):
                score += self.evaluate_piece(board.board[r][c], r, c)

        # mobility
        moves = board.generate_legal_moves()
        mobility = len(moves)
        score += (mobility * 2 if board.white_to_move else -mobility * 2)

        return score

    # ========================= SEARCH ============================

    def search(self, board, depth, alpha, beta):
        if depth == 0:
            return self.evaluate(board)

        moves = board.generate_legal_moves()
        if not moves:
            return self.evaluate(board)

        if board.white_to_move:
            max_eval = -math.inf
            for move in moves:
                board.make_move(move)
                eval = self.search(board, depth - 1, alpha, beta)
                board.undo_move()
                if eval > max_eval:
                    max_eval = eval
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval

        else:
            min_eval = math.inf
            for move in moves:
                board.make_move(move)
                eval = self.search(board, depth - 1, alpha, beta)
                board.undo_move()
                if eval < min_eval:
                    min_eval = eval
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    # ========================== BEST MOVE ==========================

    def get_best_move(self, board):
        moves = board.generate_legal_moves()
        best_move = None
        best_value = -math.inf if board.white_to_move else math.inf

        for move in moves:
            board.make_move(move)
            value = self.search(board, MAX_DEPTH, -math.inf, math.inf)
            board.undo_move()

            if board.white_to_move:
                if value > best_value:
                    best_value = value
                    best_move = move
            else:
                if value < best_value:
                    best_value = value
                    best_move = move

        return best_move
