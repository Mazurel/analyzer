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

class Terminal(val colorsEnabled: Boolean) {
  enum class ANSIStyle(val value: Int) {
    RESET(0),
    BOLD(1),
    BLACK(30),
    RED(31),
    GREEN(32),
    YELLOW(33),
    BLUE(34)
  }

  val currentLine = StringBuilder()
  var inScope = false

  val supportsColors: Boolean
    get() = this.colorsEnabled // TODO: Detect based on env

  fun ansiStyle(command: ANSIStyle) {
    if (this.supportsColors) {
      this.currentLine.append("\u001B[${command.value}m")
    }
  }

  fun write(text: String) {
    this.currentLine.append(text)
  }

  fun endLine() {
    this.write("\n")
    this.flush()
  }

  fun separate() {
    this.write(" | ")
  }

  fun flush() {
    print(this.currentLine.toString())
    this.currentLine.clear()
  }

  fun resetStyle() {
    this.ansiStyle(ANSIStyle.RESET)
  }

  inline fun scopedStyle(vararg styles: ANSIStyle, scope: Terminal.() -> Unit) {
    if (inScope) {
      throw RuntimeException("Terminal is already in scope !")
    }

    inScope = true
    for (style in styles) {
      this.ansiStyle(style)
    }
    this.scope()
    this.resetStyle()
    inScope = false
  }

  inline fun bold(scope: Terminal.() -> Unit) {
    this.scopedStyle(ANSIStyle.BOLD) { this.scope() }
  }

  inline fun red(scope: Terminal.() -> Unit) {
    this.scopedStyle(ANSIStyle.RED) { this.scope() }
  }

  inline fun green(scope: Terminal.() -> Unit) {
    this.scopedStyle(ANSIStyle.GREEN) { this.scope() }
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
    val terminal = Terminal(colorsEnabled = !disableColors)
    val baseline = LogFile(this.baselinePath.bufferedReader())
    val checked = LogFile(this.checkedPath.bufferedReader())
    var lineNumber = 1

    for ((checkedLine, baselineLine) in getDiffPairs(baseline, checked)) {
      var lineNumberStr = lineNumber.toString()
      lineNumberStr = lineNumberStr.padStart(5, ' ')
      when {
        checkedLine != null && baselineLine != null -> {
          if (!collapseOk) {
            terminal.bold { write(lineNumberStr) }
            terminal.separate()
            terminal.green { write("Ok") }
            terminal.separate()
            terminal.write(checkedLine.content.trimEnd())
            terminal.endLine()
          }
          lineNumber += 1
        }
        checkedLine != null && baselineLine == null -> {
          terminal.bold { write(lineNumberStr) }
          terminal.separate()
          terminal.red { write("Additional") }
          terminal.separate()
          terminal.write(checkedLine.content.trimEnd())
          terminal.endLine()
          lineNumber += 1
        }
        checkedLine == null && baselineLine != null -> {
          terminal.bold { write(lineNumberStr) }
          terminal.separate()
          terminal.red { write("Missing") }
          terminal.separate()
          terminal.write(baselineLine.content.trimEnd())
          terminal.endLine()
        }
        checkedLine == null && baselineLine == null -> {
          assert(false) { "Unreachable - we should never get here" }
        }
      }
    }
  }
}

fun main(args: Array<String>) = DiffCommand().main(args)
