package org.analyzer.kotlin.log.parsers

import kotlin.test.Test
import kotlin.test.assertEquals

// NOTE: Drain is assumed to be tested by original authors

class DrainTest {
  @Test
  fun `Test basic pattern extraction`() {
    val extractor = DrainParser()
    val line = "Hello Andrzej my old d0g"
    extractor.learnLine(line)
    val p = extractor.searchLine(line)
    println(p.id)
    println(p.content)

    assertEquals(listOf("Hello", "Andrzej", "my", "old", "d0g"), p.content)
  }
}
