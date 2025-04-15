import datetime
import json
import random
from typing import List, Tuple

import pygame
import pygame_gui
import pygame_menu

import consts

pygame.init()


# --- Класс для работы со статистикой ---
class StatsManager:
    def __init__(self, history_file: str) -> None:
        self.history_file = history_file
        self.history = self.load_history()

    def load_history(self) -> list[dict]:
        try:
            with open(self.history_file) as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_history(self) -> None:
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=4)

    def record(
        self,
        size_x: int,
        size_y: int,
        num_circles: int,
        circles: list[tuple[int, int]],
        selected_positions: list[tuple[int, int]],
        wins: int,
        streak: int,
        level_result: str,
    ) -> None:
        record = {
            "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "grid_size": f"{size_x}x{size_y}",
            "num_circles": num_circles,
            "circles": circles,
            "selected": selected_positions,
            "score": wins,
            "streak": streak,
            "result": level_result,
        }
        self.history.append(record)
        self.save_history()

    def get_max_streak(self) -> int:
        return max((record.get("streak", 0) for record in self.history), default=0)


# --- Основной класс игры ---
class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode(
            (consts.GUIConsts.WIDTH, consts.GUIConsts.HEIGHT),
        )
        pygame.display.set_caption("Тест на запоминание")
        self.font = pygame.font.Font('../static/comic_sans_ms.ttf', 18)
        self.running = True
        self.exit_button = None
        self.stats = StatsManager(consts.FileConsts.HISTORY_FILE)
        self.ui_manager = pygame_gui.UIManager(
            (consts.GUIConsts.WIDTH, consts.GUIConsts.HEIGHT), consts.FileConsts.THEME_FILE
        )
        self.background = pygame.Surface((consts.GUIConsts.WIDTH, consts.GUIConsts.HEIGHT))
        self.background.fill(consts.GUIConsts.BACKGROUND)
        self.screen.blit(self.background, (0, 0))

    def run(self) -> None:
        self.welcome_screen()

    def welcome_screen(self) -> None:
        clock = pygame.time.Clock()

        new_game_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (consts.GUIConsts.WIDTH // 2 - 100, consts.GUIConsts.HEIGHT // 2 - 50), (200, 50)
            ),
            text="Новая игра",
            manager=self.ui_manager,
        )

        stats_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (consts.GUIConsts.WIDTH // 2 - 100, consts.GUIConsts.HEIGHT // 2 + 20), (200, 50)
            ),
            text="Статистика",
            manager=self.ui_manager,
        )

        while self.running:
            time_delta = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.ui_manager.process_events(event)

                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == new_game_button:
                            self.__clear_screen([new_game_button, stats_button])
                            self.select_grid_size()
                            return
                        elif event.ui_element == stats_button:
                            self.show_statistics()
            self.ui_manager.update(time_delta)
            self.screen.fill(consts.GUIConsts.BACKGROUND)
            self.ui_manager.draw_ui(self.screen)
            pygame.display.flip()

    def select_grid_size(self) -> None:
        size_x = 3
        size_y = 3
        selecting = True

        self._create_exit_button()
        slider_width = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(
                (consts.GUIConsts.WIDTH // 2 - 150, consts.GUIConsts.HEIGHT // 2 - 100), (300, 30)
            ),
            start_value=3,
            value_range=(2, 10),
            manager=self.ui_manager,
        )
        slider_height = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(
                (consts.GUIConsts.WIDTH // 2 - 150, consts.GUIConsts.HEIGHT // 2 - 30), (300, 30)
            ),
            start_value=3,
            value_range=(2, 10),
            manager=self.ui_manager,
        )

        label_width = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                (consts.GUIConsts.WIDTH // 2 - 150, consts.GUIConsts.HEIGHT // 2 - 130), (300, 25)
            ),
            text="Ширина поля: 3",
            manager=self.ui_manager,
        )
        label_height = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                (consts.GUIConsts.WIDTH // 2 - 150, consts.GUIConsts.HEIGHT // 2 - 60), (300, 25)
            ),
            text="Высота поля: 3",
            manager=self.ui_manager,
        )

        start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (consts.GUIConsts.WIDTH // 2 - 100, consts.GUIConsts.HEIGHT // 2 + 50), (200, 50)
            ),
            text="Начать",
            manager=self.ui_manager,
        )

        clock = pygame.time.Clock()
        while selecting:
            time_delta = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    selecting = False
                    self.running = False
                self.ui_manager.process_events(event)
                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                        if event.ui_element == slider_width:
                            label_width.set_text(
                                f"Ширина поля: {int(slider_width.get_current_value())}"
                            )
                        elif event.ui_element == slider_height:
                            label_height.set_text(
                                f"Высота поля: {int(slider_height.get_current_value())}"
                            )
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == start_button:
                            size_x = int(slider_width.get_current_value())
                            size_y = int(slider_height.get_current_value())
                            selecting = False
                        if event.ui_element == self.exit_button:
                            level_running = False
                            self.__clear_screen([self.exit_button, slider_width,slider_height,label_width,label_height,start_button])
                            self.welcome_screen()
                            return

            self.ui_manager.update(time_delta)
            self.screen.fill(consts.GUIConsts.BACKGROUND)
            self.ui_manager.draw_ui(self.screen)
            pygame.display.flip()

        if self.running:
            self.__clear_screen(
                [slider_width, slider_height, label_width, label_height, start_button, self.exit_button]
            )
            self.start_game(size_x, size_y, num_circles=1, wins=0, errors=0, streak=0)

    def show_statistics(self) -> None:
        # Используем pygame_menu для красивого вывода статистики
        custom_theme = pygame_menu.themes.Theme(
            background_color=consts.GUIConsts.BACKGROUND,
            title_background_color=consts.GUIConsts.BACKGROUND,
            widget_font=self.font,
            widget_font_color=consts.GUIConsts.WHITE,
            widget_background_color=consts.GUIConsts.WIDGET_BACKGROUND,
            widget_selection_effect=pygame_menu.widgets.HighlightSelection(),
            widget_padding=10,
        )

        menu = pygame_menu.Menu(
            title="",
            width=consts.GUIConsts.WIDTH,
            height=consts.GUIConsts.HEIGHT,
            theme=custom_theme,
            onclose=pygame_menu.events.BACK,
        )

        history = self.stats.history
        if not history:
            menu.add.label("Нет данных", font_size=30)
        else:
            for i, entry in enumerate(history):
                # Собираем текст с данными из статистики
                text = (
                    f"Игра {i + 1} | {entry['datetime']} | Результат: {entry['result']}\n"
                    f"Размер поля: {entry['grid_size']} | Кружков: {entry['num_circles']}\n"
                    f"Счет: {entry['score']} | Серия: {entry['streak']}\n"
                    f"Выбранные клетки: {entry['selected']}"
                )
                # Добавляем фрейм для каждой записи с небольшим отступом
                game_frame = menu.add.frame_v(
                    width=consts.GUIConsts.WIDTH - 80,
                    height=140,
                    background_color=consts.GUIConsts.WIDGET_BACKGROUND,
                    padding=10,
                )
                game_frame._relax = True
                game_frame.pack(
                    menu.add.label(text, font_size=20, wordwrap=True),
                    align=pygame_menu.locals.ALIGN_LEFT,
                )

        menu.mainloop(self.screen)

    def start_game(
        self,
        size_x: int,
        size_y: int,
        num_circles: int,
        wins: int,
        errors: int,
        streak: int,
    ) -> None:
        clock = pygame.time.Clock()
        time_delta = clock.tick(60) / 1000.0
        cell_width = consts.GUIConsts.WIDTH / size_x
        cell_height = consts.GUIConsts.HEIGHT / size_y
        circle_radius = int(min(cell_width, cell_height) / 3)

        possible_positions = [(x, y) for x in range(size_x) for y in range(size_y)]
        circles = random.sample(possible_positions, num_circles)
        selected_positions = []

        self.screen.fill(consts.GUIConsts.BACKGROUND)
        for x in range(size_x):
            for y in range(size_y):
                rect = pygame.Rect(
                    x * cell_width,
                    y * cell_height,
                    cell_width,
                    cell_height,
                )
                pygame.draw.rect(self.screen, consts.GUIConsts.GRID_COLOR, rect, 1)
        for cx, cy in circles:
            pygame.draw.circle(
                self.screen,
                consts.GUIConsts.BLUE,
                (
                    int(cx * cell_width + cell_width / 2),
                    int(cy * cell_height + cell_height / 2),
                ),
                circle_radius,
            )
        pygame.display.flip()
        pygame.time.delay(800)

        score_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((consts.GUIConsts.WIDTH - 840, 0), (200, 50)),
            text=f"Выиграно: {wins}",
            manager=self.ui_manager,
        )
        record_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((consts.GUIConsts.WIDTH - 850, 35), (200, 50)),
            text=f"Рекорд: {self.stats.get_max_streak()}",
            manager=self.ui_manager,
        )
        self._create_exit_button()

        level_running = True
        while level_running:
            self.screen.fill(consts.GUIConsts.BACKGROUND)
            for x in range(size_x):
                for y in range(size_y):
                    pygame.draw.rect(
                        self.screen,
                        consts.GUIConsts.GRID_COLOR,
                        (
                            x * cell_width,
                            y * cell_height,
                            cell_width,
                            cell_height,
                        ),
                        1,
                    )
            for sx, sy in selected_positions:
                color = consts.GUIConsts.BLUE if (sx, sy) in circles else consts.GUIConsts.RED
                pygame.draw.circle(
                    self.screen,
                    color,
                    (
                        int(sx * cell_width + cell_width / 2),
                        int(sy * cell_height + cell_height / 2),
                    ),
                    circle_radius,
                )

            self.ui_manager.update(time_delta)
            self.ui_manager.draw_ui(self.screen)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    level_running = False
                    self.running = False
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.exit_button.get_abs_rect().collidepoint(event.pos):
                        level_running = False
                        self.__clear_screen([score_label, record_label, self.exit_button])
                        self.screen.fill(consts.GUIConsts.BACKGROUND)
                        self.ui_manager.update(time_delta)
                        self.ui_manager.draw_ui(self.screen)
                        pygame.display.flip()
                        self.welcome_screen()
                        return
                    x = int(event.pos[0] // cell_width)
                    y = int(event.pos[1] // cell_height)
                    if (x, y) not in selected_positions:
                        selected_positions.append((x, y))
                    color = consts.GUIConsts.BLUE if (x, y) in circles else consts.GUIConsts.RED
                    pygame.draw.circle(
                        self.screen,
                        color,
                        (
                            int(x * cell_width + cell_width / 2),
                            int(y * cell_height + cell_height / 2),
                        ),
                        circle_radius,
                    )
                    pygame.display.flip()

                    if color == consts.GUIConsts.RED:
                        streak = 0
                        pygame.time.delay(800)
                        errors += 1
                        if errors >= 2:
                            num_circles = max(1, num_circles - 1)
                        self.stats.record(
                            size_x, size_y, num_circles, circles, selected_positions, wins, streak, "loss"
                        )
                        self.__clear_screen([score_label, record_label, self.exit_button])
                        self.start_game(size_x, size_y, num_circles, wins, errors, streak)
                        return

                    if set(selected_positions) == set(circles):
                        streak += 1
                        pygame.time.delay(800)
                        self.stats.record(size_x, size_y, num_circles, circles, selected_positions, wins, streak, "win")
                        wins += 1
                        num_circles += 1
                        errors = 0
                        self.stats.history = self.stats.load_history()  # Обновляем историю
                        self.__clear_screen([score_label, record_label, self.exit_button])
                        self.start_game(size_x, size_y, num_circles, wins, errors, streak)
                        return

    def _create_exit_button(self) -> pygame_gui.elements.UIButton:
        """Создаёт и возвращает кнопку выхода."""
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((consts.GUIConsts.WIDTH - 50, 5), (45, 45)),
            text="X",
            manager=self.ui_manager,
        )

    @staticmethod
    def __clear_screen(elements: list) -> None:
        [element.kill() for element in elements]


if __name__ == "__main__":
    Game().run()
