import json
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


class GoInflationRepository:
    """
    Отвечает только за связь с Go-модулем.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def get_executable_path(self) -> Path:
        go_dir = self.project_root / "go_module"

        if sys.platform.startswith("win"):
            return go_dir / "inflation_calc.exe"

        if sys.platform.startswith("linux"):
            return go_dir / "inflation_calc_linux"

        raise RuntimeError("Эта операционная система пока не поддерживается")

    def calculate(self, csv_path: Path, years: int, window: int, price: float) -> dict:
        exe_path = self.get_executable_path()

        if not exe_path.exists():
            raise FileNotFoundError(f"Не найден Go-файл: {exe_path}")

        result = subprocess.run(
            [
                str(exe_path),
                "--file", str(csv_path),
                "--years", str(years),
                "--window", str(window),
                "--price", str(price),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            raise RuntimeError(
                "Go-модуль вернул не JSON.\n\n"
                f"STDOUT:\n{result.stdout}\n\n"
                f"STDERR:\n{result.stderr}"
            )

        if result.returncode != 0:
            raise RuntimeError(data.get("error", "Ошибка выполнения Go-модуля"))

        if "error" in data:
            raise RuntimeError(data["error"])

        return data


class InflationWindow(tk.Toplevel):
    """
    Окно варианта 10:
    - открытие файла
    - таблица
    - график
    - прогноз
    - экспорт графика
    """

    def __init__(self, master=None):
        super().__init__(master)

        self.title("Вариант 10 — инфляция в России")
        self.geometry("1050x700")

        self.project_root = Path(__file__).resolve().parent
        self.repository = GoInflationRepository(self.project_root)

        self.selected_file: Path | None = None
        self.last_result: dict | None = None

        self._build_ui()

    def _build_ui(self):
        control_frame = ttk.LabelFrame(self, text="Параметры")
        control_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(
            control_frame,
            text="Открыть CSV-файл",
            command=self.on_open_file_click
        ).grid(row=0, column=0, padx=5, pady=5)

        self.file_label = ttk.Label(control_frame, text="Файл не выбран")
        self.file_label.grid(row=0, column=1, columnspan=6, sticky="w", padx=5)

        ttk.Label(control_frame, text="Прогноз на N лет:").grid(row=1, column=0, padx=5, pady=5)
        self.years_var = tk.IntVar(value=3)
        ttk.Spinbox(control_frame, from_=1, to=30, textvariable=self.years_var, width=8).grid(row=1, column=1)

        ttk.Label(control_frame, text="Окно средней:").grid(row=1, column=2, padx=5, pady=5)
        self.window_var = tk.IntVar(value=3)
        ttk.Spinbox(control_frame, from_=2, to=15, textvariable=self.window_var, width=8).grid(row=1, column=3)

        ttk.Label(control_frame, text="Цена товара/услуги:").grid(row=1, column=4, padx=5, pady=5)
        self.price_var = tk.DoubleVar(value=1000.0)
        ttk.Entry(control_frame, textvariable=self.price_var, width=12).grid(row=1, column=5)

        ttk.Button(
            control_frame,
            text="Рассчитать и построить график",
            command=self.on_calculate_click
        ).grid(row=1, column=6, padx=10)

        ttk.Button(
            control_frame,
            text="Экспорт графика в PNG",
            command=self.on_export_click
        ).grid(row=1, column=7, padx=5)

        self.summary_label = ttk.Label(self, text="Итоговая стоимость пока не рассчитана")
        self.summary_label.pack(fill="x", padx=10, pady=5)

        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        table_frame = ttk.LabelFrame(content_frame, text="Таблица данных")
        table_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.table = ttk.Treeview(
            table_frame,
            columns=("type", "year", "inflation"),
            show="headings"
        )

        self.table.heading("type", text="Тип")
        self.table.heading("year", text="Год")
        self.table.heading("inflation", text="Инфляция, %")

        self.table.column("type", width=100, anchor="center")
        self.table.column("year", width=80, anchor="center")
        self.table.column("inflation", width=120, anchor="center")

        self.table.pack(fill="both", expand=True)

        chart_frame = ttk.LabelFrame(content_frame, text="График")
        chart_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, chart_frame)
        self.toolbar.update()

    def on_open_file_click(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл с инфляцией",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ],
        )

        if not file_path:
            return

        self.selected_file = Path(file_path)
        self.file_label.config(text=str(self.selected_file))

    def on_calculate_click(self):
        if self.selected_file is None:
            messagebox.showwarning("Файл не выбран", "Сначала выберите CSV-файл с данными.")
            return

        try:
            result = self.repository.calculate(
                csv_path=self.selected_file,
                years=self.years_var.get(),
                window=self.window_var.get(),
                price=self.price_var.get(),
            )

            self.last_result = result
            self._fill_table(result)
            self._draw_chart(result)
            self._show_summary(result)

        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    def _fill_table(self, result: dict):
        for item in self.table.get_children():
            self.table.delete(item)

        for record in result["records"]:
            self.table.insert(
                "",
                "end",
                values=("Факт", record["year"], record["inflation"])
            )

        for record in result["forecast"]:
            self.table.insert(
                "",
                "end",
                values=("Прогноз", record["year"], record["inflation"])
            )

    def _draw_chart(self, result: dict):
        self.ax.clear()

        fact_years = [item["year"] for item in result["records"]]
        fact_values = [item["inflation"] for item in result["records"]]

        forecast_years = [item["year"] for item in result["forecast"]]
        forecast_values = [item["inflation"] for item in result["forecast"]]

        self.ax.plot(fact_years, fact_values, marker="o", label="Фактическая инфляция")
        self.ax.plot(forecast_years, forecast_values, marker="o", linestyle="--", label="Прогноз")

        self.ax.set_title("Инфляция в России и прогноз")
        self.ax.set_xlabel("Год")
        self.ax.set_ylabel("Инфляция, %")
        self.ax.grid(True)
        self.ax.legend()

        self.figure.tight_layout()
        self.canvas.draw()

    def _show_summary(self, result: dict):
        base_price = result["base_price"]
        estimated_price = result["estimated_price"]
        years = result["years"]

        self.summary_label.config(
            text=(
                f"Если текущая стоимость товара/услуги: {base_price:.2f}, "
                f"то через {years} лет возможная стоимость: {estimated_price:.2f}"
            )
        )

    def on_export_click(self):
        if self.last_result is None:
            messagebox.showwarning("Нет графика", "Сначала постройте график.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Сохранить график",
            defaultextension=".png",
            filetypes=[
                ("PNG image", "*.png"),
                ("All files", "*.*"),
            ],
        )

        if not file_path:
            return

        self.figure.savefig(file_path)
        messagebox.showinfo("Готово", f"График сохранён:\n{file_path}")


def open_inflation_window(parent=None):
    """
    Эту функцию можно привязать кнопке в общем интерфейсе
    """
    InflationWindow(parent)