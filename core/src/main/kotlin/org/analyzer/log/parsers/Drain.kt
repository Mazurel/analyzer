package org.analyzer.kotlin.log.parsers.drain

import io.github.bric3.drain.core.Drain
import io.github.bric3.drain.core.LogCluster
import org.analyzer.kotlin.log.parsers.*

class Pattern(val id: PatternID, val content: List<String>) {
  companion object {
    fun fromLogCluster(cluster: LogCluster): Pattern {
      return Pattern(cluster.clusterId(), cluster.tokens())
    }
  }

  fun getPrettyPattern(): String {
    return content.joinToString(separator = " ")
  }
}

class DrainParser(private val depth: Int = 4) : LogParser {
  val drain = Drain.drainBuilder().depth(depth).build()
  val patternLookup: MutableMap<PatternID, Pattern> = mutableMapOf()

  override fun extractPattern(line: String): PatternID {
    val pat = this.searchLine(line)
    return pat.id
  }

  override fun learnLine(line: String): PatternID? {
    drain.parseLogMessage(line)
    return null
  }

  override fun humanReadable(patternId: PatternID): String {
    if (this.patternLookup.containsKey(patternId)) {
      return this.patternLookup.get(patternId)!!.getPrettyPattern()
    }

    val clusters = this.drain.clusters()
    val maybeCluster = clusters.find { it.clusterId() == patternId }
    if (maybeCluster == null) {
      throw RuntimeException("Unknown pattern ID - ${patternId}")
    }
    val pattern = Pattern.fromLogCluster(maybeCluster)
    this.patternLookup.put(patternId, pattern)
    return pattern.getPrettyPattern()
  }

  public fun searchLine(line: String): Pattern {
    val cluster = drain.searchLogMessage(line)
    val pattern = Pattern.fromLogCluster(cluster)
    this.patternLookup.put(cluster.clusterId(), pattern)
    return pattern
  }
}
