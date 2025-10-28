import random
import polyglot_book as p


# I am further inspired to improve storage and search efficiency, from
# the Sebastian League chess challenge.


piece_value = {"k": 0, "q": 10, "r": 5, "b": 3.2, "n": 3, "p": 1}
MATE = 1e5
STALEMATE = 0

TT = {}


# This function is called when there is no best move found
# Stupid yes, we should rather store a better move while searching in each stage
# And return the move if we go out of time
def find_random(valid_moves):
    # do ensure it doesnt go out of bounds
    if len(valid_moves) == 0:
        return None
    # returns a random valid move
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


def find_best_move(gs, valid_moves, depth):
    # This implementation of Transposition Table, I copy pasted this code from a repo
    # I am yet to learn more about it
    key = str(gs.board)
    if key in TT and TT[key]["depth"] >= depth:
        return TT[key]["score"]

    if depth == 0:
        score = evaluate_board(gs)
        TT[key] = {"score": score, "depth": depth}
        return score

    if len(valid_moves) == 0:
        return None
    best_move = None
    if len(gs.move_log) < 20:

        # If found, convert to Move object
        book_move = p.get_polyglot_move(gs)
        if book_move:
            return book_move

    # set
    alpha = -float("inf")
    beta = float("inf")

    # White's turn - maximize
    if gs.white_to_move:
        max_score = -float("inf")
        # check if move is in valid
        for move in valid_moves:
            gs.make_move(move)
            # check for checkmate
            if gs.checkmate:
                gs.undo()
                return move
            # Score this move using minimax
            # find scores and take the highest
            score = minimax(gs, depth - 1, alpha, beta, False)
            gs.undo()
            # for the highest score play that move
            if score > max_score:
                max_score = score
                best_move = move
                alpha = max(alpha, score)

    # Black's turn - minimize
    else:
        min_score = float("inf")

        for move in valid_moves:
            gs.make_move(move)

            if gs.checkmate:
                gs.undo()
                return move

            # Score this move using minimax
            score = minimax(gs, depth - 1, alpha, beta, True)
            gs.undo()
            if score < min_score:
                min_score = score
                best_move = move
                beta = min(beta, score)
    return best_move


# MINIMAX SEARCH ALGO
def minimax(gs, depth, alpha, beta, max_player):

    # Base case: depth 0
    if depth == 0:
        return evaluate_board(gs)
    valid_moves = gs.get_valid_moves()
    # Game over
    if len(valid_moves) == 0:
        if gs.checkmate:
            return -MATE if max_player else MATE
        return STALEMATE

    # Max if white is true
    if max_player:
        max_eval = -float("inf")
        # check for the move in valid moves
        for move in order_moves(gs, valid_moves):
            gs.make_move(move)
            # switch player
            eval_score = minimax(gs, depth - 1, alpha, beta, False)
            gs.undo()
            # get the max eval from 2 nodes
            max_eval = max(max_eval, eval_score)
            # set alpha
            alpha = max(alpha, eval_score)
            # prune a node
            if beta <= alpha:
                break
        return max_eval

    # Min if white is false
    else:
        min_eval = float("inf")
        # search for moves in the order of captures, more revision is required
        for move in order_moves(gs, valid_moves):
            gs.make_move(move)
            # switch player
            eval_score = minimax(gs, depth - 1, alpha, beta, True)
            gs.undo()
            # get beta from the nodes
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            # pruning the nodes
            if beta <= alpha:
                break
        return min_eval


# This function checks if it's endgame
def is_endgame(board):
    # Count queens and major pieces
    num_queens = sum(1 for row in board for p in row if p[1] == "q")
    num_major = sum(1 for row in board for p in row if p[1] in ["q", "r"])
    return num_queens == 0 or num_major <= 3


# We call all our other evaluation functions in this function.
def evaluate_board(gs):
    score = material_score(gs.board)
    if gs.checkmate:
        if gs.white_to_move:
            return -MATE
        else:
            return MATE

    if gs.stalemate:
        return STALEMATE
    if is_endgame(gs.board):
        score += evaluate_endgame(gs.board, gs)
    else:
        score += evaluate_position(gs.board)
    # Calculate material + position
    score += evaluate_position(gs.board)
    return score


# prioritise search as per order
def order_moves(gs, moves):
    # Prioritize captures and checks first
    scored = []
    for m in moves:
        score = 0
        #
        if m.is_capture:
            score += 10
        if gs.square_under_att(m.end_r, m.end_c):
            score += 5
        scored.append((score, m))

    # sort the moves as by captures and attacks, more revision is required
    # such as counting the value of pieces defending
    # and the value of pieces attacking.
    scored.sort(reverse=True, key=lambda x: x[0])
    return [m for _, m in scored]


# a naive assessment of position
# add score as per material
def material_score(board):
    score = 0
    for row in board:
        for s in row:
            if s[0] == "w":
                score += piece_value[s[1]]

            # careful not to use else here since "--" also exists
            elif s[0] == "b":
                score -= piece_value[s[1]]
    return score


# evaluating the board by checking if pawn is in centre, piece is developed
# better methods incled using Bit boards and PSTs(Piece Square Tables)
def evaluate_position(board):
    # check for centre control
    score = 0
    for r in range(8):
        for c in range(8):
            piece = board[r][c]

            if piece[1] == "p":
                if piece[0] == "w":
                    # White pawns: r=7 is starting, r=0 is promotion
                    # Reward pawns that move forward
                    advancement = 7 - r  # incentive to go
                    score += advancement * 0.03

                else:  # Black pawn
                    # Black pawns: r=0 is starting, r=7 is promotion
                    advancement = r  # 0 at start, 7 near promotion
                    score -= advancement * 0.05

            # Center control bonus (e4, d4, e5, d5)
            if piece != "--":
                if 3 <= r <= 4 and 3 <= c <= 4:  # Center squares
                    center_bonus = 0.21
                    if piece[0] == "w":
                        score += center_bonus
                    else:
                        score -= center_bonus

    # check for piece development
    for r in range(8):
        for c in range(8):
            piece = board[r][c]

            if piece[1] in ["n", "b"]:
                if piece[0] == "w":
                    # White pawns: r=7 is starting, r=0 is promotion
                    # Reward pawns that move forward
                    advancement = 7 - r  # incentive to go
                    score += advancement * 0.06

                else:
                    advancement = r  # 0 at start, 7 near promotion
                    score -= advancement * 0.06
            # reward centre control
            if piece != "--":
                if 3 <= r <= 4 and 3 <= c <= 4:  # Center squares
                    center_bonus = 0.2
                    if piece[0] == "w":
                        score += center_bonus
                    else:
                        score -= center_bonus
    return score


def count_pieces(board):
    """Count total pieces"""
    count = 0
    for row in board:
        for square in row:
            if square != "--":
                count += 1
    return count


# This function evaluates the position when the dynamics completely change
# When there are less pieces and more space
# This function like all others is still naive
def evaluate_endgame(board, gs):
    score = 0
    white_king_pos = gs.w_king_loc
    black_king_pos = gs.b_king_loc

    # Reward central king activity in endgame
    if white_king_pos:
        wr, wc = white_king_pos
        score += (3.5 - abs(3.5 - wr)) + (3.5 - abs(3.5 - wc))
    if black_king_pos:
        br, bc = black_king_pos
        score -= (3.5 - abs(3.5 - br)) + (3.5 - abs(3.5 - bc))

    # Penalize isolated pawns or doubled pawns
    for c in range(8):
        col_pawns = [board[r][c] for r in range(8) if board[r][c][1] == "p"]
        if col_pawns.count("wp") > 1:
            score -= 0.2
        if col_pawns.count("bp") > 1:
            score += 0.2

    return score
