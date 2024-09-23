package org.analyzer.kotlin.differ

import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.parameters.arguments.argument
import com.github.ajalt.clikt.parameters.options.flag
import com.github.ajalt.clikt.parameters.options.option
import com.github.ajalt.clikt.parameters.types.file
import kotlin.math.absoluteValue
import org.analyzer.kotlin.terminal.Terminal

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
    val diffMinTreshold = 0.03
    val terminal = Terminal(colorsEnabled = !disableColors)
    val differ = Differ()

    //
    // Loading of the files
    //
    if (debugMode) {
      terminal.endLine() // We need additional space first
      differ.onLineLoaded { logType, logLine ->
        val lineNumber = logLine.lineNumber
        val timestampEpoch = logLine.timestamp.string

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

    val baselineThreshold =
        {
          val firstLine = baseline.lines.first().timestamp.epoch!!
          val lastLine = baseline.lines.last().timestamp.epoch!!
          val totalTimestampDifference = lastLine - firstLine
          totalTimestampDifference * diffMinTreshold
        }()

    val checkedThreshold =
        {
          val firstLine = checked.lines.first().timestamp.epoch!!
          val lastLine = checked.lines.last().timestamp.epoch!!
          val totalTimestampDifference = lastLine - firstLine
          totalTimestampDifference * diffMinTreshold
        }()

    val timeEqualThreshold = maxOf(baselineThreshold, checkedThreshold)

    //
    // Handling of line numbers
    //
    var lineNumber = 1

    differ.onOk { self, other ->
      val lineNumberStr = lineNumber.toString().padStart(5, ' ')
      val selfTime = self.timestamp.epoch!! // safety: should be never null after matching
      val otherTime = other.timestamp.epoch!! // safety: should be never null after matching
      val timeDifference = (selfTime - otherTime).absoluteValue
      val timeConsideredTheSame = timeDifference < timeEqualThreshold
      val contentTheSame = self.content == other.content

      if (timeConsideredTheSame) {
        if (!collapseOk) {

          terminal.session {
            bold { write(lineNumberStr) }
            separate()
            if (contentTheSame) {
              green { write("Perfect") }
            } else {
              green { write("Ok") }
            }
            separate()
            write(self.content.trimEnd())
            if (!contentTheSame) {
              separate()
              faint { write("Baseline: ${other.content}") }
            }
            endLine()
          }
        }
      } else {
        terminal.session {
          bold { write(lineNumberStr) }
          separate()
          yellow { write("Incorrect Time") }
          separate()
          write(self.content.trimEnd())
          // TODO: Add a way to get units from timestamp !
          // separate()
          // faint { write("Time difference |$selfTime - $otherTime| = $timeDifference") }
          if (!contentTheSame) {
            separate()
            faint { write("Baseline: ${other.content}") }
          }
          endLine()
        }
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
