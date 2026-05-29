import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from models import PopulationAnalyzer

class PopulationGraphWindow:
    #Окно с таблицей и графиком населения по годам (Задание 1)
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Динамика населения РФ — график")
        self.window.geometry("1000x700")
        self.analyzer = PopulationAnalyzer()
        self._build_ui()

    def _build_ui(self):
        # Таблица
        table_frame = ttk.LabelFrame(self.window, text="Данные по годам")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10,5))

        columns = ("Год", "Население (млн)", "Прирост (млн)", "Прирост (%)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Заполнение таблицы и расчёт макс. прироста/убыли
        years = self.analyzer.get_all_years()
        pops = self.analyzer.get_all_populations()
        max_growth = -float('inf')
        max_decline = float('inf')
        max_growth_year = max_decline_year = None

        for i, (year, pop) in enumerate(zip(years, pops)):
            if i == 0:
                growth = 0.0
                percent = 0.0
            else:
                growth = round(pop - pops[i-1], 2)
                percent = round((pop / pops[i-1] - 1) * 100, 2)
                if growth > max_growth:
                    max_growth = growth
                    max_growth_year = year
                if growth < max_decline:
                    max_decline = growth
                    max_decline_year = year
            self.tree.insert("", tk.END, values=(year, pop, growth, f"{percent}%"))

        # Статистика под таблицей
        stats_frame = ttk.Frame(self.window)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        stats_text = (f"Макс. прирост: {max_growth} млн чел. ({max_growth_year} г.)   "
                      f"Макс. убыль: {max_decline} млн чел. ({max_decline_year} г.)")
        ttk.Label(stats_frame, text=stats_text, font=("Arial", 10)).pack()

        # График
        chart_frame = ttk.LabelFrame(self.window, text="График численности населения")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.plot(years, pops, marker='o', linestyle='-', color='blue', label="Население")
        self.ax.set_title("Численность населения России", fontsize=12)
        self.ax.set_xlabel("Год")
        self.ax.set_ylabel("Население (млн чел.)")
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, chart_frame)
        toolbar.update()

        # Кнопка экспорта
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text="💾 Экспорт графика в PNG", command=self._export_plot).pack()

    def _export_plot(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")]
        )
        if file_path:
            self.figure.savefig(file_path, dpi=150)
            messagebox.showinfo("Экспорт", f"График сохранён:\n{file_path}")


class PopulationForecastWindow:
    #Окно прогноза методом скользящей средней (Задание 2)
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Toplevel()
        self.window.title("Прогноз населения методом скользящей средней")
        self.window.geometry("1000x750")
        self.analyzer = PopulationAnalyzer()
        self.years = self.analyzer.get_all_years()
        self.pops = self.analyzer.get_all_populations()
        self._build_ui()

    def _build_ui(self):
        # Панель параметров
        param_frame = ttk.LabelFrame(self.window, text="Параметры прогноза")
        param_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(param_frame, text="Окно скользящей средней (n):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.window_size = tk.IntVar(value=3)
        spin_window = ttk.Spinbox(param_frame, from_=2, to=10, textvariable=self.window_size, width=5)
        spin_window.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(param_frame, text="Прогноз на N лет:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.forecast_years = tk.IntVar(value=5)
        spin_forecast = ttk.Spinbox(param_frame, from_=1, to=20, textvariable=self.forecast_years, width=5)
        spin_forecast.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        self.calc_btn = ttk.Button(param_frame, text="Рассчитать прогноз", command=self._calculate_forecast)
        self.calc_btn.grid(row=0, column=4, padx=15, pady=5)

        self.export_btn = ttk.Button(param_frame, text="Экспорт графика", command=self._export_plot, state=tk.DISABLED)
        self.export_btn.grid(row=0, column=5, padx=5, pady=5)

        # Таблица прогноза
        table_frame = ttk.LabelFrame(self.window, text="Прогнозные значения")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.forecast_tree = ttk.Treeview(table_frame, columns=("Год", "Население (млн)"), show="headings", height=8)
        self.forecast_tree.heading("Год", text="Год")
        self.forecast_tree.heading("Население (млн)", text="Население (млн)")
        self.forecast_tree.column("Год", width=100, anchor=tk.CENTER)
        self.forecast_tree.column("Население (млн)", width=150, anchor=tk.CENTER)
        self.forecast_tree.pack(fill=tk.BOTH, expand=True)

        # График
        chart_frame = ttk.LabelFrame(self.window, text="График: история + прогноз")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, chart_frame)
        self.toolbar.update()

        # Покаp историb сразу
        self._draw_history()
        self._forecast_result = None  # для хранения прогнозного ряда

    def _draw_history(self):
        self.ax.clear()
        self.ax.plot(self.years, self.pops, marker='o', linestyle='-', color='blue', label="Фактические данные")
        self.ax.set_title("Численность населения России (история)", fontsize=12)
        self.ax.set_xlabel("Год")
        self.ax.set_ylabel("Население (млн чел.)")
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.legend()
        self.canvas.draw()

    def _calculate_forecast(self):
        n = self.window_size.get()
        n_years = self.forecast_years.get()

        if n <= 0 or n_years <= 0:
            messagebox.showerror("Ошибка", "Размер окна и количество лет прогноза должны быть положительными.")
            return

        if n > len(self.pops):
            messagebox.showerror("Ошибка", f"Размер окна не может быть больше {len(self.pops)} (количество лет данных).")
            return

        # Прогноз методом скользящей средней
        values = self.pops.copy()  # исторические значения
        last_year = self.years[-1]
        forecast_values = []  # список прогнозных значений
        forecast_years = []

        for i in range(1, n_years + 1):
            # средняя за последние n значений
            avg = sum(values[-n:]) / n
            forecast_values.append(avg)
            forecast_years.append(last_year + i)
            values.append(avg)   # добавляем прогноз в ряд для следующего шага

        # Заполнtybt таблицs
        for row in self.forecast_tree.get_children():
            self.forecast_tree.delete(row)
        for y, val in zip(forecast_years, forecast_values):
            self.forecast_tree.insert("", tk.END, values=(y, round(val, 2)))

        # Отображtybt на графике
        self.ax.clear()
        self.ax.plot(self.years, self.pops, marker='o', linestyle='-', color='blue', label="Фактические данные")
        self.ax.plot(forecast_years, forecast_values, marker='s', linestyle='--', color='orange', label="Прогноз")
        self.ax.set_title(f"Прогноз на {n_years} лет (окно = {n})", fontsize=12)
        self.ax.set_xlabel("Год")
        self.ax.set_ylabel("Население (млн чел.)")
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.legend()
        self.canvas.draw()

        # Сохраняtybt для возможного экспорта
        self._forecast_result = (forecast_years, forecast_values)
        self.export_btn.config(state=tk.NORMAL)

    def _export_plot(self):
        if self._forecast_result is None:
            messagebox.showwarning("Нет прогноза", "Сначала выполните расчёт.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG image", "*.png")])
        if file_path:
            self.figure.savefig(file_path, dpi=150)
            messagebox.showinfo("Экспорт", f"График сохранён:\n{file_path}")


class Task3Report:
    #Отчёт с таблицей и максимальным приростом/убылью
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Отчёт по населению РФ")
        self.window.geometry("800x500")
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

        max_growth = -float('inf')
        max_decline = float('inf')
        max_growth_year = max_decline_year = None

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
        stats_text = (f"Максимальный прирост: {max_growth} млн чел. ({max_growth_year} г.)\n"
                      f"Максимальная убыль: {max_decline} млн чел. ({max_decline_year} г.)")
        tk.Label(stats_frame, text=stats_text, font=("Arial", 10), justify=tk.LEFT).pack()

        tk.Button(self.window, text="💾 Экспорт в CSV", command=self._export_csv, width=20).pack(pady=5)

    def _export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            years = self.analyzer.get_all_years()
            pops = self.analyzer.get_all_populations()
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("Год;Население (млн)\n")
                for year, pop in zip(years, pops):
                    f.write(f"{year};{pop}\n")
            messagebox.showinfo("Экспорт", f"Данные сохранены в {file_path}")