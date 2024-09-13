package org.analyzer.kotlin.differ

import java.io.File
import org.analyzer.kotlin.log.LogFile
import org.analyzer.kotlin.log.LogLine

enum class DifferEntryType {
  OK,
  MISSING,
  ADDITIONAL
}

enum class LogType {
  BASELINE(),
  CHECKED
}

data class DifferEntry(
    val type: DifferEntryType,
    val self: LogLine?,
    val other: LogLine?,
)

class Differ() {
  private val handlers: MutableMap<DifferEntryType, (DifferEntry) -> Unit> = mutableMapOf()
  private var lineLoadedHandler: ((LogType, LogLine) -> Unit)? = null

  public fun loadBaseline(logs: File): LogFile {
    val reader = logs.bufferedReader()
    return LogFile(reader) {
      if (this.lineLoadedHandler != null) {
        this.lineLoadedHandler!!(LogType.BASELINE, it)
      }
    }
  }

  public fun loadChecked(logs: File): LogFile {
    val reader = logs.bufferedReader()
    return LogFile(reader) {
      if (this.lineLoadedHandler != null) {
        this.lineLoadedHandler!!(LogType.CHECKED, it)
      }
    }
  }

  public fun compareLogs(baseline: LogFile, checked: LogFile) {
    val entries: MutableList<DifferEntry> = mutableListOf()
    if (checked.lines.size >= baseline.lines.size) {
      val matchedLinesFromBaseline = checked.matchWith(baseline)
      matchedLinesFromBaseline.withIndex().forEach { (i, lineFromBaseline) ->
        val checkedLine = checked.lines[i]
        if (lineFromBaseline == null) {
          entries.add(DifferEntry(DifferEntryType.ADDITIONAL, checkedLine, null))
        } else {
          entries.add(DifferEntry(DifferEntryType.OK, checkedLine, lineFromBaseline))
        }
      }
    } else {
      val matchedLinesFromChecked = baseline.matchWith(checked)
      matchedLinesFromChecked.withIndex().forEach { (i, lineFromChecked) ->
        val baselineLine = baseline.lines[i]
        if (lineFromChecked == null) {
          entries.add(DifferEntry(DifferEntryType.MISSING, null, baselineLine))
        } else {
          entries.add(DifferEntry(DifferEntryType.OK, lineFromChecked, baselineLine))
        }
      }
    }

    for (entry in entries) {
      handlers.get(entry.type).let { func ->
        if (func == null) {
          throw RuntimeException("Unresolvable differ entry: $entry")
        }

        func(entry)
      }
    }
  }

  fun onOk(handler: (LogLine, LogLine) -> Unit) {
    this.handlers.put(DifferEntryType.OK) { handler(it.self!!, it.other!!) }
  }

  fun onMissing(handler: (LogLine) -> Unit) {
    this.handlers.put(DifferEntryType.MISSING) { handler(it.other!!) }
  }

  fun onAdditional(handler: (LogLine) -> Unit) {
    this.handlers.put(DifferEntryType.ADDITIONAL) { handler(it.self!!) }
  }

  fun onLineLoaded(handler: (LogType, LogLine) -> Unit) {
    this.lineLoadedHandler = handler
  }
}
