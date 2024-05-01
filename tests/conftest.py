from pathlib import Path

import pytest

THISDIR = Path(__file__).parent


@pytest.fixture()
def data_dir() -> Path:
    return THISDIR / "data"
