from chess_engine import GameState, Move
import pygame as p

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
        #size
        x = width // 2 - 100 + i * 60
        y = height // 2 - 30
        #image icon 
        img = images[color + piece]
        #creating icon
        rect = p.Rect(x, y, sq_size, sq_size)
        #inserting the piece into list
        piece_rects.append((rect, piece))

        p.draw.rect(screen, p.Color("gray"), rect)
        #inserting image
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
        images[piece] = p.transform.scale(
            p.image.load("chess-engine/pieces/bases/" + piece + ".png"), (sq_size, sq_size)  
        )


def draw_board(screen):
    colors = [p.Color("white"), p.Color("brown")]
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, (c * sq_size, r * sq_size, sq_size, sq_size))


def draw_pieces(screen, board):
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            piece = board[r][c]
            if piece != "--":
                screen.blit(images[piece], (c * sq_size, r * sq_size))


def draw_game_state(screen, gs):
    draw_board(screen)
    draw_pieces(screen, gs.board)


def main():
    set_of_move= 0
    move_made= False
    
    load_images()
    running = True

    selected_sq = ()
    player_clicks = []
    valid_moves= gs.get_valid_moves()

    while running:
        
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False

            elif event.type == p.MOUSEBUTTONDOWN:
                
                location = p.mouse.get_pos()
                col = location[0] // sq_size
                row = location[1] // sq_size

                if selected_sq == (row, col):
                    selected_sq = ()
                    player_clicks = []
                else:
                    selected_sq = (row, col)
                    player_clicks.append(selected_sq)

                if len(player_clicks) == 2:
                    move = Move(player_clicks[0], player_clicks[1], gs.board)
                    
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i] :
                            move_made= True
                            gs.make_move(move)
                            print(move.get_chess_notation(), end= "   ") 
                            set_of_move+=1

                            if move.is_pawn_promotion:
                                piece_choice = choose_promotion(screen, move.piece_moved[0])  # <-- new GUI func
                                gs.board[move.end_r][move.end_c] = move.piece_moved[0] + piece_choice
                            
                            if set_of_move == 2:
                                print()
                                set_of_move= 0
                    if not move_made:
                        player_clicks= [selected_sq]

                    selected_sq = ()
                    player_clicks = []

            # elif event.type == p.KEYDOWN:
            #     if event.key== p.K_z:
            #         gs.undo()
            #         move_made= True
        
        if move_made:
            valid_moves= gs.get_valid_moves()  
            move_made = False

        draw_game_state(screen, gs)
        clock.tick(max_fps)
        p.display.flip()

    p.quit()


if __name__ == "__main__":
    main()
