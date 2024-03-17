package org.analyzer.kotlin.log.parsers.drain

import io.github.bric3.drain.core.Drain
import java.util.UUID

class Pattern(
    val id: UUID,
    val content: List<String>
)


class DrainParser(private val depth: Int = 4) {
    // TODO: Implement drain wrapper

    val drain = Drain.drainBuilder().depth(depth).build()

    fun learnLine(line: String) {
        drain.parseLogMessage(line)
    }

    fun searchLine(line: String): Pattern {
        val cluster = drain.searchLogMessage(line)
        return Pattern(cluster.clusterId(), cluster.tokens())
    }
}
