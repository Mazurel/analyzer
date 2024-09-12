package org.analyzer.kotlin.log

import java.io.BufferedReader
import java.io.FileReader
import kotlin.math.abs
import org.analyzer.kotlin.log.parsers.*
import org.analyzer.kotlin.monge.BitonicMongeArray

data class Log2Log(
    public val baseline: MutableList<LogLine> = mutableListOf(),
    public val checked: MutableList<LogLine> = mutableListOf()
)

class LogFile(
    inputFile: BufferedReader,
    private val format: LogFormat = LogFormat.basic(),
    private val parser: LogParser? = defaultParser,
    lineLoadedCallback: (LogLine) -> Unit = {}
) {
  public val lines: List<LogLine>

  public val hasParser
    get() = parser != null

  companion object {
    fun fromPath(path: String): LogFile = LogFile(FileReader(path).buffered())
  }

  init {
    lines = this.loadLines(inputFile, lineLoadedCallback)
    this.fillTimestamps()
  }

  private fun loadLines(inputFile: BufferedReader, lineLoadedCB: (LogLine) -> Unit): List<LogLine> {
    return inputFile
        .readLines()
        .mapIndexed { i, line ->
          LogLine(line, lineNumber = i + 1, format = this.format, parser = this.parser).let {
            lineLoadedCB(it)
            it
          }
        }
        .toList()
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

        j += 1
      }
    }
  }

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
    checked.lines.forEach { perTemplateLogs.getOrPut(it.patternID!!) { Log2Log() }.checked.add(it) }

    for (patternId in perTemplateLogs.keys) {
      val log2log = perTemplateLogs[patternId]
      if (log2log == null) {
        continue
      }

      if (log2log.baseline.size <= log2log.checked.size) {
        BitonicMongeArray(log2log.baseline, log2log.checked) { a: LogLine, b: LogLine ->
              abs(a.timestamp.epoch!! - b.timestamp.epoch!!)
            }
            .perfmatch()
            .forEachIndexed { i, matchingResult ->
              assert(matchingResult != null) { "Due to what perfmatch guarantees" }
              resultMatching[log2log.baseline[i].lineNumber - 1] = matchingResult!!.second
            }
      } else {
        BitonicMongeArray(log2log.checked, log2log.baseline) { a: LogLine, b: LogLine ->
              abs(a.timestamp.epoch!! - b.timestamp.epoch!!)
            }
            .perfmatch()
            .forEachIndexed { i, matchingResult ->
              assert(matchingResult != null) { "Due to what perfmatch guarantees" }
              resultMatching[matchingResult!!.second.lineNumber - 1] = log2log.checked[i]
            }
      }
    }

    return resultMatching.toList()
  }
}
