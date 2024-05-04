import pytest

import kloch.filesyntax


def test_read_profile_from_file(monkeypatch, data_dir):
    monkeypatch.setenv(kloch.KENV_PROFILE_PATH_ENV_VAR, str(data_dir))

    profile_echoes_beta_path = kloch.filesyntax.get_profile_file_path(
        "knots:echoes:beta"
    )
    profile_echoes_beta = kloch.filesyntax.read_profile_from_file(
        profile_echoes_beta_path
    )
    assert profile_echoes_beta.identifier == "knots:echoes:beta"
    assert profile_echoes_beta.base is None

    profile_echoes_path = kloch.filesyntax.get_profile_file_path("knots:echoes")
    profile_echoes = kloch.filesyntax.read_profile_from_file(profile_echoes_path)
    assert profile_echoes.identifier == "knots:echoes"
    assert profile_echoes.base == profile_echoes_beta

    m_profile = profile_echoes.get_merged_profile()
    assert m_profile.identifier == "knots:echoes"
    assert m_profile.base is None


def test_read_profile_from_file_old(monkeypatch, data_dir):
    monkeypatch.setenv(kloch.KENV_PROFILE_PATH_ENV_VAR, str(data_dir))

    profile_path = kloch.filesyntax.get_profile_file_path("version1")
    with pytest.raises(SyntaxError):
        kloch.filesyntax.read_profile_from_file(profile_path)
