import pandas as pd
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
