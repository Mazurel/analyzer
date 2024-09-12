package org.analyzer.kotlin.console

import com.varabyte.kotter.foundation.*
import com.varabyte.kotter.foundation.input.*
import com.varabyte.kotter.foundation.text.*
import com.varabyte.kotter.runtime.render.*
import com.varabyte.kotter.terminal.system.SystemTerminal
import kotlin.io.path.bufferedReader
import kotlin.io.path.bufferedWriter
import org.analyzer.kotlin.log.LogLine
import org.analyzer.kotlin.log.parsers.DrainParser

inline fun perform_benchmark(args: Arguments, reportStatus: (String) -> Unit) {
  try {
    val inFileName = args.inputFile!!.toAbsolutePath().normalize()
    val outFileName = args.outputFile!!.toAbsolutePath().normalize()

    val dictParser = DrainParser()
    val logLines =
        inFileName.bufferedReader().readLines().mapIndexed { i, line ->
          LogLine(line, i + 1, parser = dictParser)
        }

    if (logLines.size == 0) {
      reportStatus("Input file is empty ? No lines found at ${inFileName.toString()}")
      return
    }

    val outFile = outFileName.bufferedWriter()
    Csv(logLines).writeFile(outFile)
    outFile.close()
    val ft = logLines[0].timestamp.string != ""
    reportStatus("Success ! Timestamp Extracted = $ft")
  } catch (err: Exception) {
    val stackTraceStr = err.stackTraceToString()
    reportStatus("Failed with error: $err\nStack trace:\n$stackTraceStr")
  }
}

fun tui_ui(args: Arguments): Int {
  val errs = args.collectErrors()
  session(
      terminal =
          listOf(
                  { SystemTerminal() },
                  // { VirtualTerminal.create() },
              )
              .firstSuccess()) {
        var status by liveVarOf("")
        section {
              bold { textLine("== Dict Parser benchmark ==") }
              for (err in errs) {
                red(isBright = true) { textLine("- $err") }
              }
              if (status.length > 0) {
                textLine(status)
              }
            }
            .runUntilSignal {
              if (errs.size > 0) {
                signal()
              } else {
                perform_benchmark(args) { status = it }
                signal()
              }
            }
      }
  return 0
}

fun cli_ui(args: Arguments): Int {
  val errs = args.collectErrors()
  for (err in errs) {
    println("- $err")
  }
  if (errs.size > 0) {
    return 1
  }
  perform_benchmark(args) { println(it) }
  return 0
}

fun main(args: Array<String>) {
  val inArguments = Arguments().fetchArguments(args)

  var exit_code: Int
  try {
    exit_code = tui_ui(inArguments)
  } catch (err: java.lang.IllegalStateException) {
    exit_code = cli_ui(inArguments)
  }
  System.exit(exit_code)
}
