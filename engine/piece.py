from utils.constants import PieceRank, Team


class Piece:
    """
    Represents a single game piece (soldier, bomb, or flag).
    Handles identity, position, and visibility logic.
    """

    def __init__(self, rank: PieceRank, team: Team, position: tuple = None):
        """
        Initialize a game piece.

        :param rank: The rank of the piece from PieceRank enum.
        :param team: The team it belongs to (RED or BLUE).
        :param position: Initial (x, y) coordinates on the board.
        """
        self.rank = rank
        self.team = team
        self.position = position  # Example: (x, y)

        # Visibility states
        self.is_revealed = False  # Becomes True once it engages in combat
        self.is_captured = False  # Becomes True if the piece is removed from board

        # Movement capability logic
        self.can_move = self._check_if_movable()

    def _check_if_movable(self) -> bool:
        """
        Internal check to see if the piece type is allowed to move.
        Bombs and Flags are stationary.
        """
        if self.rank in [PieceRank.BOMB, PieceRank.FLAG]:
            return False
        return True

    def reveal(self):
        """Sets the piece to revealed state after an interaction."""
        self.is_revealed = True

    def move_to(self, new_position: tuple):
        """
        Updates the piece's coordinates.
        Note: Validation happens in Board/GameLogic classes.
        """
        if self.can_move:
            self.position = new_position

    def __repr__(self):
        """Used for debugging and CLI display (Phase 1)."""
        return f"{self.team.name[0]}{self.rank.value}"

    def get_display(self, viewer_team):
        """
        Returns the string representation of the piece based on who is looking.
        If it's the opponent looking, hide the rank!
        """
        if self.team == viewer_team:
            return f"{self.team.name[0]}{self.rank.value}"
        else:
            return f"{self.team.name[0]}?"