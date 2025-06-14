import pandas as pd
import numpy as np
import re
import math
import matplotlib.pyplot as plt
import ace_tools_open as tools

# 1. Загрузка данных
file_path = "wb_pc_easy.xlsx"
df = pd.read_excel(file_path)

# 2. Отображаем первые 10 строк
tools.display_dataframe_to_user("Первые 10 строк датасета", df.head(10))

# 3. Информация о датасете
info = df.info()

# 4. Числовое описание
desc = df.describe().T
tools.display_dataframe_to_user("Числовое описание основных признаков", desc)

# 5. Подсчёт пропущенных значений
missing = df.isna().sum().to_frame("Количество пропусков")
tools.display_dataframe_to_user("Пропущенные значения", missing)

# 6. Чистка и преобразования для дисковых объёмов
def parse_size(val):
    if isinstance(val, (int, float)) and not math.isnan(val):
        return float(val)
    if isinstance(val, str):
        val = val.strip().lower().replace(',', '.')
        match = re.search(r'([\d\.]+)', val)
        if match:
            num = float(match.group(1))
            if 'tb' in val:
                return num * 1000  # перевод TB → GB
            return num
    return np.nan

df["SSD_GB"] = df["Объем накопителя SSD"].apply(parse_size)
df["HDD_GB"] = df["Объем накопителя HDD"].apply(parse_size)

# 7. Корреляционный анализ
numeric_cols = ["Цена, руб.", "Количество ядер процессора",
                "Объем оперативной памяти (Гб)", "SSD_GB", "HDD_GB"]
corr = df[numeric_cols].corr()
tools.display_dataframe_to_user("Корреляционная матрица", corr)

# 8. ТОП-10 продавцов
top_vendors = df["Продавец"].value_counts().head(10).to_frame("Количество товаров")
tools.display_dataframe_to_user("ТОП-10 продавцов", top_vendors)

# --- Визуализации ---
# Гистограмма цен
plt.figure()
df["Цена, руб."].hist(bins=40)
plt.title("Распределение цен")
plt.xlabel("Цена, руб.")
plt.ylabel("Количество товаров")
plt.show()

# Scatter: Цена vs. Число ядер
plt.figure()
plt.scatter(df["Количество ядер процессора"], df["Цена, руб."], alpha=0.5)
plt.title("Цена vs. Количество ядер процессора")
plt.xlabel("Количество ядер процессора")
plt.ylabel("Цена, руб.")
plt.show()

# Bar: распределение по видеопроцессору
plt.figure()
gpu_counts = df["Видеопроцессор"].value_counts()
gpu_counts.plot(kind="bar")
plt.title("Распределение товаров по типу видеопроцессора")
plt.xlabel("Видеопроцессор")
plt.ylabel("Количество товаров")
plt.show()
