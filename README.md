
# Chess Engine

# Chess Engine with Python


## Introduction

Chess has been a significant part of my life for the past few years. As a programmer, I've always been curious about how chess engines work—from the AI decision-making to the UI mechanics that validate legal moves at every step. The intricate rules like en passant, castling, and checkmate detection fascinated me, and I wanted to understand them by building my own implementation.

This project is the result of that curiosity and dedication. It's a working chess engine with a graphical interface, move validation, and an AI opponent that uses minimax search with alpha-beta pruning. While it's not perfect, it represents my learning journey in both chess and algorithms.

I'm sharing this on GitHub to document my progress and to learn from the community. I hope to continue improving this engine as I deepen my understanding of chess programming.

---

## Features

- **Playable Chess Game**: Full chess implementation with all standard rules
- **AI Opponent**: Minimax algorithm with alpha-beta pruning (configurable depth)
- **Opening Book**: Uses polyglot opening book for early game moves
- **Move Validation**: Complete legal move generation including:
  - En passant captures
  - Castling (kingside and queenside)
  - Pawn promotion
  - Check and checkmate detection
- **Graphical Interface**: Pygame-based UI with:
  - Move highlighting
  - Smooth piece animations
  - Interactive piece selection
  - Visual feedback for legal moves

---

## Files Overview

### `chess_engine.py`
The core game logic implementing all chess rules.

**Key Components:**
- `GameState`: Manages the board state, move history, and game status
  - 8×8 board representation using 2-character strings (color + piece type)
  - King position tracking for efficient check detection
  - Castling rights management
  - En passant tracking
  
- `Move`: Represents individual moves with chess notation support
  - Converts between array indices and algebraic notation
  - Handles special moves (castling, en passant, promotion)
  
- `Castle_R`: Stores castling rights for both players

**Core Methods:**
- `make_move()` / `undo()`: Execute and reverse moves
- `get_valid_moves()`: Generates all legal moves (filters out moves that leave king in check)
- `all_possible_moves()`: Generates pseudo-legal moves for each piece type
- `check()` / `square_under_att()`: Detects checks and attacked squares
- Piece-specific move generators: `get_pawn_moves()`, `get_knight_moves()`, etc.

---

### `Engine_Move.py`
The AI engine that selects moves using minimax search.

**Key Features:**

**Piece Values:**
```python
piece_value = {"k": 0, "q": 10, "r": 5, "b": 3.2, "n": 3, "p": 1}
```

**Search Algorithm:**
- `find_best_move()`: Entry point for AI move selection
  - Checks opening book for early game
  - Uses minimax with alpha-beta pruning
  - Returns best move based on evaluation
  
- `minimax()`: Recursive search function
  - Alpha-beta pruning for efficient tree exploration
  - Configurable depth (default: 3)
  - Move ordering for better pruning efficiency

**Evaluation Functions:**
- `material_score()`: Calculates piece material advantage
- `evaluate_position()`: Positional evaluation including:
  - Pawn advancement bonuses
  - Center control (d4, e4, d5, e5)
  - Piece development (knights and bishops)
  
- `evaluate_endgame()`: Endgame-specific evaluation
  - King centralization
  - Pawn structure (penalizes doubled/isolated pawns)
  - Triggered when queens are traded or few major pieces remain

**Optimizations:**
- Transposition table (basic implementation)
- Move ordering: prioritizes captures and attacks
- Opening book integration

---

### `main.py`
The graphical interface and game loop using Pygame.

**UI Components:**
- Board rendering with alternating square colors
- Piece sprites loaded from image files
- Move animations with smooth interpolation
- Square highlighting for selected pieces and legal moves

**Key Functions:**
- `load_images()`: Loads piece sprites
- `draw_board()` / `draw_pieces()`: Renders the board and pieces
- `animate_move()`: Smooth piece movement animation
- `highlight()`: Visual feedback for selected squares and legal moves
- `choose_promotion()`: Interactive pawn promotion selection

**Game Loop:**
- Handles player input (mouse clicks)
- Manages turn-based play (human vs AI)
- Validates moves against legal move list
- Triggers AI move calculation on engine's turn
- Updates display at 60 FPS for smooth animations

**Configuration:**
- Board size: 480×480 pixels (60×60 per square)
- Player colors: Set `player_one` and `player_two` (True = human, False = AI)
- AI depth: Configurable in the engine move call

---

## How It Works

### Game Flow
1. Board is initialized in starting position
2. Player selects a piece (blue border shows selection)
3. Legal moves are highlighted with gray overlays
4. Player clicks destination square
5. Move is validated and animated
6. Board state updates (check/checkmate detection, castling rights, etc.)
7. AI calculates response using minimax
8. AI move is animated and executed
9. Loop continues until checkmate or stalemate

### AI Decision Making
1. Check opening book for known positions (first 20 moves)
2. If no book move, run minimax search to configured depth
3. For each legal move:
   - Make move on temporary board state
   - Recursively evaluate resulting positions
   - Alpha-beta pruning eliminates inferior branches
4. Select move with best evaluation score
5. Fallback to random valid move if search fails

### Move Validation
All moves go through legality checking:
1. Generate pseudo-legal moves (piece movement rules only)
2. For each move, temporarily execute it
3. Check if king is in check after the move
4. If king is safe, add to valid moves list
5. Detect checkmate (in check with no valid moves) or stalemate (no valid moves, not in check)

---

## Installation & Usage

### Requirements
```bash
pip install pygame
```

### Running the Game
```bash
python main.py
```

### Configuration
Edit `main.py` to configure:
- **Player types**: Set `player_one = True` (human) or `False` (AI)
- **AI difficulty**: Adjust `depth` parameter in AI move call (higher = stronger but slower)
- **Piece images path**: Update path in `load_images()` to match your directory structure

---

## Known Limitations & Future Improvements

### Current Limitations
- Basic evaluation function (doesn't consider complex positional factors)
- Simple transposition table implementation
- No iterative deepening (fixed depth search)
- Move ordering could be more sophisticated
- No endgame tablebases

### Planned Improvements
- **Better Evaluation**: 
  - Piece-square tables for positional evaluation
  - King safety metrics
  - Mobility and threat evaluation
  - Pawn structure analysis
  
- **Search Enhancements**:
  - Iterative deepening with time management
  - Quiescence search for tactical positions
  - Better move ordering (MVV-LVA, killer moves, history heuristic)
  - Proper transposition table with Zobrist hashing
  
- **UI Improvements**:
  - Move history display
  - Game save/load functionality
  - Position analysis features
  - Multiple board themes

- **Code Quality**:
  - Better documentation
  - Unit tests for move generation
  - Performance profiling and optimization

---

## Technical Notes

### Board Representation
- Array-based: `board[row][col]` where (0,0) is a8, (7,7) is h1
- Pieces stored as 2-char strings: first char = color ('w'/'b'), second char = type ('p','n','b','r','q','k')
- Empty squares: `"--"`

### Coordinate System
- Rows: 0-7 (rank 8 to rank 1)
- Columns: 0-7 (files a to h)
- Conversion handled by `Move` class dictionaries

### Special Moves Implementation
- **En Passant**: Tracked via `enpassant_possible` tuple storing target square
- **Castling**: Rights stored in `Castle_R` object, validated by checking squares and attack status
- **Promotion**: Detected when pawn reaches opposite back rank, UI prompts for piece selection

---

## Learning Resources

This project was inspired by and learned from various chess programming resources:
- Sebastian Lague's chess challenge
- Chess programming wikis and forums
- Various open-source chess engines

---

## Contributing

This is a learning project, and I welcome feedback, suggestions, and contributions! Feel free to:
- Open issues for bugs or feature requests
- Submit pull requests with improvements
- Share educational resources about chess programming
- Suggest better approaches to evaluation or search

---

## License

MIT License

---

## Acknowledgments

- Sebastian Lague for inspiring efficient storage and search techniques
- The chess programming community for extensive documentation and resources
- Polyglot opening book format and contributors
