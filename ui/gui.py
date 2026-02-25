import pygame
import sys
import os
from game_screen import GameScreen
from engine.board import Board
from engine.game_logic import GameLogic
from ai.ai_bot import AIBot
from utils.constants import Team, GameState

# --- 1. Pygame Initialization ---
pygame.init()
pygame.mixer.init()

# --- 2. Constants & Settings ---
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Stratego Elite")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (50, 100, 200)
RED = (200, 50, 50)
GREEN = (50, 200, 50)

# Fonts
FONT_LARGE = pygame.font.SysFont("Arial", 48, bold=True)
FONT_MEDIUM = pygame.font.SysFont("Arial", 32)
FONT_SMALL = pygame.font.SysFont("Arial", 24)
FONT_EMOJI = pygame.font.SysFont("Segoe UI Emoji", 28)

# Load Music (Error handling in case file is missing)
try:
    music_path = os.path.join(os.path.dirname(__file__), "..", "assets", "Epic Music instrumental- 02.mp3")
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)  # Loop forever
except Exception as e:
    print(f"Warning: Could not load music file. Make sure assets/music.mp3 exists. Error: {e}")

# --- Load Images ---
background_img = None
try:
    # Construct the path to the background image
    bg_path = os.path.join(os.path.dirname(__file__), "..", "assets", "menu_background.png")
    print(f"🕵️‍♂️ Looking for image exactly at: {os.path.abspath(bg_path)}")
    # Load the image
    loaded_img = pygame.image.load(bg_path)
    # Scale the image to exactly fit the screen dimensions
    background_img = pygame.transform.scale(loaded_img, (WIDTH, HEIGHT))
except Exception as e:
    print(f"Warning: Could not load background image. Error: {e}")

# Global Volume State
current_volume = 50  # 0 to 100
is_muted = False
pygame.mixer.music.set_volume(current_volume / 100.0)


# --- 3. UI Widget Classes ---

class Button:
    """A simple clickable button."""

    def __init__(self, x, y, width, height, text, font=FONT_MEDIUM):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False

        self.base_color = (20, 20, 30, 180)
        self.hover_color = (40, 40, 60, 210)
        self.border_color = (200, 200, 255, 200)

    def draw(self, surface):
        self.is_hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        current_bg = self.hover_color if self.is_hovered else self.base_color
        text_color = WHITE if not self.is_hovered else (255, 255, 220)

        glass_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        pygame.draw.rect(glass_surface, current_bg, glass_surface.get_rect(), border_radius=15)

        pygame.draw.rect(glass_surface, self.border_color, glass_surface.get_rect(), width=2, border_radius=15)

        shadow_surf = self.font.render(self.text, True, (0, 0, 0, 150))  # سایه نیمه‌شفاف
        shadow_rect = shadow_surf.get_rect(center=(self.rect.width // 2 + 2, self.rect.height // 2 + 2))
        glass_surface.blit(shadow_surf, shadow_rect)

        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        glass_surface.blit(text_surf, text_rect)

        surface.blit(glass_surface, self.rect.topleft)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered


class Slider:
    """A horizontal slider for adjusting values (like volume)."""

    def __init__(self, x, y, width, height, initial_val):
        self.rect = pygame.Rect(x, y, width, height)
        self.val = initial_val  # 0 to 100
        self.is_dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            # Calculate value based on mouse X position
            mouse_x = event.pos[0]
            rel_x = max(0, min(mouse_x - self.rect.x, self.rect.width))
            self.val = int((rel_x / self.rect.width) * 100)
            return True  # Value changed
        return False

    def draw(self, surface):
        # Draw background track
        pygame.draw.rect(surface, DARK_GRAY, self.rect, border_radius=self.rect.height // 2)

        # Draw filled track
        fill_width = max(10, int((self.val / 100) * self.rect.width))
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(surface, GREEN, fill_rect, border_radius=self.rect.height // 2)

        # Draw knob
        pygame.draw.circle(surface, WHITE, (self.rect.x + fill_width, self.rect.y + self.rect.height // 2),
                           self.rect.height)


class TextBox:
    """A text input box specifically for numbers."""

    def __init__(self, x, y, width, height, initial_text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = str(initial_text)
        self.is_active = False

    def handle_event(self, event):
        value_changed = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_RETURN:
                self.is_active = False
                value_changed = True  # Trigger update on Enter
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit() and len(self.text) < 3:
                self.text += event.unicode
        return value_changed

    def draw(self, surface):
        color = BLUE if self.is_active else DARK_GRAY
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(surface, color, self.rect, 3)

        text_surf = FONT_MEDIUM.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


# --- 4. Main Application Loop ---

def  run_gui():
    global current_volume, is_muted

    clock = pygame.time.Clock()
    state = "MAIN_MENU"
    game_board = Board()
    game_logic = GameLogic(game_board)
    game_screen = GameScreen(WIDTH, HEIGHT, game_board, game_logic)
    ai_player = AIBot(Team.BLUE, game_logic, level=2)

    # Main Menu Buttons
    btn_vs_human = Button(250, 200, 300, 60, "Play vs Human")
    btn_vs_bot = Button(250, 280, 300, 60, "Play vs AI Bot")
    btn_online = Button(250, 360, 300, 60, "Play Online")
    btn_settings = Button(20, HEIGHT - 80, 60, 60, "⚙️", font=FONT_EMOJI)

    # Settings Widgets
    btn_back = Button(300, 500, 200, 50, "Back")
    vol_slider = Slider(200, 250, 300, 20, current_volume)
    vol_textbox = TextBox(520, 235, 70, 50, current_volume)
    btn_mute = Button(130, 235, 50, 50, "🔇" if is_muted else "🔊", font=FONT_EMOJI)

    def update_volume_system():
        """Applies the volume to Pygame mixer"""
        if is_muted:
            pygame.mixer.music.set_volume(0.0)
            btn_mute.text = "🔇"
        else:
            pygame.mixer.music.set_volume(current_volume / 100.0)
            btn_mute.text = "🔊"

    ai_think_start_time = 0
    is_ai_thinking = False

    running = True
    while running:
        SCREEN.fill(BLACK)  # Background

        # --- Event Handling ---
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            # if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            #     pygame.display.set_mode((WIDTH, HEIGHT))
            if state == "MAIN_MENU":
                if btn_vs_human.is_clicked(event):
                    print("Transition to Local Game...")
                elif btn_vs_bot.is_clicked(event):
                    state = "PLAYING_AI"
                    # pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                elif btn_online.is_clicked(event):
                    print("Transition to Online Game...")
                elif btn_settings.is_clicked(event):
                    state = "SETTINGS"

            elif state == "SETTINGS":
                if btn_back.is_clicked(event):
                    state = "MAIN_MENU"

                # Mute Button Logic
                if btn_mute.is_clicked(event):
                    is_muted = not is_muted
                    update_volume_system()

                # Slider Logic
                if vol_slider.handle_event(event):
                    current_volume = vol_slider.val
                    vol_textbox.text = str(current_volume)
                    if not is_muted: update_volume_system()

                # TextBox Logic
                if vol_textbox.handle_event(event):
                    # When Enter is pressed
                    try:
                        new_vol = int(vol_textbox.text)
                        new_vol = max(0, min(new_vol, 100))  # Clamp between 0-100
                        current_volume = new_vol
                        vol_textbox.text = str(current_volume)
                        vol_slider.val = current_volume
                        if not is_muted: update_volume_system()
                    except ValueError:
                        vol_textbox.text = str(current_volume)  # Revert if empty/invalid

            elif state == "PLAYING_AI":
                game_screen.handle_event(event)
        if state == "PLAYING_AI" and game_logic.game_state == GameState.IN_PROGRESS:
            if game_logic.current_turn == Team.BLUE:
                # 1. Start the timer if AI just started thinking
                if not is_ai_thinking:
                    is_ai_thinking = True
                    ai_think_start_time = pygame.time.get_ticks()

                # 2. Check if 600ms have passed since thinking started
                current_time = pygame.time.get_ticks()
                if current_time - ai_think_start_time > 1500:
                    ai_move = ai_player.get_move()
                    if ai_move:
                        start_pos, end_pos = ai_move
                        print(f"🤖 AI chose to move from {start_pos} to {end_pos}")
                        game_logic.execute_move(start_pos, end_pos)
                    else:
                        print("🤖 AI has no valid moves left!")

                    # 3. Reset thinking state for the next turn
                    is_ai_thinking = False


        # --- Drawing Phase ---
        SCREEN.fill(BLACK)  # Always clear the screen first

        # Draw the background image if it was loaded successfully

        if background_img:
            SCREEN.blit(background_img, (0, 0))

        if state == "MAIN_MENU":
            if not background_img:
                title_surf = FONT_LARGE.render("SUPER STRATEGO ELITE", True, WHITE)
                SCREEN.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 80))

            btn_vs_human.draw(SCREEN)
            btn_vs_bot.draw(SCREEN)
            btn_online.draw(SCREEN)
            # We only draw the settings button since it's not part of the background image
            btn_settings.draw(SCREEN)

        elif state == "SETTINGS":
            # (Settings section code remains unchanged)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            SCREEN.blit(overlay, (0, 0))

            title_surf = FONT_LARGE.render("SETTINGS", True, WHITE)
            SCREEN.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 80))

            vol_label = FONT_MEDIUM.render("Music Volume:", True, WHITE)
            SCREEN.blit(vol_label, (200, 190))

            btn_mute.draw(SCREEN)
            vol_slider.draw(SCREEN)
            vol_textbox.draw(SCREEN)
            btn_back.draw(SCREEN)

        elif state == "PLAYING_AI":
            game_screen.draw(SCREEN)
        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_gui()