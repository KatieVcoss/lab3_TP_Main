# main_menu.py
import tkinter as tk
from tkinter import ttk, messagebox
from ui_main import MainUI
from inflation_module import open_inflation_window
from currency_menu import open_currency_module

class MainMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Главное меню — Лабораторная работа №3")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self._build()

    def _build(self):
        tk.Label(self.root, text="Система анализа данных",
                 font=("Arial", 16, "bold")).pack(pady=20)
        tk.Label(self.root, text="Выберите раздел:",
                 font=("Arial", 12)).pack(pady=10)

        # Кнопка 1 — твоя (Вариант 5: Население России)
        btn1 = tk.Button(self.root, text="Население РФ (Вариант 5)",
                         font=("Arial", 11), width=35, height=2,
                         command=self._open_variant_5)
        btn1.pack(pady=8)

        # Кнопка 2 — одногруппник 1
        btn2 = tk.Button(self.root, text="Глинков (Вариант 10)",
                         font=("Arial", 11), width=35, height=2,
                         command=self._open_variant_2)
        btn2.pack(pady=8)

        # Кнопка 3 — одногруппник 2
        btn3 = tk.Button(self.root, text="Коржова (Вариант ?)",
                         font=("Arial", 11), width=35, height=2,
                         command=self._open_variant_3)
        btn3.pack(pady=8)

        tk.Label(self.root, text="\nСтуденты: Викторова, Глинков, Коржова | Группа: 4427",
                 font=("Arial", 9), fg="gray").pack(side=tk.BOTTOM, pady=10)

    def _open_variant_5(self): #Открывает модуль (Вариант 5)
        self.root.withdraw()
        MainUI(self.root)

    def _open_variant_2(self):
        open_inflation_window(self.root)

    def _open_variant_3(self):
        open_currency_module(self.root)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    MainMenu().run()
