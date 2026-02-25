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

        # --- Define Auto-Deploy Button Rect ---
        panel_x = self.board_x + self.board_width + 40
        # Position the button at the bottom of the side panel
        self.btn_auto_deploy = pygame.Rect(panel_x + 20, self.height - 80, 200, 45)

        # --- Action Phase Variables ---
        # To remember which piece the player clicked on the board
        self.selected_board_pos = None

    def handle_event(self, event):
        """Handle clicks on the board and the side panel."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            # --- 1. Check if Auto-Deploy Button is clicked ---
            if not self.setup_complete and self.btn_auto_deploy.collidepoint(mouse_x, mouse_y):
                print("⚡ Auto-deploying RED team...")

                # 1. Clear the bottom 4 rows in case the player manually placed a few pieces before clicking Auto
                for r in range(self.rows - 4, self.rows):
                    for c in range(self.cols):
                        self.board.grid[r][c] = None

                # 2. Summon the AutoSetup AI
                ai_setup = AutoSetup(self.logic)

                # 3. Setup RED team, then BLUE team
                ai_setup._smart_setup_team(Team.RED)
                ai_setup._smart_setup_team(Team.BLUE)

                # 4. Empty the player's inventory list visually
                for piece in self.inventory:
                    self.inventory[piece] = 0

                # 5. Finalize the setup phase
                self.setup_complete = True
                self.selected_piece_name = None
                self.logic.game_state = GameState.IN_PROGRESS
                print("✅ Both armies deployed instantly! Let the battle begin!")
                return  # Stop processing this click

            # 2. Check if clicked inside the BOARD area
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

                # --- ACTION PHASE LOGIC ---
                elif self.logic.game_state == GameState.IN_PROGRESS:
                    clicked_piece = self.board.get_piece_at(col, row)
                    # 1. If no piece is currently selected
                    if self.selected_board_pos is None:
                        # Select only if it's our piece (RED team)
                        if clicked_piece and clicked_piece.team == Team.RED:
                            self.selected_board_pos = (col, row)
                    # 2. If a piece is already selected
                    else:
                        # If clicked on another RED piece, change selection
                        if clicked_piece and clicked_piece.team == Team.RED:
                            self.selected_board_pos = (col, row)
                        # If clicked on empty cell or Enemy piece, try to MOVE/ATTACK
                        else:
                            start_pos = self.selected_board_pos
                            end_pos = (col, row)
                            # Ask GameLogic if this move is legal
                            if self.logic.validate_move(start_pos, end_pos):
                                report = self.logic.execute_move(start_pos, end_pos)
                                self.selected_board_pos = None
                                if report and report.get("battle"):
                                    self.draw(pygame.display.get_surface())
                                    self.show_battle_alert(pygame.display.get_surface(), report)
                            else:
                                self.selected_board_pos = None  # Deselect if invalid move


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

                # --- Highlight Selected Piece ---
                # Draw a thick gold border around the currently selected piece
                if self.selected_board_pos == (col, row):
                    pygame.draw.rect(surface, HIGHLIGHT_COLOR, cell_rect, 4)

                # --- Draw the Pieces ---
                # Ask the backend board if there is a piece at this (col, row)
                piece = self.board.get_piece_at(col, row)

                if piece:
                    piece_color = RED_TEAM_COLOR if piece.team == Team.RED else BLUE_TEAM_COLOR
                    center = cell_rect.center

                    # Draw the piece as a circle
                    pygame.draw.circle(surface, piece_color, center, self.cell_size // 2 - 4)
                    pygame.draw.circle(surface, DARK_BROWN, center, self.cell_size // 2 - 4, 2)  # Border

                    if piece.team == Team.RED or piece.is_revealed:
                        text_val = str(piece.rank.value)
                    else:
                        text_val = "?"

                    # Draw the rank value (number/letter) in the center of the piece
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
        pygame.draw.line(surface, DARK_BROWN, (panel_x + 10, panel_y + 60), (panel_x + panel_width - 10, panel_y + 60),2)

        # --- Dynamic Turn Indicator ---
        if self.logic.current_turn == Team.RED:
            turn_str = "Turn: RED TEAM"
            turn_color = RED_TEAM_COLOR
        else:
            turn_str = "Turn: BLUE TEAM (AI)"
            turn_color = BLUE_TEAM_COLOR

        turn_text = self.font_text.render(turn_str, True, turn_color)
        surface.blit(turn_text, (panel_x + 20, panel_y + 80))

        phase_text = self.font_text.render("Phase: SETUP", True, DARK_BROWN)
        surface.blit(phase_text, (panel_x + 20, panel_y + 110))


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

            # --- Draw the Auto-Deploy Button ---
            pygame.draw.rect(surface, BLUE_TEAM_COLOR, self.btn_auto_deploy, border_radius=10)
            btn_text = self.font_piece.render("Auto Deploy", True, WHITE)
            surface.blit(btn_text, btn_text.get_rect(center=self.btn_auto_deploy.center))

    def show_battle_alert(self, surface, report):
        """Displays a MODERN, tactical modal for battle results."""
        if not report.get("battle"):
            return

        # --- 1. Extract Report Data ---
        sx, sy = report["start"]
        ex, ey = report["end"]
        start_str = f"{chr(65 + sx)}{sy + 1}"
        end_str = f"{chr(65 + ex)}{ey + 1}"

        att_team = report["attacker_team"]
        att_rank_name = report["attacker_rank"]
        def_team = report["defender_team"]
        def_rank_name = report["defender_rank"]
        msg = report["message"]

        # Determine team colors for display
        att_color = RED_TEAM_COLOR if att_team == "RED" else BLUE_TEAM_COLOR
        def_color = BLUE_TEAM_COLOR if def_team == "BLUE" else RED_TEAM_COLOR

        # --- 2. Modern UI Settings ---
        box_width, box_height = 500, 320
        box_x = (self.width - box_width) // 2
        box_y = (self.height - box_height) // 2

        # Modern Colors
        MODERN_BG = (30, 40, 50, 230)  # Semi-transparent dark background
        BORDER_COLOR = (100, 200, 255)  # Neon blue for borders
        TEXT_WHITE = (240, 240, 240)
        TEXT_GRAY = (180, 180, 180)

        # Custom fonts for the panel
        font_header = pygame.font.SysFont("Arial", 28, bold=True)
        font_rank_big = pygame.font.SysFont("Arial", 36, bold=True)
        font_details = pygame.font.SysFont("Arial", 20)
        font_result = pygame.font.SysFont("Arial", 22, bold=True, italic=True)

        # Modern OK Button dimensions and rect
        btn_width, btn_height = 160, 45
        btn_rect = pygame.Rect(box_x + (box_width - btn_width) // 2, box_y + box_height - 65, btn_width, btn_height)

        clock = pygame.time.Clock()
        waiting = True

        # Blocking Loop (Halts the game until acknowledged)
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys;
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                        waiting = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_rect.collidepoint(event.pos):
                        waiting = False

            # --- Drawing Elements ---

            # 1. Create a glass-like surface for the panel background
            panel_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            pygame.draw.rect(panel_surface, MODERN_BG, panel_surface.get_rect(), border_radius=20)
            pygame.draw.rect(panel_surface, BORDER_COLOR, panel_surface.get_rect(), width=3, border_radius=20)
            surface.blit(panel_surface, (box_x, box_y))

            # 2. Main Title
            title_surf = font_header.render("TACTICAL ENGAGEMENT REPORT", True, BORDER_COLOR)
            title_rect = title_surf.get_rect(center=(box_x + box_width // 2, box_y + 35))
            surface.blit(title_surf, title_rect)

            # 3. Information Layout (Left: Attacker, Right: Defender)
            center_x = box_x + box_width // 2
            left_center = box_x + box_width // 4
            right_center = box_x + 3 * box_width // 4
            content_y_start = box_y + 90

            # --- Left Column (Attacker) ---
            att_label = font_details.render(f"ATTACKER ({att_team})", True, TEXT_GRAY)
            surface.blit(att_label, att_label.get_rect(center=(left_center, content_y_start)))

            att_rank_surf = font_rank_big.render(att_rank_name, True, att_color)
            surface.blit(att_rank_surf, att_rank_surf.get_rect(center=(left_center, content_y_start + 40)))

            # --- Center (VS) ---
            vs_surf = font_header.render("VS", True, TEXT_WHITE)
            surface.blit(vs_surf, vs_surf.get_rect(center=(center_x, content_y_start + 40)))

            # --- Right Column (Defender) ---
            def_label = font_details.render(f"DEFENDER ({def_team})", True, TEXT_GRAY)
            surface.blit(def_label, def_label.get_rect(center=(right_center, content_y_start)))

            def_rank_surf = font_rank_big.render(def_rank_name, True, def_color)
            surface.blit(def_rank_surf, def_rank_surf.get_rect(center=(right_center, content_y_start + 40)))

            # --- Movement Coordinates ---
            move_surf = font_details.render(f"Sector: {start_str}  >>>  {end_str}", True, TEXT_GRAY)
            surface.blit(move_surf, move_surf.get_rect(center=(center_x, content_y_start + 85)))

            # --- Divider Line and Result ---
            pygame.draw.line(surface, (100, 100, 100), (box_x + 30, box_y + 200), (box_x + box_width - 30, box_y + 200),
                             2)

            result_surf = font_result.render(f"OUTCOME: {msg}", True, BORDER_COLOR)
            surface.blit(result_surf, result_surf.get_rect(center=(center_x, box_y + 225)))

            # 4. Draw the Modern OK Button
            is_hovered = btn_rect.collidepoint(pygame.mouse.get_pos())
            btn_color = (50, 150, 200) if is_hovered else (30, 100, 150)
            pygame.draw.rect(surface, btn_color, btn_rect, border_radius=15)
            pygame.draw.rect(surface, BORDER_COLOR, btn_rect, width=2, border_radius=15)

            btn_text_surf = font_details.render("ROGER THAT", True, TEXT_WHITE)
            surface.blit(btn_text_surf, btn_text_surf.get_rect(center=btn_rect.center))

            pygame.display.flip()
            clock.tick(60)