package org.analyzer.kotlin.console.apps

import org.analyzer.kotlin.log.parsers.dict.DictParser

import com.varabyte.kotter.foundation.text.*
import com.varabyte.kotter.foundation.input.*
import com.varabyte.kotter.foundation.*
import com.varabyte.kotter.runtime.Session

class Parsers: App {
    override fun run(): (Session.() -> Unit) = {
        var inputLine by liveVarOf<String?>(null)
        val parser = DictParser()

        section {
            if (inputLine == null) {
                text("Provide a line to be parsed: ")
                input()
            }
            else {
                val pattern = parser.extractPatternFromLine(inputLine!!)
                val id = parser.putPattern(pattern)
                pattern.humanReadable().let {
                    text("Input line: $inputLine\n")
                    text("Pattern: $it\n")
                    text("Pattern ID: $id\n")
                    text("Press enter to continue ...")
                }
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

    override fun getAppName() = "Parsers Exploration"
}
