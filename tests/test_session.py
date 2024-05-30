import time
from pathlib import Path

import kloch.session


def test__SessionDir(tmp_path: Path):
    session = kloch.session.SessionDirectory.initialize(tmp_path)
    assert session.path.exists()
    assert session.path is not tmp_path
    assert session.timestamp_path.exists()
    assert not session.profile_path.exists()


def test__clean_outdated_session_dirs(tmp_path: Path):
    session1 = kloch.session.SessionDirectory.initialize(tmp_path)
    time.sleep(0.005)
    session2 = kloch.session.SessionDirectory.initialize(tmp_path)
    time.sleep(0.005)
    session3 = kloch.session.SessionDirectory.initialize(tmp_path)
    time.sleep(0.005)
    session4 = kloch.session.SessionDirectory.initialize(tmp_path)
    time.sleep(0.005)

    Path(tmp_path / "nothingtoseehere.randomfile").write_text("eat the rich")

    lifetime = 0.015 / 3600  # to hours
    cleaned = kloch.session.clean_outdated_session_dirs(tmp_path, lifetime=lifetime)
    assert len(cleaned) == 2
    assert session4.path.exists()
    assert session3.path.exists()
    assert not session2.path.exists()
    assert not session1.path.exists()
