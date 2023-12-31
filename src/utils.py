from pathlib import Path


class Configuration:
    VER = 1
    RAW_DATA_PATH = Path(__file__).parents[1].joinpath("data/raw")
    INTERIM_DATA_PATH = Path(__file__).parents[1].joinpath("data/interim")
    EXTERNAL_DATA_PATH = Path(__file__).parents[1].joinpath("data/external")
