# Kotlin Analizer

This is reimplementation of the original project with major improvements, rewritten in Kotlin.
Currently, due to drain, it targets JVM only.

## Building

You need to use **JAVA 17** !

```bash
$ ./gradlew build
```

## Dict parser benchmarking

NOTE: Needs Python

```bash
$ ./gradlew benchmark:performBenchmark
```

## E2E regression tests

NOTE: Needs Python

```bash
$ ./gradlew e2e-tests:e2eRegression
```
