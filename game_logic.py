# game_logic.py
# This file contains the core logic for the checkers game, including AI.

class CheckersGameLogic:
    # Mapping for AI search depth based on difficulty
    AI_SEARCH_DEPTH_MAP = {
        "Łatwy": 1,
        "Średni": 3,
        "Trudny": 5
    }

    def __init__(self, ai_difficulty="Średni", player_color=1):
        self.ai_difficulty = ai_difficulty
        self.ai_search_depth = self.AI_SEARCH_DEPTH_MAP.get(ai_difficulty, 3)
        self.player_color = player_color  # 1 for white, 2 for black (player's chosen color)
        self.ai_color = 2 if self.player_color == 1 else 1  # AI is the opposite color

        self.board = self._initialize_board()
        self.current_player = 1  # Always starts with white (player 1)
        self.message = "Ruch białych."  # Message displayed to the user
        self.selected_piece_pos = None  # Position of the currently selected piece (row, col)
        self.forced_capture_piece = None  # Position of the piece that must perform a subsequent capture

    def _initialize_board(self):
        """Initializes the game board with pieces in their starting positions."""
        # 0: empty square
        # 1: white pawn, 2: black pawn
        # 3: white king, 4: black king
        board = [[0 for _ in range(8)] for _ in range(8)]
        for r in range(8):
            for c in range(8):
                if (r + c) % 2 == 1:  # Only dark squares
                    if r < 3:
                        board[r][c] = 2  # Black pawns
                    elif r > 4:
                        board[r][c] = 1  # White pawns
        return board

    def get_board_state(self):
        """Returns the current state of the game board."""
        return self.board

    def get_current_player(self):
        """Returns the current player (1 for white, 2 for black)."""
        return self.current_player

    def get_player_color(self):
        """Returns the human player's chosen color."""
        return self.player_color

    def get_ai_color(self):
        """Returns the AI's color."""
        return self.ai_color

    def get_message(self):
        """Returns the current status message of the game."""
        return self.message

    def reset_game(self, ai_difficulty="Średni", player_color=1):
        """Generates the game logic for the given difficulty and player color."""
        self.ai_difficulty = ai_difficulty
        self.ai_search_depth = self.AI_SEARCH_DEPTH_MAP.get(ai_difficulty, 3)
        self.player_color = player_color
        self.ai_color = 2 if self.player_color == 1 else 1

        self.board = self._initialize_board()
        self.current_player = 1  # Game always starts with white (player 1)
        self.message = "Ruch białych."
        self.selected_piece_pos = None
        self.forced_capture_piece = None

    def is_player_piece(self, row, col, player_type=None, board=None):
        """
        Checks if the piece at (row, col) belongs to the specified player_type.
        If player_type is None, uses self.current_player.
        If board is None, uses self.board.
        """
        if board is None:
            board = self.board
        if player_type is None:
            player_type = self.current_player

        piece = board[row][col]
        if player_type == 1:  # White player
            return piece == 1 or piece == 3  # White pawn or white king
        else:  # Black player
            return piece == 2 or piece == 4  # Black pawn or black king

    def is_opponent_piece(self, row, col, player_type=None, board=None):
        """
        Checks if the piece at (row, col) belongs to the opponent of player_type.
        If player_type is None, uses self.current_player.
        If board is None, uses self.board.
        """
        if board is None:
            board = self.board
        if player_type is None:
            player_type = self.current_player

        piece = board[row][col]
        if player_type == 1:  # White player (opponent is black)
            return piece == 2 or piece == 4
        else:  # Black player (opponent is white)
            return piece == 1 or piece == 3

    def get_possible_moves(self, r, c, board=None, player_type=None):
        """
        Returns a list of (row, col) tuples for possible destination squares for the piece at (r, c).
        Prioritizes captures over normal moves.
        Returns (moves_list, is_capture_move_found_flag).
        """
        if board is None:
            board = self.board
        if player_type is None:
            player_type = self.current_player

        moves = []
        captures = []
        piece = board[r][c]

        # Check for captures first (always prioritized in checkers)
        current_captures = self._get_captures_for_piece(r, c, board, player_type)
        if current_captures:
            captures.extend(current_captures)
            return captures, True  # Return captures and a flag indicating captures are found

        # If no captures, check for normal moves
        # Pawns (white and black)
        if piece == 1 or piece == 2:
            # Direction: -1 for white (upwards), 1 for black (downwards)
            direction = -1 if piece == 1 else 1
            # Check forward diagonal moves
            for dc in [-1, 1]:
                nr, nc = r + direction, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8 and board[nr][nc] == 0:
                    moves.append((nr, nc))
        # Kings (white and black)
        elif piece == 3 or piece == 4:
            # Kings can move diagonally in 4 directions
            for dr in [-1, 1]:
                for dc in [-1, 1]:
                    for i in range(1, 8):  # Can move multiple squares
                        nr, nc = r + dr * i, c + dc * i
                        if 0 <= nr < 8 and 0 <= nc < 8:
                            if board[nr][nc] == 0:
                                moves.append((nr, nc))
                            else:
                                # Blocked by another piece, cannot pass further in this direction
                                break
                        else:
                            break
        return moves, False  # Return normal moves and a flag indicating no captures

    def _get_captures_for_piece(self, r, c, board=None, player_type=None):
        """
        Returns a list of (row, col) tuples for possible capture destinations for the piece at (r, c).
        Can operate on a given board and for a given player_type for Minimax.
        """
        if board is None:
            board = self.board
        if player_type is None:
            player_type = self.current_player

        captures = []
        piece = board[r][c]
        if piece == 0:
            return []

        # Possible capture directions for pawns and kings
        directions = []
        if piece == 1 or piece == 2:  # Pawns
            direction_forward = -1 if piece == 1 else 1  # White moves up, black moves down
            directions.append((direction_forward, -1))
            directions.append((direction_forward, 1))
        elif piece == 3 or piece == 4:  # Kings
            directions.extend([(dr, dc) for dr in [-1, 1] for dc in [-1, 1]])  # All 4 diagonal directions

        for dr, dc in directions:
            if piece in [1, 2]:  # Pawns: capture by jumping 2 squares
                nr, nc = r + dr, c + dc  # Square where a potential opponent piece is
                n2r, n2c = r + 2 * dr, c + 2 * dc  # Square behind the opponent (destination)

                if (0 <= n2r < 8 and 0 <= n2c < 8 and
                        self.is_opponent_piece(nr, nc, player_type, board) and board[n2r][n2c] == 0):
                    captures.append((n2r, n2c))
            elif piece in [3, 4]:  # Kings: capture at a distance
                opponent_found_on_path = None  # Stores the coordinates of the captured opponent piece

                for i in range(1, 8):  # Iterate through squares in this diagonal direction
                    nr, nc = r + dr * i, c + dc * i
                    if not (0 <= nr < 8 and 0 <= nc < 8):
                        break  # Out of bounds

                    current_square_piece = board[nr][nc]

                    if current_square_piece == 0:
                        if opponent_found_on_path:  # If an opponent was already found, this empty square is a valid landing spot
                            captures.append((nr, nc))
                        # If no opponent found yet, just continue searching along this path
                        continue
                    elif self.is_player_piece(nr, nc, player_type, board):  # Own piece blocks the path
                        break
                    elif self.is_opponent_piece(nr, nc, player_type, board):  # Opponent piece found
                        if opponent_found_on_path:  # Already captured an opponent, cannot capture another in the same jump
                            break
                        else:  # This is the first opponent piece found on this line
                            opponent_found_on_path = (nr, nc)
                            # Continue searching for empty landing spots *after* this captured piece
                            continue
                    else:  # Should not happen (e.g., piece type 5 or something unexpected)
                        break
        return captures

    def get_all_possible_moves_for_player(self, board=None, player_type=None, forced_capture_piece=None):
        """
        Returns a dictionary { (start_r, start_c): [(end_r, end_c), ...] }
        for all possible moves and captures for the current player.
        If any captures are available, only captures are returned.
        Returns (moves_dict, has_forced_captures_flag).
        Can operate on a given board and for a given player_type for Minimax.
        """
        if board is None:
            board = self.board
        if player_type is None:
            player_type = self.current_player
        if forced_capture_piece is None:
            forced_capture_piece = self.forced_capture_piece  # Use game's actual forced capture piece by default

        all_player_moves = {}
        all_player_captures = {}

        for r in range(8):
            for c in range(8):
                if self.is_player_piece(r, c, player_type, board):
                    # If there's a forced capture piece, and this piece is NOT it, skip it.
                    # This ensures that only the piece required to make a subsequent capture is considered.
                    if forced_capture_piece and (r, c) != forced_capture_piece:
                        continue

                    moves_for_piece, has_captures = self.get_possible_moves(r, c, board, player_type)
                    if moves_for_piece:
                        if has_captures:
                            all_player_captures[(r, c)] = moves_for_piece
                        else:
                            all_player_moves[(r, c)] = moves_for_piece

        # print(f"DEBUG: get_all_possible_moves_for_player called for player_type={player_type}, forced_capture_piece={forced_capture_piece}")
        if all_player_captures:
            # print(f"DEBUG: Player {player_type} has captures: {all_player_captures}")
            return all_player_captures, True
        else:
            # print(f"DEBUG: Player {player_type} has no captures. Checking normal moves: {all_player_moves}")
            # Determine if there are *any* moves at all for the player
            overall_has_moves = bool(all_player_moves)  # True if all_player_moves is not empty, False otherwise
            return all_player_moves, overall_has_moves

    def is_move_valid(self, start_pos, end_pos):
        """
        Validates if a move from start_pos to end_pos is legal according to checkers rules.
        Updates self.message with reasons for invalid moves.
        """
        start_r, start_c = start_pos
        end_r, end_c = end_pos

        # print(f"\n--- DEBUG: is_move_valid called for move: {start_pos} -> {end_pos} ---")
        # print(f"DEBUG: current_player: {self.current_player}, forced_capture_piece: {self.forced_capture_piece}")
        # print("DEBUG: Current Board State:")
        # for r_dbg in range(8):
        #     print(f"DEBUG: {self.board[r_dbg]}")
        # print("--------------------------------------------------")

        if not (0 <= start_r < 8 and 0 <= start_c < 8 and
                0 <= end_r < 8 and 0 <= end_c < 8):
            self.message = "Ruch poza planszą."
            # print(f"DEBUG: {self.message}")
            return False

        piece = self.board[start_r][start_c]
        if piece == 0 or not self.is_player_piece(start_r, start_c):
            self.message = "Na wybranym polu nie ma twojego pionka."
            # print(f"DEBUG: {self.message}")
            return False

        if self.board[end_r][end_c] != 0:
            self.message = "Pole docelowe jest zajęte."
            # print(f"DEBUG: {self.message}")
            return False

        # Check if the selected piece must continue capturing
        if self.forced_capture_piece and self.forced_capture_piece != start_pos:
            self.message = "Musisz kontynuować bicie tym samym pionkiem!"
            # print(f"DEBUG: {self.message}")
            return False

        # Get all valid moves for the current player based on the current board state and forced capture rule
        all_valid_moves, has_forced_captures = self.get_all_possible_moves_for_player(
            board=self.board,
            player_type=self.current_player,
            forced_capture_piece=self.forced_capture_piece  # Pass the current forced_capture_piece
        )
        # print(f"DEBUG: all_valid_moves for validation: {all_valid_moves}, has_forced_captures: {has_forced_captures}")

        # Check if the intended move (start_pos -> end_pos) is among the valid moves.
        # This covers both normal moves and all allowed captures (including multiple jumps).
        if start_pos not in all_valid_moves or end_pos not in all_valid_moves.get(start_pos, []):
            if has_forced_captures:
                # This means captures are available, but the chosen move is not a valid capture or is not by the forced piece.
                if self.forced_capture_piece:  # If a specific piece MUST capture
                    if start_pos != self.forced_capture_piece:
                        self.message = "Musisz kontynuować bicie tym samym pionkiem!"
                    else:
                        self.message = "Ten ruch nie jest poprawnym biciem! Wybrany pionek musi kontynuować bicie."
                else:  # Captures are available, but not from the selected piece or not a valid capture move
                    self.message = "Ten ruch nie jest poprawnym biciem! Musisz wykonać bicie."
            else:
                # No captures are available, but the chosen move is not a valid normal move.
                self.message = "Niepoprawny ruch. (Pamiętaj o biciach, jeśli są dostępne!)"
            # print(f"DEBUG: {self.message}")
            return False

        # print("DEBUG: Move is valid.")
        return True

    def make_move(self, start_pos, end_pos, board=None, player_type=None):
        """
        Executes a move on the board (or a copy of board for minimax).
        Handles capturing, promotion, and updates current player/forced capture state.
        Returns (new_board, new_player_type, new_forced_capture_piece, is_capture_made).
        If board/player_type are None, operates on self.board/self.current_player.
        """
        # Create a deep copy of the board to avoid modifying the original during simulation
        if board is None:
            temp_board = [row[:] for row in self.board]
            is_main_game_move = True
        else:
            temp_board = [row[:] for row in board]
            is_main_game_move = False

        # Use provided player_type or current game player
        if player_type is None:
            current_player_for_move = self.current_player
        else:
            current_player_for_move = player_type

        start_r, start_c = start_pos
        end_r, end_c = end_pos
        piece_type = temp_board[start_r][start_c]

        dr_abs = abs(end_r - start_r)
        dc_abs = abs(end_c - start_c)

        dr = (end_r - start_r) // dr_abs if dr_abs > 0 else 0
        dc = (end_c - start_c) // dc_abs if dc_abs > 0 else 0

        is_capture = False

        # Check if the move is a capture (distance > 1 implies capture in checkers)
        if dr_abs > 1 or dc_abs > 1:  # If move involves jumping over at least one square
            is_capture = True
            # Find and remove the first opponent piece along the jump path
            captured_r, captured_c = None, None

            # Iterate from start_pos towards end_pos, one step at a time
            current_r, current_c = start_r, start_c
            while True:
                current_r += dr
                current_c += dc

                if current_r == end_r and current_c == end_c:
                    # Reached the destination, no more pieces to check on path,
                    # or the captured piece was the last one before end_pos.
                    break

                if not (0 <= current_r < 8 and 0 <= current_c < 8):
                    break  # Out of bounds

                if self.is_opponent_piece(current_r, current_c, current_player_for_move, temp_board):
                    captured_r, captured_c = current_r, current_c
                    # print(f"DEBUG: Captured piece found at ({captured_r}, {captured_c})")
                    break  # Found the piece to be captured, break from finding opponent

                elif temp_board[current_r][current_c] != 0:  # Blocked by own piece or another piece that isn't opponent
                    # print(f"DEBUG: Path unexpectedly blocked by piece at ({current_r}, {current_c}).")
                    captured_r = None  # Invalidate capture if path is unexpectedly blocked
                    break

            if captured_r is not None:
                temp_board[captured_r][captured_c] = 0  # Remove the captured piece
                # print(f"DEBUG: Removed captured piece at ({captured_r}, {captured_c})")
            else:
                # print("DEBUG: No opponent found to capture on path. This implies an invalid capture move was attempted.")
                is_capture = False  # Ensure is_capture is False if no piece was actually captured

        # Execute the piece's move
        temp_board[end_r][end_c] = piece_type
        temp_board[start_r][start_c] = 0
        # print(f"DEBUG: Moved piece from ({start_r}, {start_c}) to ({end_r}, {end_c})")

        # Check for promotion on the temporary board
        promoted_from_pawn = 0
        if temp_board[end_r][end_c] == 1 and end_r == 0:
            temp_board[end_r][end_c] = 3  # White king
            promoted_from_pawn = 1
            # print(f"DEBUG: Piece promoted to white king at ({end_r}, {end_c})")
        elif temp_board[end_r][end_c] == 2 and end_r == 7:
            temp_board[end_r][end_c] = 4  # Black king
            promoted_from_pawn = 2
            # print(f"DEBUG: Piece promoted to black king at ({end_r}, {end_c})")

        new_forced_capture_piece = None
        if is_capture:
            # Check if the same piece can perform further captures on the temporary board
            remaining_captures = self._get_captures_for_piece(end_r, end_c, temp_board, current_player_for_move)
            if remaining_captures:
                new_forced_capture_piece = (end_r, end_c)
                # print(f"DEBUG: Remaining captures found for ({end_r}, {end_c}): {remaining_captures}")

        # Update main game state if this is not a minimax simulation
        if is_main_game_move:
            self.board = temp_board
            if is_capture and new_forced_capture_piece:
                self.forced_capture_piece = new_forced_capture_piece
                self.message = "Musisz kontynuować bicie!"
            else:
                self.forced_capture_piece = None
                self.current_player = 1 if current_player_for_move == 2 else 2
                self.message = f"Ruch {'białych' if self.current_player == 1 else 'czarnych'}."

            if promoted_from_pawn:
                self.message = "Pionek został promowany na damkę!" + (" " + self.message if self.message else "")

            return True  # Indicates move was made successfully

        else:  # For minimax simulation, return the new state
            next_player_type = current_player_for_move
            if not is_capture or not new_forced_capture_piece:
                next_player_type = 1 if current_player_for_move == 2 else 2

            # Return new board state, next player, new forced capture, and if a capture was made
            return temp_board, next_player_type, new_forced_capture_piece, is_capture

    def _evaluate_board(self, board, current_ai_player_type):
        """
        Evaluates the current board state for the AI player.
        Positive values are good for AI, negative for opponent.
        """
        score = 0
        opponent_player_type = 1 if current_ai_player_type == 2 else 2

        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece == 0:
                    continue

                if (current_ai_player_type == 1 and (piece == 1 or piece == 3)) or \
                        (current_ai_player_type == 2 and (piece == 2 or piece == 4)):  # AI's pieces
                    if piece == 1 or piece == 2:  # Pawn
                        score += 10
                        # Bonus for advancing pawns (for white, moving to lower rows is good; for black, higher rows)
                        if current_ai_player_type == 1:  # White AI
                            score += (7 - r)  # Max 7 for r=0, min 0 for r=7
                        else:  # Black AI
                            score += r  # Max 7 for r=7, min 0 for r=0
                    elif piece == 3 or piece == 4:  # King
                        score += 30  # Kings are more valuable
                elif (opponent_player_type == 1 and (piece == 1 or piece == 3)) or \
                        (opponent_player_type == 2 and (piece == 2 or piece == 4)):  # Opponent's pieces
                    if piece == 1 or piece == 2:  # Pawn
                        score -= 10
                        # Penalize opponent's advancing pawns
                        if opponent_player_type == 1:  # White Opponent
                            score -= (7 - r)
                        else:  # Black Opponent
                            score -= r
                    elif piece == 3 or piece == 4:  # King
                        score -= 30
        return score

    def _minimax(self, board, depth, maximizing_player, alpha, beta, current_ai_player_type,
                 original_forced_capture_piece):
        """
        Minimax algorithm with Alpha-Beta pruning to find the best move.
        maximizing_player: True if current node is for the AI (maximizing player), False for opponent.
        current_ai_player_type: The type of the AI player (1 or 2).
        original_forced_capture_piece: The piece that was forced to capture at the start of this minimax branch.
                                       This helps maintain capture rules across recursive calls.
        """
        # Base case: reached max depth or game over
        # Note: self.check_game_over for minimax needs to be careful about whose turn it is in the simulation
        # It takes player_type, so it knows which player has no moves.
        sim_player_type_for_game_over_check = current_ai_player_type if maximizing_player else (
            1 if current_ai_player_type == 2 else 2)
        if depth == 0 or self.check_game_over(board, sim_player_type_for_game_over_check,
                                              original_forced_capture_piece):
            return self._evaluate_board(board, current_ai_player_type)

        # Determine whose turn it is in the current simulation step
        sim_player_type = current_ai_player_type if maximizing_player else (1 if current_ai_player_type == 2 else 2)

        possible_moves_dict, has_forced_captures = self.get_all_possible_moves_for_player(board, sim_player_type,
                                                                                          original_forced_capture_piece)

        if not possible_moves_dict:  # No moves available for the current player in simulation
            return self._evaluate_board(board, current_ai_player_type)

        if maximizing_player:
            max_eval = float('-inf')
            # Iterate through all possible moves (including forced captures if applicable)
            for start_pos, end_positions in possible_moves_dict.items():
                for end_pos in end_positions:
                    # Simulate the move on a temporary board
                    new_board, next_player_type_after_move, new_forced_capture, is_capture = self.make_move(start_pos,
                                                                                                            end_pos,
                                                                                                            board,
                                                                                                            sim_player_type)

                    if is_capture and new_forced_capture:  # If capture and needs to continue
                        # Same player, same depth, but with the new forced_capture_piece for the next recursive call
                        eval = self._minimax(new_board, depth, maximizing_player, alpha, beta, current_ai_player_type,
                                             new_forced_capture)
                    else:
                        # Opponent's turn, reduce depth
                        eval = self._minimax(new_board, depth - 1, False, alpha, beta, current_ai_player_type, None)

                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break  # Beta cut-off
                if beta <= alpha:
                    break
            return max_eval
        else:  # Minimizing player
            min_eval = float('inf')
            # Iterate through all possible moves (including forced captures if applicable)
            for start_pos, end_positions in possible_moves_dict.items():
                for end_pos in end_positions:
                    # Simulate the move on a temporary board
                    new_board, next_player_type_after_move, new_forced_capture, is_capture = self.make_move(start_pos,
                                                                                                            end_pos,
                                                                                                            board,
                                                                                                            sim_player_type)

                    if is_capture and new_forced_capture:  # If capture and needs to continue
                        # Same player, same depth, but with the new forced_capture_piece
                        eval = self._minimax(new_board, depth, maximizing_player, alpha, beta, current_ai_player_type,
                                             new_forced_capture)
                    else:
                        # Maximizing player's turn, reduce depth
                        eval = self._minimax(new_board, depth - 1, True, alpha, beta, current_ai_player_type, None)

                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break  # Alpha cut-off
                if beta <= alpha:
                    break
            return min_eval

    def get_ai_move(self):
        """
        Determines the best move for the AI (black player) using Minimax with Alpha-Beta pruning.
        Returns a tuple (start_pos, end_pos) or None if no move is possible.
        """
        current_ai_player_type = self.current_player  # AI is always current player when this is called
        best_eval = float('-inf')
        best_move = None

        # print(f"AI: Current player {current_ai_player_type}, forced_capture_piece: {self.forced_capture_piece}")
        # print(f"AI: Board state at start of get_ai_move: {self.board}")

        # Get all possible moves for the current AI player
        possible_moves, has_forced_captures = self.get_all_possible_moves_for_player(self.board, current_ai_player_type,
                                                                                     self.forced_capture_piece)
        # print(f"AI: Possible moves for AI: {possible_moves}, has_forced_captures: {has_forced_captures}")

        if not possible_moves:
            self.message = "AI nie ma dostępnych ruchów."
            # print("AI: No possible moves found for AI.")
            return None, None  # AI cannot move

        # If there are forced captures, we must only consider those moves
        moves_to_evaluate = {}
        if has_forced_captures:
            if self.forced_capture_piece and self.forced_capture_piece in possible_moves:
                moves_to_evaluate[self.forced_capture_piece] = possible_moves[self.forced_capture_piece]
            else:  # If has_forced_captures is True but no specific forced_capture_piece set yet (first capture)
                moves_to_evaluate = possible_moves
        else:
            moves_to_evaluate = possible_moves

        # Sort moves for consistent AI behavior (optional, but good for reproducibility)
        sorted_start_positions = sorted(moves_to_evaluate.keys())

        for start_pos in sorted_start_positions:
            end_positions = sorted(moves_to_evaluate[start_pos])  # Sort end positions too
            for end_pos in end_positions:
                # Simulate the move
                new_board, next_player_type_after_move, new_forced_capture, is_capture = \
                    self.make_move(start_pos, end_pos, self.board, current_ai_player_type)

                # If AI made a capture and must continue, its turn continues, so depth doesn't decrease for minimax
                if is_capture and new_forced_capture:
                    eval = self._minimax(new_board, self.ai_search_depth, True, float('-inf'), float('inf'),
                                         current_ai_player_type, new_forced_capture)
                else:
                    # Opponent's turn (minimizing player)
                    eval = self._minimax(new_board, self.ai_search_depth - 1, False, float('-inf'), float('inf'),
                                         current_ai_player_type, None)

                # print(f"AI: Evaluating move {start_pos} -> {end_pos}, Eval: {eval}")

                if eval > best_eval:
                    best_eval = eval
                    best_move = (start_pos, end_pos)

        # print(f"AI: Best move found: {best_move} with eval: {best_eval}")
        return best_move

    def check_game_over(self, board=None, player_type=None, forced_capture_piece=None):
        """
        Checks if the game has ended (current player has no valid moves).
        Can operate on a given board and for a given player_type for Minimax.
        """
        if board is None:
            board = self.board
        if player_type is None:
            player_type = self.current_player
        if forced_capture_piece is None:
            forced_capture_piece = self.forced_capture_piece

        all_moves_available, has_any_moves = self.get_all_possible_moves_for_player(board, player_type,
                                                                                    forced_capture_piece)

        # print(f"DEBUG_GAME_OVER: Player {player_type} moves dict: {all_moves_available}, has_any_moves: {has_any_moves}, forced_capture_piece: {forced_capture_piece}")

        if not has_any_moves and not forced_capture_piece:
            winning_player = 1 if player_type == 2 else 2  # The other player wins
            if board is self.board:  # Only update game_logic's message if it's the main board
                self.message = f"Koniec gry! {'Biali' if winning_player == 1 else 'Czarni'} wygrywają! Brak ruchów dla {'czarnych' if player_type == 2 else 'białych'}."
            # print(f"DEBUG_GAME_OVER: Game is OVER for player {player_type}.")
            return True
        # print(f"DEBUG_GAME_OVER: Game is NOT over for player {player_type}.")
        return False
