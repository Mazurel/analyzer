package org.analyzer.kotlin.console

import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.parameters.arguments.argument
import com.github.ajalt.clikt.parameters.types.enum
import com.github.ajalt.clikt.parameters.types.file
import kotlin.io.path.bufferedReader
import kotlin.io.path.bufferedWriter
import org.analyzer.kotlin.log.LogLine
import org.analyzer.kotlin.log.parsers.LogParserType
import org.analyzer.kotlin.terminal.Terminal

enum class ExitCode(val code: Int) {
  TIMESTAMP_FOUND(0),
  TIMESTAMP_NOT_FOUND(1),
  INTERNAL_ERROR(2)
}

class BenchmarkCommand : CliktCommand() {
  val inputPath by argument().file(mustExist = true)
  val destinationPath by argument().file(mustExist = false)
  val parserType by argument().enum<LogParserType>()

  val logLines: Lazy<List<LogLine>> = lazy {
    val inFileName = this.inputPath.normalize()
    inFileName.bufferedReader().readLines().mapIndexed { i, line ->
      LogLine(line, i + 1, parser = parserType.parser)
    }
  }

  fun isTimestampFound(): Boolean {
    return this.logLines.value[0].timestamp.string != ""
  }

  fun terminate(exitCode: ExitCode) {
    System.exit(exitCode.code)
  }

  override fun run() {
    val terminal = Terminal()

    try {
      val outFileName = this.destinationPath.normalize()

      if (this.logLines.value.size == 0) {
        terminal.session {
          red { write("Input file is empty? No lines found!") }
          endLine()
        }
        this.terminate(ExitCode.INTERNAL_ERROR)
      }

      outFileName.bufferedWriter().let {
        Csv(this.logLines.value).writeFile(it)
        it.close()
      }

      when (this.isTimestampFound()) {
        false -> {
          terminal.session {
            write("Success ! Timestamp Extracted = ")
            red { write("no") }
            endLine()
          }
          this.terminate(ExitCode.TIMESTAMP_NOT_FOUND)
        }
        true -> {
          terminal.session {
            write("Success ! Timestamp Extracted = ")
            green { write("yes") }
            endLine()
          }
          this.terminate(ExitCode.TIMESTAMP_FOUND)
        }
      }
    } catch (err: Exception) {
      val stackTraceStr = err.stackTraceToString()
      terminal.session {
        red { write("Failed with error: $err") }
        endLine()
        write("Stack trace:")
        endLine()
        write("$stackTraceStr")
        endLine()
      }
      this.terminate(ExitCode.INTERNAL_ERROR)
    }
  }
}

fun main(args: Array<String>) = BenchmarkCommand().main(args)
