#!/usr/bin/env bash

./gradlew console-app:shadowJar && java -jar ./console-app/build/libs/console-frontend-1.0.jar
