package org.analyzer.kotlin.console

import com.varabyte.kotter.foundation.*
import com.varabyte.kotter.foundation.input.*
import com.varabyte.kotter.foundation.text.*
import com.varabyte.kotter.runtime.render.*
import kotlin.io.path.bufferedReader
import kotlin.io.path.bufferedWriter
import org.analyzer.kotlin.log.LogFile

fun main(args: Array<String>) {
  session {
    val inArguments = Arguments().fetchArguments(args)
    val errs = inArguments.collectErrors()
    section {
          for (err in errs) {
            red(isBright = true) { textLine("- $err") }
          }
        }
        .run {}

    if (errs.size == 0) {
      var status by liveVarOf("Initializing ...")
      section { textLine(status) }
          .runUntilSignal {
            try {
              val inFileName = inArguments.inputFile!!.toAbsolutePath().normalize()
              val outFileName = inArguments.outputFile!!.toAbsolutePath().normalize()

              val file =
                  LogFile(inFileName.bufferedReader()) {
                    if (it.lineNumber % 10 == 0) {
                      status = "Loading line ${it.lineNumber} - ${it.humanReadablePattern}"
                    }
                  }

              if (file.lines.size == 0) {
                status = "Input file is empty ? No lines found at ${inFileName.toString()}"
                signal()
              }

              val outFile = outFileName.bufferedWriter()

              outFile.write("LineId,Content,EventId,Template\n")
              for (line in file.lines) {
                val pattern = line.humanReadablePattern
                outFile.write(
                    "${line.lineNumber},${line.content},${line.patternID!!.toString()},${pattern}\n")
                status =
                    "Writing to file ${outFileName.toString()} line number ${line.lineNumber} ..."
              }

              outFile.close()
            } catch (err: Exception) {
              status = "ERR: $err"
            }
            signal()
          }
    }
  }
}
