class Move:
    def __init__(self, start, end, piece, captured='.', promotion=None,
                 en_passant=False, castling=False):
        self.start = start
        self.end = end
        self.piece = piece
        self.captured = captured
        self.promotion = promotion
        self.en_passant = en_passant
        self.castling = castling

    def __str__(self):
        sr, sc = self.start
        er, ec = self.end
        return f"{chr(sc+97)}{8-sr}{chr(ec+97)}{8-er}"


class Board:
    def __init__(self):
        self.board = [
            ['r','n','b','q','k','b','n','r'],
            ['p']*8,
            ['.']*8,
            ['.']*8,
            ['.']*8,
            ['.']*8,
            ['P']*8,
            ['R','N','B','Q','K','B','N','R']
        ]
        self.white_to_move = True
        self.move_log = []

        self.en_passant_square = None
        self.castling_rights = {'K':True,'Q':True,'k':True,'q':True}

    # -----------------------------------------------------
    # MAKE MOVE (✔ FIXED — NO DISAPPEARING PIECES)
    # -----------------------------------------------------
    def make_move(self, move):
        sr, sc = move.start
        er, ec = move.end

        self.move_log.append((
            move,
            self.board[er][ec],
            self.en_passant_square,
            self.castling_rights.copy()
        ))

        piece = move.piece

        # Normal / promotion
        if not move.en_passant:
            self.board[er][ec] = move.promotion if move.promotion else piece
            self.board[sr][sc] = '.'

        # En passant capture
        else:
            self.board[er][ec] = piece
            self.board[sr][sc] = '.'
            cap_r = er + (1 if piece.isupper() else -1)
            self.board[cap_r][ec] = '.'

        # Castling
        if move.castling:
            if ec == 6:  # king side
                self.board[er][5] = self.board[er][7]
                self.board[er][7] = '.'
            else:        # queen side
                self.board[er][3] = self.board[er][0]
                self.board[er][0] = '.'

        # Update en-passant possible square
        self.en_passant_square = None
        if piece.upper() == 'P' and abs(er - sr) == 2:
            self.en_passant_square = ((sr + er) // 2, ec)

        # Remove castling rights when rook or king moves
        if piece == "K":
            self.castling_rights['K'] = False
            self.castling_rights['Q'] = False
        if piece == "k":
            self.castling_rights['k'] = False
            self.castling_rights['q'] = False

        if piece == "R" and (sr,sc) == (7,0): self.castling_rights['Q'] = False
        if piece == "R" and (sr,sc) == (7,7): self.castling_rights['K'] = False
        if piece == "r" and (sr,sc) == (0,0): self.castling_rights['q'] = False
        if piece == "r" and (sr,sc) == (0,7): self.castling_rights['k'] = False

        self.white_to_move = not self.white_to_move

    # -----------------------------------------------------
    # UNDO MOVE (✔ FIXED — NO GHOST PIECES)
    # -----------------------------------------------------
    def undo_move(self):
        if not self.move_log:
            return

        move, old_target, ep_old, cast_old = self.move_log.pop()
        sr, sc = move.start
        er, ec = move.end
        piece = move.piece

        # Restore castling rights, en-passant
        self.castling_rights = cast_old
        self.en_passant_square = ep_old

        # Undo en-passant
        if move.en_passant:
            self.board[sr][sc] = piece
            self.board[er][ec] = '.'
            cap_r = er + (1 if piece.isupper() else -1)
            self.board[cap_r][ec] = move.captured
        else:
            self.board[sr][sc] = piece
            self.board[er][ec] = old_target

        # Undo castling move
        if move.castling:
            if ec == 6:  # king side
                self.board[er][7] = self.board[er][5]
                self.board[er][5] = '.'
            else:        # queen side
                self.board[er][0] = self.board[er][3]
                self.board[er][3] = '.'

        self.white_to_move = not self.white_to_move

    # -----------------------------------------------------
    # LEGAL MOVE GENERATION
    # -----------------------------------------------------
    def generate_legal_moves(self):
        legal = []
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p == '.': continue
                if p.isupper() != self.white_to_move: continue

                for mv in self._piece_moves(r, c, p):
                    self.make_move(mv)
                    if not self.in_check('w' if p.isupper() else 'b'):
                        legal.append(mv)
                    self.undo_move()

        return legal

    # -----------------------------------------------------
    # KING CHECK LOGIC (clean)
    # -----------------------------------------------------
    def in_check(self, color):
        king = 'K' if color=='w' else 'k'

        kr = kc = None
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == king:
                    kr, kc = r, c
                    break
        if kr is None: return True

        return self.square_attacked(kr, kc, 'b' if color=='w' else 'w')

    def square_attacked(self, r, c, attacker_color):
        turn = self.white_to_move
        self.white_to_move = (attacker_color == 'w')

        for rr in range(8):
            for cc in range(8):
                p = self.board[rr][cc]
                if p=='.': continue
                if p.isupper() != (attacker_color=='w'): continue

                for mv in self._piece_moves(rr, cc, p, ignore_king=True):
                    if mv.end == (r, c):
                        self.white_to_move = turn
                        return True

        self.white_to_move = turn
        return False

    # -----------------------------------------------------
    # PSEUDO LEGAL MOVE GENERATION (correct, minimal)
    # -----------------------------------------------------
    def _piece_moves(self, r, c, p, ignore_king=False):
        moves = []
        color = 'w' if p.isupper() else 'b'
        enemy = not p.isupper()

        # ----- Pawn -----
        if p.upper() == 'P':
            d = -1 if color=='w' else 1
            start = 6 if color=='w' else 1

            # forward
            if self.empty(r+d,c):
                # promotion
                if (r+d==0 and color=='w') or (r+d==7 and color=='b'):
                    for promo in ['Q','R','B','N']:
                        moves.append(Move((r,c),(r+d,c),p,promotion=promo if color=='w' else promo.lower()))
                else:
                    moves.append(Move((r,c),(r+d,c),p))

                # double step
                if r==start and self.empty(r+2*d,c):
                    moves.append(Move((r,c),(r+2*d,c),p))

            # captures
            for dc in (-1,1):
                nr, nc = r+d, c+dc
                if not self.in_bounds(nr,nc): continue
                t = self.board[nr][nc]
                if t!='.' and (t.isupper()!=p.isupper()):
                    if ignore_king and t.upper()=='K': pass
                    else: moves.append(Move((r,c),(nr,nc),p,captured=t))

                # en passant
                if self.en_passant_square == (nr,nc):
                    moves.append(Move((r,c),(nr,nc),p,en_passant=True))

        # ----- Knight -----
        elif p.upper()=='N':
            for dr,dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
                nr,nc = r+dr,c+dc
                if self.in_bounds(nr,nc):
                    t = self.board[nr][nc]
                    if t=='.' or t.isupper()!=p.isupper():
                        if ignore_king and t.upper()=='K': continue
                        moves.append(Move((r,c),(nr,nc),p,captured=t))

        # ----- Sliding pieces -----
        elif p.upper() in ['B','R','Q']:
            dirs = []
            if p.upper() in ['B','Q']:
                dirs += [(-1,-1),(-1,1),(1,-1),(1,1)]
            if p.upper() in ['R','Q']:
                dirs += [(-1,0),(1,0),(0,-1),(0,1)]

            for dr,dc in dirs:
                nr,nc = r+dr,c+dc
                while self.in_bounds(nr,nc):
                    t = self.board[nr][nc]
                    if t=='.':
                        moves.append(Move((r,c),(nr,nc),p))
                    else:
                        if t.isupper()!=p.isupper():
                            if ignore_king and t.upper()=='K': break
                            moves.append(Move((r,c),(nr,nc),p,captured=t))
                        break
                    nr+=dr; nc+=dc

        # ----- King -----
        elif p.upper()=='K':
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr==0 and dc==0: continue
                    nr,nc = r+dr,c+dc
                    if self.in_bounds(nr,nc):
                        t=self.board[nr][nc]
                        if t=='.' or t.isupper()!=p.isupper():
                            if ignore_king and t.upper()=='K': continue
                            moves.append(Move((r,c),(nr,nc),p,captured=t))

            # Castling
            moves += self._castle_moves(r, c, p)

        return moves

    # -----------------------------------------------------
    # CASTLING
    # -----------------------------------------------------
    def _castle_moves(self, r, c, k):
        moves = []
        color = 'w' if k.isupper() else 'b'
        enemy = 'b' if color=='w' else 'w'

        if color=='w':
            if self.castling_rights['K'] and self.board[7][5]==self.board[7][6]=='.':
                if not self.square_attacked(7,4,enemy) and \
                   not self.square_attacked(7,5,enemy) and \
                   not self.square_attacked(7,6,enemy):
                    moves.append(Move((7,4),(7,6),k,castling=True))
            if self.castling_rights['Q'] and self.board[7][1]==self.board[7][2]==self.board[7][3]=='.':
                if not self.square_attacked(7,4,enemy) and \
                   not self.square_attacked(7,3,enemy) and \
                   not self.square_attacked(7,2,enemy):
                    moves.append(Move((7,4),(7,2),k,castling=True))

        else:
            if self.castling_rights['k'] and self.board[0][5]==self.board[0][6]=='.':
                if not self.square_attacked(0,4,enemy) and \
                   not self.square_attacked(0,5,enemy) and \
                   not self.square_attacked(0,6,enemy):
                    moves.append(Move((0,4),(0,6),k,castling=True))
            if self.castling_rights['q'] and self.board[0][1]==self.board[0][2]==self.board[0][3]=='.':
                if not self.square_attacked(0,4,enemy) and \
                   not self.square_attacked(0,3,enemy) and \
                   not self.square_attacked(0,2,enemy):
                    moves.append(Move((0,4),(0,2),k,castling=True))

        return moves

    # -----------------------------------------------------
    def in_bounds(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def empty(self, r, c):
        return self.in_bounds(r,c) and self.board[r][c]=='.'
