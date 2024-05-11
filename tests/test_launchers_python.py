import kloch.launchers


def test__PythonLauncher(tmp_path, data_dir, capfd):
    script_path = data_dir / "test-script-a.py"
    launcher = kloch.launchers.PythonLauncher(
        command=["first arg"],
        python_file=str(script_path),
        environ={
            "PATH": ["$PATH", "D:\\some\\path"],
        },
    )
    expected_argv = [str(script_path), "first arg", "second arg"]

    launcher.execute(command=["second arg"], tmpdir=tmp_path)
    result = capfd.readouterr()
    assert f"{kloch.__name__} test script working" in result.out
    # XXX: test might fail on unix due to the \r ?
    assert result.out.endswith(f"{str(expected_argv)}\r\n")
