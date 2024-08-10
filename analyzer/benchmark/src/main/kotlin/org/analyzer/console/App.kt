package org.analyzer.kotlin.console

import com.varabyte.kotter.foundation.*
import com.varabyte.kotter.foundation.input.*
import com.varabyte.kotter.foundation.text.*
import com.varabyte.kotter.runtime.render.*
import com.varabyte.kotter.terminal.system.SystemTerminal
import com.varabyte.kotter.terminal.virtual.VirtualTerminal
import kotlin.io.path.bufferedReader
import kotlin.io.path.bufferedWriter
import org.analyzer.kotlin.log.LogLine
import org.analyzer.kotlin.log.parsers.dict.DictParser

fun main(args: Array<String>) {
  val inArguments = Arguments().fetchArguments(args)
  val errs = inArguments.collectErrors()
  session(
      terminal =
          listOf(
                  { SystemTerminal() },
                  { VirtualTerminal.create() },
              )
              .firstSuccess()) {
        var status by liveVarOf("")
        section {
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
                try {
                  val inFileName = inArguments.inputFile!!.toAbsolutePath().normalize()
                  val outFileName = inArguments.outputFile!!.toAbsolutePath().normalize()

                  val dictParser = DictParser()
                  val logLines =
                      inFileName.bufferedReader().readLines().mapIndexed { i, line ->
                        val ln = LogLine(line + 1, i, parser = dictParser)
                        status = "Loaded line ${i + 1}"
                        ln
                      }

                  if (logLines.size == 0) {
                    status = "Input file is empty ? No lines found at ${inFileName.toString()}"
                    signal()
                  }

                  val outFile = outFileName.bufferedWriter()
                  Csv(logLines).writeFile(outFile)
                  outFile.close()
                  val ft = logLines[0].timestamp.string != ""
                  status = "Success ! Timestamp Extracted = $ft"
                } catch (err: Exception) {
                  status = "Failed with error: $err"
                }
                signal()
              }
            }
      }
}
