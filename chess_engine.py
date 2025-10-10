class GameState:
    def __init__(self):
        self.board = [
            ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]
        ]

        self.white_to_move = True
        self.move_log = []
        
        self.is_p_promotion = False 

        #keeping track of black and white kings
        self.b_king_loc= (0,4)
        self.w_king_loc= (7,4)        

        #checkmate and stale mate
        self.checkmate = False
        self.stalemate = False
        self.enpassant_possible = ()

    
    def make_move(self, move):

        if move.is_enpassant:
            self.board[move.start_r][move.end_c]= "--"

        # Update board
        self.board[move.start_r][move.start_c] = "--"
        self.board[move.end_r][move.end_c] = move.piece_moved

        # Log move
        self.move_log.append(move)

        # Switch turn
        self.white_to_move = not self.white_to_move

        if move.piece_moved == "bk":
            self.b_king_loc= (move.end_r, move.end_c)
        elif move.piece_moved == "wk":
            self.w_king_loc= (move.end_r, move.end_c)

        if move.piece_moved == "p" and abs(move.start_r - move.end_r) == 2:
            self.enpassant_possible = ((move.start_r + move.end_r)//2, move.start_c)
        else:
            self.enpassant_possible = ()

        # if move.is_pawn_promotion:
        #     self.board[move.end_r][move.end_c]= move.piece_moved[0] + "q"

    def undo(self):
        
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_r][move.start_c] = move.piece_moved
            self.board[move.end_r][move.end_c] = move.piece_captured
            self.white_to_move = not self.white_to_move

            if move.piece_moved == "bk":
                self.b_king_loc = (move.start_r, move.start_c)
                
            elif move.piece_moved == "wk":
                self.w_king_loc = (move.start_r, move.start_c)
                
            if move.is_enpassant:
                if move.piece_moved[0] == "w":
                    self.board[move.end_r + 1][move.end_c] = "bp"  # restore black pawn
                else:
                    self.board[move.end_r - 1][move.end_c] = "wp" #restor white pawn

            if len(self.move_log) > 0:
                last_move = self.move_log[-1]
                if last_move.piece_moved[0] == "w" and last_move.start_r - last_move.end_r == 2:
                    self.enpassant_possible = ((last_move.start_r + last_move.end_r)//2, last_move.start_c)
                elif last_move.piece_moved[0] == "b" and last_move.end_r - last_move.start_r == 2:
                    self.enpassant_possible = ((last_move.start_r + last_move.end_r)//2, last_move.start_c)
                else:
                    self.enpassant_possible = ()
            else:
                self.enpassant_possible = ()


    def get_valid_moves(self):

        moves=  self.all_possible_moves()
        valid_moves = []

        #generate all possivle moves and only add the legal ones
        #then see if they attack king then dont add them
        for i in range(len(moves)):
            self.make_move(moves[i])
            self.white_to_move= not self.white_to_move
            if not self.check():
                valid_moves.append(moves[i])
            self.undo()

        #If no possible moves
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

        self.white_to_move = not self.white_to_move
        for move in self.all_possible_moves():
            if move.end_r == r and move.end_c == c:
                self.white_to_move = not self.white_to_move
                return True
        self.white_to_move = not self.white_to_move
        return False


    def check(self):

        if self.white_to_move:
            return self.square_under_att(self.w_king_loc[0],self.w_king_loc[1])
        else:
            return self.square_under_att(self.b_king_loc[0],self.b_king_loc[1])

    def all_possible_moves(self):
        
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn= self.board[r][c][0]
                if (turn== "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece= self.board[r][c][1]

                    if piece== 'p':  # Pawn
                        self.get_pawn_moves(r, c, moves)
                    elif piece == 'r':  # Rook
                         self.get_rook_moves(r, c, moves)
                    elif piece == 'n':  # Knight
                         self.get_knight_moves(r, c, moves)
                    elif piece == 'b':  # Bishop
                         self.get_bishop_moves(r, c, moves)
                    elif piece == 'q':  # Queen
                         self.get_queen_moves(r, c, moves)
                    elif piece == 'k':  # King
                         self.get_king_moves(r, c, moves)
        return moves


    def get_pawn_moves(self, r, c, moves):

        if self.white_to_move:
            if r > 0 and self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board, double_move=True))

            for d_col in [-1, 1]:
                end_c = c + d_col
                if 0 <= end_c < 8 and r > 0:
                    if self.board[r-1][end_c][0] == "b":
                        moves.append(Move((r, c), (r-1, end_c), self.board))
                
                    if (r - 1, end_c) == self.enpassant_possible:
                        moves.append(Move((r, c), (r - 1, end_c), self.board, is_enpassant=True))


        #black to move
        else:
            if r < 7 and self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board, double_move=True))
            for d_col in [-1, 1]:
                end_c = c + d_col
                if 0 <= end_c < 8 and r < 7:
                    if self.board[r+1][end_c][0] == "w":
                        moves.append(Move((r, c), (r+1, end_c), self.board))
                    #en passant    
                    if (r + 1, end_c) == self.enpassant_possible:
                        moves.append(Move((r, c), (r + 1, end_c), self.board, is_enpassant=True))



    def get_rook_moves(self, r, c, moves):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            dr, dc = d
            end_r, end_c = r + dr, c + dc
            while 0 <= end_r < 8 and 0 <= end_c < 8:
                end_piece = self.board[end_r][end_c]
                if end_piece == "--":
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                elif end_piece[0] == enemy_color:  # capture
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                    break
                else: 
                    break
                end_r += dr
                end_c += dc

    def get_bishop_moves(self, r, c, moves):
        directions = [(-1, -1), (1, 1), (1, -1), (-1, 1), ]  # diagonls
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            dr, dc = d
            end_r, end_c = r + dr, c + dc
            while 0 <= end_r < 8 and 0 <= end_c < 8:
                end_piece = self.board[end_r][end_c]
                if end_piece == "--":
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                elif end_piece[0] == enemy_color:  # capture
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                    break
                else: 
                    break
                end_r += dr
                end_c += dc

    def get_queen_moves(self, r, c, moves):
        directions = [(-1, -1), (1, 1), (1, -1), (-1, 1),(-1, 0), (1, 0), (0, -1), (0, 1) ]  # diagonls
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            dr, dc = d
            end_r, end_c = r + dr, c + dc
            while 0 <= end_r < 8 and 0 <= end_c < 8:
                end_piece = self.board[end_r][end_c]
                if end_piece == "--":
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                elif end_piece[0] == enemy_color:  # capture
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                    break
                else: 
                    break
                end_r += dr
                end_c += dc    

    def get_knight_moves(self, r, c, moves):
        directions = [(-1, -2), (2, 1), (2, -1), (-2, 1),(-1, 2), (1, 2), (-2, -1), (1, -2) ]  #L shapes
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            dr, dc = d
            end_r, end_c = r + dr, c + dc
            if 0 <= end_r < 8 and 0 <= end_c < 8:
                end_piece = self.board[end_r][end_c]
                if end_piece == "--":
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                elif end_piece[0] == enemy_color:  # capture
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                                    
    def get_king_moves(self, r, c, moves):
        directions = [(-1, -1), (1, 1), (1, -1), (-1, 1),(-1, 0), (1, 0), (0, -1), (0, 1) ]  # diagonls
        enemy_color = "b" if self.white_to_move else "w"

        for d in directions:
            dr, dc = d
            end_r, end_c = r + dr, c + dc
            if 0 <= end_r < 8 and 0 <= end_c < 8:
                end_piece = self.board[end_r][end_c]
                if end_piece == "--":
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                    
                elif end_piece[0] == enemy_color:  # capture
                    moves.append(Move((r, c), (end_r, end_c), self.board))
                    
        

class Move:
    # Mappings for board notation
    cols_to_files = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
    files_to_cols = {v: k for k, v in cols_to_files.items()}

    rows_to_ranks = {0: "8", 1: "7", 2: "6", 3: "5", 4: "4", 5: "3", 6: "2", 7: "1"}
    ranks_to_rows = {v: k for k, v in rows_to_ranks.items()}

    #For annotation
    piece_symbols = {
        "p": "",  
        "r": "R",
        "n": "N",
        "b": "B",
        "q": "Q",
        "k": "K",
    }

    def __init__(self, start_sq, end_sq, board, is_enpassant= False, double_move = False):

        #Start and end squares
        self.start_r, self.start_c = start_sq
        self.end_r, self.end_c = end_sq

        #Piece selected
        self.piece_moved = board[self.start_r][self.start_c]

        #piece captured
        self.piece_captured = board[self.end_r][self.end_c]

        self.is_enpassant = is_enpassant


        # #double movee
        self.double_move = double_move


        #pawn promotion
        self.is_pawn_promotion= False
        if (self.piece_moved == "wp" and self.end_r == 0) or (self.piece_moved == "bp" and self.end_r == 7):
             self.is_pawn_promotion = True

    def __eq__(self, other):
            
            if isinstance(other, Move):
                return (self.start_r == other.start_r and self.start_c == other.start_c and
                    self.end_r == other.end_r and self.end_c == other.end_c and
                    self.piece_moved == other.piece_moved and
                    self.piece_captured == other.piece_captured)
            
            return False


    def get_chess_notation(self):

        move_str = ""

        # Determine piece letter 
        piece= self.piece_symbols[self.piece_moved[1]]

        # If pawn move and capture
        if self.piece_moved[1] == "p":
            if self.piece_captured != "--":
                move_str += self.cols_to_files[self.start_c] + "x" + self.get_rank_file(self.end_r, self.end_c)
            else:
                move_str += self.get_rank_file(self.end_r, self.end_c)
        else:
            if self.piece_captured != "--":
                move_str += piece + "x" + self.get_rank_file(self.end_r, self.end_c)
            else:
                move_str += piece + self.get_rank_file(self.end_r, self.end_c)

        return move_str

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]


