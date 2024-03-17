package org.analyzer.kotlin.log.parsers.drain

import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.fail
import kotlin.test.assertTrue
import kotlin.test.assertEquals

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
