package org.analyzer.kotlin.console

import com.varabyte.kotter.foundation.*
import com.varabyte.kotter.foundation.input.*
import com.varabyte.kotter.foundation.text.*
import com.varabyte.kotter.runtime.render.*
import java.nio.file.Path
import java.nio.file.NoSuchFileException
import kotlin.io.path.Path
import kotlin.io.path.writeLines
import kotlin.io.path.readLines
import kotlin.io.path.bufferedReader
import kotlin.io.path.bufferedWriter
import kotlin.io.path.absolute

import org.analyzer.kotlin.log.parsers.LogParser
import org.analyzer.kotlin.log.LogFile
import org.analyzer.kotlin.log.parsers.dict.DictParser

class Arguments(public var inputFile: Path? = null, public var outputFile: Path? = null) {
    private val existingErrors = mutableListOf<String>()

    fun collectErrors(): List<String> {
        val ls: MutableList<String> = mutableListOf()

        if (inputFile == null) {
            ls.add("Input file not specified, please use `if=...`")
        }

        if (inputFile == null) {
            ls.add("Output file not specified, please use `of=...`")
        }

        for (err in existingErrors) {
            ls.add(err)
        }

        return ls.toList()
    }

    fun fetchArguments(args: Array<String>): Arguments {
        for (arg in args) {
            when {
                arg.startsWith("if=") -> {
                    inputFile = Path(arg.slice(3..arg.length - 1))
                }
                arg.startsWith("of=") -> {
                    outputFile = Path(arg.slice(3..arg.length - 1))
                }
                else -> {
                    existingErrors.add("Unknown argument: $arg")
                }
            }
        }
        return this
    }
}

fun main(args: Array<String>) {
    session {
        val inArguments = Arguments().fetchArguments(args)
        val errs = inArguments.collectErrors()
        section {
            for (err in errs) {
                red(isBright = true) { textLine("- $err") }
            }
        }.run {}

        if (errs.size == 0) {
            var status by liveVarOf("Initializing ...")
            section {
                textLine(status)
            }.runUntilSignal {
                try {
                    val inFileName = inArguments.inputFile!!.toAbsolutePath().normalize()
                    val outFileName = inArguments.outputFile!!.toAbsolutePath().normalize()

                    val file = LogFile(inFileName.bufferedReader()) {
                        status = "Loading line ${it.lineNumber} from ${inFileName.toString()}"
                    }

                    if (file.lines.size == 0) {
                        status = "Input file is empty ? No lines found at ${inFileName.toString()}"
                        signal()
                    }

                    val outFile = outFileName.bufferedWriter()

                    outFile.write("LineId,Content,EventId\n")
                    for (line in file.lines) {
                        outFile.write("${line.lineNumber},${line.content},${line.patternID!!.toString()}\n")
                        status = "Writing to file ${outFileName.toString()} line number ${line.lineNumber} ..."
                    }

                    outFile.close()
                }
                catch (err: Exception) {
                    status = "ERR: $err"
                }
                signal()
            }
        }
    }
}
