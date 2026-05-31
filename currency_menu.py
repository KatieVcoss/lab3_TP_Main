import tkinter as tk
from tkinter import messagebox
from currency_module import Task1Graph, Task2Forecast, Task3Report

class CurrencyMenu:
    def __init__(self, parent_window):
        self.parent = parent_window
        self.window = tk.Toplevel(parent_window)
        self.window.title("Анализ курсов валют (Вариант 2)")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        self._build()

    def _build(self):
        tk.Label(self.window, text="Анализ курсов валют", font=("Arial", 14, "bold")).pack(pady=20)
        tk.Label(self.window, text="Выберите действие:", font=("Arial", 12)).pack(pady=10)

        btn1 = tk.Button(self.window, text="1. Таблица + график + статистика",
                         font=("Arial", 11), width=35, height=2,
                         command=self._open_graph)
        btn1.pack(pady=8)

        btn2 = tk.Button(self.window, text="2. Прогноз скользящей средней",
                         font=("Arial", 11), width=35, height=2,
                         command=self._open_forecast_dialog)
        btn2.pack(pady=8)

        btn3 = tk.Button(self.window, text="3. Полный отчёт",
                         font=("Arial", 11), width=35, height=2,
                         command=self._open_report)
        btn3.pack(pady=8)

        btn_back = tk.Button(self.window, text="← Назад", font=("Arial", 10),
                             command=self.window.destroy, width=15)
        btn_back.pack(pady=20)

    def _open_graph(self):
        Task1Graph()

    def _open_forecast_dialog(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Параметры прогноза")
        dialog.geometry("300x220")
        dialog.grab_set()

        tk.Label(dialog, text="Окно скользящей средней (N):").pack(pady=5)
        n_entry = tk.Entry(dialog)
        n_entry.insert(0, "5")
        n_entry.pack()

        tk.Label(dialog, text="Количество дней прогноза (M):").pack(pady=5)
        m_entry = tk.Entry(dialog)
        m_entry.insert(0, "7")
        m_entry.pack()

        def on_ok():
            try:
                n = int(n_entry.get())
                m = int(m_entry.get())
                if n <= 0 or m <= 0:
                    raise ValueError
                dialog.destroy()
                Task2Forecast(window_size=n, steps=m)
            except:
                messagebox.showerror("Ошибка", "Введите целые положительные числа")

        tk.Button(dialog, text="Прогноз", command=on_ok).pack(pady=10)

    def _open_report(self):
        Task3Report()

def open_currency_module(parent_window):
    CurrencyMenu(parent_window)