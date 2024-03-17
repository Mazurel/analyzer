package org.analyzer.kotlin.dictionary

import kotlin.test.Test
import kotlin.test.assertNotNull
import kotlin.test.assertTrue
import kotlin.test.assertFalse

class DictTest {
    @Test fun `Test alphabethic compare`() {
        val a = "Ala"
        val b = "Bob"
        val c = "Wendy"

        assertTrue(alphabethicCompare(a, b) < 0)
        assertTrue(alphabethicCompare(c, b) > 0)
        assertTrue(alphabethicCompare(a, c) < 0)
        assertTrue(alphabethicCompare(a, a) == 0)
    }

    @Test fun `Test looking up words`() {
        val lookup = DictLookuper("/lookup-test-set.txt", resourceObject=this)
        assertTrue(lookup.lookupWord("Who"))
        assertTrue(lookup.lookupWord("Am"))
        assertTrue(lookup.lookupWord("HeLLo"))
        assertFalse(lookup.lookupWord("nope"))
    }
}
