import dataclasses
from pathlib import Path
from typing import Optional

import pytest

import kloch
import kloch.launchers
from kloch.launchers import BaseLauncher
from kloch.launchers import BaseLauncherSerialized
from kloch.launchers import get_launcher_class
from kloch.launchers import get_available_launchers_classes
from kloch.launchers import get_launcher_serialized_class
from kloch.launchers import get_available_launchers_serialized_classes


def test__get_launcher_class():
    result = get_launcher_class(".base")
    assert result is kloch.launchers.BaseLauncher

    result = get_launcher_class("system")
    assert result is kloch.launchers.SystemLauncher

    result = get_launcher_class("@python")
    assert result is kloch.launchers.PythonLauncher


# ensure the subclasses have properly overridden class attributes
# (this is because there is no way of having abstract attribute with abc module)
def test__launchers__implementation():
    for launcher in get_available_launchers_classes():
        if launcher is not BaseLauncher:
            assert launcher.name != BaseLauncher.name
        assert issubclass(launcher, BaseLauncher)


# ensure developer didn't missed to add documentation before adding a new subclass
def test__launchers__serialized_implementation():
    # ensure each launcher have a serialized class
    assert len(get_available_launchers_classes()) == len(
        get_available_launchers_serialized_classes()
    )
    for serialized in get_available_launchers_serialized_classes():
        assert issubclass(serialized, BaseLauncherSerialized)

    ser_launchers = get_available_launchers_serialized_classes()

    # ensure each serialized class have correctly implemented attributes
    for lnch_ser in ser_launchers:
        assert hasattr(lnch_ser, "fields")
        assert hasattr(lnch_ser, "source")
        assert hasattr(lnch_ser, "identifier")
        assert hasattr(lnch_ser, "summary")
        assert hasattr(lnch_ser, "description")

        if lnch_ser is not BaseLauncherSerialized:
            assert lnch_ser.source is not BaseLauncherSerialized
            assert lnch_ser.fields is not BaseLauncherSerialized.fields
            assert lnch_ser.summary is not BaseLauncherSerialized.summary
            assert lnch_ser.description is not BaseLauncherSerialized.description
            assert lnch_ser.identifier is not BaseLauncherSerialized.identifier

        fields_ser = dataclasses.fields(lnch_ser.fields)
        fields_source = dataclasses.fields(lnch_ser.source)

        assert len(fields_ser) >= len(fields_source), lnch_ser
        for field_ser in fields_ser:
            assert "required" in field_ser.metadata
            assert "description" in field_ser.metadata
