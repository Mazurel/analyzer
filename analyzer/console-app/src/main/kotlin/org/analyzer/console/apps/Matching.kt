package org.analyzer.kotlin.console.apps

import com.varabyte.kotter.foundation.*
import com.varabyte.kotter.foundation.input.*
import com.varabyte.kotter.foundation.text.*
import com.varabyte.kotter.runtime.Session
import kotlin.math.abs
import org.analyzer.kotlin.monge.BitonicMongeArray

private enum class MatchingAppState {
    CHOOSING_REDS,
    CHOOSING_BLUES,
    SHOW_MATCHING
}

class MatchingApp : App {
    override fun run(): (Session.() -> Unit) = {
        var state by liveVarOf<MatchingAppState>(MatchingAppState.CHOOSING_REDS)
        var reds by liveVarOf<List<Int>>(listOf())
        var blues by liveVarOf<List<Int>>(listOf())

        section {
            when (state) {
                MatchingAppState.CHOOSING_REDS -> {
                    textLine("Please provide reds (comma separated)")
                    input()
                }
                MatchingAppState.CHOOSING_BLUES -> {
                    textLine("Please provide blues (comma separated)")
                    input()
                }
                MatchingAppState.SHOW_MATCHING -> {
                    val monge = BitonicMongeArray(reds, blues) { a, b -> abs(a - b) }
                    monge.perfmatch()
                    monge.show(
                            printText = { text(it) },
                            newLine = { textLine() },
                            printHighlightedText = { green { text(it) } }
                    )
                }
                else -> TODO()
            }
        }
                .run {
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
