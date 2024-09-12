package org.analyzer.kotlin.log.parsers

import io.github.bric3.drain.core.Drain
import io.github.bric3.drain.core.LogCluster
import org.analyzer.kotlin.log.parsers.*

public class DrainPattern(public val id: PatternID, public val content: List<String>) {
  companion object {
    public fun fromLogCluster(cluster: LogCluster): DrainPattern {
      return DrainPattern(cluster.clusterId(), cluster.tokens())
    }
  }

  public fun getPrettyPattern(): String {
    return content.joinToString(separator = " ")
  }
}

class DrainParser(private val depth: Int = 4) : LogParser {
  val drain = Drain.drainBuilder().depth(depth).build()
  val patternLookup: MutableMap<PatternID, DrainPattern> = mutableMapOf()

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
    val pattern = DrainPattern.fromLogCluster(maybeCluster)
    this.patternLookup.put(patternId, pattern)
    return pattern.getPrettyPattern()
  }

  public fun searchLine(line: String): DrainPattern {
    val cluster = drain.searchLogMessage(line)
    val pattern = DrainPattern.fromLogCluster(cluster)
    this.patternLookup.put(cluster.clusterId(), pattern)
    return pattern
  }
}
