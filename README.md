# Chess Engine with Pythin

A fully functional chess game built with Python and Pygame, featuring a complete rule implementation including special moves like en passant and pawn promotion.

## Features

- **Full Chess Rules Implementation**
  - All piece movements (Pawns, Rooks, Knights, Bishops, Queens, Kings)
  - Pawn promotion with GUI selection
  - En passant captures
  - Check and checkmate detection
  - Stalemate detection
  - Legal move validation

- **Interactive GUI**
  - Click-to-move interface
  - Visual board with alternating colors
  - Piece sprites for all chess pieces
  - Promotion piece selection dialog

## Prerequisites

- Python 3.7 or higher
- Pygame library

## Installation

1. Clone or download this repository

2. Install Pygame:
```bash
pip install pygame
```

3. Ensure your directory structure looks like this:
```
chess-engine/
├── main.py
├── chess_engine.py
└── pieces/
    └── bases/
        ├── wp.png
        ├── wr.png
        ├── wn.png
        ├── wb.png
        ├── wq.png
        ├── wk.png
        ├── bp.png
        ├── br.png
        ├── bn.png
        ├── bb.png
        ├── bq.png
        └── bk.png
```

## Usage

Run the game with:
```bash
python main.py
```

### How to Play

1. **Making Moves**: Click on a piece to select it, then click on a valid destination square
2. **Deselecting**: Click on the same piece again to deselect it
3. **Pawn Promotion**: When a pawn reaches the opposite end, a dialog will appear allowing you to choose the promotion piece (Queen, Rook, Bishop, or Knight)
4. **Game End**: The game detects checkmate and stalemate automatically

### Controls

- **Mouse Click**: Select and move pieces
- **Close Window**: Exit the game

## Game Rules Implemented

### Standard Moves
- **Pawns**: Move forward one square (or two from starting position), capture diagonally
- **Rooks**: Move horizontally or vertically any number of squares
- **Knights**: Move in an L-shape (2+1 squares)
- **Bishops**: Move diagonally any number of squares
- **Queens**: Combine rook and bishop movements
- **Kings**: Move one square in any direction

### Special Moves
- **En Passant**: Capture an enemy pawn that just moved two squares forward, as if it had only moved one
- **Pawn Promotion**: When a pawn reaches the opposite end of the board, it must be promoted to a Queen, Rook, Bishop, or Knight

### Game End Conditions
- **Checkmate**: When a king is in check and has no legal moves to escape
- **Stalemate**: When a player has no legal moves but is not in check (draw)

## Code Structure

### `main.py`
Contains the game loop and GUI rendering:
- `load_images()`: Loads all chess piece sprites
- `draw_board()`: Renders the chess board
- `draw_pieces()`: Renders all pieces on the board
- `choose_promotion()`: Displays promotion selection dialog
- `main()`: Main game loop handling user input and game state

### `chess_engine.py`
Contains the game logic:
- **`GameState` class**: Manages the board state, move validation, and game rules
  - `make_move()`: Executes a move and updates the board
  - `undo()`: Reverts the last move
  - `get_valid_moves()`: Returns all legal moves for the current player
  - `check()`: Determines if the current player is in check
  - `get_*_moves()`: Individual move generation for each piece type

- **`Move` class**: Represents a chess move
  - Handles move notation (algebraic notation)
  - Tracks special move types (en passant, promotion)

## Chess Notation

The game prints moves in algebraic notation:
- Piece moves: `Nf3`, `Bb5`, `Qd4`
- Captures: `Nxe5`, `Bxc6`, `exd5`
- Pawn moves: `e4`, `d5`
- Pawn captures: `exd5`, `cxd4`

## Customization

### Board Colors
Edit the `draw_board()` function in `main.py`:
```python
colors = [p.Color("white"), p.Color("brown")]
```

### Board Size
Modify at the top of `main.py`:
```python
width = height = 480  # Change to desired size
```

### Frame Rate
Adjust the FPS:
```python
max_fps = 15  # Increase for smoother animation
```

## Known Limitations

- No castling implementation
- No move timer
- No AI opponent (two-player only)
- No move history display
- No game save/load functionality

## Future Enhancements

- [ ] Add castling (kingside and queenside)
- [ ] Implement undo functionality with keyboard shortcut
- [ ] Add move highlighting for selected pieces
- [ ] Display captured pieces
- [ ] Add game timer/clock
- [ ] Implement basic AI opponent
- [ ] Add move sound effects
- [ ] Save/load game functionality
- [ ] Move history panel

## Troubleshooting

**Images not loading**: Ensure the piece images are in the correct directory (`chess-engine/pieces/bases/`) with the correct naming convention (e.g., `wp.png` for white pawn)

**Pygame not found**: Install pygame using `pip install pygame`

**Game crashes on promotion**: Ensure all piece images (q, r, b, n) exist for both colors

## Credits

Built with Python and Pygame. Chess piece images should be placed in the appropriate directory structure.

## License

Free to use and modify for personal and educational purposes.
