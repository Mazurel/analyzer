package org.analyzer.kotlin.differ

import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.parameters.arguments.argument
import com.github.ajalt.clikt.parameters.options.flag
import com.github.ajalt.clikt.parameters.options.option
import com.github.ajalt.clikt.parameters.types.file

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

  enum class ANSICommand(val value: String) {
    ERASE_IN_LINE("2K")
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

  fun ansiCommand(command: ANSICommand) {
    if (this.supportsColors) {
      this.currentLine.append("\u001B[${command.value}")
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

  fun clearLine() {
    this.ansiCommand(ANSICommand.ERASE_IN_LINE)
    this.write("\r")
    this.flush()
  }
}

class DiffCommand : CliktCommand() {
  val baselinePath by
      argument(name = "Baseline log path", help = "Path to the baseline file")
          .file(mustExist = true)
  val checkedPath by
      argument(name = "Checked log path", help = "Path to the checked file").file(mustExist = true)
  val collapseOk by option("-c", "--collapse-ok").flag(default = false)
  val debugMode by option("-d", "--debug").flag(default = false)
  val disableColors by option("-nc", "--no-colors").flag(default = false)

  override fun run() {
    val terminal = Terminal(colorsEnabled = !disableColors)
    val differ = Differ()

    //
    // Loading of the files
    //
    if (debugMode) {
      terminal.endLine() // We need additional space first
      differ.onLineLoaded { logType, logLine ->
        val lineNumber = logLine.lineNumber
        val timestampEpoch = logLine.timestamp.actualEpoch

        if (lineNumber % 100 == 0) {
          when (logType) {
            LogType.BASELINE -> {
              terminal.clearLine()
              terminal.write("Loaded line $lineNumber from Baseline $timestampEpoch")
              terminal.flush()
            }
            LogType.CHECKED -> {
              terminal.clearLine()
              terminal.write("Loaded line $lineNumber from Checked $timestampEpoch")
              terminal.flush()
            }
          }
        }
      }
    }

    val baseline = differ.loadBaseline(this.baselinePath)
    val checked = differ.loadChecked(this.checkedPath)

    //
    // Handling of line numbers
    //
    var lineNumber = 1

    differ.onOk { self, _ ->
      val lineNumberStr = lineNumber.toString().padStart(5, ' ')
      if (!collapseOk) {
        terminal.bold { write(lineNumberStr) }
        terminal.separate()
        terminal.green { write("Ok") }
        terminal.separate()
        terminal.write(self.content.trimEnd())
        terminal.endLine()
      }
      lineNumber += 1
    }

    differ.onMissing { other ->
      val lineNumberStr = lineNumber.toString().padStart(5, ' ')
      terminal.bold { write(lineNumberStr) }
      terminal.separate()
      terminal.red { write("Missing") }
      terminal.separate()
      terminal.write(other.content.trimEnd())
      terminal.endLine()
    }

    differ.onAdditional { self ->
      val lineNumberStr = lineNumber.toString().padStart(5, ' ')
      terminal.bold { write(lineNumberStr) }
      terminal.separate()
      terminal.red { write("Additional") }
      terminal.separate()
      terminal.write(self.content.trimEnd())
      terminal.endLine()
      lineNumber += 1
    }

    differ.compareLogs(baseline, checked)
  }
}

fun main(args: Array<String>) = DiffCommand().main(args)
