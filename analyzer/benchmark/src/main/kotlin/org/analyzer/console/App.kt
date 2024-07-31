package org.analyzer.kotlin.console

import com.varabyte.kotter.foundation.*
import com.varabyte.kotter.foundation.input.*
import com.varabyte.kotter.foundation.text.*
import com.varabyte.kotter.runtime.render.*
import java.nio.file.Path
import kotlin.io.path.Path
import kotlin.io.path.bufferedReader
import kotlin.io.path.bufferedWriter
import org.analyzer.kotlin.log.LogFile

class Arguments(public var inputFile: Path? = null, public var outputFile: Path? = null) {
    private val existingErrors = mutableListOf<String>()

    private class FetchingState() {
        var argName: String? = null
    }

    private fun reportError(error: String) {
        this.existingErrors.add(error)
    }

    fun collectErrors(): List<String> {
        if (inputFile == null) {
            this.reportError("Input file not specified, please use `--input_file`")
        } else if (!this.inputFile!!.toFile().exists()) {
            this.reportError("File ${this.inputFile} doesnt exist")
        }

        if (inputFile == null) {
            this.reportError("Output file not specified, please use `--output_file`")
        } else if (this.outputFile!!.toFile().exists()) {
            this.reportError("File ${this.outputFile} exist ! Are you sure you want to remove it ?")
        }

        return this.existingErrors.toList()
    }

    fun fetchArgument(arg_name: String, arg_val: String?) {
        when {
            arg_name == "input_file" && arg_val != null -> {
                this.inputFile = Path(arg_val)
            }
            arg_name == "output_file" && arg_val != null -> {
                this.outputFile = Path(arg_val)
            }
            else -> {
                this.reportError("Unexpected argument ${arg_name} with val ${arg_val}")
            }
        }
    }

    fun fetchArguments(args: Array<String>): Arguments {
        val fetching_state = Arguments.FetchingState()

        for (arg in args) {
            when {
                arg.startsWith("--") -> {
                    if (fetching_state.argName != null) {
                        this.fetchArgument(fetching_state.argName!!, null)
                    }
                    fetching_state.argName = arg.slice(2..arg.length - 1)
                }
                else -> {
                    if (fetching_state.argName != null) {
                        this.fetchArgument(fetching_state.argName!!, arg)
                        fetching_state.argName = null
                    }
                }
            }
        }
        if (fetching_state.argName != null) {
            this.fetchArgument(fetching_state.argName!!, null)
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
        }
                .run {}

        if (errs.size == 0) {
            var status by liveVarOf("Initializing ...")
            section { textLine(status) }.runUntilSignal {
                try {
                    val inFileName = inArguments.inputFile!!.toAbsolutePath().normalize()
                    val outFileName = inArguments.outputFile!!.toAbsolutePath().normalize()

                    val file =
                            LogFile(inFileName.bufferedReader()) {
                                status =
                                        "Loading line ${it.lineNumber} from ${inFileName.toString()}"
                            }

                    if (file.lines.size == 0) {
                        status = "Input file is empty ? No lines found at ${inFileName.toString()}"
                        signal()
                    }

                    val outFile = outFileName.bufferedWriter()

                    outFile.write("LineId,Content,EventId\n")
                    for (line in file.lines) {
                        outFile.write(
                                "${line.lineNumber},${line.content},${line.patternID!!.toString()}\n"
                        )
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
