package org.analyzer.kotlin.console.apps

import kotlin.math.abs
import kotlin.math.min
import kotlin.math.max
import kotlin.math.floor
import kotlin.random.Random
import kotlin.io.path.isRegularFile
import kotlin.io.path.bufferedReader
import kotlin.io.path.Path
import kotlin.io.normalize

import org.analyzer.kotlin.console.components.loadFile
import org.analyzer.kotlin.console.components.SelectFileContext
import org.analyzer.kotlin.monge.BitonicMongeArray
import org.analyzer.kotlin.log.LogFile
import org.analyzer.kotlin.log.LogLine

import com.varabyte.kotter.foundation.*
import com.varabyte.kotter.foundation.render.*
import com.varabyte.kotter.foundation.input.*
import com.varabyte.kotter.foundation.text.*
import com.varabyte.kotter.runtime.render.*
import com.varabyte.kotter.runtime.Session
import com.varabyte.kotterx.grid.*

fun Int.min(v: Int): Int {
    return min(this, v)
}

fun Int.max(v: Int): Int {
    return max(this, v)
}

fun String.padTokenTo(width: Int = 10, offset: Int = 0): String
    = this.drop(offset)
    .drop(offset)
    .replace('\t', ' ')
    .take(width)
    .padEnd(width, ' ')

fun RenderScope.showLineComparison(lineNumber: Int, baseline: LogLine, checked: LogLine?, offset: Int = 0) {
    val maxLineLength = 56
    val dtWidth = 6

    val t0 = "$lineNumber.".toString().padEnd(5, ' ')
    val t1 = baseline.line.padTokenTo(width=maxLineLength, offset=offset)

    val t2 = checked.let {
        if (it == null) "" else it.line
    }.padTokenTo(width=maxLineLength, offset=offset)


    var t3 = ""
    if (checked != null) {
        t3 = abs(baseline.timestamp.epoch!! - checked.timestamp.epoch!!).toString()
    }
    t3 = t3.padTokenTo(width=dtWidth)

    val t4 = baseline.patternID.toString().padTokenTo(width=40)

    scopedState {
        when {
            checked == null -> green()
            baseline.timestamp.nonTimestampString == checked.timestamp.nonTimestampString -> black(isBright=true)
            else -> white()
        }
        textLine("$t0 | $t1 | $t2 | $t3 | $t4")
    }
}

class LogMatchingApp : App {
    private val linesAmount = 30

    override fun run(): (Session.() -> Unit) = {
        var rerun: Boolean = true

        val initialPath = Path("../legacy-analyzer/sample-logs/").toAbsolutePath().normalize().toString()
        val baselineFileContext = SelectFileContext(initialPath)
        val checkedFileContext = SelectFileContext(initialPath)

        while (rerun) {
            rerun = false

            loadFile("Select baseline file", baselineFileContext)
            loadFile("Select checked file", checkedFileContext)

            if (!baselineFileContext.isValidInput() || !checkedFileContext.isValidInput()) {
                section {
                    red {
                        textLine("Invalid file provided ...")
                        if (!baselineFileContext.isValidInput()) {
                            textLine(" Invalid baseline - ${baselineFileContext.getCurrentPath()}")
                        }
                        if (!checkedFileContext.isValidInput()) {
                            textLine(" Invalid checked - ${checkedFileContext.getCurrentPath()}")
                        }
                    }
                }.runUntilSignal {
                    onKeyPressed { signal() }
                }
                rerun = false // quit
                continue
            }

            val baselinePath = baselineFileContext.getCurrentPath()
            val checkedPath = checkedFileContext.getCurrentPath()
            var baseline: LogFile? = null
            var checked: LogFile? = null

            val progressLength = 10
            var status by liveVarOf("")
            var progress by liveVarOf<Int>(0)
            section {
                textLine("$status - $progress")
            }.runUntilSignal {
                status = "Loading baseline lines"
                progress = 0
                baseline = LogFile(baselinePath.bufferedReader()) {
                    progress += 1
                }
                status = "Loading checked lines"
                progress = 0
                checked = LogFile(checkedPath.bufferedReader()) {
                    progress += 1
                }
                signal()
            }

            val matchingResult = baseline!!.matchWith(checked!!)

            var verticalIndex by liveVarOf(1)
            var horizontalIndex by liveVarOf(0)
            var gotoLine by liveVarOf(false)
            val scrollingSpeed = 2

            section {
                textLine()
                textLine("Baseline -> $baselinePath")
                textLine("Checked -> $checkedPath")
                textLine()
                for (i in verticalIndex..(verticalIndex+linesAmount).min(matchingResult.size - 1)) {
                    try {
                        showLineComparison(i, baseline!!.lineAt(i), matchingResult[i - 1], offset=horizontalIndex)
                    }
                    catch (ex: Exception) {
                        textLine(ex.toString())
                        ex.printStackTrace()
                    }
                }

                if (gotoLine) {
                    text(": "); input(); textLine()
                }
            }.runUntilSignal {
                onInputEntered {
                    try {
                        verticalIndex = input.toInt()
                    }
                    catch (ex: NumberFormatException) {
                        // pass
                    }
                    gotoLine = false
                }

                onKeyPressed {
                    when (key) {
                        Keys.ESC -> {
                            signal()
                        }
                        Keys.ENTER -> {
                            if (gotoLine) {
                                // pass
                            }
                            else {
                                rerun = true
                                signal()
                            }
                        }
                        Keys.DOWN -> {
                            verticalIndex = (verticalIndex + scrollingSpeed).min(matchingResult.size - 1)
                        }
                        Keys.UP -> {
                            verticalIndex= (verticalIndex - scrollingSpeed).max(1)
                        }
                        Keys.RIGHT -> {
                            horizontalIndex = (horizontalIndex + scrollingSpeed)
                        }
                        Keys.LEFT -> {
                            horizontalIndex = (horizontalIndex - scrollingSpeed).max(0)
                        }
                        Keys.G -> {
                            val bottom = (matchingResult.size - linesAmount - 1).max(1)
                            verticalIndex = if (verticalIndex != bottom) bottom else 1
                        }
                        Keys.COLON -> {
                            gotoLine = true
                        }
                    }
                }
            }
        }
    }

    override fun getAppName(): String = "Log Matching exploration"
}
