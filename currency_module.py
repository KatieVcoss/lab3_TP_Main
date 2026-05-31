import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
# Анализ курсов валют: вариант 2 без пандас
class CurrencyAnalyzer:
    def __init__(self):
        self.data = []  # список словарей {date: datetime, usd: float, eur: float}
        self.currency_cols = []  # названия валютных колонок
        self.dates = []  # список дат для графика
        self.currency_data = {}  # {col: [values]}

    def load_file(self, filepath):
        rows = []
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            headers = [h.lower().strip() for h in reader.fieldnames]
            if 'date' not in headers:
                raise ValueError("Файл должен содержать колонку 'date'")
            # Определить числовые колонки (первые две, кроме date)
            numeric_cols = []
            for col in headers:
                if col != 'date':
                    numeric_cols.append(col)
                    if len(numeric_cols) == 2:
                        break
            if len(numeric_cols) < 2:
                raise ValueError("Нужно минимум две колонки с курсами валют")
            self.currency_cols = numeric_cols

            for row in reader:
                new_row = {}
                for h in headers:
                    val = row[h].strip()
                    if h == 'date':
                        new_row['date'] = datetime.strptime(val, '%Y-%m-%d')
                    elif h in numeric_cols:
                        new_row[h] = float(val)
                rows.append(new_row)

        # Сортировка по дате
        rows.sort(key=lambda x: x['date'])
        self.data = rows

        # Формирование данных для графиков
        self.dates = [r['date'] for r in self.data]
        self.currency_data = {}
        for col in self.currency_cols:
            self.currency_data[col] = [r[col] for r in self.data]

        return True

    def get_table_data(self):
        return self.data

    def get_dates(self):
        return self.dates

    def get_currency_names(self):
        return self.currency_cols

    def get_currency_values(self, col):
        return self.currency_data[col]

    def daily_changes(self):
       # список изменений по дням
        changes = []
        for i in range(1, len(self.data)):
            change = {'date': self.data[i]['date']}
            for col in self.currency_cols:
                prev_val = self.data[i - 1][col]
                curr_val = self.data[i][col]
                abs_diff = curr_val - prev_val
                pct_diff = (abs_diff / prev_val) * 100 if prev_val != 0 else 0
                change[f'{col}_abs'] = abs_diff
                change[f'{col}_pct'] = pct_diff
            changes.append(change)
        return changes

    def max_increase_decrease(self):
        changes = self.daily_changes()
        result = {}
        for col in self.currency_cols:
            max_inc = None
            max_inc_date = None
            max_inc_pct = None
            min_dec = None
            min_dec_date = None
            min_dec_pct = None

            for ch in changes:
                abs_val = ch[f'{col}_abs']
                pct_val = ch[f'{col}_pct']
                if max_inc is None or abs_val > max_inc:
                    max_inc = abs_val
                    max_inc_date = ch['date']
                    max_inc_pct = pct_val
                if min_dec is None or abs_val < min_dec:
                    min_dec = abs_val
                    min_dec_date = ch['date']
                    min_dec_pct = pct_val

            result[col] = {
                'max_inc': (max_inc_date.strftime('%Y-%m-%d'), max_inc, max_inc_pct),
                'max_dec': (min_dec_date.strftime('%Y-%m-%d'), min_dec, min_dec_pct)
            }
        return result

    def moving_average_forecast(self, col, window, steps):
        """Прогноз скользящей средней на steps шагов"""
        series = self.currency_data[col].copy()
        if len(series) < window:
            raise ValueError(f"Окно {window} больше данных ({len(series)})")
        forecast = []
        data = series.copy()
        for _ in range(steps):
            avg = sum(data[-window:]) / window
            forecast.append(avg)
            data.append(avg)
        return forecast

#  Классы интерфейса
class Task1Graph:
# Задание 1: Таблица + график + статистика приростов/падений
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Курсы валют — таблица и график")
        self.window.geometry("1400x900")
        self.analyzer = CurrencyAnalyzer()
        self.fig = None
        self.canvas = None
        self._build()

    def _build(self):
        # Кнопка загрузки файла
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(btn_frame, text=" Загрузить CSV файл", command=self.load_file).pack(side=tk.LEFT, padx=5)
        self.export_btn = tk.Button(btn_frame, text=" Экспорт графика", command=self.export_plot, state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        # Таблица
        table_frame = tk.LabelFrame(self.window, text="Данные по дням")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree = ttk.Treeview(table_frame)
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # График
        graph_frame = tk.LabelFrame(self.window, text="График курсов")
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.fig, self.ax = plt.subplots(figsize=(8,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Статистика
        self.stats_text = tk.Text(self.window, height=6, state=tk.DISABLED)
        self.stats_text.pack(fill=tk.X, padx=10, pady=5)
        btn_back = tk.Button(self.window, text="← Назад", command=self.window.destroy, width=15)
        btn_back.pack(pady=10)


    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return
        try:
            self.analyzer.load_file(filepath)
            self.show_table()
            self.plot_graph()
            self.show_stats()
            self.export_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def show_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = self.analyzer.get_table_data()
        if not data:
            return
        cols = ['date'] + self.analyzer.get_currency_names()
        self.tree['columns'] = cols
        self.tree['show'] = 'headings'
        for col in cols:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=120, anchor='center')
        for row in data:
            values = [row['date'].strftime('%Y-%m-%d')] + [f"{row[col]:.4f}" for col in
                                                           self.analyzer.get_currency_names()]
            self.tree.insert('', tk.END, values=values)

    def plot_graph(self):
        self.ax.clear()
        dates = self.analyzer.get_dates()
        for col in self.analyzer.get_currency_names():
            values = self.analyzer.get_currency_values(col)
            self.ax.plot(dates, values, marker='o', label=col.upper())
        self.ax.set_xlabel('Дата')
        self.ax.set_ylabel('Курс')
        self.ax.set_title('Динамика курсов валют')
        self.ax.legend()
        self.ax.grid(True)
        self.fig.autofmt_xdate()
        self.canvas.draw()

    def show_stats(self):
        stats = self.analyzer.max_increase_decrease()
        text = "Максимальный прирост и падение за день:\n"
        for curr, data in stats.items():
            inc_date, inc_abs, inc_pct = data['max_inc']
            dec_date, dec_abs, dec_pct = data['max_dec']
            text += f"\n{curr.upper()}:\n"
            text += f"   Прирост: {inc_abs:.2f} ({inc_pct:.2f}%) — {inc_date}\n"
            text += f"   Падение: {dec_abs:.2f} ({dec_pct:.2f}%) — {dec_date}\n"
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, text)
        self.stats_text.config(state=tk.DISABLED)

    def export_plot(self):
        if not self.fig:
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")])
        if filepath:
            self.fig.savefig(filepath, dpi=150)
            messagebox.showinfo("Сохранено", f"График сохранён в {filepath}")

class Task2Forecast:
# Задание 2: Прогноз скользящей средней на N дней
    def __init__(self, window_size, steps):
        self.window = tk.Toplevel()
        self.window.title(f"Прогноз курсов валют (окно={window_size}, шагов={steps})")
        self.window.geometry("1000x600")
        self.analyzer = CurrencyAnalyzer()
        self.window_size = window_size
        self.steps = steps
        self._build()

    def _build(self):
        # Загрузка файла
        tk.Button(self.window, text=" Загрузить CSV", command=self.load_and_forecast).pack(pady=5)
        self.graph_frame = tk.LabelFrame(self.window, text="Результат прогноза")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.fig, self.ax = plt.subplots(figsize=(8,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        btn_back = tk.Button(self.window, text="← Назад", command=self.window.destroy, width=15)
        btn_back.pack(pady=10)

    def load_and_forecast(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return
        try:
            self.analyzer.load_file(filepath)
            self.make_forecast()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def make_forecast(self):
        dates = self.analyzer.get_dates()
        currency_cols = self.analyzer.get_currency_names()
        self.ax.clear()
        for col in currency_cols:
            values = self.analyzer.get_currency_values(col)
            self.ax.plot(dates, values, marker='o', label=f'{col.upper()} (история)')

        last_date = dates[-1]
        pred_dates = [last_date + timedelta(days=i + 1) for i in range(self.steps)]
        for col in currency_cols:
            pred_vals = self.analyzer.moving_average_forecast(col, self.window_size, self.steps)
            self.ax.plot(pred_dates, pred_vals, '--', linewidth=2, label=f'{col.upper()} (прогноз)')

        self.ax.set_xlabel('Дата')
        self.ax.set_ylabel('Курс')
        self.ax.set_title(f'Скользящая средняя (окно={self.window_size}), прогноз на {self.steps} дней')
        self.ax.legend()
        self.ax.grid(True)
        self.fig.autofmt_xdate()
        self.canvas.draw()

        btn_export = tk.Button(self.window, text=" Сохранить график", command=self.export_plot)
        btn_export.pack(pady=5)

    def export_plot(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")])
        if filepath:
            self.fig.savefig(filepath, dpi=150)
            messagebox.showinfo("Сохранено", f"График прогноза сохранён")

class Task3Report:
# Задание 3: отчет и экспорт
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Отчёт по курсам валют")
        self.window.geometry("1000x700")
        self.analyzer = CurrencyAnalyzer()
        self._build()

    def _build(self):
        tk.Button(self.window, text=" Загрузить CSV", command=self.load_and_show).pack(pady=5)

        self.table_frame = tk.Frame(self.window)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree = ttk.Treeview(self.table_frame)
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.stats_text = tk.Text(self.window, height=8, state=tk.DISABLED)
        self.stats_text.pack(fill=tk.X, padx=10, pady=5)

        self.export_btn = tk.Button(self.window, text=" Экспорт таблицы в CSV", command=self.export_csv, state=tk.DISABLED)
        self.export_btn.pack(pady=5)
        btn_back = tk.Button(self.window, text="← Назад", command=self.window.destroy, width=15)
        btn_back.pack(pady=10)

    def load_and_show(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return
        try:
            self.analyzer.load_file(filepath)
            self.show_table()
            self.show_stats()
            self.export_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def show_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = self.analyzer.get_table_data()
        if not data:
            return
        cols = ['date'] + self.analyzer.get_currency_names()
        self.tree['columns'] = cols
        self.tree['show'] = 'headings'
        for col in cols:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=120, anchor='center')
        for row in data:
            values = [row['date'].strftime('%Y-%m-%d')] + [f"{row[col]:.4f}" for col in
                                                           self.analyzer.get_currency_names()]
            self.tree.insert('', tk.END, values=values)

    def show_stats(self):
        stats = self.analyzer.max_increase_decrease()
        text = " Статистика по варианту 2:\n"
        for curr, data in stats.items():
            inc_date, inc_abs, inc_pct = data['max_inc']
            dec_date, dec_abs, dec_pct = data['max_dec']
            text += f"\n{curr.upper()}:\n  Прирост: {inc_abs:.2f} ({inc_pct:.2f}%) — {inc_date}\n  Падение: {dec_abs:.2f} ({dec_pct:.2f}%) — {dec_date}\n"
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, text)
        self.stats_text.config(state=tk.DISABLED)

    def export_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filepath:
            data = self.analyzer.get_table_data()
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                headers = ['date'] + self.analyzer.get_currency_names()
                writer.writerow(headers)
                for row in data:
                    writer.writerow(
                        [row['date'].strftime('%Y-%m-%d')] + [row[col] for col in self.analyzer.get_currency_names()])
            messagebox.showinfo("Экспорт", f"Таблица сохранена в {filepath}")
