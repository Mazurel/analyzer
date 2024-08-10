package org.analyzer.kotlin.console

import java.io.BufferedWriter
import org.analyzer.kotlin.log.LogLine

class Csv(val logLines: List<LogLine>) {
  companion object {
    const val SEPARATOR: Char = ','
  }

  public fun writeFile(fileWriter: BufferedWriter) {
    fileWriter.write(this.getHeader())
    this.logLines.forEach { fileWriter.write(this.getRow(it)) }
  }

  private fun getHeader(): String {
    return StringBuilder()
        .append("LineId")
        .append(SEPARATOR)
        .append("Content")
        .append(SEPARATOR)
        .append("EventId")
        .append(SEPARATOR)
        .append("Template")
        .append("\n")
        .toString()
  }

  private fun getRow(line: LogLine): String {
    return StringBuilder()
        .append(line.lineNumber.toString())
        .append(SEPARATOR)
        .append(this.sanitizeFieldContent(line.line))
        .append(SEPARATOR)
        .append(line.patternID.toString())
        .append(SEPARATOR)
        .append(this.sanitizeFieldContent(line.pattern!!))
        .append('\n')
        .toString()
  }

  private fun sanitizeFieldContent(field: String): String {
    if (!field.contains(SEPARATOR)) {
      return field
    }

    val sb = StringBuilder()
    sb.append('"')

    field.toCharArray().forEach {
      when {
        it == '"' -> {
          sb.append("\"\"")
        }
        else -> {
          sb.append(it)
        }
      }
    }

    return sb.append('"').toString()
  }
}
