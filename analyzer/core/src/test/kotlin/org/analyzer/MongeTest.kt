package org.analyzer.kotlin.monge

import kotlin.test.Test
import kotlin.math.abs
import kotlin.test.assertFalse
import kotlin.test.fail
import kotlin.test.assertTrue
import kotlin.test.assertEquals
import kotlin.random.Random

class MongeArrayTests {
    @Test
    fun `Test creating monge array`() {
        val reds = listOf(1, 10, 20, 32)
        val blues = listOf(2, 4, 5, 10)

        val monge = BitonicMongeArray(reds, blues) { a, b -> abs(a - b) }

        monge.show()
    }

    @Test
    fun `Test basic monge matching (height == width)`() {
        val reds = listOf(1, 10, 20, 32)
        val blues = listOf(2, 4, 5, 10)
        val expectedDistances = listOf(1, 6, 15, 22)

        val monge = BitonicMongeArray(reds, blues) { a, b -> abs(a - b) }
        val match = monge.perfmatch()
        for (i in 0..match.size-1) {
            println(i)
            assertEquals(expectedDistances[i], match[i]!!.first)
            assertEquals(blues[i], match[i]!!.second)
        }
    }

    @Test
    fun `Test monge matching`() {
        val reds = listOf(1, 3, 10, 20, 21)
        val blues = listOf(2, 4, 5, 11, 18, 32, 45)
        val monge = BitonicMongeArray(reds, blues) { a, b -> abs(a - b) }

        monge.show()

        val expectedMatching = listOf(
            Pair(1, 2),
            Pair(1, 4),
            Pair(1, 11),
            Pair(2, 18),
            Pair(11, 32),
        )
        val result = monge.perfmatch()
        assertEquals(expectedMatching, result)
    }
}
