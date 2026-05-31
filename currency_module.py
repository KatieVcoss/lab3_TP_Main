import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import os
# Анализ курсов валют: вариант 2
class CurrencyAnalyzer:
    def __init__(self):
        self.df = None
        self.currency_cols = []  # два названия колонок

    def load_file(self, filepath): # загрузка файлов с колонками date, валюта1, валюта2
        df = pd.read_csv(filepath)
        df.columns = [c.lower().strip() for c in df.columns]
        if 'date' not in df.columns:
            raise ValueError("Файл должен содержать колонку 'date'")
        df['date'] = pd.to_datetime(df['date'])
        # Взять первые две числовые колонки (кроме даты)
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_cols) < 2:
            raise ValueError("Нужно минимум две колонки с курсами валют")
        self.currency_cols = numeric_cols[:2]
        self.df = df
        return True

    def get_table_data(self):
        return self.df

    def get_currency_names(self):
        return self.currency_cols

    def daily_changes(self):
        changes = pd.DataFrame()
        for col in self.currency_cols:
            changes[f'{col}_abs'] = self.df[col].diff()
            changes[f'{col}_pct'] = self.df[col].pct_change() * 100
        changes['date'] = self.df['date']
        return changes # вернуть DataFrame с абс и процентными изменениями для каждой валюты

    def max_increase_decrease(self):
        # Для каждой валюты: дата макс прироста, абс_прирост, пкт_прирост,
        # дата макс падения, абс_падение, пкт_падение
        changes = self.daily_changes()
        result = {}
        for col in self.currency_cols:
            # Прирост
            abs_inc = changes[f'{col}_abs'].max()
            date_inc = changes.loc[changes[f'{col}_abs'].idxmax(), 'date'].strftime('%Y-%m-%d')
            pct_inc = changes.loc[changes[f'{col}_abs'].idxmax(), f'{col}_pct']
            # Падение
            abs_dec = changes[f'{col}_abs'].min()
            date_dec = changes.loc[changes[f'{col}_abs'].idxmin(), 'date'].strftime('%Y-%m-%d')
            pct_dec = changes.loc[changes[f'{col}_abs'].idxmin(), f'{col}_pct']
            result[col] = {
                'max_inc': (date_inc, abs_inc, pct_inc),
                'max_dec': (date_dec, abs_dec, pct_dec)
            }
        return result

    def moving_average_forecast(self, col, window, steps):
        series = self.df[col].tolist()
        if len(series) < window:
            raise ValueError(f"Окно {window} больше данных ({len(series)})")
        forecast = []
        data = series.copy()
        for _ in range(steps):
            avg = sum(data[-window:]) / window
            forecast.append(avg)
            data.append(avg)
        return forecast # список прогнозных значений на steps шагов (скользящая средняя)

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
        df = self.analyzer.get_table_data()
        cols = list(df.columns)
        self.tree['columns'] = cols
        self.tree['show'] = 'headings'
        for col in cols:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=100, anchor='center')
        for _, row in df.iterrows():
            values = [row[col] for col in cols]
            self.tree.insert('', tk.END, values=values)

    def plot_graph(self):
        self.ax.clear()
        df = self.analyzer.get_table_data()
        currency_cols = self.analyzer.get_currency_names()
        for col in currency_cols:
            self.ax.plot(df['date'], df[col], marker='o', label=col.upper())
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

