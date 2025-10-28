import chess
import chess.polyglot

BOOK_PATH = "books/M112.bin"


def get_polyglot_move(gs):
    """
    Query polyglot book for best move

    Returns: Move object or None
    """
    try:
        # Convert your board to python-chess format
        fen = gs.board_to_fen()
        board = chess.Board(fen)

        # Query the book
        with chess.polyglot.open_reader(BOOK_PATH) as reader:
            entries = list(reader.find_all(board))

            if entries:
                # Pick move with highest weight (most popular/best)
                best_entry = max(entries, key=lambda e: e.weight)
                uci_move = best_entry.move.uci()  # e.g., "e2e4"
                # Convert to your Move object
                return uci_to_move(uci_move, gs)

    except Exception as e:
        return None

    return None


def uci_to_move(uci_string, gs):
    """Convert UCI format (e2e4) to your Move object"""
    from_file = ord(uci_string[0]) - ord("a")
    from_rank = 8 - int(uci_string[1])
    to_file = ord(uci_string[2]) - ord("a")
    to_rank = 8 - int(uci_string[3])

    # Find matching move in valid moves
    valid_moves = gs.get_valid_moves()
    for move in valid_moves:
        if (
            move.start_r == from_rank
            and move.start_c == from_file
            and move.end_r == to_rank
            and move.end_c == to_file
        ):
            return move

    return None
