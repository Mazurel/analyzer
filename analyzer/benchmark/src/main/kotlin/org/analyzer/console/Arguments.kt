package org.analyzer.kotlin.console

import java.nio.file.Path

import org.analyzer.kotlin.log.LogFile
import org.analyzer.kotlin.console.Arguments

import kotlin.io.path.Path

class Arguments(
    public var inputFile: Path? = null,
    public var outputFile: Path? = null,
) {
    private val existingErrors = mutableListOf<String>()

    private class FetchingState() {
        var argName: String? = null
    }

    private fun reportError(error: String) {
        this.existingErrors.add(error)
    }

    public fun collectErrors(): List<String> {
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

    private fun fetchArgument(arg_name: String, arg_val: String?) {
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

    public fun fetchArguments(args: Array<String>): Arguments {
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
