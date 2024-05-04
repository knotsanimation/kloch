# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2024-05-04

### changed

- ! changed  the concept of `managers` to `launchers`, everywhere.

## [0.3.0] - 2024-05-04

### features

- allow to specify a `.base` manager that is merged with others on resolve.
- add `kenvmanager.get_available_managers_classes`
- add a new `system` manager
- allow environment variable expansion in `environ`
- add path normalization in `environ` 

### fixed

- finalize the implementation of the `--` command in the CLI

### changed

- ! `kenvmanager.managers.rezenv` was made private

### chores

- add custom `execinject` extension to build more dynamic documentation
- use `execinject` to automatize the documentation of managers


## [0.2.0] - 2024-05-02

Minor version bump for development purpose. No changes.

## [0.1.0] - 2024-05-02

Initial release.
