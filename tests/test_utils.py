import logging

import kloch._utils

LOGGER = logging.getLogger(__name__)


def test__expand_envvars():
    src_str = "${PATH}/foobar"
    result = kloch._utils.expand_envvars(src_str)
    assert result != src_str

    src_str = "foo/$${PATH}/foobar"
    result = kloch._utils.expand_envvars(src_str)
    assert result == "foo/${PATH}/foobar"

    src_str = "foo/tmp##${PATH}/foobar"
    result = kloch._utils.expand_envvars(src_str)
    assert result.startswith("foo/tmp##")
