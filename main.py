from src.chess_engine import GameState, Move
import src.Engine_Move as E
import pygame as p
import os

p.init()
width = height = 480
DIMENSIONS = 8
sq_size = height // DIMENSIONS
max_fps = 15
screen = p.display.set_mode((width, height))
images = {}
clock = p.time.Clock()
gs = GameState()


def choose_promotion(screen, color):

    # Piece Icon
    choices = ["q", "r", "b", "n"]
    piece_rects = []
    for i, piece in enumerate(choices):
        # size
        x = width // 2 - 100 + i * 60
        y = height // 2 - 30
        # image icon
        img = images[color + piece]
        # creating icon
        rect = p.Rect(x, y, sq_size, sq_size)
        # inserting the piece into list
        piece_rects.append((rect, piece))

        p.draw.rect(screen, p.Color("gray"), rect)
        # inserting image
        screen.blit(img, (x, y))

    p.display.flip()

    while True:
        for event in p.event.get():
            if event.type == p.MOUSEBUTTONDOWN:
                pos = p.mouse.get_pos()
                for rect, piece in piece_rects:
                    if rect.collidepoint(pos):
                        # Return "q", "r", "b", or "n"
                        return piece


def load_images():
    pieces = ["br", "bn", "bb", "bq", "bk", "bp", "wr", "wn", "wb", "wq", "wk", "wp"]
    for piece in pieces:
        path = os.path.join(r"C:/Users/DELL/c/chess-engine/pieces/bases/" + piece)
        images[piece] = p.transform.scale(
            p.image.load(path + ".png"), (sq_size, sq_size)
        )


def draw_board(screen):
    colors = [p.Color("white"), p.Color("brown")]
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, (c * sq_size, r * sq_size, sq_size, sq_size))


def animate_move(screen, board, move, clock):

    d_r = move.end_r - move.start_r
    d_c = move.end_c - move.start_c
    # keep high fps for smoother animations
    frames_per_square = 3
    # no. of frames
    frame_count = (abs(d_r) + abs(d_c)) * frames_per_square

    for frame in range(frame_count + 1):
        r = move.start_r + d_r * frame / frame_count
        c = move.start_c + d_c * frame / frame_count

        draw_board(screen)
        draw_pieces(screen, board)

        # Erase piece from ending square
        color = (
            p.Color("white") if (move.end_r + move.end_c) % 2 == 0 else p.Color("brown")
        )
        end_square = p.Rect(
            move.end_c * sq_size, move.end_r * sq_size, sq_size, sq_size
        )
        p.draw.rect(screen, color, end_square)

        # Draw captured piece if any
        if move.piece_captured != "--":
            screen.blit(
                images[move.piece_captured],
                (move.end_c * sq_size, move.end_r * sq_size),
            )

        # Draw moving piece
        screen.blit(images[move.piece_moved], (c * sq_size, r * sq_size))
        clock.tick(60)


def draw_pieces(screen, board):
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            piece = board[r][c]
            if piece != "--":
                screen.blit(images[piece], (c * sq_size, r * sq_size))


def draw_game_state(screen, gs, valid_moves, sq_selected):
    draw_board(screen)
    draw_pieces(screen, gs.board)
    highlight(screen, gs, valid_moves, sq_selected)


def highlight(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        # Check a piece is of the same colour as the colour to move
        if gs.board[r][c][0] == ("w" if gs.white_to_move else "b"):
            # Draw border for selected square
            border_color = p.Color("blue")
            border_rect = p.Rect(c * sq_size, r * sq_size, sq_size, sq_size)
            p.draw.rect(screen, border_color, border_rect, 3)  # 3 is border width

            # Highlight valid moves with semi-transparent gray circles
            for move in valid_moves:
                if move.start_r == r and move.start_c == c:
                    surface = p.Surface((sq_size, sq_size))
                    surface.set_alpha(100)
                    surface.fill(p.Color("gray"))
                    screen.blit(surface, (sq_size * move.end_c, sq_size * move.end_r))


def main():
    move_made = False

    load_images()
    running = True

    selected_sq = ()
    player_clicks = []
    valid_moves = gs.get_valid_moves()

    # if human is white then true else false
    player_one = True
    player_two = False

    while running:
        is_human_turn = (gs.white_to_move and player_one) or (
            not gs.white_to_move and player_two
        )

        for event in p.event.get():
            if event.type == p.QUIT:
                running = False

            elif event.type == p.MOUSEBUTTONDOWN:
                if is_human_turn:
                    # this is really smart dividing the coordinates into regions, found this online
                    location = p.mouse.get_pos()
                    col = location[0] // sq_size
                    row = location[1] // sq_size

                    # if clicked on same square again ensure no move happens
                    if selected_sq == (row, col):
                        selected_sq = ()
                        player_clicks = []

                    # assign new square
                    else:
                        selected_sq = (row, col)
                        player_clicks.append(selected_sq)

                    # if 2 clicks then make move
                    if len(player_clicks) == 2:
                        move = Move(player_clicks[0], player_clicks[1], gs.board)

                        # search if the move is in valid moves
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                # when you find a matching valid move:
                                move_made = True
                                selected_move = valid_moves[i]
                                animate_move(screen, gs.board, selected_move, clock)
                                gs.make_move(selected_move)
                                print(selected_move.get_chess_notation(), end="   ")
                                ...
                                if selected_move.is_pawn_promotion:
                                    piece_choice = choose_promotion(
                                        screen, selected_move.piece_moved[0]
                                    )
                                    gs.board[selected_move.end_r][
                                        selected_move.end_c
                                    ] = (selected_move.piece_moved[0] + piece_choice)

                                # if 2 moves have happened then print a new line
                                if len(gs.move_log) % 2 == 0:
                                    print()

                                break

                        # If move has not been made, then add prev selection to the list
                        if not move_made:
                            player_clicks = [selected_sq]

                        selected_sq = ()
                        player_clicks = []

            # elif event.type == p.KEYDOWN:
            #     if event.key== p.K_z:
            #         gs.undo()
            #         move_made= True

        # Engine move finder
        if not is_human_turn:
            depth = 3
            ai_move = E.find_best_move(gs, valid_moves, depth)
            if ai_move is None:
                ai_move = E.find_random(valid_moves)

            if ai_move:
                # animate ai move
                animate_move(screen, gs.board, ai_move, clock)
                gs.make_move(ai_move)
                # print the notation for ai moves
                print(ai_move.get_chess_notation(), end="   ")
                set_of_move += 1
                # calling pawn promotion
                if ai_move.is_pawn_promotion:
                    gs.board[ai_move.end_r][ai_move.end_c] = (
                        ai_move.piece_moved[0] + "q"
                    )
                if len(gs.move_log) % 2 == 0:
                    print()
                    set_of_move = 0
                move_made = True

        # if move was made then call new valid moves and set boolean to false
        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        # selected_sq is named as sq_selected in other functions, do not be confused
        clock.tick(60)
        # ensure this is in while loop, if screen doesnt appear
        draw_game_state(screen, gs, valid_moves, selected_sq)
        p.display.flip()

    p.quit()


if __name__ == "__main__":
    main()
