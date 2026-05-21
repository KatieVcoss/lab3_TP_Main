# teammate_tasks.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from models import PopulationAnalyzer  # Берем данные из models.py


class Task1Graph: # Задание 1: График населения по годам

    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Динамика населения РФ")
        self.window.geometry("800x600")
        self.analyzer = PopulationAnalyzer()
        self._build()

    def _build(self):
        years = self.analyzer.get_all_years()
        pops = self.analyzer.get_all_populations()

        # Таблица
        frame = tk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("Год", "Население (млн)", "Прирост (млн)", "Прирост (%)")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Заполняем таблицу
        max_growth = -float('inf')
        max_decline = float('inf')
        max_growth_year = ""
        max_decline_year = ""

        for i, (year, pop) in enumerate(zip(years, pops)):
            if i == 0:
                growth = 0
                percent = 0
            else:
                growth = round(pop - pops[i - 1], 2)
                percent = round((pop / pops[i - 1] - 1) * 100, 2)

                if growth > max_growth:
                    max_growth = growth
                    max_growth_year = year
                if growth < max_decline:
                    max_decline = growth
                    max_decline_year = year

            tree.insert("", tk.END, values=(year, pop, growth, f"{percent}%"))

        # Статистика
        stats_frame = tk.LabelFrame(self.window, text="Статистика", padx=10, pady=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        stats_text = (
            f"Максимальный прирост: {max_growth} млн чел. ({max_growth_year} г.)\n"
            f"Максимальная убыль: {max_decline} млн чел. ({max_decline_year} г.)\n"
        )
        tk.Label(stats_frame, text=stats_text, font=("Arial", 10),
                 justify=tk.LEFT).pack()

        # Кнопка экспорта
        tk.Button(self.window, text="💾 Экспорт в CSV",
                  command=self._export_csv, width=20).pack(pady=5)


class Task2Forecast: #Задание 2: Прогноз методом скользящей средней

    def __init__(self, n_years: int):
        self.window = tk.Toplevel()
        self.window.title(f"🔮 Прогноз на {n_years} лет")
        self.window.geometry("800x600")
        self.analyzer = PopulationAnalyzer()
        self.n = n_years
        self._build()

    def _build(self):
        years = self.analyzer.get_all_years()
        pops = self.analyzer.get_all_populations()

        # Скользящая средняя
        n = min(self.n, len(pops))
        moving_avg = []
        for i in range(len(pops) - n + 1):
            avg = sum(pops[i:i + n]) / n
            moving_avg.append(avg)

        # Прогноз
        last_avg = moving_avg[-1] if moving_avg else pops[-1]
        forecast = last_avg

        # Рисуешь на Canvas: исходные данные + прогноз
        # ...

        # Вывод результатов
        text = scrolledtext.ScrolledText(self.window, font=("Consolas", 11))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        info = (
            f"📊 Прогноз методом скользящей средней\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Период скольжения (n): {self.n} лет\n"
            f"Последняя скользящая средняя: {last_avg:.2f} млн чел.\n"
            f"Прогноз на следующий год: {forecast:.2f} млн чел.\n"
        )
        text.insert(tk.END, info)
        text.config(state=tk.DISABLED)


class Task3Report: #Задание 3: Таблица данных + прирост/убыль.

    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Отчёт по населению РФ")
        self.window.geometry("900x600")
        self.analyzer = PopulationAnalyzer()
        self._build()

    def _build(self):
        years = self.analyzer.get_all_years()
        pops = self.analyzer.get_all_populations()

        # Таблица
        frame = tk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("Год", "Население (млн)", "Прирост (млн)", "Прирост (%)")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Заполняем таблицу
        max_growth = -float('inf')
        max_decline = float('inf')
        max_growth_year = ""
        max_decline_year = ""

        for i, (year, pop) in enumerate(zip(years, pops)):
            if i == 0:
                growth = 0
                percent = 0
            else:
                growth = round(pop - pops[i - 1], 2)
                percent = round((pop / pops[i - 1] - 1) * 100, 2)

                if growth > max_growth:
                    max_growth = growth
                    max_growth_year = year
                if growth < max_decline:
                    max_decline = growth
                    max_decline_year = year

            tree.insert("", tk.END, values=(year, pop, growth, f"{percent}%"))

        # Статистика
        stats_frame = tk.LabelFrame(self.window, text="📊 Статистика", padx=10, pady=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        stats_text = (
            f"Максимальный прирост: {max_growth} млн чел. ({max_growth_year} г.)\n"
            f"Максимальная убыль: {max_decline} млн чел. ({max_decline_year} г.)\n"
        )
        tk.Label(stats_frame, text=stats_text, font=("Arial", 10),
                 justify=tk.LEFT).pack()

        # Кнопка экспорта
        tk.Button(self.window, text="💾 Экспорт в CSV",
                  command=self._export_csv, width=20).pack(pady=5)

    def _export_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            years = self.analyzer.get_all_years()
            pops = self.analyzer.get_all_populations()

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("Год;Население (млн)\n")
                for year, pop in zip(years, pops):
                    f.write(f"{year};{pop}\n")

            messagebox.showinfo("Экспорт", f"Данные сохранены в {file_path}")
