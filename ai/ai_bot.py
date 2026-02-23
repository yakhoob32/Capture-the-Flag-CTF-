import random
from utils.constants import Team, CellType, PieceRank


class AIBot:
    """
    Artificial Intelligence for Stratego.
    Supports 3 levels of difficulty:
    1: Random Legal Moves
    2: Greedy (Always attacks if possible)
    3: Smart/Sherlock (Uses heuristics to guess bombs and prioritize forward movement)
    """

    def __init__(self, team: Team, logic, level: int = 2):
        self.team = team
        self.logic = logic
        self.board = logic.board
        self.level = level

    def get_move(self):
        """Returns the best move (start_pos, end_pos) based on the AI level."""
        valid_moves = self._get_all_legal_moves()

        if not valid_moves:
            return None  # AI has no legal moves left (Loses the game)

        if self.level == 1:
            return self._level_1_random(valid_moves)
        elif self.level == 2:
            return self._level_2_greedy(valid_moves)
        elif self.level == 3:
            return self._level_3_smart(valid_moves)

    # ==========================================
    # AI STRATEGIES (LEVELS)
    # ==========================================

    def _level_1_random(self, valid_moves):
        """Level 1: Pick any legal move completely at random."""
        return random.choice(valid_moves)

    def _level_2_greedy(self, valid_moves):
        """Level 2: Prioritize attacking enemy pieces."""
        scored_moves = []
        for start_pos, end_pos in valid_moves:
            score = 0
            target_piece = self.board.get_piece_at(end_pos[0], end_pos[1])

            if target_piece:
                score += 50  # Massive bonus for attacking

            # Add a tiny random value to break ties randomly
            score += random.randint(0, 5)
            scored_moves.append((score, start_pos, end_pos))

        # Sort by score descending and pick the best one
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        return (scored_moves[0][1], scored_moves[0][2])

    def _level_3_smart(self, valid_moves):
        """Level 3: Heuristics-based decision making."""
        scored_moves = []
        forward_dir = -1 if self.team == Team.BLUE else 1
        enemy_back_row = 0 if self.team == Team.BLUE else (self.board.size - 1)

        for start_pos, end_pos in valid_moves:
            score = 0
            piece = self.board.get_piece_at(start_pos[0], start_pos[1])
            target_piece = self.board.get_piece_at(end_pos[0], end_pos[1])

            if target_piece:
                # 1. Attacking the enemy back row (High chance of Bomb or Flag)
                if end_pos[1] == enemy_back_row:
                    if piece.rank == PieceRank.MINER:
                        score += 100  # Miners are perfect for back row!
                    else:
                        score -= 50  # Keep other units away from back-row bombs!
                else:
                    score += 40  # Normal attack
            else:
                # 2. Movement heuristics
                dy = end_pos[1] - start_pos[1]
                if dy == forward_dir:
                    score += 10  # Reward moving forward
                    if piece.rank in [PieceRank.SCOUT, PieceRank.MINER]:
                        score += 5  # Extra reward for scouts/miners advancing

            score += random.randint(0, 3)  # Tie-breaker
            scored_moves.append((score, start_pos, end_pos))

        scored_moves.sort(key=lambda x: x[0], reverse=True)
        return (scored_moves[0][1], scored_moves[0][2])

    # ==========================================
    # LEGAL MOVE GENERATOR (SILENT ENGINE)
    # ==========================================

    def _get_all_legal_moves(self):
        """Scans the board and returns all possible legal moves for the AI's team."""
        moves = []
        for y in range(self.board.size):
            for x in range(self.board.size):
                piece = self.board.get_piece_at(x, y)
                if piece and piece.team == self.team and piece.can_move:
                    piece_moves = self._get_moves_for_piece(piece, x, y)
                    for mx, my in piece_moves:
                        moves.append(((x, y), (mx, my)))
        return moves

    def _get_moves_for_piece(self, piece, x, y):
        """Calculates valid destinations for a specific piece."""
        moves = []

        # Scout logic: Can move in straight lines
        if piece.rank == PieceRank.SCOUT:
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            for dx, dy in directions:
                step = 1
                while True:
                    nx, ny = x + (dx * step), y + (dy * step)
                    if not self.board.is_within_bounds(nx, ny): break
                    if self.board.cell_metadata[ny][nx] == CellType.LAKE: break

                    target = self.board.get_piece_at(nx, ny)
                    if target:
                        if target.team != self.team:
                            moves.append((nx, ny))  # Attack possible
                        break  # Blocked by any piece

                    moves.append((nx, ny))
                    step += 1
        # All other movable pieces
        else:
            adjacent_cells = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
            for nx, ny in adjacent_cells:
                if self.board.is_within_bounds(nx, ny):
                    if self.board.cell_metadata[ny][nx] != CellType.LAKE:
                        target = self.board.get_piece_at(nx, ny)
                        if not target or target.team != self.team:
                            moves.append((nx, ny))
        return moves