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

### Sample usage

```sh
$ ./differ -c e2e-tests/tests/MiddleOfLogRemoved/baseline.txt e2e-tests/tests/MiddleOfLogRemoved/checked.txt
21 | Missing | [20.0] Aed ZOVfSgU hy88Eq OGen3jzET LqU1Sc YEnNl egWld6
21 | Missing | [21.0] Error: uUXDumLi occurred at XIeO17W timestamp: nwa7Mx2Nw
21 | Missing | [22.0] Error: s59Ud6p occurred at 1UkIW51v timestamp: F6zdizc
21 | Missing | [23.0] New: KN2wuh9 template for cikYK8mFnm second log yAeF8fWwmk
21 | Missing | [24.0] Warning: HnaKF detected at WbVTLRYj5J timestamp: qxCy9B6fW
21 | Missing | [25.0] Error: M1HoXzDZ4 occurred at aTr2Ir timestamp: FeKxayZ
21 | Missing | [26.0] Aed ZOVfSgU hy88Eq llxql2cnN LqU1Sc YEnNl egWld6
21 | Missing | [27.0] New: dvpzPzh template for Od1dGQ second log J2CrgQx
21 | Missing | [28.0] Warning: dtPrgdzuX detected at gyKvt1194A timestamp: 9wyKKM7t2c
21 | Missing | [29.0] Warning: o4Hay detected at rA83W5L1KE timestamp: i1XNRQDHs
```

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
