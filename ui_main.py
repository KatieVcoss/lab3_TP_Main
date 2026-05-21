# ui_main.py
import tkinter as tk
from tkinter import ttk, messagebox
from teammate_task import Task1Graph, Task2Forecast, Task3Report


class MainUI:
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Анализ населения РФ — Вариант 5")
        self.window.geometry("600x500")
        self._build()

    def _build(self):
        tk.Label(self.window, text="Анализ численности населения России",
                 font=("Arial", 14, "bold")).pack(pady=15)

        # Задание 1: График
        frame1 = tk.LabelFrame(self.window, text="Задание 1", padx=10, pady=10)
        frame1.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(frame1, text="Построить график населения по годам",
                 font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Button(frame1, text="Открыть график",
                  command=self._open_graph).pack(side=tk.RIGHT)

        # Задание 2: Прогноз
        frame2 = tk.LabelFrame(self.window, text="Задание 2", padx=10, pady=10)
        frame2.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(frame2, text="🔮 Прогноз методом скользящей средней",
                 font=("Arial", 10)).pack(side=tk.LEFT)

        # Поле для ввода N
        tk.Label(frame2, text="N лет:", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        self.n_entry = tk.Entry(frame2, width=5, font=("Arial", 10))
        self.n_entry.insert(0, "5")
        self.n_entry.pack(side=tk.LEFT)

        tk.Button(frame2, text="Прогноз",
                  command=self._open_forecast).pack(side=tk.RIGHT)

        # Задание 3: Таблица и статистика
        frame3 = tk.LabelFrame(self.window, text="Задание 3", padx=10, pady=10)
        frame3.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(frame3, text="Таблица данных и расчёт прироста/убыли",
                 font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Button(frame3, text="Открыть отчёт",
                  command=self._open_report).pack(side=tk.RIGHT)

        tk.Button(self.window, text="← Назад в меню",
                  command=self._go_back, width=20).pack(pady=20)

    def _open_graph(self):
        Task1Graph()

    def _open_forecast(self):
        try:
            n = int(self.n_entry.get())
            if n <= 0:
                raise ValueError
            Task2Forecast(n)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целое положительное число")

    def _open_report(self):
        Task3Report()

    def _go_back(self):
        self.window.master.deiconify()
        self.window.destroy()



