# Analyzer

Set of utilities for anomaly detection based on application logs.
It consists of two main modules:

- `core` - containing all of the logic described in the master thesis (TODO: thesis is not ready and in polish)
- `differ` - CLI application that can be used to compare two log files from the same system.

There are also other utility modules.

## Building

This project is implemented in Kotlin and Java, targeting JVM platform.
Currently it targets Java **17** only.

The build system is managed by Gradle.
To make a full application build and run tests, you can run:

```bash
$ ./gradlew build
```

To see all available tasks:

```bash
$ ./gradlew tasks
```

## Differ

Differ is a tool for comparing two log files from the same system.
Official release can be obtained through Github releases page.

### E2E Regression

Differ has a simple regression system that can be triggered via Gradle:

```bash
$ ./gradlew e2eRegression
```

The command above tests all testcases defined in the `e2e-tests/tests` folder.

NOTE: It requires Python3 with standard libraries

## Log Parser Benchmarking

Collect benchmarking data from available parsers (WIP)

NOTE: This task needs Python 3 with Pandas and SciPy

```bash
$ ./gradlew performBenchmark
```
