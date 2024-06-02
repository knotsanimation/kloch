import kloch


def test__Environ():
    envvars = kloch.Environ.list_all()
    assert isinstance(envvars, list)
    assert kloch.Environ.CONFIG_ENV_VAR in envvars
    assert all([isinstance(env, str) for env in envvars])
