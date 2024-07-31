/*
 * drain-java
 *
 * Copyright (c) 2021, Today - Brice Dutheil
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

plugins {
    `java-library`

    alias(libs.plugins.versions)
    alias(libs.plugins.download)
    alias(libs.plugins.gradle.extensions) apply false
}

description = "Drain Java Implementation"

group = "io.github.bric3.drain"

repositories {
    // Use Maven Central for resolving dependencies.
    mavenCentral()
}

plugins.withId("java-library") {
    configure<JavaPluginExtension> {
        withSourcesJar()
        withJavadocJar()
    }
}

dependencies {
    implementation(libs.jsr305)

    testImplementation(libs.assertj.core)
    testImplementation(libs.junit.jupiter.api)
    testRuntimeOnly(libs.junit.jupiter.engine)
}
java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
    kotlinOptions {
        jvmTarget = "17"
    }
}
