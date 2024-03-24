package org.analyzer.kotlin.log.parsers

import java.io.BufferedReader
import java.io.FileReader
import java.util.UUID

typealias PatternID = UUID

interface LogParser {
    public fun extractPattern(line: String): PatternID
    public fun learnLine(line: String): PatternID?
}
