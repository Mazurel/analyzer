package org.analyzer.kotlin.console

import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.parameters.arguments.argument
import com.github.ajalt.clikt.parameters.options.flag
import com.github.ajalt.clikt.parameters.options.option
import com.github.ajalt.clikt.parameters.types.file
import org.analyzer.kotlin.log.LogFile
import org.analyzer.kotlin.log.LogLine

class DifferAcumulator {
  private val linesLeft: MutableList<LogLine?> = mutableListOf()
  private val linesRight: MutableList<LogLine?> = mutableListOf()
  private var index = 0

  val left: List<LogLine?>
    get() = this.linesLeft.toList()

  val right: List<LogLine?>
    get() = this.linesRight.toList()

  fun lineLeft(line: LogLine) {
    this.linesLeft.add(line)
  }

  fun lineRight(line: LogLine) {
    this.linesRight.add(line)
  }

  fun finishLine() {
    if (this.linesLeft.size <= index) {
      this.linesLeft.add(null)
    }
    if (this.linesRight.size <= index) {
      this.linesRight.add(null)
    }
    index += 1

    assert(this.linesLeft.size > index)
    assert(this.linesRight.size > index)
  }
}

fun getDiffPairs(baseline: LogFile, checked: LogFile): List<Pair<LogLine?, LogLine?>> {
  val differ = DifferAcumulator()

  if (checked.lines.size >= baseline.lines.size) {
    val matchedLinesFromBaseline = checked.matchWith(baseline)
    matchedLinesFromBaseline.withIndex().forEach { (i, lineFromBaseline) ->
      differ.lineLeft(checked.lines[i])
      if (lineFromBaseline != null) {
        differ.lineRight(lineFromBaseline)
      }
      differ.finishLine()
    }
  } else {
    val matchedLinesFromChecked = baseline.matchWith(checked)
    matchedLinesFromChecked.withIndex().forEach { (i, lineFromChecked) ->
      differ.lineRight(baseline.lines[i])
      if (lineFromChecked != null) {
        differ.lineLeft(lineFromChecked)
      }
      differ.finishLine()
    }
  }

  return differ.left.zip(differ.right).toList()
}

enum class ANSIColor(val value: Int) {
  RESET(0),
  BOLD(1),
  BLACK(30),
  RED(31),
  GREEN(32),
  YELLOW(33),
  BLUE(34);

  override fun toString(): String {
    return "\u001B[${this.value}m"
  }
}

class DiffCommand : CliktCommand() {
  val baselinePath by
      argument(name = "Baseline log path", help = "Path to the baseline file")
          .file(mustExist = true)
  val checkedPath by
      argument(name = "Checked log path", help = "Path to the checked file").file(mustExist = true)
  val collapseOk by option("-c", "--collapse-ok").flag(default = false)
  val disableColors by option("-nc", "--no-colors").flag(default = false)

  override fun run() {
    val baseline = LogFile(this.baselinePath.bufferedReader())
    val checked = LogFile(this.checkedPath.bufferedReader())
    var lineNumber = 1
    var wasPreviousOk = false

    for ((checkedLine, baselineLine) in getDiffPairs(baseline, checked)) {
      val lineBuilder = StringBuilder()
      var lineNumberStr = lineNumber.toString()
      var shouldPrint = true
      lineNumberStr = lineNumberStr.padStart(5, ' ')
      lineBuilder.append("${lineNumberStr} | ")
      when {
        checkedLine != null && baselineLine != null -> {
          if (collapseOk) {
            shouldPrint = false
          }
          lineBuilder.append("${ANSIColor.GREEN}OK${ANSIColor.RESET} | ${checkedLine.content}")
          lineNumber += 1
        }
        checkedLine != null && baselineLine == null -> {
          lineBuilder.append(
              "${ANSIColor.RED}ADDITIONAL${ANSIColor.RESET} | ${checkedLine.content}")
          lineNumber += 1
        }
        checkedLine == null && baselineLine != null -> {
          lineBuilder.append("${ANSIColor.RED}MISSING${ANSIColor.RESET} | ${baselineLine.content}")
        }
        checkedLine == null && baselineLine == null -> {
          assert(false) { "Unreachable - we should never get here" }
        }
      }
      if (shouldPrint) {
        println(lineBuilder.toString())
      }
    }
  }
}

fun main(args: Array<String>) = DiffCommand().main(args)
