package org.analyzer.kotlin.log.parsers

import kotlin.test.Test
import kotlin.test.assertEquals

class DictTest {
  @Test
  fun `Test basic pattern extraction`() {
    val extractor = DictParser()
    val line = "Hello Andrzej my old d0g"
    val expectedPattern =
        listOf(
            DictSymbolNode("Hello"),
            CUSTOM_WORD_NODE,
            DictSymbolNode("my"),
            DictSymbolNode("old"),
            DictParamNode(),
        )
    assertEquals(DictPattern(expectedPattern), extractor.extractPatternFromLine(line))
  }

  @Test
  fun `Test basic pattern extraction with number`() {
    val extractor = DictParser()
    val line = "2 + 2 is 4"
    val expectedPattern =
        listOf(
            NUMBER_NODE,
            SYMBOL_NODE,
            NUMBER_NODE,
            DictSymbolNode("is"),
            NUMBER_NODE,
        )
    assertEquals(DictPattern(expectedPattern), extractor.extractPatternFromLine(line))
  }

  @Test
  fun `Test complex pattern extraction`() {
    val extractor = DictParser()
    val line = "Got response 404 from server - shutting down"
    val expectedPattern =
        listOf(
            DictSymbolNode("Got"),
            DictSymbolNode("response"),
            NUMBER_NODE,
            DictSymbolNode("from"),
            DictSymbolNode("server"),
            SYMBOL_NODE,
            DictSymbolNode("shutting"),
            DictSymbolNode("down"),
        )
    assertEquals(DictPattern(expectedPattern), extractor.extractPatternFromLine(line))
  }
}
