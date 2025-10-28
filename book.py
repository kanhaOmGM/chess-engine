OPENING_BOOK = {
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -": [
        "e2e4",  # King's Pawn Opening
        "d2d4",  # Queen's Pawn Opening
        "c2c4",  # English Opening
        "g1f3",  # Reti Opening (lowercase)
    ],
    # After 1.e4 (white played e4)
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3": [
        "e7e5",  # Open Game
        "c7c5",  # Sicilian Defense
        "e7e6",  # French Defense
    ],
    # After 1.e4 e5 (both played e4 and e5)
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6": [
        "g1f3",  # King's Knight Opening (lowercase)
        "f2f4",  # King's Gambit
        "f1c4",  # Bishop's Opening (lowercase)
    ],
    # After 1.e4 e5 2.Nf3
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -": [
        "b8c6",  # Normal development (lowercase)
        "g8f6",  # Petrov Defense (lowercase)
    ],
    # After 1.d4
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3": [
        "d7d5",  # Closed Game
        "g8f6",  # Indian Defense (lowercase)
    ],
}


def get_book_fen(gs):

    try:
        # Get the full FEN from your board
        full_fen = gs.board_to_fen()

        # Split it into parts
        parts = full_fen.split()

        # Validate we have enough parts
        if len(parts) < 4:
            return None

        # Only keep first 4 parts (ignore move counters)
        book_key = " ".join(parts[:4])

        return book_key

    except Exception as e:

        return None


def string_to_move(move_string, gs, valid_moves):

    try:
        # Remove piece letter if present: "Ng1f3" → "g1f3"
        if len(move_string) >= 5 and move_string[0].isupper():
            move_string = move_string[1:]

        # Ensure we have at least 4 characters
        if len(move_string) < 4:
            return None

        # Now we have format: "e2e4" or "e2e4q" (from-square to-square [promotion])

        # Parse FROM square: "e2"
        from_file = ord(move_string[0].lower()) - ord("a")  # 'e' → 4 (0-indexed)
        from_rank = 8 - int(move_string[1])  # '2' → row 6 (board is flipped)

        # Parse TO square: "e4"
        to_file = ord(move_string[2].lower()) - ord("a")  # 'e' → 4
        to_rank = 8 - int(move_string[3])  # '4' → row 4

        # Check bounds
        if not (
            0 <= from_file < 8
            and 0 <= from_rank < 8
            and 0 <= to_file < 8
            and 0 <= to_rank < 8
        ):
            return None

        # Find this move in valid_moves
        for move in valid_moves:
            if (
                move.start_r == from_rank
                and move.start_c == from_file
                and move.end_r == to_rank
                and move.end_c == to_file
            ):
                return move
        return None

    except (ValueError, IndexError) as e:
        return None


def get_opening_book_move(gs, valid_moves):
    """
    Main function to get an opening book move for the current position.
    Returns a Move object or None if position not in book.
    """
    book_key = get_book_fen(gs)

    if book_key is None:
        return None

    if book_key not in OPENING_BOOK:
        return None

    # Get candidate moves from book
    candidate_strings = OPENING_BOOK[book_key]

    # Try each candidate
    for move_string in candidate_strings:
        move = string_to_move(move_string, gs, valid_moves)
        if move is not None:
            return move
    return None
