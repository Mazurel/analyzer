package org.analyzer.kotlin.monge

import kotlin.math.abs
import kotlin.test.Test
import kotlin.test.assertEquals

class MongeArrayTests {
  @Test
  fun `Test creating monge array`() {
    val reds = listOf(1, 10, 20, 32)
    val blues = listOf(2, 4, 5, 10)

    val monge = BitonicMongeArray(reds, blues) { a, b -> abs(a - b).toDouble() }

    monge.show()
  }

  @Test
  fun `Test basic monge matching (height == width)`() {
    val reds = listOf(1, 10, 20, 32)
    val blues = listOf(2, 4, 5, 10)
    val expectedDistances = listOf(1, 6, 15, 22)

    val monge = BitonicMongeArray(reds, blues) { a, b -> abs(a - b).toDouble() }
    val match = monge.perfmatch()
    for (i in 0..match.size - 1) {
      println(i)
      assertEquals(expectedDistances[i], match[i]!!.first.toInt())
      assertEquals(blues[i], match[i]!!.second)
    }
  }

  @Test
  fun `Test monge matching`() {
    val reds = listOf(1, 3, 10, 20, 21)
    val blues = listOf(2, 4, 5, 11, 18, 32, 45)
    val monge = BitonicMongeArray(reds, blues) { a, b -> abs(a - b).toDouble() }

    monge.show()

    val expectedMatching =
        listOf(
            Pair(1, 2),
            Pair(1, 4),
            Pair(1, 11),
            Pair(2, 18),
            Pair(11, 32),
        )
    val result = monge.perfmatch().map { Pair(it!!.first.toInt(), it.second) }
    assertEquals(expectedMatching, result)
  }

  @Test
  fun `Test monge harder matching`() {
    val reds = listOf(17, 69, 119, 132, 215, 282, 317)
    val blues = listOf(33, 76, 120, 133, 150, 175, 256, 328, 355, 375, 403, 456)
    val monge = BitonicMongeArray(reds, blues) { a, b -> abs(a - b).toDouble() }

    monge.show()

    val expectedMatching =
        listOf(
            Pair(16, 33),
            Pair(7, 76),
            Pair(1, 120),
            Pair(1, 133),
            Pair(40, 175),
            Pair(26, 256),
            Pair(11, 328),
        )
    val result = monge.perfmatch().map { Pair(it!!.first.toInt(), it.second) }
    assertEquals(expectedMatching, result)
  }

  //        21.0   56.0   62.0   91.0
  // 56.0   35.0   0.0    6.0    35.0
  // 62.0   41.0   6.0    0.0    29.0
  // 91.0   70.0   35.0   29.0   0.0
  @Test
  fun `Test monge matching basic edge case`() {
    val reds = listOf(56, 62, 91)
    val blues = listOf(21, 56, 62, 91)
    val monge = BitonicMongeArray(reds, blues) { a, b -> abs(a - b).toDouble() }

    monge.show()

    val expectedMatching =
        listOf(
            Pair(0, 56),
            Pair(0, 62),
            Pair(0, 91),
        )
    val result = monge.perfmatch().map { Pair(it!!.first.toInt(), it.second) }
    assertEquals(expectedMatching, result)
  }
}
