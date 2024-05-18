import contextlib
import os


@contextlib.contextmanager
def patch_environ(**environ):
    """
    Temporarily change ``os.environ`` and restore it once finished.

    Usage::

        with patch_environ():
            # the environ is left untouched by default
            os.environ.clear()
            os.environ["PATH"] = "/foo"

    """
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


def expand_envvars(src_str: str) -> str:
    """
    Resolve environment variable pattern in the given string.

    Using ``os.path.expandvars`` but allow escaping using ``$$``
    """
    # temporary remove escape character
    new_str = src_str.replace("$$", "##tmp##")
    # environment variable expansion
    new_str = os.path.expandvars(new_str)
    # restore escaped character
    new_str = new_str.replace("##tmp##", "$")
    return new_str
