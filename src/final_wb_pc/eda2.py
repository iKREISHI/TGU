import pandas as pd, numpy as np, re, math, ace_tools_open as tools

# Load
df = pd.read_excel("wb_pc_easy.xlsx")

def parse_size(v):
    if isinstance(v, (int, float)) and not math.isnan(v):
        return float(v)
    if isinstance(v, str):
        s = v.strip().lower().replace(",", ".")
        m = re.search(r"([\d\.]+)", s)
        if m:
            num = float(m.group(1))
            return num * 1000 if "tb" in s else num
    return np.nan

df["SSD_GB"] = df["Объем накопителя SSD"].apply(parse_size)
df["HDD_GB"] = df["Объем накопителя HDD"].apply(parse_size)
df.rename(columns={
    "Цена, руб.":"Price",
    "Количество ядер процессора":"CPU_Cores",
    "Объем оперативной памяти (Гб)":"RAM_GB",
    "Операционная система":"OS",
    "Видеопроцессор":"GPU"
}, inplace=True)
df["CPU_Cores"] = df["CPU_Cores"].astype("Int64")

# GPU vendor extraction
def vendor(x):
    if isinstance(x, str):
        xl = x.lower()
        if "nvidia" in xl: return "NVIDIA"
        if "amd" in xl: return "AMD"
        if "intel" in xl: return "Intel"
    return "Unknown"
df["GPU_Vendor"] = df["GPU"].apply(vendor)

# Median price by CPU_Cores & GPU_Vendor
median_price = (
    df.groupby(["CPU_Cores","GPU_Vendor"], dropna=False)["Price"]
      .median()
      .rename("MedianGroupPrice")
      .reset_index()
)

df = df.merge(median_price, on=["CPU_Cores","GPU_Vendor"], how="left")
df["RelPrice"] = df["Price"] / df["MedianGroupPrice"]

# Flags
df["Overpriced"] = df["RelPrice"] > 1.3
df["LowSpec"] = (df["RAM_GB"] <= 8) | (df["SSD_GB"] <= 256)
df["MissingGPU"] = df["GPU_Vendor"] == "Unknown"
df["MissingOS"] = df["OS"].str.lower().fillna("").str.contains("не установлена|dos|без ос")

df["Unsellable"] = df["Overpriced"] & (df["LowSpec"] | df["MissingGPU"] | df["MissingOS"])

unsellable_df = df[df["Unsellable"]].copy()

# Show top 25 by relative price
unsellable_top = unsellable_df.sort_values("RelPrice", ascending=False).head(25)

tools.display_dataframe_to_user("Potentially unsellable PCs (top 25)", unsellable_top[[
    "Идентификатор товара","Наименование","Price","CPU_Cores","RAM_GB","SSD_GB","GPU","OS",
    "RelPrice","LowSpec","MissingGPU","MissingOS"
]])
