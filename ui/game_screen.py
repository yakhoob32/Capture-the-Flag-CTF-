import pygame

# --- تعریف تم رنگی (قهوه‌ای و آجری) ---
LIGHT_BROWN = (235, 213, 179)  # قهوه‌ای خیلی روشن (کرمی/چوبی) برای خانه‌های روشن
BRICK_RED = (184, 58, 36)  # قرمز آجری/سفالی برای خانه‌های تیره
PANEL_BG = (245, 240, 230)  # پس‌زمینه پنل‌های کناری (رنگ کاغذ/پوست‌نوشته)
DARK_BROWN = (60, 40, 30)  # قهوه‌ای تیره برای متن‌ها و حاشیه‌ها
WHITE = (255, 255, 255)


class GameScreen:
    """این کلاس تمام مسئولیت‌های رسم صفحه اصلی بازی و پنل اطلاعات رو بر عهده داره."""

    def __init__(self, width, height):
        self.width = width
        self.height = height

        # --- تنظیمات ابعاد تخته 10x10 ---
        self.cols = 10
        self.rows = 10
        self.cell_size = 50  # اندازه هر مربع روی تخته
        self.board_width = self.cols * self.cell_size
        self.board_height = self.rows * self.cell_size

        # محاسبه جایگاه تخته (کمی متمایل به چپ تا سمت راست برای پنل جا باشه)
        self.board_x = 40
        self.board_y = (self.height - self.board_height) // 2

        # فونت‌ها
        self.font_coord = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_text = pygame.font.SysFont("Arial", 18)

    def handle_event(self, event):
        """پردازش کلیک‌ها روی صفحه بازی"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            # اگر روی تخته بازی کلیک شد، مختصات (سطر و ستون) رو پیدا می‌کنیم
            if self.board_x <= mouse_x < self.board_x + self.board_width and \
                    self.board_y <= mouse_y < self.board_y + self.board_height:
                col = (mouse_x - self.board_x) // self.cell_size
                row = (mouse_y - self.board_y) // self.cell_size
                print(f"🎯 Clicked on Board -> Row: {row}, Col: {col}")

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

        # رسم خانه‌های 10x10
        for row in range(self.rows):
            for col in range(self.cols):
                # برای ایجاد حالت شطرنجی، مجموع سطر و ستون رو زوج و فرد می‌کنیم
                color = LIGHT_BROWN if (row + col) % 2 == 0 else BRICK_RED

                cell_rect = pygame.Rect(self.board_x + col * self.cell_size,
                                        self.board_y + row * self.cell_size,
                                        self.cell_size, self.cell_size)
                pygame.draw.rect(surface, color, cell_rect)

                # نکته: بعداً اینجا منطق رسمِ دریاچه‌ها و مهره‌ها رو اضافه می‌کنیم.

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