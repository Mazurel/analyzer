package org.analyzer.kotlin.log

import kotlin.time.Duration
import kotlinx.datetime.LocalDateTime

import java.io.BufferedReader
import java.io.FileReader

import org.analyzer.kotlin.log.parsers.LogParser
import org.analyzer.kotlin.log.parsers.PatternID
import org.analyzer.kotlin.log.parsers.dict.DictParser
import org.analyzer.kotlin.monge.BitonicMongeArray

public val dictParser = DictParser()

class Timestamp(
    private val line: String,
    private val format: LogFormat,
    private val lineNumber: Int,
) {
    init {
        TODO("Implement timestamp mechanics")
    }
}

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

    public fun matchWith(checked: LogFile): List<LogLine?> {
        if (!hasParser) {
            throw RuntimeException("Baseline file is missing parser")
        }

        if (!checked.hasParser) {
            throw RuntimeException("Checked file is missing parser")
        }

        var resultMatching: MutableList<LogLine?> = MutableList(lines.size) { null }

        val perTemplateLogs: MutableMap<PatternID, Log2Log> = mutableMapOf()

        lines.forEach { perTemplateLogs.getOrPut(it.patternID!!) { Log2Log() }.baseline.add(it) }
        checked.lines.forEach {
            perTemplateLogs.getOrPut(it.patternID!!) { Log2Log() }.checked.add(it)
        }

        for (patternId in perTemplateLogs.keys) {
            val log2log = perTemplateLogs[patternId]
            if (log2log == null) {
                continue
            }

            if (log2log.baseline.size > log2log.checked.size) {
                TODO()
            }
            else {
                // BitonicMongeArray(log2log.baseline, log2log.checked) { a, b -> }
                TODO()
            }
        }

        return resultMatching.toList()
    }
}
