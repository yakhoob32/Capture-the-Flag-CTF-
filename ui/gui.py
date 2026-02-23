import pygame
import sys
import os

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

# Load Music (Error handling in case file is missing)
try:
    music_path = os.path.join(os.path.dirname(__file__), "..", "assets", "Epic Music instrumental- 02.mp3")
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)  # Loop forever
except Exception as e:
    print(f"Warning: Could not load music file. Make sure assets/music.mp3 exists. Error: {e}")

# Global Volume State
current_volume = 50  # 0 to 100
is_muted = False
pygame.mixer.music.set_volume(current_volume / 100.0)


# --- 3. UI Widget Classes ---

class Button:
    """A simple clickable button."""

    def __init__(self, x, y, width, height, text, color=BLUE, hover_color=GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        self.is_hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)  # Border

        text_surf = FONT_MEDIUM.render(self.text, True, WHITE if not self.is_hovered else BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

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

def run_gui():
    global current_volume, is_muted

    clock = pygame.time.Clock()
    state = "MAIN_MENU"

    # Main Menu Buttons
    btn_vs_human = Button(250, 200, 300, 60, "Play vs Human")
    btn_vs_bot = Button(250, 280, 300, 60, "Play vs AI Bot")
    btn_online = Button(250, 360, 300, 60, "Play Online")
    btn_settings = Button(250, 440, 300, 60, "Settings", color=DARK_GRAY)

    # Settings Widgets
    btn_back = Button(300, 500, 200, 50, "Back", color=RED)
    vol_slider = Slider(200, 250, 300, 20, current_volume)
    vol_textbox = TextBox(520, 235, 70, 50, current_volume)
    btn_mute = Button(130, 235, 50, 50, "M", color=RED if is_muted else GREEN)  # "M" for Mute

    def update_volume_system():
        """Applies the volume to Pygame mixer"""
        if is_muted:
            pygame.mixer.music.set_volume(0.0)
            btn_mute.color = RED
        else:
            pygame.mixer.music.set_volume(current_volume / 100.0)
            btn_mute.color = GREEN

    running = True
    while running:
        SCREEN.fill(BLACK)  # Background

        # --- Event Handling ---
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            if state == "MAIN_MENU":
                if btn_vs_human.is_clicked(event):
                    print("Transition to Local Game...")
                elif btn_vs_bot.is_clicked(event):
                    print("Transition to AI Game...")
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

        # --- Drawing Phase ---
        if state == "MAIN_MENU":
            # Title
            title_surf = FONT_LARGE.render("SUPER STRATEGO ELITE", True, WHITE)
            SCREEN.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 80))

            btn_vs_human.draw(SCREEN)
            btn_vs_bot.draw(SCREEN)
            btn_online.draw(SCREEN)
            btn_settings.draw(SCREEN)

        elif state == "SETTINGS":
            # Title
            title_surf = FONT_LARGE.render("SETTINGS", True, WHITE)
            SCREEN.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 80))

            # Volume Label
            vol_label = FONT_MEDIUM.render("Music Volume:", True, WHITE)
            SCREEN.blit(vol_label, (200, 190))

            btn_mute.draw(SCREEN)
            vol_slider.draw(SCREEN)
            vol_textbox.draw(SCREEN)
            btn_back.draw(SCREEN)

        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_gui()