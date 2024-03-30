package org.analyzer.kotlin.log

import java.io.BufferedReader
import java.io.FileReader
import org.analyzer.kotlin.log.parsers.LogParser
import org.analyzer.kotlin.log.parsers.PatternID
import org.analyzer.kotlin.log.parsers.dict.DictParser

public val dictParser = DictParser()

class LogLine(
        public val line: String,
        public val lineNumber: Int,
        public val format: LogFormat = LogFormat.basic(),
        private val parser: LogParser? = null
) {
    private val formattingResult = format.matchLine(line)
    private var innerPatternID: PatternID? = null

    public val content = formattingResult.content
    public val metadata = formattingResult.fields
    public val patternID: PatternID?
        get() = innerPatternID

    init {
        if (parser != null) {
            // If parser is available, use it
            innerPatternID = parser.learnLine(line)
        }
    }

    public fun extractPatternIfPossible() {
        if (parser != null) {
            innerPatternID = parser.extractPattern(line)
        }
    }
}

data class Log2Log(
        public val baseline: MutableList<LogLine> = mutableListOf(),
        public val checked: MutableList<LogLine> = mutableListOf()
)

class LogFile(
        file: BufferedReader,
        format: LogFormat = LogFormat.basic(),
        private val parser: LogParser? = dictParser
) {
    public val lines =
            file.readLines()
                    .mapIndexed { i, line ->
                        LogLine(line, lineNumber = i, format = format, parser = parser)
                    }
                    .toList()

    init {
        lines.forEach { it.extractPatternIfPossible() }
    }

    companion object {
        fun fromPath(path: String): LogFile = LogFile(FileReader(path).buffered())
    }

    public val hasParser
        get() = parser != null

    public fun matchWith(checked: LogFile) {
        if (!hasParser) {
            throw RuntimeException("Baseline file is missing parser")
        }

        if (!checked.hasParser) {
            throw RuntimeException("Checked file is missing parser")
        }

        val perTemplateLogs: MutableMap<PatternID, Log2Log> = mutableMapOf()

        lines.forEach { perTemplateLogs.getOrPut(it.patternID!!) { Log2Log() }.baseline.add(it) }
        checked.lines.forEach {
            perTemplateLogs.getOrPut(it.patternID!!) { Log2Log() }.checked.add(it)
        }
    }
}
