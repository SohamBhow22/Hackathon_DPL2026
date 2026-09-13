from src.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    OUTPUT_DIR,
)


def test_project_directories_exist():
    assert RAW_DATA_DIR.exists()
    assert PROCESSED_DATA_DIR.exists()
    assert OUTPUT_DIR.exists()