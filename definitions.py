from pathlib import Path
from typing import Final


ROOT_DIR: Final = Path(__file__).parent

ASSETS_DIR: Final = ROOT_DIR.joinpath("assets")
OUTPUT_DIR: Final = ROOT_DIR.joinpath("output")
DATA_DIR: Final = ROOT_DIR.joinpath("data")
TEMPLATES_DIR: Final = ROOT_DIR.joinpath("templates")



for p in [ROOT_DIR, ASSETS_DIR, DATA_DIR, TEMPLATES_DIR]:
    assert p.exists() and p.is_dir()
