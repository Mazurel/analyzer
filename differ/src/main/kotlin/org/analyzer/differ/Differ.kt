package org.analyzer.kotlin.differ

import org.analyzer.kotlin.log.LogFile
import org.analyzer.kotlin.log.LogLine

enum class DifferEntryType {
  OK,
  MISSING,
  ADDITIONAL
}

data class DifferEntry(
    val type: DifferEntryType,
    val self: LogLine?,
    val other: LogLine?,
)

class Differ(val differEntries: List<DifferEntry>) {
  private val handlers: MutableMap<DifferEntryType, (DifferEntry) -> Unit> = mutableMapOf()

  fun resolve() {
    for (entry in this.differEntries) {
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

  companion object {
    fun buildDiffer(baseline: LogFile, checked: LogFile): Differ {
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

      return Differ(entries)
    }
  }
}
