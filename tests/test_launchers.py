import dataclasses

import kloch
import kloch.launchers
from kloch.launchers import get_launcher_class
from kloch.launchers import get_available_launchers_classes
from kloch.launchers import is_launcher_plugin
from kloch.launchers._plugins import check_launcher_serialized_implementation
from kloch.launchers._plugins import check_launcher_implementation
from kloch.launchers import get_available_launchers_serialized_classes


def test__get_launcher_class(data_dir, monkeypatch):
    result = get_launcher_class(".base")
    assert result is kloch.launchers.BaseLauncher
    assert not is_launcher_plugin(result)

    result = get_launcher_class("system")
    assert result is kloch.launchers.SystemLauncher
    assert not is_launcher_plugin(result)

    result = get_launcher_class("@python")
    assert result is kloch.launchers.PythonLauncher
    assert not is_launcher_plugin(result)

    result = get_launcher_class("behr")
    assert result is None
    result = get_launcher_class("tyfa")
    assert result is None

    plugin_path = data_dir / "plugins-behr"
    monkeypatch.syspath_prepend(plugin_path)
    plugin_path = data_dir / "plugins-tyfa"
    monkeypatch.syspath_prepend(plugin_path)
    monkeypatch.setenv(
        kloch.KlochConfig.get_field("launcher_plugins").metadata["environ"],
        "kloch_behr,kloch_tyfa",
    )

    result = get_launcher_class("behr")
    assert result.name == "behr"
    assert is_launcher_plugin(result)
    result = get_launcher_class("tyfa")
    assert result.name == "tyfa"
    assert is_launcher_plugin(result)


def test__get_available_launchers_classes__config_edit(data_dir, monkeypatch):
    plugin_path = data_dir / "plugins-behr"
    monkeypatch.syspath_prepend(plugin_path)
    plugin_path = data_dir / "plugins-tyfa"
    monkeypatch.syspath_prepend(plugin_path)
    monkeypatch.setenv(
        kloch.KlochConfig.get_field("launcher_plugins").metadata["environ"],
        "kloch_behr,kloch_tyfa",
    )
    launchers = get_available_launchers_classes()
    assert len(launchers) == len(kloch.launchers._BUILTINS_LAUNCHERS) + 2


def test__get_available_launchers_classes__arg(data_dir, monkeypatch):
    plugin_path = data_dir / "plugins-behr"
    monkeypatch.syspath_prepend(plugin_path)
    plugin_path = data_dir / "plugins-tyfa"
    monkeypatch.syspath_prepend(plugin_path)

    launchers = get_available_launchers_classes(
        launcher_plugins=["kloch_behr", "kloch_tyfa"]
    )
    assert len(launchers) == len(kloch.launchers._BUILTINS_LAUNCHERS) + 2


# ensure the subclasses have properly overridden class attributes
# (this is because there is no way of having abstract attribute with abc module)
def test__launchers__implementation():
    for launcher in get_available_launchers_classes():
        check_launcher_implementation(launcher)


# ensure developer didn't missed to add documentation before adding a new subclass
def test__launchers__serialized_implementation():
    # ensure each launcher have a serialized class
    assert len(get_available_launchers_classes()) == len(
        get_available_launchers_serialized_classes()
    )
    for serialized in get_available_launchers_serialized_classes():
        check_launcher_serialized_implementation(serialized)
