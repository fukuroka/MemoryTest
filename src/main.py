import datetime
import json
import random
from typing import List, Tuple

import pygame
import pygame_gui

import consts

pygame.init()


# --- Класс для работы со статистикой ---
class StatsManager:
    def __init__(self, history_file: str = consts.FileConsts.HISTORY_FILE) -> None:
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

    def get_recent_history(self, minutes: int = 10) -> list[dict]:
        # Фильтрация по времени: последние 'minutes' минут
        now = datetime.datetime.now()
        cutoff_time = now - datetime.timedelta(minutes=minutes)
        recent_history = [
            entry
            for entry in self.history
            if datetime.datetime.strptime(entry["datetime"], "%Y-%m-%d %H:%M:%S") > cutoff_time
        ]
        return recent_history


# --- Основной класс игры ---
class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode(
            (consts.GUIConsts.WIDTH, consts.GUIConsts.HEIGHT),
        )
        pygame.display.set_caption("Тест на запоминание")
        self.font = pygame.font.Font(None, 36)
        self.running = True
        self.stats = StatsManager()
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
                            self.__clear_screen([stats_button])
                            self.show_statistics()

            self.ui_manager.update(time_delta)
            self.screen.fill(consts.GUIConsts.BACKGROUND)
            self.ui_manager.draw_ui(self.screen)
            pygame.display.flip()

    def select_grid_size(self) -> None:
        size_x = 3
        size_y = 3
        selecting = True

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

            self.ui_manager.update(time_delta)
            self.screen.fill(consts.GUIConsts.BACKGROUND)
            self.ui_manager.draw_ui(self.screen)
            pygame.display.flip()

        if self.running:
            self.__clear_screen(
                [   slider_width,
                    slider_height,
                    label_width,
                    label_height,
                    start_button,
                ]
            )
            self.start_game(size_x, size_y, num_circles=1, wins=0, errors=0, streak=0)

    def show_statistics(self) -> None:
        # Получаем статистику за последние 10 минут
        recent_entries = self.stats.get_recent_history(10)

        if not recent_entries:
            self.screen.fill(consts.GUIConsts.BACKGROUND)
            no_data_text = self.font.render("Нет данных за последние 10 минут.", True, consts.GUIConsts.BLACK)
            self.screen.blit(no_data_text, (consts.GUIConsts.WIDTH // 2 - 150, consts.GUIConsts.HEIGHT // 2))
            pygame.display.flip()
            pygame.time.delay(2000)
            self.welcome_screen()
            return

        self.screen.fill(consts.GUIConsts.BACKGROUND)

        table_headers = ["Дата", "Размер", "Кружков", "Результат", "Рекорд"]
        column_widths = [200, 100, 100, 100, 80]
        font = pygame.font.Font(None, 24)

        # Рисуем заголовки таблицы
        y_offset = 50
        for i, header in enumerate(table_headers):
            header_text = font.render(header, True, consts.GUIConsts.BLACK)
            self.screen.blit(header_text, (50 + sum(column_widths[:i]), y_offset))

        # Рисуем линии сетки
        y_offset += 30
        for i in range(1, len(table_headers)):
            pygame.draw.line(
                self.screen,
                consts.GUIConsts.BLACK,
                (40 + sum(column_widths[:i]), 50),
                (40 + sum(column_widths[:i]), y_offset + len(recent_entries) * 30),
                1,
            )

        # Рисуем строки таблицы
        for entry in recent_entries:
            row = [
                entry["datetime"],
                entry["grid_size"],
                str(entry["num_circles"]),
                entry["result"],
                str(entry["streak"]),
            ]
            for i, cell in enumerate(row):
                cell_text = font.render(cell, True, consts.GUIConsts.BLACK)
                self.screen.blit(cell_text, (50 + sum(column_widths[:i]), y_offset))
            y_offset += 30

        # Рисуем горизонтальные линии
        pygame.draw.line(
            self.screen, consts.GUIConsts.BLACK, (50, y_offset), (50 + sum(column_widths), y_offset), 1
        )

        pygame.display.flip()
        pygame.time.delay(5000)
        self.welcome_screen()

    def start_game(
        self,
        size_x: int,
        size_y: int,
        num_circles: int,
        wins: int,
        errors: int,
        streak: int,
    ) -> None:
        # Вычисляем размеры ячейки так, чтобы сетка занимала весь экран
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

        level_running = True
        while level_running:
            self.screen.fill(consts.GUIConsts.BACKGROUND)
            # Рисуем сетку
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
            # Рисуем выбранные кружки
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

            score_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((consts.GUIConsts.WIDTH - 190, 5), (200, 50)),
                text=f"Выиграно: {wins}",
                manager=self.ui_manager,
            )
            record_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((consts.GUIConsts.WIDTH - 200, 45), (200, 50)),
                text=f"Рекорд: {self.stats.get_max_streak()}",
                manager=self.ui_manager,
            )
            self.ui_manager.update(time_delta)
            self.ui_manager.draw_ui(self.screen)
            pygame.display.flip()
            self.__clear_screen([score_label, record_label])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    level_running = False
                    self.running = False
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
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

                    # Если выбрана неправильная клетка, уровень провален
                    if color == consts.GUIConsts.RED:
                        streak = 0
                        pygame.time.delay(800)
                        errors += 1
                        if errors >= 2:
                            num_circles = max(1, num_circles - 1)
                        self.stats.record(
                            size_x, size_y, num_circles, circles, selected_positions, wins, streak, "loss"
                        )
                        self.start_game(size_x, size_y, num_circles, wins, errors, streak)
                        return

                    # Если выбранные клетки совпадают с кружками, уровень пройден
                    if set(selected_positions) == set(circles):
                        streak += 1
                        pygame.time.delay(800)
                        self.stats.record(size_x, size_y, num_circles, circles, selected_positions, wins, streak, "win")
                        wins += 1
                        num_circles += 1
                        errors = 0
                        self.stats.history = self.stats.load_history()  # Обновляем историю
                        self.start_game(size_x, size_y, num_circles, wins, errors, streak)
                        return

    @staticmethod
    def __clear_screen(elements: list) -> None:
        [element.kill() for element in elements]


if __name__ == "__main__":
    Game().run()
