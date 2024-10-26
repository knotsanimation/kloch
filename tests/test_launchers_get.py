import kloch
import kloch.launchers
from kloch.launchers import get_available_launchers_classes
from kloch.launchers import is_launcher_plugin
from kloch.launchers._plugins import _check_launcher_serialized_implementation
from kloch.launchers._plugins import _check_launcher_implementation
from kloch.launchers import get_available_launchers_serialized_classes


def test__get_available_launchers_classes(data_dir, monkeypatch):
    plugin_path = data_dir / "plugins-behr"
    monkeypatch.syspath_prepend(plugin_path)
    plugin_path = data_dir / "plugins-tyfa"
    monkeypatch.syspath_prepend(plugin_path)
    launchers = get_available_launchers_classes()
    assert len(launchers) == len(kloch.launchers._BUILTINS_LAUNCHERS)

    loaded = kloch.launchers.load_plugin_launchers(
        ["kloch_behr", "kloch_tyfa"],
        kloch.launchers.BaseLauncher,
    )
    launchers = get_available_launchers_classes(plugins=loaded)
    assert len(launchers) == len(kloch.launchers._BUILTINS_LAUNCHERS) + 2


# ensure the native subclasses have properly overridden class attributes
# (this is because there is no way of having abstract attribute with abc module)
def test__launchers__implementation():
    for launcher in get_available_launchers_classes():
        _check_launcher_implementation(launcher)


# ensure developer didn't missed to add documentation before adding a new subclass
def test__launchers__serialized_implementation():
    # ensure each launcher have a serialized class
    assert len(get_available_launchers_classes()) == len(
        get_available_launchers_serialized_classes()
    )
    for serialized in get_available_launchers_serialized_classes():
        _check_launcher_serialized_implementation(serialized)


def test__is_launcher_plugin(data_dir, monkeypatch):
    plugin_path = data_dir / "plugins-behr"
    monkeypatch.syspath_prepend(plugin_path)
    plugin_path = data_dir / "plugins-tyfa"
    monkeypatch.syspath_prepend(plugin_path)

    loaded = kloch.launchers.load_plugin_launchers(
        ["kloch_behr", "kloch_tyfa"],
        kloch.launchers.BaseLauncher,
    )
    results = [is_launcher_plugin(launcher) for launcher in loaded.launchers]
    # XXX: kloch_tyfa will return the native PythonLauncher
    assert not all(results), loaded.launchers
    assert results == [True, False, True]

    loaded = kloch.launchers.load_plugin_launchers(
        ["kloch_behr", "kloch_tyfa"],
        kloch.launchers.BaseLauncherSerialized,
    )
    results = [is_launcher_plugin(launcher) for launcher in loaded.launchers]
    assert all(results), loaded.launchers
    assert results == [True, True]
