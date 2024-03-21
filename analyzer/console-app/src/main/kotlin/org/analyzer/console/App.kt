package org.analyzer.kotlin.console

import com.varabyte.kotter.foundation.*
import com.varabyte.kotter.foundation.input.*
import com.varabyte.kotter.foundation.text.*
import org.analyzer.kotlin.console.apps.DictParser
import org.analyzer.kotlin.console.apps.DrainParser

fun main() = session {
    val applications = listOf(DictParser(), DrainParser())
    var selectedIndex by liveVarOf(0)
    var exit by liveVarOf(false)

    fun nextIndex() {
        selectedIndex += 1
        if (selectedIndex >= applications.size) {
            selectedIndex = 0
        }
    }

    fun prevIndex() {
        selectedIndex -= 1
        if (selectedIndex < 0) {
            selectedIndex = applications.size - 1
        }
    }

    while (!exit) {
        section {
            clearAll()

            bold { text("Select application to be used\n") }

            (0..applications.size-1).forEach {
                text("- ")
                when {
                    it == selectedIndex -> {
                        underline { text(applications[it].getAppName()) }
                    }
                    else -> {
                        text(applications[it].getAppName())
                    }
                }
                text("\n")
            }
        }.runUntilSignal {
            onKeyPressed {
                when (key) {
                    Keys.DOWN -> nextIndex()
                    Keys.UP -> prevIndex()
                    Keys.ESC -> {
                        exit = true
                        signal()
                    }
                    Keys.ENTER -> {
                        signal()
                    }
                }
            }
        }

        if (!exit) {
            applications[selectedIndex].run()()
        }
    }
}
