import datetime
import json

# --- Класс для работы со статистикой ---
class StatsManager:
    """
    Класс для работы с историей статистики игры. Загружает, сохраняет и записывает статистику.
    """

    def __init__(self, history_file: str) -> None:
        """
        Инициализирует объект StatsManager.

        :param history_file: Путь к файлу, в котором хранится история игры.
        """
        self.history_file = history_file
        # Загружаем историю, если файл существует.
        self.history = self.load_history()

    def load_history(self) -> list[dict]:
        """
        Загружает историю из файла. Если файл не найден, возвращает пустой список.

        :return: Список записей истории игры.
        """
        try:
            with open(self.history_file) as f:
                return json.load(f)
        except FileNotFoundError:
            # Если файл не найден, возвращаем пустой список
            return []

    def save_history(self) -> None:
        """
        Сохраняет текущую историю в файл.

        :return: None
        """
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
        """
        Добавляет новую запись в историю игры.

        :param size_x: Ширина поля.
        :param size_y: Высота поля.
        :param num_circles: Количество кружков на поле.
        :param circles: Список позиций кружков на поле.
        :param selected_positions: Список позиций выбранных клеток.
        :param wins: Количество побед.
        :param streak: Текущая серия побед.
        :param level_result: Результат игры ("win" или "loss").
        """
        record = {
            "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Текущая дата и время
            "grid_size": f"{size_x}x{size_y}",  # Размер поля
            "num_circles": num_circles,  # Количество кружков
            "circles": circles,  # Позиции кружков
            "selected": selected_positions,  # Позиции выбранных клеток
            "score": wins,  # Количество побед
            "streak": streak,  # Серия побед
            "result": level_result,  # Результат игры
        }
        # Добавляем запись в историю
        self.history.append(record)
        # Сохраняем обновленную историю
        self.save_history()

    def get_record(self) -> int:
        """
        Возвращает максимальную серию побед из истории.

        :return: Максимальная серия побед.
        """
        return max((record.get("streak", 0) for record in self.history), default=0)
