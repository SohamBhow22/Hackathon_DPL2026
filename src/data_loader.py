import pandas as pd

from .config import RAW_DATA_FILE


def load_raw_data() -> pd.DataFrame:
    return pd.read_csv(RAW_DATA_FILE)