package org.analyzer

import org.analyzer.kotlin.log.parsers.DictParser

fun main() {
    val parser = DictParser()

    val d = io.github.bric3.drain.core.Drain.drainBuilder().depth(4).build()
    d.parseLogMessage("Test")

    while (true) {
      val input = readLine()
      if (input != null) {
          val pattern = parser.extractPatternFromLine(input)
          val id = parser.putPattern(pattern)
          pattern.humanReadable().let {
              println("id = $id for $it ($input)")
          }
      }
    }
}
