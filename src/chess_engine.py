class GameState:
    """
    Represents the complete state of a chess game.
    Handles board representation, move execution, and game rules.
    """

    def __init__(self):
        """Initialize the chess board and game state variables."""

        # 8x8 board: each piece is a 2-char string (color + type)
        # "w"=white, "b"=black; "p"=pawn, "r"=rook, "n"=knight, "b"=bishop, "q"=queen, "k"=king
        # "--" represents empty square
        self.board = [
            [
                "br",
                "bn",
                "bb",
                "bq",
                "bk",
                "bb",
                "bn",
                "br",
            ],  # Rank 8 (black back rank)
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],  # Rank 7 (black pawns)
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # Rank 6 (empty)
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # Rank 5 (empty)
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # Rank 4 (empty)
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # Rank 3 (empty)
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],  # Rank 2 (white pawns)
            [
                "wr",
                "wn",
                "wb",
                "wq",
                "wk",
                "wb",
                "wn",
                "wr",
            ],  # Rank 1 (white back rank)
        ]

        self.white_to_move = True  # White moves first
        self.move_log = []  # History of all moves played

        self.is_p_promotion = False  # Currently unused

        # King position tracking for efficient check detection (row, col)
        self.b_king_loc = (0, 4)  # Black king at e8
        self.w_king_loc = (7, 4)  # White king at e1

        # Game end conditions
        self.checkmate = False
        self.stalemate = False

        # En passant: stores (row, col) where capture is possible, or ()
        self.enpassant_possible = ()

        # Castling rights tracker
        self.is_possible_castling = Castle_R(True, True, True, True)
        self.castling_log = [
            Castle_R(
                self.is_possible_castling.w_k_s,
                self.is_possible_castling.w_q_s,
                self.is_possible_castling.b_k_s,
                self.is_possible_castling.b_q_s,
            )
        ]

    def board_to_fen(self):
        fen_parts = []

        for r in self.board:

            # COUNT NO. OF EMPTY SQUARES
            empty_count = 0
            r_string = ""
            for c in r:
                if c == "--":
                    empty_count += 1

                else:
                    if empty_count > 0:
                        r_string += str(empty_count)
                        empty_count = 0

                    piece = c[1]
                    if c[0] == "w":
                        piece = piece.upper()
                    r_string += piece

            if empty_count > 0:
                r_string += str(empty_count)

            fen_parts.append(r_string)

        fen = "/".join(fen_parts)

        fen += "w" if self.white_to_move else "b"
        fen += " -"

        # En passant target
        if self.enpassant_possible:
            # Convert to algebraic notation
            files = "abcdefgh"
            ranks = "87654321"
            r, c = self.enpassant_possible
            fen += f" {files[c]}{ranks[r]}"
        else:
            fen += " -"

        return fen

    # def fen_to_board(self, fen):

    #     parts = fen.split()

    #     if len(parts)<4:
    #         raise ValueError("Invalid FEN")

    #     rows = parts[0].split('/')
    #     for r_string in rows:
    #         row = []
    #         for char in r_string:
    #             if char.isdigit():
    #                 # Empty squares
    #                 row.extend(["--"] * int(char))
    #             else:
    #                 # Piece: uppercase = white, lowercase = black
    #                 color = "w" if char.isupper() else "b"
    #                 piece = char.lower()
    #                 row.append(color + piece)
    #             self.board.append(row)

    #     # 2. Active color
    #     self.white_to_move = (parts[1] == "w")

    #     # 4. En passant target
    #     if parts[3] != "-":
    #         files = "abcdefgh"
    #         ranks = "87654321"
    #         file = files.index(parts[3][0])
    #         rank = ranks.index(parts[3][1])
    #         self.enpassant_possible = (rank, file)
    #     else:
    #         self.enpassant_possible = ()

    #     # 5. Update king locations
    #     for r in range(8):
    #         for c in range(8):
    #             if self.board[r][c] == "wk":
    #                 self.w_king_loc = (r, c)
    #             elif self.board[r][c] == "bk":
    #                 self.b_king_loc = (r, c)

    #     # Reset move log
    #     self.move_log = []
    #     self.checkmate = False
    #     self.stalemate = False

    def make_move(self, move):
        """Execute a move and update game state."""

        # Handle en passant: captured pawn is not on the destination square
        if move.is_enpassant:
            if self.white_to_move:
                self.board[move.end_r + 1][move.end_c] = "--"  # Remove black pawn
            else:
                self.board[move.end_r - 1][move.end_c] = "--"  # Remove white pawn

        # Execute move
        self.board[move.start_r][move.start_c] = "--"
        self.board[move.end_r][move.end_c] = move.piece_moved

        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

        # Update king position tracker
        if move.piece_moved == "bk":
            self.b_king_loc = (move.end_r, move.end_c)
        elif move.piece_moved == "wk":
            self.w_king_loc = (move.end_r, move.end_c)

        # Set en passant opportunity if pawn moved 2 squares
        if move.piece_moved[1] == "p" and abs(move.start_r - move.end_r) == 2:
            self.enpassant_possible = ((move.start_r + move.end_r) // 2, move.start_c)
        else:
            self.enpassant_possible = ()

        # Update castling rights
        self.update_castle(move)
        self.castling_log.append(
            Castle_R(
                self.is_possible_castling.w_k_s,
                self.is_possible_castling.w_q_s,
                self.is_possible_castling.b_k_s,
                self.is_possible_castling.b_q_s,
            )
        )

    def update_castle(self, move):
        """
        Update castling rights based on piece movements.
        Rights are lost when: king moves (both sides) or rook moves (that side).
        Also handles rook movement during castling execution.
        """

        # King moves: lose all castling rights
        if move.piece_moved == "wk":
            self.is_possible_castling.w_k_s = False
            self.is_possible_castling.w_q_s = False
        elif move.piece_moved == "bk":
            self.is_possible_castling.b_k_s = False
            self.is_possible_castling.b_q_s = False

        # Rook moves from starting position: lose that side's castling
        elif move.piece_moved == "wr":
            if move.start_r == 7:
                if move.start_c == 0:
                    self.is_possible_castling.w_q_s = False
                elif move.start_c == 7:
                    self.is_possible_castling.w_k_s = False

        elif move.piece_moved == "br":
            if move.start_r == 0:
                if move.start_c == 0:
                    self.is_possible_castling.b_q_s = False
                elif move.start_c == 7:
                    self.is_possible_castling.b_k_s = False

        # Execute castling: move the rook
        if move.is_castle:
            if move.end_c - move.start_c == 2:  # Kingside
                self.board[move.end_r][move.end_c - 1] = self.board[move.end_r][
                    move.end_c + 1
                ]
                self.board[move.end_r][move.end_c + 1] = "--"
            else:  # Queenside
                self.board[move.end_r][move.end_c + 1] = self.board[move.end_r][
                    move.end_c - 2
                ]
                self.board[move.end_r][move.end_c - 2] = "--"

    def undo(self):
        """Undo the last move and restore all game state."""

        if len(self.move_log) != 0:
            move = self.move_log.pop()

            # Restore board
            self.board[move.start_r][move.start_c] = move.piece_moved
            self.board[move.end_r][move.end_c] = move.piece_captured
            self.white_to_move = not self.white_to_move

            # Restore king position
            if move.piece_moved == "bk":
                self.b_king_loc = (move.start_r, move.start_c)
            elif move.piece_moved == "wk":
                self.w_king_loc = (move.start_r, move.start_c)

            # Restore en passant captured pawn
            if move.is_enpassant:
                self.board[move.end_r][move.end_c] = "--"
                if move.piece_moved[0] == "w":
                    self.board[move.end_r + 1][move.end_c] = "bp"
                else:
                    self.board[move.end_r - 1][move.end_c] = "wp"

            # Restore en passant opportunity
            if len(self.move_log) > 0:
                last_move = self.move_log[-1]
                if (
                    last_move.piece_moved[1] == "p"
                    and abs(last_move.start_r - last_move.end_r) == 2
                ):
                    self.enpassant_possible = (
                        (last_move.start_r + last_move.end_r) // 2,
                        last_move.start_c,
                    )
                else:
                    self.enpassant_possible = ()
            else:
                self.enpassant_possible = ()

            # Restore castling rights
            self.castling_log.pop()
            last_rights = self.castling_log[-1]

            # Copy those values back into our main, standalone state object
            self.is_possible_castling.w_k_s = last_rights.w_k_s
            self.is_possible_castling.w_q_s = last_rights.w_q_s
            self.is_possible_castling.b_k_s = last_rights.b_k_s
            self.is_possible_castling.b_q_s = last_rights.b_q_s

            # Undo castling rook movement
            if move.is_castle:
                if move.end_c - move.start_c == 2:  # Kingside
                    self.board[move.end_r][move.end_c + 1] = self.board[move.end_r][
                        move.end_c - 1
                    ]
                    self.board[move.end_r][move.end_c - 1] = "--"
                else:  # Queenside
                    self.board[move.end_r][move.end_c - 2] = self.board[move.end_r][
                        move.end_c + 1
                    ]
                    self.board[move.end_r][move.end_c + 1] = "--"

    def get_valid_moves(self):
        """
        Get all legal moves (pseudo-legal moves that don't leave king in check).
        Also detects checkmate and stalemate.
        """

        moves = self.all_possible_moves()
        valid_moves = []
        # Add castling moves
        if self.white_to_move:
            self.get_castling_moves(self.w_king_loc[0], self.w_king_loc[1], moves)
        else:
            self.get_castling_moves(self.b_king_loc[0], self.b_king_loc[1], moves)

        # Test each move to ensure it doesn't leave our king in check
        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])
            self.white_to_move = not self.white_to_move
            if not self.check():
                valid_moves.append(moves[i])
            self.white_to_move = not self.white_to_move
            self.undo()

        # Detect game-ending conditions
        if len(valid_moves) == 0:
            if self.check():
                self.checkmate = True
                self.stalemate = False
            else:
                self.stalemate = True
                self.checkmate = False
        else:
            self.checkmate = False
            self.stalemate = False
        return valid_moves

    def square_under_att(self, r, c):
        """Check if square (r, c) is under attack by opponent."""
        self.white_to_move = not self.white_to_move
        for move in self.all_possible_moves():
            if move.end_r == r and move.end_c == c:
                self.white_to_move = not self.white_to_move
                return True
        self.white_to_move = not self.white_to_move
        return False

    def check(self):
        """Check if current player's king is in check."""
        if self.white_to_move:
            return self.square_under_att(self.w_king_loc[0], self.w_king_loc[1])
        else:
            return self.square_under_att(self.b_king_loc[0], self.b_king_loc[1])

    def all_possible_moves(self):
        """Generate all pseudo-legal moves (may leave king in check)."""
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_to_move) or (
                    turn == "b" and not self.white_to_move
                ):
                    piece = self.board[r][c][1]

                    if piece == "p":
                        self.get_pawn_moves(r, c, moves)
                    elif piece == "r":
                        self.get_rook_moves(r, c, moves)
                    elif piece == "n":
                        self.get_knight_moves(r, c, moves)
                    elif piece == "b":
                        self.get_bishop_moves(r, c, moves)
                    elif piece == "q":
                        self.get_queen_moves(r, c, moves)
                    elif piece == "k":
                        self.get_king_moves(r, c, moves)
        return moves

    def get_pawn_moves(self, r, c, moves):
        """Generate pawn moves: forward, double, captures, and en passant."""
        if self.white_to_move:
            # Forward move
            if r > 0 and self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                # Double move from starting position
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))

            # Diagonal captures and en passant
            for d_col in [-1, 1]:
                end_c = c + d_col
                if 0 <= end_c < 8 and r > 0:
                    if self.board[r - 1][end_c][0] == "b":
                        moves.append(Move((r, c), (r - 1, end_c), self.board))
                    elif (r - 1, end_c) == self.enpassant_possible:
                        moves.append(
                            Move((r, c), (r - 1, end_c), self.board, is_enpassant=True)
                        )

        else:  # Black
            if r < 7 and self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))

            for d_col in [-1, 1]:
                end_c = c + d_col
                if 0 <= end_c < 8 and r < 7:
                    if self.board[r + 1][end_c][0] == "w":
                        moves.append(Move((r, c), (r + 1, end_c), self.board))
                    elif (r + 1, end_c) == self.enpassant_possible:
                        moves.append(
                            Move((r, c), (r + 1, end_c), self.board, is_enpassant=True)
                        )

    def get_rook_moves(self, r, c, moves):
        """Generate rook moves (horizontal and vertical lines)."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            dr, dc = d
            end_r, end_c = r + dr, c + dc
            while 0 <= end_r < 8 and 0 <= end_c < 8:
                end_piece = self.board[end_r][end_c]
                if end_piece == "--":
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                elif end_piece[0] == enemy_color:
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                    break
                else:
                    break
                end_r += dr
                end_c += dc

    def get_bishop_moves(self, r, c, moves):
        """Generate bishop moves (diagonal lines)."""
        directions = [(-1, -1), (1, 1), (1, -1), (-1, 1)]
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            dr, dc = d
            end_r, end_c = r + dr, c + dc
            while 0 <= end_r < 8 and 0 <= end_c < 8:
                end_piece = self.board[end_r][end_c]
                if end_piece == "--":
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                elif end_piece[0] == enemy_color:
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                    break
                else:
                    break
                end_r += dr
                end_c += dc

    def get_queen_moves(self, r, c, moves):
        """Generate queen moves (rook + bishop combined)."""
        directions = [
            (-1, -1),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            dr, dc = d
            end_r, end_c = r + dr, c + dc
            while 0 <= end_r < 8 and 0 <= end_c < 8:
                end_piece = self.board[end_r][end_c]
                if end_piece == "--":
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                elif end_piece[0] == enemy_color:
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                    break
                else:
                    break
                end_r += dr
                end_c += dc

    def get_knight_moves(self, r, c, moves):
        """Generate knight moves (L-shaped jumps)."""
        directions = [
            (-1, -2),
            (2, 1),
            (2, -1),
            (-2, 1),
            (-1, 2),
            (1, 2),
            (-2, -1),
            (1, -2),
        ]
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            dr, dc = d
            end_r, end_c = r + dr, c + dc
            if 0 <= end_r < 8 and 0 <= end_c < 8:
                end_piece = self.board[end_r][end_c]
                if end_piece == "--":
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                elif end_piece[0] == enemy_color:
                    moves.append(Move((r, c), (end_r, end_c), self.board))

    def get_king_moves(self, r, c, moves):
        """Generate king moves (one square in any direction)."""
        directions = [
            (-1, -1),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            dr, dc = d
            end_r, end_c = r + dr, c + dc
            if 0 <= end_r < 8 and 0 <= end_c < 8:
                end_piece = self.board[end_r][end_c]
                if end_piece == "--":
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                elif end_piece[0] == enemy_color:
                    moves.append(Move((r, c), (end_r, end_c), self.board))

    def get_castling_moves(self, r, c, moves):
        """
        Generate castling moves if legal.
        Requirements: pieces haven't moved, squares empty, not moving through/into check.
        """
        if self.square_under_att(r, c):
            return

        if self.white_to_move:
            # White kingside
            if self.is_possible_castling.w_k_s:
                if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
                    if not self.square_under_att(
                        r, c + 1
                    ) and not self.square_under_att(r, c + 2):
                        moves.append(
                            Move((r, c), (r, c + 2), self.board, is_castle=True)
                        )

            # White queenside
            if self.is_possible_castling.w_q_s:
                if (
                    self.board[r][c - 1] == "--"
                    and self.board[r][c - 2] == "--"
                    and self.board[r][c - 3] == "--"
                ):
                    if not self.square_under_att(
                        r, c - 1
                    ) and not self.square_under_att(r, c - 2):
                        moves.append(
                            Move((r, c), (r, c - 2), self.board, is_castle=True)
                        )

        else:  # Black
            # Black kingside
            if self.is_possible_castling.b_k_s:
                if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
                    if not self.square_under_att(
                        r, c + 1
                    ) and not self.square_under_att(r, c + 2):
                        moves.append(
                            Move((r, c), (r, c + 2), self.board, is_castle=True)
                        )

            # Black queenside
            if self.is_possible_castling.b_q_s:
                if (
                    self.board[r][c - 1] == "--"
                    and self.board[r][c - 2] == "--"
                    and self.board[r][c - 3] == "--"
                ):
                    if not self.square_under_att(
                        r, c - 1
                    ) and not self.square_under_att(r, c - 2):
                        moves.append(
                            Move((r, c), (r, c - 2), self.board, is_castle=True)
                        )


class Castle_R:
    """Stores castling rights for both players (kingside and queenside)."""

    def __init__(
        self, white_king_side, white_queen_side, black_king_side, black_queen_side
    ):
        self.w_k_s = white_king_side
        self.w_q_s = white_queen_side
        self.b_k_s = black_king_side
        self.b_q_s = black_queen_side


class Move:
    """Represents a single chess move with notation support."""

    # Board coordinate mappings
    cols_to_files = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
    files_to_cols = {v: k for k, v in cols_to_files.items()}
    rows_to_ranks = {0: "8", 1: "7", 2: "6", 3: "5", 4: "4", 5: "3", 6: "2", 7: "1"}
    ranks_to_rows = {v: k for k, v in rows_to_ranks.items()}

    # Chess notation symbols
    piece_symbols = {"p": "", "r": "R", "n": "N", "b": "B", "q": "Q", "k": "K"}

    def __init__(
        self,
        start_sq,
        end_sq,
        board,
        is_enpassant=False,
        double_move=False,
        is_castle=False,
    ):
        self.start_r, self.start_c = start_sq
        self.end_r, self.end_c = end_sq

        # assign captured and moved piece
        self.piece_moved = board[self.start_r][self.start_c]
        self.piece_captured = board[self.end_r][self.end_c]

        # enpassant and castle booleans
        self.is_enpassant = is_enpassant
        self.double_move = double_move
        self.is_castle = is_castle

        # get which piece is captured, moved and if is captured for engine
        self.is_capture = (self.piece_captured != "--") or self.is_enpassant
        self.captured_piece_type = None
        if self.piece_captured != "--":
            self.captured_piece_type = self.piece_captured[1]  # 'p','n','b','r','q','k'
        self.moved_piece_type = self.piece_moved[1]

        # Check if pawn reaches promotion rank
        self.is_pawn_promotion = False
        if (self.piece_moved == "wp" and self.end_r == 0) or (
            self.piece_moved == "bp" and self.end_r == 7
        ):
            self.is_pawn_promotion = True

    def __eq__(self, other):
        """Compare moves by start and end positions."""
        if isinstance(other, Move):
            return (
                self.start_r == other.start_r
                and self.start_c == other.start_c
                and self.end_r == other.end_r
                and self.end_c == other.end_c
            )
        return False

    def get_chess_notation(self):
        """Convert move to standard chess notation (e.g., 'e4', 'Nf3', 'exd5')."""
        move_str = ""
        piece = self.piece_symbols[self.piece_moved[1]]

        if self.piece_moved[1] == "p":
            # Pawn moves
            if self.piece_captured != "--" or self.is_enpassant:
                move_str += (
                    self.cols_to_files[self.start_c]
                    + "x"
                    + self.get_rank_file(self.end_r, self.end_c)
                )
            else:
                move_str += self.get_rank_file(self.end_r, self.end_c)
        else:
            # Piece moves
            if self.piece_captured != "--":
                move_str += piece + "x" + self.get_rank_file(self.end_r, self.end_c)
            else:
                move_str += piece + self.get_rank_file(self.end_r, self.end_c)

        return move_str

    def get_rank_file(self, r, c):
        """Convert row/col to chess notation (e.g., (0,4) -> 'e8')."""
        return self.cols_to_files[c] + self.rows_to_ranks[r]
