package org.analyzer.kotlin.log

import kotlin.test.*

class TimestampTests {
    @Test
    fun `Test timestamp substrings`() {
        val subtokens = TimestampSubtokens(" [test] hello   world").asSequence().toList()
        val expected = listOf("[test] hello world", "[test] hello", "[test]", "test")

        assertEquals(expected.size, subtokens.size)

        subtokens.zip(expected).forEachIndexed { i, (exp, got) ->
            assertEquals(exp, got, "Assertion failed on index $i")
        }
    }

    @Test
    fun `Check timestamps without format`() {
        for ((line1, line2) in
                listOf(
                        Pair(
                                LogLine("2020-01-01 12:20:10 INFO Test", 1),
                                LogLine("2020-01-01 12:30:10 INFO Test", 1)
                        ),
                        Pair(
                                LogLine("03/01/2024 INFO Test", 1),
                                LogLine("03/02/2024 INFO Test", 1)
                        ),
                )) {
            assert(line1.timestamp.extractEpoch()!! < line2.timestamp.extractEpoch()!!)
        }
    }
}
