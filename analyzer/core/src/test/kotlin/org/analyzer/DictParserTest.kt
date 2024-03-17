package org.analyzer.kotlin.log.parsers.dict

import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.fail
import kotlin.test.assertTrue
import kotlin.test.assertEquals

class DictTest {
    @Test
    fun `Test basic pattern extraction`() {
        val extractor = DictParser()
        val line = "Hello Andrzej my old d0g"
        val expectedPattern = listOf(
            SymbolNode("Hello"),
            CUSTOM_WORD_NODE,
            SymbolNode("my"),
            SymbolNode("old"),
            ParamNode(),
        )
        assertEquals(Pattern(expectedPattern), extractor.extractPatternFromLine(line))
    }

    @Test
    fun `Test basic pattern extraction with number`() {
        val extractor = DictParser()
        val line = "2 + 2 is 4"
        val expectedPattern = listOf(
            NUMBER_NODE,
            SYMBOL_NODE,
            NUMBER_NODE,
            SymbolNode("is"),
            NUMBER_NODE,
        )
        assertEquals(Pattern(expectedPattern), extractor.extractPatternFromLine(line))
    }

    @Test
    fun `Test complex pattern extraction`() {
        val extractor = DictParser()
        val line = "Got response 404 from server - shutting down"
        val expectedPattern = listOf(
            SymbolNode("Got"),
            SymbolNode("response"),
            NUMBER_NODE,
            SymbolNode("from"),
            SymbolNode("server"),
            SYMBOL_NODE,
            SymbolNode("shutting"),
            SymbolNode("down"),
        )
        assertEquals(Pattern(expectedPattern), extractor.extractPatternFromLine(line))
    }
}
