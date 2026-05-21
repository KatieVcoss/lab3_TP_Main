import tkinter as tk
from tkinter import ttk, messagebox
from models import PopulationAnalyzer

class PopulationApp: # Окно приложения для вар. 5

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Анализ населения РФ (2011–2025)")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.analyzer = PopulationAnalyzer()

        self._build_ui()

    def _build_ui(self): # Строит интерфейс
        # --- Заголовок ---
        title = tk.Label(self.root, text="Анализ численности населения РФ",
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # --- Основной фрейм ---
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- Таблица ---
        columns = ("year", "population")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=10)
        self.tree.heading("year", text="Год")
        self.tree.heading("population", text="Население (млн чел.)")
        self.tree.column("year", width=150, anchor="center")
        self.tree.column("population", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._fill_table()

        # --- Фрейм для статистики ---
        stats_frame = tk.LabelFrame(self.root, text="Статистика", font=("Arial", 12, "bold"))
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        self.stats_text = tk.Text(stats_frame, height=5, wrap=tk.WORD, state=tk.DISABLED,
                                  font=("Consolas", 10))
        self.stats_text.pack(fill=tk.BOTH, padx=5, pady=5)

        self._update_stats()

        # --- Кнопки ---
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Обновить статистику",
                  command=self._update_stats, width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="О программе",
                  command=self._show_about, width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Выход",
                  command=self.root.quit, width=20).pack(side=tk.LEFT, padx=5)

        # --- Фрейм для заданий ---
        tasks_frame = tk.LabelFrame(self.root, text="👥 Задания команды",
                                    font=("Arial", 12, "bold"))
        tasks_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(tasks_frame, text="Задание 1: График населения",
                  command=self._task_placeholder, width=30).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(tasks_frame, text="Задание 2: Прогноз на 2026",
                  command=self._task_placeholder, width=30).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(tasks_frame, text="Задание 3: Сравнение регионов",
                  command=self._task_placeholder, width=30).pack(side=tk.LEFT, padx=5, pady=5)

    def _fill_table(self): #Заполняет таблицу данными.
        for entry in self.analyzer.data:
            self.tree.insert("", tk.END, values=(entry["year"], entry["population"]))

    def _update_stats(self):
        #Обновляет блок статистики
        min_year, min_pop, max_year, max_pop = self.analyzer.get_min_max_population()
        avg = self.analyzer.get_average_population()
        trend = self.analyzer.get_trend()

        text = (
            f"Минимум: {min_year} г. — {min_pop} млн чел.\n"
            f"Максимум: {max_year} г. — {max_pop} млн чел.\n"
            f"Среднее: {avg} млн чел.\n"
            f"Тенденция: {trend}"
        )

        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, text)
        self.stats_text.config(state=tk.DISABLED)

    def _show_about(self):
        #Показывает окно 'О программе'
        messagebox.showinfo(
            "О программе",
            "Анализ численности населения РФ\n"
            "Период: 2011–2025 гг.\n"
            "Разработано в рамках курсового проекта\n"
            "© 2026"
        )

    def _task_placeholder(self): #Заглушка для заданий
        messagebox.showinfo("Задание", "Функция будет реализована на следующем этапе!")

def main():
    root = tk.Tk()
    app = PopulationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
