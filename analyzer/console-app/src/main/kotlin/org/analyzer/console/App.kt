package org.analyzer.kotlin.console

import org.analyzer.kotlin.log.parsers.DictParser

import kotlinx.coroutines.delay

import com.varabyte.kotter.foundation.text.*
import com.varabyte.kotter.foundation.input.*
import com.varabyte.kotter.foundation.*

fun main() = session {
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

