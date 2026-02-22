from utils.config import BOARD_SIZE
from utils.constants import CellType, Team, PieceRank
from engine.piece import Piece


class Board:
    """
    Manages the game grid, obstacle placement, and piece locations.
    """

    def __init__(self):
        """Initializes the board with a fixed size and empty cells."""
        self.size = BOARD_SIZE
        # The actual grid containing Piece objects or None
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        # Metadata for cell types (LAKE, CLOUD, etc.)
        self.cell_metadata = [[CellType.EMPTY for _ in range(self.size)] for _ in range(self.size)]

        # Initialize obstacles
        self._setup_lakes()

    def _has_cloud_vision(self, team) -> bool:
        """
        Checks if the given team has a Scout inside a Cloud cell.
        This grants them 'Cloud Vision' to see enemy positions inside the fog.
        """
        for y in range(self.size):
            for x in range(self.size):
                if self.cell_metadata[y][x] == CellType.CLOUD:
                    piece = self.grid[y][x]
                    # If there is a piece, it belongs to the viewing team, and it's a Scout
                    if piece and piece.team == team and piece.rank == PieceRank.SCOUT:
                        return True
        return False

    def _setup_lakes(self):
        """
        Creates lakes. Adapts perfectly for the standard 10x10 board.
        """
        if self.size == 10:
            lake_rows = [4, 5]  # Middle rows for 10x10
            for r in lake_rows:
                # Standard Stratego lake columns
                for c in [2, 3, 6, 7]:
                    self.set_cell_type(c, r, CellType.LAKE)
        else:
            # Fallback for smaller testing boards (like our old 6x6)
            mid = self.size // 2
            lake_rows = [mid - 1, mid]
            for r in lake_rows:
                for c in [1, 2, self.size - 3, self.size - 2]:
                    if self.is_within_bounds(c, r):
                        self.set_cell_type(c, r, CellType.LAKE)

    def is_within_bounds(self, x: int, y: int) -> bool:
        """Checks if the given coordinates are inside the board."""
        return 0 <= x < self.size and 0 <= y < self.size

    def set_cell_type(self, x: int, y: int, cell_type: CellType):
        """Defines a cell as a Lake, Cloud, or Empty."""
        if self.is_within_bounds(x, y):
            self.cell_metadata[y][x] = cell_type

    def get_piece_at(self, x: int, y: int) -> Piece | None:
        """Returns the piece object at the specified location."""
        if self.is_within_bounds(x, y):
            return self.grid[y][x]
        return None

    def place_piece(self, piece, x: int, y: int):
        """Places a piece on the board at (x, y)."""
        if self.is_within_bounds(x, y):
            self.grid[y][x] = piece
            if piece:
                piece.position = (x, y)

    def display_terminal(self, viewer_team):
        """
        Prints a structured, grid-like table of the board in the terminal.
        Includes Cloud Vision logic: enemies in clouds are completely hidden
        unless the viewing team has a Scout inside the cloud.
        """
        cell_width = 10  # Width of each cell

        # Header
        header_row = "    "
        for x in range(self.size):
            header_row += f"{x:^{cell_width}}"
        print("\n" + header_row)

        horizontal_line = "    " + ("-" * (self.size * cell_width))
        print(horizontal_line)

        # Check if the current viewer has a Scout in the cloud
        has_cloud_vision = self._has_cloud_vision(viewer_team)

        # Main Board Loop
        for y in range(self.size):
            row_content = f"{y:<2} |"
            spacer_line = "   |"

            for x in range(self.size):
                cell_text = "."
                cell_type = self.cell_metadata[y][x]
                piece = self.grid[y][x]

                if cell_type == CellType.CLOUD:
                    if piece:
                        if piece.team == viewer_team or has_cloud_vision:
                            cell_text = f"[{piece.get_display(viewer_team)}]"
                        else:
                            cell_text = "##FOG##"
                    else:
                        cell_text = "##FOG##"

                elif piece:
                    cell_text = f"[{piece.get_display(viewer_team)}]"
                elif cell_type == CellType.LAKE:
                    cell_text = "~LAKE~"

                row_content += f"{cell_text:^{cell_width}}"
                spacer_line += f"{'':^{cell_width}}"

            print(spacer_line)
            print(row_content)
            print(spacer_line)
            print(horizontal_line)

        print("\n")