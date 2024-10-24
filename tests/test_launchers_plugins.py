from kloch.launchers import BaseLauncher
from kloch.launchers import BaseLauncherSerialized
import kloch.launchers._plugins


def test__load_plugin_launchers(data_dir, monkeypatch):

    plugin_path = data_dir / "plugins-behr"
    monkeypatch.syspath_prepend(plugin_path)

    loaded = kloch.launchers._plugins.load_plugin_launchers(
        module_names=["kloch_behr"],
        subclass_type=kloch.launchers.BaseLauncher,
    )
    assert loaded.given == ["kloch_behr"]
    assert not loaded.missed
    assert len(loaded.launchers) == 1
    assert issubclass(loaded.launchers[0], kloch.launchers.BaseLauncher)
    assert loaded.launchers[0].name == "behr"

    loaded = kloch.launchers._plugins.load_plugin_launchers(
        module_names=["kloch_behr"],
        subclass_type=kloch.launchers.BaseLauncherSerialized,
    )
    assert not loaded.missed
    assert len(loaded.launchers) == 1
    assert issubclass(loaded.launchers[0], kloch.launchers.BaseLauncherSerialized)
    assert loaded.launchers[0].identifier == "behr"

    plugin_path = data_dir / "plugins-tyfa"
    monkeypatch.syspath_prepend(plugin_path)

    loaded = kloch.launchers._plugins.load_plugin_launchers(
        module_names=["kloch_tyfa"],
        subclass_type=kloch.launchers.BaseLauncher,
    )
    # XXX: tyfa import PythonLauncher so it is discovered
    assert len(loaded.launchers) == 2


def test__load_plugin_launchers__missing(data_dir, monkeypatch):

    plugin_path = data_dir / "plugins-rerr"
    monkeypatch.syspath_prepend(plugin_path)

    loaded = kloch.launchers._plugins.load_plugin_launchers(
        module_names=["kloch_rerr"],
        subclass_type=kloch.launchers.BaseLauncher,
    )
    assert len(loaded.missed) == 1
    assert "kloch_rerr" in loaded.missed
    assert not loaded.launchers


def test__check_launcher_plugins(data_dir, monkeypatch):
    plugin_path = data_dir / "plugins-behr"
    monkeypatch.syspath_prepend(str(plugin_path))
    plugin_path = data_dir / "plugins-rerr"
    monkeypatch.syspath_prepend(str(plugin_path))

    plugins = kloch.launchers.load_plugin_launchers(
        ["kloch_behr"], BaseLauncherSerialized
    )
    errors = kloch.launchers._plugins.check_launcher_plugins(plugins)

    assert not errors

    plugins = kloch.launchers.load_plugin_launchers(
        ["kloch_rerr"], BaseLauncherSerialized
    )
    errors = kloch.launchers._plugins.check_launcher_plugins(plugins)
    error1 = errors[0]
    assert isinstance(error1, kloch.launchers._plugins.PluginModuleError)
    assert BaseLauncher.__name__ in str(error1)
