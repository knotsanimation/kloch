# TODO

Collection of various ideas to improve kloch.

## features

- [x] ~~validation of keys/value on profile read~~
- [x] ~~add a "python/pip/poetry" package manager ?~~ (implemented as launcher with kiche)
- [x] ~~use `+-` to append command~~ (rejected)
- [ ] token replacement system ?
  - [ ] PROFILE_DIR token
  - [ ] environment variable resolving ?
- [ ] allow multiples arg in `base`
- [ ] set cwd for relative paths
- [ ] allow to specify an absolute path to a profile instead of identifier
- [ ] do something with the version attribute ? allow duplicate identifier in path, but with different version ?
- [x] ~~log on disk ?~~
- [ ] private profiles ? with a dot prefix signifying they can only be inherited and not used directly ?
- [ ] allow `python_file` to be an url to a python file to download
- [ ] introduce operating system functions ? like maybe tokens or if conditions ?
- [ ] new merge rule `!=` create if doesn't exist (for dict keys)

## refacto

- [x] ~~naming of thing ? package manager could just be "launchers"~~
- [x] ~~internalise PyYaml dependenciyes (add it to vendor module)~~ (impossible) 
- [ ] ensure environment can be reproducible
  - always store them as an intermediate resolved file before execution ?
  - remove all resolving from launcher and perform all of this upstream ?
  - store intermediate resolved file at user-defined location OR tmp location ?
    Including also the tmp dir passed to launcher.execute() ?
    - define unique hash for dir ? like `timestamp-machine-user-uuid`
    - define config param to auto clear archived entries after X time
  - perhaps its too complicated to achieve, so achieve a middle ground, where
    you resolve the requirements formulated in the profile and store them on disk,
    (code at Serialized level) then use that file to launch.
- [ ] abstract `subprocess.run` in BaseLauncher and offer a `prepare_execution`
  abstractmethod instead.
- [ ] change default merge rule to be append and add token to specify explicit override
  - `-=` remove
  - `==` override
  - `+=` append (default)
- [ ] rename profile `base` key to `inherit` (limit similarities with `.base`)

## chore

- [x] ~~doc: explain how to add a new package manager support~~
- [x] ~~doc: replace index h1 with svg logotype~~