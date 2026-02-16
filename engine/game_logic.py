from utils.constants import Team, PieceRank, CellType, GameState
from utils.config import BOARD_SIZE


class GameLogic:
    """
    The referee of the game. Handles turn management, move validation,
    and game state updates.
    """

    def __init__(self, board):
        """
        :param board: The game board object (from engine.board).
        """
        self.board = board
        self.current_turn = Team.RED  # Red always starts first
        self.game_state = GameState.SETUP_PHASE
        self.winner = None

    def switch_turn(self):
        """Switches the active player."""
        if self.current_turn == Team.RED:
            self.current_turn = Team.BLUE
        else:
            self.current_turn = Team.RED
        print(f"Turn switched! Now it's {self.current_turn.name}'s turn.")

    def validate_move(self, start_pos: tuple, end_pos: tuple) -> bool:
        """
        Checks if a move from start_pos to end_pos is legal.

        :return: True if valid, False otherwise (with a print message explaining why).
        """
        sx, sy = start_pos
        ex, ey = end_pos

        # 1. Check board boundaries
        if not (self.board.is_within_bounds(sx, sy) and self.board.is_within_bounds(ex, ey)):
            print("Error: Move out of bounds.")
            return False

        # 2. Check if there is a piece at the start position
        piece = self.board.get_piece_at(sx, sy)
        if not piece:
            print("Error: No piece at starting position.")
            return False

        # 3. Check turn ownership
        if piece.team != self.current_turn:
            print(f"Error: It is {self.current_turn.name}'s turn. You cannot move {piece.team.name} pieces.")
            return False

        # 4. Check if the piece is movable (Bombs and Flags are static)
        if not piece.can_move:
            print(f"Error: {piece.rank.name} cannot move.")
            return False

        # 5. Check destination cell type (Cannot move into Lakes)
        if self.board.cell_metadata[ey][ex] == CellType.LAKE:
            print("Error: Cannot move into a Lake.")
            return False

        # 6. Check destination occupancy (Cannot move onto own piece)
        dest_piece = self.board.get_piece_at(ex, ey)
        if dest_piece and dest_piece.team == piece.team:
            print("Error: Cannot move onto a square occupied by your own piece.")
            return False

        # 7. Movement Rules based on Rank
        dx = abs(ex - sx)
        dy = abs(ey - sy)

        # Rule for Scout (Rank 2): Can move any distance in a straight line, but not jump
        if piece.rank == PieceRank.SCOUT:
            if dx > 0 and dy > 0:
                print("Error: Scout can only move in straight lines (horizontally or vertically).")
                return False
            if not self._is_path_clear(start_pos, end_pos):
                print("Error: Path is blocked. Scouts cannot jump over pieces or lakes.")
                return False

        # Rule for all other pieces: Can move only 1 step
        else:
            if dx + dy != 1:
                print("Error: This piece can only move 1 step adjacent.")
                return False

        return True

    def _is_path_clear(self, start_pos, end_pos) -> bool:
        """
        Helper method for Scout movement. Checks if the path is free of obstacles.
        """
        sx, sy = start_pos
        ex, ey = end_pos

        # Determine direction
        step_x = 0 if sx == ex else (1 if ex > sx else -1)
        step_y = 0 if sy == ey else (1 if ey > sy else -1)

        curr_x, curr_y = sx + step_x, sy + step_y

        # Loop until we reach the cell BEFORE the destination
        while (curr_x, curr_y) != (ex, ey):
            # Check for piece
            if self.board.get_piece_at(curr_x, curr_y):
                return False
            # Check for Lake
            if self.board.cell_metadata[curr_y][curr_x] == CellType.LAKE:
                return False

            curr_x += step_x
            curr_y += step_y

        return True

    def execute_move(self, start_pos: tuple, end_pos: tuple):
        """
        Moves the piece and handles combat if necessary.
        """
        sx, sy = start_pos
        ex, ey = end_pos

        attacker = self.board.get_piece_at(sx, sy)
        defender = self.board.get_piece_at(ex, ey)

        # Remove attacker from old position regardless of outcome
        self.board.grid[sy][sx] = None
        attacker.position = None  # Temporarily in limbo

        if defender:
            print(f"⚔️ COMBAT! {attacker} attacks {defender}...")
            winner, message = self._resolve_battle(attacker, defender)
            print(f"Result: {message}")

            if winner == attacker:
                # Attacker takes the spot
                self.board.place_piece(attacker, ex, ey)
                # Defender is removed (already overwritten or handled)
            elif winner == defender:
                # Attacker dies, Defender stays
                # We need to put the defender back (it wasn't moved, but just to be safe)
                pass
            else:
                # It's a Tie (Both die)
                self.board.grid[ey][ex] = None
        else:
            # Simple move (No combat)
            self.board.place_piece(attacker, ex, ey)
            print(f"Moved {attacker} to ({ex}, {ey}).")

        self.switch_turn()

    def _resolve_battle(self, attacker, defender):
        """
        Determines the winner of a battle.
        Returns: (Winning_Piece_Object, "Reason Message")
        If tie, returns (None, "Tie Message")
        """
        # 1. Capture Flag
        if defender.rank == PieceRank.FLAG:
            self.game_state = GameState.FINISHED
            self.winner = attacker.team
            return attacker, f"🚩 FLAG CAPTURED! {attacker.team.name} WINS!"

        # 2. Hitting a Bomb
        if defender.rank == PieceRank.BOMB:
            if attacker.rank == PieceRank.MINER:
                return attacker, "Miner defused the Bomb!"
            else:
                return defender, "BOOM! Attacker blew up."

        # 3. Spy vs Marshal
        if attacker.rank == PieceRank.SPY and defender.rank == PieceRank.MARSHAL:
            return attacker, "Spy assassinated the Marshal!"

        # 4. Standard Rank Comparison
        # We need to handle 'S' (Spy) carefully since it's a string, not int for comparison
        att_val = attacker.rank.value
        def_val = defender.rank.value

        # Spy is effectively rank 1 when attacked or attacking anything other than Marshal
        if attacker.rank == PieceRank.SPY: att_val = 1
        if defender.rank == PieceRank.SPY: def_val = 1

        if att_val > def_val:
            return attacker, f"Attacker ({att_val}) beats Defender ({def_val})"
        elif att_val < def_val:
            return defender, f"Defender ({def_val}) beats Attacker ({att_val})"
        else:
            return None, f"Tie! Both ({att_val}) are eliminated."