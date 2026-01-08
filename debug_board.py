from board import Board

def show_board(b):
    print("Board rows (r0..r7):")
    for i, row in enumerate(b.board):
        print(f"{i}: {''.join(row)}")
    print("\nEmpty-square symbols found in board:", {cell for row in b.board for cell in row if cell == '.'})
    print()

def show_kings_and_meta(b):
    white_king = b.get_king_position(True)
    black_king = b.get_king_position(False)
    print("White king:", white_king)
    print("Black king:", black_king)
    print("White to move:", b.white_to_move)
    print("Castling rights:", b.castling_rights)
    print("En-passant:", b.en_passant_target)
    print("Halfmove:", b.halfmove_clock)
    print("Fullmove:", b.fullmove_number)
    print()

def main():
    print("Importing Board from board.py ...")
    b = Board()
    show_board(b)
    show_kings_and_meta(b)

    pseudo = b.generate_pseudo_legal_moves()
    print("Pseudo-legal moves count:", len(pseudo))
    legal = b.generate_legal_moves()
    print("Legal moves count:", len(legal))
    print()

    if pseudo:
        print("First pseudo-legal moves:")
        for i, m in enumerate(pseudo[:20]):
            print(f"  {i+1:2}. {m}  (start={m.start}, end={m.end}, promo={m.promotion}, enp={m.en_passant}, castle={m.castle})")
        print()

    if legal:
        print("First legal moves:")
        for i, m in enumerate(legal[:10]):
            print(f"  {i+1:2}. {m}")
        print()

    # quick sanity check
    test_move = pseudo[0]
    print("Testing make/undo on pseudo-legal move:", test_move)
    before_board = [r[:] for r in b.board]
    before_meta = (b.white_to_move, b.castling_rights.copy(), b.en_passant_target)

    b.make_move(test_move)
    print("After making move (first 4 rows):")
    for row in b.board[:4]:
        print(" ", ''.join(row))

    b.undo_move(test_move, test_move.captured)
    after_board = [r[:] for r in b.board]
    after_meta = (b.white_to_move, b.castling_rights.copy(), b.en_passant_target)

    print("Restored board equals before? ->", before_board == after_board)
    print("Restored meta equals before? ->", before_meta == after_meta)
    print()

    wk = b.get_king_position(True)
    bk = b.get_king_position(False)
    print("is_attacked(white_king, by_white=False) -> should be False:", b.is_attacked(wk, by_white=False))
    print("is_attacked(black_king, by_white=True)  -> should be False:", b.is_attacked(bk, by_white=True))

if __name__ == "__main__":
    main()
