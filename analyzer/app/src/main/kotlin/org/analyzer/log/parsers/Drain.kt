package org.analyzer.kotlin.log.parsers

import io.github.bric3.drain.core.Drain

class DrainParser(private val depth: Int = 4) {
    // TODO: Implement drain wrapper

    val drain = Drain.drainBuilder().depth(depth).build()

    fun learnLine(line: String) {
        TODO()
    }

    fun searchLine(line: String) {
        TODO()
    }
}
