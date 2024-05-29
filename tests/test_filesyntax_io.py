from pathlib import Path

import pytest

import kloch.filesyntax


def test__read_profile_from_file__envvar(data_dir):
    profile_echoes_beta_paths = kloch.filesyntax.get_profile_file_path(
        "knots:echoes:beta",
        profile_locations=[data_dir],
    )
    assert len(profile_echoes_beta_paths) == 1
    profile_echoes_beta = kloch.filesyntax.read_profile_from_file(
        profile_echoes_beta_paths[0],
        profile_locations=[data_dir],
    )
    assert profile_echoes_beta.identifier == "knots:echoes:beta"
    assert profile_echoes_beta.base is None

    profile_echoes_path = kloch.filesyntax.get_profile_file_path(
        "knots:echoes",
        profile_locations=[data_dir],
    )[0]
    profile_echoes = kloch.filesyntax.read_profile_from_file(
        profile_echoes_path,
        profile_locations=[data_dir],
    )
    assert profile_echoes.identifier == "knots:echoes"
    assert profile_echoes.base == profile_echoes_beta

    m_profile = profile_echoes.get_merged_profile()
    assert m_profile.identifier == "knots:echoes"
    assert m_profile.base is None


def test__read_profile_from_id(data_dir):
    profile_echoes_beta = kloch.filesyntax.read_profile_from_id(
        "knots:echoes:beta",
        profile_locations=[data_dir],
    )
    assert profile_echoes_beta.identifier == "knots:echoes:beta"
    assert profile_echoes_beta.base is None


def test__read_profile_from_file__old(monkeypatch, data_dir):
    profile_paths = kloch.filesyntax.get_profile_file_path(
        "version1", profile_locations=[data_dir]
    )
    assert len(profile_paths) == 1
    with pytest.raises(SyntaxError):
        kloch.filesyntax.read_profile_from_file(profile_paths[0])


def test__serialize_profile(data_dir, tmp_path: Path):
    # test back and forth conversion
    profile_src = kloch.filesyntax.read_profile_from_id(
        "knots:echoes:beta",
        profile_locations=[data_dir],
    )
    serialized = kloch.filesyntax.serialize_profile(
        profile_src,
        profile_locations=[data_dir],
    )
    profile_new_path = tmp_path / "profile.yml"
    profile_new_path.write_text(serialized)

    profile_new = kloch.filesyntax.read_profile_from_file(
        profile_new_path,
        profile_locations=[data_dir],
    )
    assert profile_src == profile_new


def test__write_profile_to_file(data_dir, tmp_path: Path):
    # test back and forth conversion
    profile_src = kloch.filesyntax.read_profile_from_id(
        "knots:echoes:beta",
        profile_locations=[data_dir],
    )
    profile_new_path = tmp_path / "profile.yml"
    kloch.filesyntax.write_profile_to_file(
        profile_src,
        file_path=profile_new_path,
        profile_locations=[data_dir],
        check_valid_id=False,
    )
    assert profile_new_path.exists()
    profile_new = kloch.filesyntax.read_profile_from_file(
        profile_new_path,
        profile_locations=[data_dir],
    )
    assert profile_src == profile_new

    with pytest.raises(ValueError):
        kloch.filesyntax.write_profile_to_file(
            profile_src,
            file_path=profile_new_path,
            profile_locations=[data_dir],
            check_valid_id=True,
        )
