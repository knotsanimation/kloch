from pathlib import Path

import pytest

import kloch
from kloch.__main__ import main


def test__main__logging(monkeypatch, tmp_path: Path):
    log_path = tmp_path / "kloch.log"
    monkeypatch.setenv(kloch.Environ.CONFIG_CLI_LOGGING_PATHS, str(log_path))
    assert not log_path.exists()
    with pytest.raises(SystemExit):
        main(argv=["list"])
    assert log_path.exists()

    assert f"starting {kloch.__name__} v{kloch.__version__}" in log_path.read_text(
        encoding="utf-8"
    )
