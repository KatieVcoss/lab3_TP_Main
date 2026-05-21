from storage import load_population_data

class PopulationAnalyzer: # Анализирует данные о численности населения

    def __init__(self):
        self.data = load_population_data()

    def get_population_by_year(self, year: int) -> float | None:
        # Возвращает население для указанного года
        for entry in self.data:
            if entry["year"] == year:
                return entry["population"]
        return None

    def get_all_years(self) -> list[int]:
        # Возвращает список всех годов
        return [entry["year"] for entry in self.data]

    def get_all_populations(self) -> list[float]:
        # Возвращает список всех значений населения
        return [entry["population"] for entry in self.data]

    def get_min_max_population(self) -> tuple:
        # Возвращает (год_минимума, мин_население, год_максимума, макс_население)
        min_entry = min(self.data, key=lambda x: x["population"])
        max_entry = max(self.data, key=lambda x: x["population"])
        return min_entry["year"], min_entry["population"], max_entry["year"], max_entry["population"]

    def get_average_population(self) -> float:
        # Возвращает среднюю численность населения за весь период
        populations = self.get_all_populations()
        return round(sum(populations) / len(populations), 2)

    def get_trend(self) -> str:
        # Определяет тенденцию: рост, спад или стабильность
        first = self.data[0]["population"]
        last = self.data[-1]["population"]
        if last > first:
            return "Рост"
        elif last < first:
            return "Спад"
        else:
            return "➡Стабильно"
