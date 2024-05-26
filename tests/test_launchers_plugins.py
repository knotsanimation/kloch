import pytest

from kloch.launchers import BaseLauncher
import kloch.launchers._plugins


def test__load_plugin_launchers(data_dir, monkeypatch):

    plugin_path = data_dir / "plugins-behr"
    monkeypatch.syspath_prepend(plugin_path)

    launchers, missed = kloch.launchers._plugins.load_plugin_launchers(
        module_names=["kloch_behr"],
        subclass_type=kloch.launchers.BaseLauncher,
    )
    assert not missed
    assert len(launchers) == 1
    assert issubclass(launchers[0], kloch.launchers.BaseLauncher)
    assert launchers[0].name == "behr"

    launchers, missed = kloch.launchers._plugins.load_plugin_launchers(
        module_names=["kloch_behr"],
        subclass_type=kloch.launchers.BaseLauncherSerialized,
    )
    assert not missed
    assert len(launchers) == 1
    assert issubclass(launchers[0], kloch.launchers.BaseLauncherSerialized)
    assert launchers[0].identifier == "behr"

    plugin_path = data_dir / "plugins-tyfa"
    monkeypatch.syspath_prepend(plugin_path)

    launchers, missed = kloch.launchers._plugins.load_plugin_launchers(
        module_names=["kloch_tyfa"],
        subclass_type=kloch.launchers.BaseLauncher,
    )
    # XXX: tyfa import PythonLauncher so it is discovered
    assert len(launchers) == 2


def test__load_plugin_launchers__missing(data_dir, monkeypatch):

    plugin_path = data_dir / "plugins-rerr"
    monkeypatch.syspath_prepend(plugin_path)

    launchers, missed = kloch.launchers._plugins.load_plugin_launchers(
        module_names=["kloch_rerr"],
        subclass_type=kloch.launchers.BaseLauncher,
    )
    assert len(missed) == 1
    assert not launchers


def test__check_launcher_plugins(data_dir, monkeypatch):
    plugin_path = data_dir / "plugins-behr"
    monkeypatch.syspath_prepend(str(plugin_path))
    plugin_path = data_dir / "plugins-rerr"
    monkeypatch.syspath_prepend(str(plugin_path))

    kloch.launchers._plugins.check_launcher_plugins(["kloch_behr"])

    with pytest.raises(ImportError) as error:
        kloch.launchers._plugins.check_launcher_plugins(["kloch_rerr"])
        assert BaseLauncher.__name__ in error
