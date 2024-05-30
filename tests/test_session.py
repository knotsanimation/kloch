from pathlib import Path

import kloch.session


def test__SessionDir(tmp_path: Path):
    session = kloch.session.SessionDirectory.initialize(tmp_path)
    assert session.path.exists()
    assert session.path is not tmp_path
    assert session.timestamp_path.exists()
    assert not session.profile_path.exists()
