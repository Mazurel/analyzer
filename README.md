# Kotlin Analizer

This is reimplementation of the original project with major improvements, rewritten in Kotlin.
Currently, due to drain, it targets JVM only.

## Building

This project is build using Kotlin and Java, targeting JVM platform.
Currently it targets Java **17** only.

Build system is managed by Gradle:

```bash
$ ./gradlew build
```

To see all available tasks:

```bash
$ ./gradlew tasks
```

## Dict parser benchmarking

Collect benchmarking data from available parsers (WIP)

NOTE: This task needs Python 3 with some additional dependencies

```bash
$ ./gradlew performBenchmark
```

## E2E regression tests

Run regression on differ tool, testing all core components.

NOTE: This task needs Python 3

```bash
$ ./gradlew e2eRegression
```
