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
        private val parser: LogParser? = null,
        timestampFormat: String? = null
) {
    private val formattingResult = format.matchLine(line)
    private var innerPatternID: PatternID? = null

    public val content = formattingResult.content
    public val metadata = formattingResult.fields
    public val patternID: PatternID?
        get() = innerPatternID
    public val timestamp = Timestamp(this, timestampFormat)

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
        private val parser: LogParser? = dictParser,
        lineLoaded: (LogLine) -> Unit = { }
) {
    public val lines =
            file.readLines()
                    .mapIndexed { i, line ->
                        val l = LogLine(line, lineNumber = i + 1, format = format, parser = parser)
                        lineLoaded(l)
                        l
                    }
                    .toList()

    companion object {
        fun fromPath(path: String): LogFile = LogFile(FileReader(path).buffered())
    }

    init {
        lines.forEach { it.extractPatternIfPossible() }
        fillTimestamps()
    }

    private fun fillTimestamps() {
        for (i in 0 until lines.size) {
            var j = 1
            // We find closest line with timestamp,
            // when `i`th line has no timestamp.
            while (lines[i].timestamp.epoch == null) {
                val i1 = i - j
                val i2 = i + j

                if (i1 < 0 && i2 >= lines.size) {
                    throw RuntimeException("Too few timestamps in the log file")
                }

                if (i1 >= 0 && lines[i1].timestamp.epoch != null) {
                    lines[i].timestamp.injectedEpoch = lines[i1].timestamp.epoch
                }
                if (i2 < lines.size && lines[i2].timestamp.epoch != null) {
                    lines[i].timestamp.injectedEpoch = lines[i2].timestamp.epoch
                }
            }
        }
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
                    abs((a.timestamp.epoch!! - b.timestamp.epoch!!).toInt())
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
                    abs((a.timestamp.epoch!! - b.timestamp.epoch!!).toInt())
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
