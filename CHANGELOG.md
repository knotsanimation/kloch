# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.1] - 2024-06-29

### chores

- fixed documentation not building because of import errors

## [0.8.0] - 2024-06-29

### added

- io: `read_profile_from_id()`
- constants module with environment variables
- logging to disk with `cli_logging_paths` config key
- control for the "session directory" using config

### changed

- !io: drop the global system to add profile locations, all profile location
  are added on each function call.
- io: made `is_file_environment_profile` public
- cli: add KlochConfig propagated through cli

### chores

- fixing tests CI
- pyproject use _extras_ instead of poetry groups
- remove app packaging script: not used anymore


## [0.7.0] - 2024-05-27

### added

- plugin system for launchers
- individual config values can now be retrieved from environment variable

### changed

- ! removed `rezenv` launcher to be extracted as plugin at https://github.com/knotsanimation/kloch-launcher-rezenv
- logic change in the MergeableDict class when subclassing to return the 
  proper subclass when adding 2 instances.

### chores

- updated `Usage` documentation 

## [0.6.0] - 2024-05-25

### added

- `cli` add `python` subcommand to execute a file with the internal interpreter
- `launchers` add a new `@python` launcher
- `launchers` add `cwd` attribute
- add configuration system

### changed

- !! complex refacto of launcher serialization system.
- `launchers` improve error message when missing a required field to a launcher
- `launchers` improve debbug message of subprocess
- `launchers` resolve `environ` earlier at init instead of in `execute()`
- `launchers.rezenv` remove `requires` from required_fileds
- ! `io` allow to specify a `profile_locations` arg

### fixed

- `profile` merging of `.base` when token in launcher name
- ensure python 3.7 compatibility (mostly invalid type hints)

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
