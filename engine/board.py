from utils.config import BOARD_SIZE
from utils.constants import CellType


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

    def _setup_lakes(self):
        """
        Creates two 2x2 lakes in the middle of the board.
        """
        mid = self.size // 2
        lake_rows = [mid - 1, mid]  # Middle rows

        # Lake 1 (Left-ish)
        for r in lake_rows:
            for c in [1, 2]:  # Example columns for size 6
                if self.is_within_bounds(c, r):
                    self.set_cell_type(c, r, CellType.LAKE)

        # Lake 2 (Right-ish)
        for r in lake_rows:
            for c in [self.size - 3, self.size - 2]:
                if self.is_within_bounds(c, r):
                    self.set_cell_type(c, r, CellType.LAKE)

    def is_within_bounds(self, x: int, y: int) -> bool:
        """Checks if the given coordinates are inside the board."""
        return 0 <= x < self.size and 0 <= y < self.size

    def set_cell_type(self, x: int, y: int, cell_type: CellType):
        """Defines a cell as a Lake, Cloud, or Empty."""
        if self.is_within_bounds(x, y):
            self.cell_metadata[y][x] = cell_type

    def get_piece_at(self, x: int, y: int):
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

    def display_terminal(self):
        """
        Prints a structured, grid-like table of the board in the terminal.
        """
        cell_width = 10  # Width of each cell

        # Header
        header_row = "    "
        for x in range(self.size):
            header_row += f"{x:^{cell_width}}"
        print("\n" + header_row)

        horizontal_line = "    " + ("-" * (self.size * cell_width))
        print(horizontal_line)

        # Main Board Loop
        for y in range(self.size):
            row_content = f"{y:<2} |"
            spacer_line = "   |"

            for x in range(self.size):
                cell_text = "."
                cell_type = self.cell_metadata[y][x]
                piece = self.grid[y][x]

                if piece:
                    cell_text = f"[{piece}]"
                elif cell_type == CellType.LAKE:
                    cell_text = "~LAKE~"
                elif cell_type == CellType.CLOUD:
                    cell_text = "##FOG##"

                row_content += f"{cell_text:^{cell_width}}"
                spacer_line += f"{'':^{cell_width}}"

            print(spacer_line)
            print(row_content)
            print(spacer_line)
            print(horizontal_line)
        print("\n")