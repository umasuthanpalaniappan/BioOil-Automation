"""Load and lightly normalize the raw pyrolysis dataset."""
from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "biooil_pyrolysis_dataset.xlsx"

RENAME_MAP = {
    "Oil _yield": "Oil_yield",
    "Cal_ value": "Cal_value",
    "Gas_ yield ": "Gas_yield",
    "Char_ yield ": "Char_yield",
}

DROP_COLS = ["Gas_yield", "Char_yield"]  # entirely empty per data spec

FEATURE_COLS = [
    "Cel", "Hem", "Lig",       # biomass composition
    "VM", "Ash", "FC",         # proximate analysis
    "C%", "H%", "O%", "N%",    # ultimate analysis
    "Size", "HR", "PT", "Temp",  # process conditions
]

TARGET_COLS = ["O/C", "H/C", "Cal_value", "Oil_yield"]
PRIMARY_TARGET = "O/C"


def load_raw(sheet: str = "data") -> pd.DataFrame:
    df = pd.read_excel(DATA_PATH, sheet_name=sheet)
    df = df.rename(columns=RENAME_MAP)
    df = df.drop(columns=[c for c in DROP_COLS if c in df.columns])

    # Source workbook has stray placeholder strings ('-', ' ', non-breaking
    # spaces around numbers) in otherwise-numeric columns; normalize to NaN
    # or clean numerics rather than dropping rows here.
    numeric_cols = [c for c in FEATURE_COLS + TARGET_COLS if c in df.columns]
    for c in numeric_cols:
        if df[c].dtype == object:
            df[c] = (
                df[c]
                .astype(str)
                .str.replace("\xa0", "", regex=False)
                .str.strip()
                .replace({"-": None, "": None, "nan": None})
            )
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


if __name__ == "__main__":
    df = load_raw()
    print(df.shape)
    print(df.columns.tolist())
