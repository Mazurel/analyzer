package org.analyzer.kotlin.console.apps

import kotlin.math.abs
import kotlin.random.Random

import org.analyzer.kotlin.monge.BitonicMongeArray

import com.varabyte.kotter.foundation.*
import com.varabyte.kotter.foundation.input.*
import com.varabyte.kotter.foundation.text.*
import com.varabyte.kotter.runtime.Session

private enum class MatchingAppState {
    CHOOSING_REDS,
    CHOOSING_BLUES,
    SHOW_MATCHING
}

class MatchingApp : App {
    private fun randomInitialInput(size: Int): String {
        val rnd = Random(System.currentTimeMillis())
        val sb = StringBuilder()
        var num = 0

        for (x in 1..size) {
            num += rnd.nextInt(10, 100)
            sb.append(num.toString())

            if (x != size) {
                sb.append(", ")
            }
        }

        return sb.toString()
    }

    override fun run(): (Session.() -> Unit) = {
        var state by liveVarOf<MatchingAppState>(MatchingAppState.CHOOSING_REDS)
        var reds by liveVarOf<List<Int>>(listOf())
        var blues by liveVarOf<List<Int>>(listOf())

        section {
            when (state) {
                MatchingAppState.CHOOSING_REDS -> {
                    textLine("Please provide reds (comma separated)")
                    input(id="reds", initialText=randomInitialInput(7))
                }
                MatchingAppState.CHOOSING_BLUES -> {
                    textLine("Please provide blues (comma separated)")
                    input(id="blues", initialText=randomInitialInput(12))
                }
                MatchingAppState.SHOW_MATCHING -> {
                    val monge = BitonicMongeArray(reds, blues) { a, b -> abs(a - b) }
                    try {
                        val res = monge.perfmatch()
                        textLine("reds: " + reds.toString())
                        textLine("blues: " + blues.toString())
                        textLine(res.toString())
                        monge.show(
                                printText = { text(it) },
                                newLine = { textLine() },
                                printHighlightedText = { green { text(it) } }
                        )
                        textLine()
                    } catch (ex: Exception) {
                        textLine("EX: $ex")
                        ex.printStackTrace()
                    }
                }
                else -> TODO()
            }
        }.run {
            onInputEntered {
                when (state) {
                    MatchingAppState.CHOOSING_REDS -> {
                        reds = input.split(",").map { it.trim().toInt() }.toList()
                        state = MatchingAppState.CHOOSING_BLUES
                    }
                    MatchingAppState.CHOOSING_BLUES -> {
                        blues = input.split(",").map { it.trim().toInt() }.toList()
                        state = MatchingAppState.SHOW_MATCHING
                    }
                    else -> TODO()
                }
            }

            onKeyPressed {
                when (key) {
                    Keys.ESC -> {
                        signal()
                    }
                    Keys.ENTER -> {
                        if (state == MatchingAppState.SHOW_MATCHING) {
                            state = MatchingAppState.CHOOSING_REDS
                        }
                    }
                }
            }

            waitForSignal()
        }
    }

    override fun getAppName(): String = "Matching exploration"
}
