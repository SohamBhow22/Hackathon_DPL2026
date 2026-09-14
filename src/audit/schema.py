import pandas as pd


def audit_schema(df: pd.DataFrame) -> pd.DataFrame:
    audit = pd.DataFrame({
        "column": df.columns,
        "dtype": df.dtypes.astype(str).values,
        "non_null": df.notna().sum().values,
        "missing": df.isna().sum().values,
        "missing_pct": (df.isna().mean() * 100).values,
        "unique": df.nunique(dropna=True).values,
    })

    return audit