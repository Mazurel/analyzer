package org.analyzer.kotlin.console.apps

import java.io.FileReader
import java.io.File

import org.analyzer.kotlin.log.parsers.dict.DictParser
import org.analyzer.kotlin.log.parsers.drain.DrainParser

import com.varabyte.kotter.foundation.text.*
import com.varabyte.kotter.foundation.input.*
import com.varabyte.kotter.foundation.*
import com.varabyte.kotter.runtime.render.RenderScope
import com.varabyte.kotter.runtime.Session

abstract class ParsersApp: App {
    val usedColors: List<Color> = listOf(
        Color.BRIGHT_GREEN,
        Color.BRIGHT_BLUE
    )

    override fun run(): (Session.() -> Unit) = {
        var inputLine by liveVarOf<String?>(null)

        section {
            if (inputLine == null) {
                text("Provide a line to be parsed: ")
                input()
                text("\nHint: To specify file, start with: 'file:'")
            }
            else {
                var lines = getFileContent(inputLine!!)
                    ?: listOf(inputLine!!)

                lines.forEachIndexed {
                    i, line ->
                      color(usedColors[i % usedColors.size]) {
                          text(printLine(line))
                      }
                }
                text("Press enter to continue ...")
            }
        }.run {
            onInputEntered {
                when (inputLine) {
                    null -> {
                      inputLine = input
                    }
                }
            }

            onKeyPressed {
                when (key) {
                    Keys.ENTER -> {
                      if (inputLine != null) {
                        inputLine = null
                      }
                    }
                    Keys.ESC -> {
                      signal()
                    }
                }
            }

            waitForSignal()
        }
    }

    abstract fun printLine(line: String): String

    private fun getFileContent(input: String): List<String>? {
        if (!input.startsWith("file:")) {
            return null
        }

        val path = input.slice(5..input.length-1)
        if (!File(path).exists()) {
            return null
        }

        return FileReader(path).readLines()
    }
}

class DictParser: ParsersApp() {
    val parser = DictParser()

    override fun printLine(line: String): String {
        val pattern = parser.extractPatternFromLine(line)
        val id = parser.putPattern(pattern)
        val stringBuilder = StringBuilder()
        pattern.humanReadable().let {
            stringBuilder.append("Input line: $line\n")
            stringBuilder.append("Pattern: $it\n")
            stringBuilder.append("Pattern ID: $id\n")
        }
        return stringBuilder.toString()
    }

    override fun getAppName() = "Dict parser exploration"
}

class DrainParser: ParsersApp() {
    private val parser = DrainParser(10)

    override fun printLine(line: String): String {
        parser.learnLine(line)
        val pattern = parser.searchLine(line)
        val id = pattern.id
        val stringBuilder = StringBuilder()
        stringBuilder.append("Input line: $line\n")
        stringBuilder.append("Pattern: ${pattern.getPrettyPattern()}\n")
        stringBuilder.append("Pattern ID: $id\n")
        return stringBuilder.toString()
    }

    override fun getAppName() = "Drain parser exploration"
}
