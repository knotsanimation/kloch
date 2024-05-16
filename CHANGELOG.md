# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2024-05-16

### added

- `cli` add `python` subcommand to execute a file with the internal interpreter
- `launchers` add a new `@python` launcher
- `launchers` add `cwd` attribute

### changed

- `launchers` improve error message when missing a required field to a launcher
- `launchers` improve debbug message of subprocess
- `launchers` resolve `environ` earlier at init instead of in `execute()`
- `launchers.rezenv` remove `requires` from required_fileds
- `io` allow to specify a `profile_locations` arg

### fixed

- `profile` merging of `.base` when token in launcher name

### chores

- improved unittesting
- run unittest in CI


## [0.5.2] - 2024-05-06

### chores

- added application packaging with `nuitka` in complement of `pyinstaller`
- add branding (logo, typography, colors, ...)
- add `copy-button` extension to sphinx doc
- minor documentation hierarchy changes
- improve index/README

## [0.5.1] - 2024-05-04

### added

- `command` attribute to the `.base` launcher
  - available for all launcher, it is prioritary over the CLI command which is appened to it.


## [0.5.0] - 2024-05-04

### changed

- ! renamed the core repository name to `kloch` (previously `kenvmanager`)
- ! renamed profile magic name to `kloch_profile` (from `KenvEnvironmentProfile`)

## [0.4.0] - 2024-05-04

### changed

- ! changed  the concept of `managers` to `launchers`, everywhere.
- ! bump the profile version to 2

## [0.3.0] - 2024-05-04

### added

- allow to specify a `.base` manager that is merged with others on resolve.
- add `kloch.get_available_managers_classes`
- add a new `system` manager
- allow environment variable expansion in `environ`
- add path normalization in `environ` 

### fixed

- finalize the implementation of the `--` command in the CLI

### changed

- ! `kloch.managers.rezenv` was made private

### chores

- add custom `execinject` extension to build more dynamic documentation
- use `execinject` to automatize the documentation of managers


## [0.2.0] - 2024-05-02

Minor version bump for development purpose. No changes.

## [0.1.0] - 2024-05-02

Initial release.
