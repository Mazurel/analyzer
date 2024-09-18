package org.analyzer.kotlin.log.parsers

public val defaultParser = DictParser()

public enum class LogParserType(val parser: LogParser) {
  DICT(DictParser()),
  DRAIN(DrainParser()),
}
