import pygame
from utils.constants import CellType, Team, PieceRank, GameState
from engine.piece import Piece
from utils.config import ARMY_COMPOSITION
from engine.game_logic import GameLogic
from ai.auto_setup import AutoSetup

# --- تعریف تم رنگی (قهوه‌ای و آجری) ---
LIGHT_BROWN = (235, 213, 179)  # قهوه‌ای خیلی روشن (کرمی/چوبی) برای خانه‌های روشن
BRICK_RED = (184, 58, 36)  # قرمز آجری/سفالی برای خانه‌های تیره
PANEL_BG = (245, 240, 230)  # پس‌زمینه پنل‌های کناری (رنگ کاغذ/پوست‌نوشته)
DARK_BROWN = (60, 40, 30)  # قهوه‌ای تیره برای متن‌ها و حاشیه‌ها
WHITE = (255, 255, 255)
LAKE_BLUE = (70, 130, 180)  # Added a nice Steel Blue color for lakes
# --- Colors for Pieces ---
RED_TEAM_COLOR = (200, 50, 50)
BLUE_TEAM_COLOR = (50, 100, 200)
HIGHLIGHT_COLOR = (218, 165, 32)


class GameScreen:
    """Handles the rendering of the game board and info panel."""

    # Added 'board' parameter to the constructor
    def __init__(self, width, height, board, logic):
        self.width = width
        self.height = height
        self.board = board
        self.logic = logic


        # --- Board Dimensions ---
        self.cols = self.board.size
        self.rows = self.board.size
        self.cell_size = 50
        self.board_width = self.cols * self.cell_size
        self.board_height = self.rows * self.cell_size

        # Calculate board position
        self.board_x = 40
        self.board_y = (self.height - self.board_height) // 2

        # Fonts
        self.font_coord = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_text = pygame.font.SysFont("Arial", 18)
        self.font_piece = pygame.font.SysFont("Arial", 20, bold=True)

        # --- Setup Phase Variables ---
        # Create a fresh copy of the army list so we can subtract from it
        self.inventory = ARMY_COMPOSITION.copy()

        # Tracks which piece the player clicked from the right panel
        self.selected_piece_name = None

        # Becomes True when all 40 pieces are placed
        self.setup_complete = False

    def handle_event(self, event):
        """Handle clicks on the board and the side panel."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            # 1. Check if clicked inside the BOARD area
            if self.board_x <= mouse_x < self.board_x + self.board_width and \
                    self.board_y <= mouse_y < self.board_y + self.board_height:

                col = (mouse_x - self.board_x) // self.cell_size
                row = (mouse_y - self.board_y) // self.cell_size

                # If we are in setup phase AND holding a piece
                if not self.setup_complete and self.selected_piece_name:
                    # Stratego Rule: Red team can only place in the bottom 4 rows
                    if row >= self.rows - 4:
                        # Rule: Cell must be empty AND not a lake
                        if self.board.get_piece_at(col, row) is None and self.board.cell_metadata[row][
                            col] != CellType.LAKE:

                            # Create the actual Piece object and place it in the backend
                            new_piece = Piece(PieceRank[self.selected_piece_name], Team.RED, (col, row))
                            self.board.place_piece(new_piece, col, row)

                            # Decrease inventory count
                            self.inventory[self.selected_piece_name] -= 1

                            # Deselect if we run out of this specific piece
                            if self.inventory[self.selected_piece_name] == 0:
                                self.selected_piece_name = None

                            # Check if all 40 pieces are placed
                            if all(count == 0 for count in self.inventory.values()):
                                self.setup_complete = True
                                print("Setup Phase Complete! Army is ready.")
                                # 1. Instantiate the AutoSetup class using our game logic
                                ai_setup = AutoSetup(self.logic)

                                # 2. Tell the AI to specifically deploy the BLUE team's pieces
                                ai_setup._smart_setup_team(Team.BLUE)

                                # 3. Update the game referee (GameLogic) that we are ready to play
                                self.logic.game_state = GameState.IN_PROGRESS
                                print("🤖 Smart AI Deployment Complete! Let the battle begin!")

                        else:
                            print("Invalid placement: Cell is occupied or is a Lake.")
                    else:
                        print("Invalid placement: Must be in the bottom 4 rows.")

            # 2. Check if clicked inside the INVENTORY PANEL (Right side)
            else:
                panel_x = self.board_x + self.board_width + 40
                start_y = self.board_y + 140
                y_offset = 0

                # Check which piece name was clicked
                for piece_name, count in self.inventory.items():
                    if count > 0:
                        item_rect = pygame.Rect(panel_x + 10, start_y + y_offset, 200, 25)
                        if item_rect.collidepoint(mouse_x, mouse_y):
                            self.selected_piece_name = piece_name  # Pick up the piece
                        y_offset += 30
    def draw(self, surface):
        """رسم تمام اجزای صفحه بازی"""
        # ۱. پاک کردن صفحه با رنگ ملایم
        surface.fill(PANEL_BG)

        # ۲. رسم تخته بازی
        self.draw_board(surface)

        # ۳. رسم پنل اطلاعات سمت راست
        self.draw_side_panel(surface)

    def draw_board(self, surface):
        """رسم خانه‌های شطرنجی و مختصات (A-J و 1-10)"""
        # رسم قابِ دورِ تخته
        border_rect = pygame.Rect(self.board_x - 4, self.board_y - 4,
                                  self.board_width + 8, self.board_height + 8)
        pygame.draw.rect(surface, DARK_BROWN, border_rect, border_radius=5)

        # Draw the 10x10 grid cells
        for row in range(self.rows):
            for col in range(self.cols):
                # 1. Check if the cell is a LAKE in the backend logic
                if self.board.cell_metadata[row][col] == CellType.LAKE:
                    color = LAKE_BLUE
                else:
                    # 2. Otherwise, use the standard checkerboard pattern
                    color = LIGHT_BROWN if (row + col) % 2 == 0 else BRICK_RED

                cell_rect = pygame.Rect(self.board_x + col * self.cell_size,
                                        self.board_y + row * self.cell_size,
                                        self.cell_size, self.cell_size)
                pygame.draw.rect(surface, color, cell_rect)

                # --- Draw the Pieces ---
                # Ask the backend board if there is a piece at this (col, row)
                piece = self.board.get_piece_at(col, row)

                if piece:
                    piece_color = RED_TEAM_COLOR if piece.team == Team.RED else BLUE_TEAM_COLOR
                    center = cell_rect.center

                    # Draw the piece as a circle
                    pygame.draw.circle(surface, piece_color, center, self.cell_size // 2 - 4)
                    pygame.draw.circle(surface, DARK_BROWN, center, self.cell_size // 2 - 4, 2)  # Border

                    # Draw the rank value (number/letter) in the center of the piece
                    text_val = str(piece.rank.value)
                    text_surf = self.font_piece.render(text_val, True, WHITE)
                    surface.blit(text_surf, text_surf.get_rect(center=center))

        # رسم حروف A تا J بالای تخته
        for col in range(self.cols):
            text = self.font_coord.render(chr(65 + col), True, DARK_BROWN)
            surface.blit(text, (self.board_x + col * self.cell_size + 18, self.board_y - 25))

        # رسم اعداد 1 تا 10 کنار تخته
        for row in range(self.rows):
            text = self.font_coord.render(str(row + 1), True, DARK_BROWN)
            surface.blit(text, (self.board_x - 25, self.board_y + row * self.cell_size + 15))

    def draw_side_panel(self, surface):
        """رسم باکسی شبیه به محیط شطرنج برای اطلاعات بازی"""
        panel_x = self.board_x + self.board_width + 40
        panel_y = self.board_y
        panel_width = self.width - panel_x - 40
        panel_height = self.board_height

        # رسم بدنه پنل
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(surface, WHITE, panel_rect, border_radius=10)
        pygame.draw.rect(surface, DARK_BROWN, panel_rect, width=2, border_radius=10)

        # تایتل پنل
        title_surf = self.font_title.render("GAME INFO", True, DARK_BROWN)
        surface.blit(title_surf, (panel_x + panel_width // 2 - title_surf.get_width() // 2, panel_y + 20))

        # خط جداکننده
        pygame.draw.line(surface, DARK_BROWN, (panel_x + 10, panel_y + 60), (panel_x + panel_width - 10, panel_y + 60),
                         2)

        # اطلاعات تستی (بعداً داینامیک میشه)
        turn_text = self.font_text.render("Turn: RED TEAM", True, (200, 50, 50))
        surface.blit(turn_text, (panel_x + 20, panel_y + 80))

        phase_text = self.font_text.render("Phase: SETUP", True, DARK_BROWN)
        surface.blit(phase_text, (panel_x + 20, panel_y + 110))

        # راهنمای موقت
        help_text = self.font_text.render("Click board to test", True, (100, 100, 100))
        surface.blit(help_text, (panel_x + 20, panel_height - 20))

        # --- Draw the Piece Inventory (Setup Phase Only) ---
        if not self.setup_complete:
            start_y = panel_y + 140
            y_offset = 0

            for piece_name, count in self.inventory.items():
                if count > 0:  # Only show pieces that are not zero
                    # Highlight the text if it is the currently selected piece
                    is_selected = (self.selected_piece_name == piece_name)
                    text_color = HIGHLIGHT_COLOR if is_selected else DARK_BROWN

                    inv_text = self.font_text.render(f"{piece_name}: {count}", True, text_color)
                    surface.blit(inv_text, (panel_x + 20, start_y + y_offset))

                    # Draw a small dot next to the selected piece
                    if is_selected:
                        pygame.draw.circle(surface, HIGHLIGHT_COLOR, (panel_x + 10, start_y + y_offset + 10), 4)

                    y_offset += 30