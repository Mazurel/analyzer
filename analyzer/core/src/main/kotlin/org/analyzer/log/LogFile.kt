package org.analyzer.kotlin.log

import java.io.BufferedReader
import java.io.FileReader

import kotlin.math.abs

import org.analyzer.kotlin.log.parsers.LogParser
import org.analyzer.kotlin.log.parsers.PatternID
import org.analyzer.kotlin.log.parsers.dict.DictParser
import org.analyzer.kotlin.monge.BitonicMongeArray

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
    public val timestamp: Timestamp
        get() = Timestamp(this)

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
                        LogLine(line, lineNumber = i + 1, format = format, parser = parser)
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

    public fun lineAt(lineNumber: Int): LogLine {
        return lines[lineNumber - 1]
    }

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
                BitonicMongeArray(log2log.checked, log2log.baseline) { a: LogLine, b: LogLine ->
                    abs((a.timestamp.extractEpoch()!! - b.timestamp.extractEpoch()!!).toInt())
                }
                        .perfmatch()
                        .forEachIndexed { i, matchingResult ->
                            if (matchingResult != null) {
                                resultMatching[matchingResult.second.lineNumber - 1] =
                                        log2log.checked[i]
                            }
                        }
            } else {
                BitonicMongeArray(log2log.baseline, log2log.checked) { a: LogLine, b: LogLine ->
                    abs((a.timestamp.extractEpoch()!! - b.timestamp.extractEpoch()!!).toInt())
                }
                        .perfmatch()
                        .forEachIndexed { i, matchingResult ->
                            if (matchingResult != null) {
                                resultMatching[log2log.baseline[i].lineNumber - 1] =
                                        matchingResult.second
                            }
                        }
            }
        }

        return resultMatching.toList()
    }
}
