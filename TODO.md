# TODO

Collection of various ideas to improve kloch.

## features

- [x] validation of keys/value on profile read
- [ ] token replacement system ?
  - [ ] PROFILE_DIR token
  - [ ] environment variable resolving ?
- [ ] add a "python/pip/poetry" package manager ?
- [ ] allow multiples arg in `base`
- [ ] set cwd for relative paths
- [x] ~~use `+-` to append command~~ (rejected)
- [ ] allow to specify an absolute path to a profile instead of identifier
- [ ] do something with the version attribute ? allow duplicate identifier in path, but with different version ?
- [ ] log on disk ?
- [ ] private profiles ? with a dot prefix signifying they can only be inherited and not used directly ?

## refacto

- [ ] ensure environment can be reproducible
  - always store them as an intermediate resolved file before execution ?
  - remove all resolving from launcher and perform all of this upstream ?
  - store intermediate resolved file at user-defined location OR tmp location ?
    Including also the tmp dir passed to launcher.execute() ?
    - define unique hash for dir ? like `timestamp-machine-user-uuid`
    - define config param to auto clear archived entries after X time
- [ ] abstract `subprocess.run` in BaseLauncher and offer a `prepare_execution`
  abstractmethod instead.
- [x] naming of thing ? package manager could just be "launchers"
- [ ] change default merge rule to be append and add token to specify explicit override
  - `-=` remove
  - `==` override
  - `+=` append (default)
- [ ] ~~internalise PyYaml dependenciyes (add it to vendor module)~~ (impossible) 

## chore

- [ ] doc: explain how to add a new package manager support
- [x] doc: replace index h1 with svg logotype