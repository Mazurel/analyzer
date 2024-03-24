package org.analyzer.kotlin.log

import java.io.BufferedReader
import java.io.FileReader

import org.analyzer.kotlin.log.parsers.LogParser
import org.analyzer.kotlin.log.parsers.dict.DictParser

public val dictParser = DictParser()

class LogLine(line: String, val lineNumber: Int, format: LogFormat = LogFormat.basic(), parser: LogParser? = null) {
    private val formattingResult = format.matchLine(line)

    public val content = formattingResult.content
    public val metadata = formattingResult.fields

    init {
        if (parser != null) {
            // If parser is available, use it
            parser.learnLine(line)
        }
    }
}

class LogFile(file: BufferedReader, format: LogFormat = LogFormat.basic(), parser: LogParser? = dictParser) {
    public val lines =
        file.readLines().mapIndexed { i, line -> LogLine(line, lineNumber = i, format = format, parser = parser) }.toList()

    companion object {
        fun fromPath(path: String): LogFile = LogFile(FileReader(path).buffered())
    }
}
