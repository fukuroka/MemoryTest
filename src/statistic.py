import datetime
import json

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