import random
import pygame
import pygame_gui
import pygame_menu
from src import statistic, consts

pygame.init()


# --- Основной класс игры ---
class Game:
    def __init__(self) -> None:
        """
        Инициализация игры, создание экрана, менеджера UI и статистики.
        """
        self.screen = pygame.display.set_mode(
            (consts.GUIConsts.WIDTH, consts.GUIConsts.HEIGHT),
        )
        pygame.display.set_caption("Тест на запоминание")
        self.font = pygame.font.Font(consts.FileConsts.FONT_FILE, 18)
        self.running = True
        self.exit_button = None
        self.stats = statistic.StatsManager(consts.FileConsts.HISTORY_FILE)
        self.ui_manager = pygame_gui.UIManager(
            (consts.GUIConsts.WIDTH, consts.GUIConsts.HEIGHT), consts.FileConsts.THEME_FILE
        )
        self.background = pygame.Surface((consts.GUIConsts.WIDTH, consts.GUIConsts.HEIGHT))
        self.background.fill(consts.GUIConsts.BACKGROUND)
        self.screen.blit(self.background, (0, 0))

    def run(self) -> None:
        """
        Запуск игры, отображение начального экрана.
        """
        self.welcome_screen()

    def welcome_screen(self) -> None:
        """
        Отображение приветственного экрана с кнопками 'Новая игра' и 'Статистика'.
        """
        clock = pygame.time.Clock()

        # Кнопки для новой игры и статистики
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

        # Главный цикл ожидания событий
        while self.running:
            time_delta = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.ui_manager.process_events(event)

                # Обработка нажатий на кнопки
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
        """
        Экран выбора размера поля для игры.
        """
        size_x = 3
        size_y = 3
        selecting = True

        # Создание кнопки выхода
        self._create_exit_button()

        # Ползунки для выбора ширины и высоты поля
        slider_width = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(
                (consts.GUIConsts.WIDTH // 2 - 125, consts.GUIConsts.HEIGHT // 2 - 90), (260, 33)
            ),
            start_value=3,
            value_range=(2, 10),
            manager=self.ui_manager,
        )
        slider_height = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(
                (consts.GUIConsts.WIDTH // 2 - 125, consts.GUIConsts.HEIGHT // 2), (260, 33)
            ),
            start_value=3,
            value_range=(2, 10),
            manager=self.ui_manager,
        )

        # Лейблы для отображения текущего значения ползунков
        label_width = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                (consts.GUIConsts.WIDTH // 2 - 150, consts.GUIConsts.HEIGHT // 2 - 130), (300, 25)
            ),
            text="Ширина поля: 3",
            manager=self.ui_manager,
        )
        label_height = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                (consts.GUIConsts.WIDTH // 2 - 150, consts.GUIConsts.HEIGHT // 2 - 40), (300, 25)
            ),
            text="Высота поля: 3",
            manager=self.ui_manager,
        )

        # Кнопка для начала игры
        start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (consts.GUIConsts.WIDTH // 2 - 100, consts.GUIConsts.HEIGHT // 2 + 70), (200, 50)
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
                            self.__clear_screen([self.exit_button, slider_width, slider_height, label_width, label_height, start_button])
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
        """
        Отображение статистики игры через pygame_menu.
        """
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
                text = (
                    f"Игра {i + 1} | {entry['datetime']} | Результат: {entry['result']}\n"
                    f"Размер поля: {entry['grid_size']} | Кружков: {entry['num_circles']}\n"
                    f"Счет: {entry['score']} | Серия: {entry['streak']}\n"
                    f"Выбранные клетки: {entry['selected']}"
                )
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
        """
        Основной игровой процесс. Отображение сетки, появление кружков, обработка выбора.
        """
        clock = pygame.time.Clock()
        time_delta = clock.tick(60) / 1000.0
        cell_width = consts.GUIConsts.WIDTH / size_x
        cell_height = consts.GUIConsts.HEIGHT / size_y
        circle_radius = int(min(cell_width, cell_height) / 3)

        # Генерация случайных позиций для кружков
        possible_positions = [(x, y) for x in range(size_x) for y in range(size_y)]
        circles = random.sample(possible_positions, num_circles)
        selected_positions = []

        self.screen.fill(consts.GUIConsts.BACKGROUND)
        # Отображение сетки
        for x in range(size_x):
            for y in range(size_y):
                rect = pygame.Rect(
                    x * cell_width,
                    y * cell_height,
                    cell_width,
                    cell_height,
                )
                pygame.draw.rect(self.screen, consts.GUIConsts.GRID_COLOR, rect, 1)
        # Отображение кружков
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
            text=f"Рекорд: {self.stats.get_record()}",
            manager=self.ui_manager,
        )
        self._create_exit_button()

        level_running = True
        while level_running:
            self.screen.fill(consts.GUIConsts.BACKGROUND)
            # Отображение сетки
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
            # Отображение выбранных позиций
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

                    # Обработка ошибок и выигрыша
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
        """
        Создание кнопки для выхода из игры.
        """
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((consts.GUIConsts.WIDTH - 50, 5), (40, 40)),
            text="X",
            manager=self.ui_manager,
        )

    @staticmethod
    def __clear_screen(elements: list) -> None:
        """
        Очистка списка элементов на экране.
        """
        [element.kill() for element in elements]


if __name__ == "__main__":
    Game().run()
