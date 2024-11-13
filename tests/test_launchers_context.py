import dataclasses

from kloch.launchers._context import LauncherContext
from kloch.launchers._context import LauncherPlatform
from kloch.launchers._context import unserialize_context_expression
from kloch.launchers._context import resolve_context_expression


def test__ProfileContext():

    ctx1 = LauncherContext(platform=LauncherPlatform.linux, user="unittest")
    ctx2 = LauncherContext(platform=LauncherPlatform.linux, user="unittest")
    assert ctx1 == ctx2

    ctx3 = LauncherContext(platform=LauncherPlatform.linux)
    assert ctx1 == ctx3

    ctx4 = LauncherContext(platform=LauncherPlatform.windows)
    assert ctx1 != ctx4

    assert LauncherContext.create_from_system() == LauncherContext.create_from_system()


def test__ProfileContext__devmistake():
    for field in dataclasses.fields(LauncherContext):
        assert "unserialize" in field.metadata
        assert "serialized_name" in field.metadata
        assert "doc" in field.metadata
        assert "value" in field.metadata["doc"]
        assert "description" in field.metadata["doc"]


def test__unserialize_context_expression():
    source = "he!$69@os=windows"
    result = unserialize_context_expression(source)
    assert result.platform == LauncherPlatform.windows
    assert result.user is None

    source = "he!$69@os=windows@user=babos@@mik"
    result = unserialize_context_expression(source)
    assert result.platform == LauncherPlatform.windows
    assert result.user == "babos@mik"

    source = "wow@@gmail.com"
    result = unserialize_context_expression(source)
    assert result.platform is None
    assert result.user is None


def test__resolve_context_expression():
    source = "he!$69@os=windows"
    result = resolve_context_expression(source)
    expected = "he!$69"
    assert result == expected

    source = "he!$69@os=windows@user=babos@@mik"
    result = resolve_context_expression(source)
    expected = "he!$69"
    assert result == expected

    source = "wow@@gmail.com"
    result = resolve_context_expression(source)
    expected = "wow@gmail.com"
    assert result == expected
