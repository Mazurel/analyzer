package org.analyzer.kotlin.log

import kotlin.test.*

class TimestampTests {
  @Test
  fun `Test timestamp substrings`() {
    val subtokens = TimestampSubtokens(" [test hello]   world").asSequence().toList()
    val expected = listOf("test hello")

    assertEquals(expected.size, subtokens.size, "Got tokens $subtokens")

    subtokens.zip(expected).forEachIndexed { i, (exp, got) ->
      assertEquals(exp, got, "Assertion failed on index $i")
    }
  }

  @Test
  fun `Test timestamp substrings v2`() {
    val subtokens = TimestampSubtokens("test hello world").asSequence().toList()
    val expected = listOf("test hello world", "test hello", "test")

    assertEquals(expected.size, subtokens.size, "Got tokens $subtokens")

    subtokens.zip(expected).forEachIndexed { i, (exp, got) ->
      assertEquals(exp, got, "Assertion failed on index $i")
    }
  }

  @Test
  fun `Test timestamp parsing`() {
    val timestamp = Timestamp("   Sat Jun 11 23:39:35 2005     abc")

    assertTrue(timestamp.epoch != null)
    assertEquals("Sat Jun 11 23:39:35 2005", timestamp.string)
    assertNotNull(timestamp.epoch)
    // assertEquals("INFO Test", line.timestamp.nonTimestampString)
  }

  @Test
  fun `Test extracting string from timestamps`() {
    val line = LogLine("2020-01-01 12:20:10 INFO Test", 1)

    assertTrue(line.timestamp.epoch != null)
    assertEquals("2020-01-01 12:20:10", line.timestamp.string)
    assertEquals("INFO Test", line.timestamp.nonTimestampString)
  }

  @Test
  fun `Test extracting string from android timestamps`() {
    var line = LogLine("03-17 16:13:38.123 xyz", 1)
    assertTrue(line.timestamp.epoch != null)
    assertEquals("03-17 16:13:38.123", line.timestamp.string)

    line = LogLine("03-17 16:13:38 xyz", 1)
    assertTrue(line.timestamp.epoch != null)
    assertEquals("03-17 16:13:38", line.timestamp.string)
  }

  @Test
  fun `Test extracting string from apache timestamps`() {
    var line = LogLine("Sat Jun 11 01:35:55 2005 xyz", 1) // Sat Jun 11 23:39:35 2005
    assertTrue(line.timestamp.epoch != null)
    assertEquals("Sat Jun 11 01:35:55 2005", line.timestamp.string)

    line = LogLine("[Sat Jun 11 03:03:05 2005] [error] [client 222.166.160.74] xyz", 1)
    assertTrue(line.timestamp.epoch != null)
    assertEquals("Sat Jun 11 03:03:05 2005", line.timestamp.string)
    assertNotNull(line.timestamp.epoch)
  }

  @Test
  fun `Test injecting timestamp`() {
    val line = LogLine("INFO Test", 1)

    assertEquals(null, line.timestamp.epoch)
    line.timestamp.injectedEpoch = 1.0
    assertTrue(line.timestamp.epoch != null)
  }

  @Test
  fun `Check timestamps with format`() {
    for ((line1, line2) in
        listOf(
            Pair(
                LogLine(
                    "2020,01|01 12:20:10 INFO Test", 1, timestampFormat = "yyyy,MM|dd HH:mm:ss"),
                LogLine(
                    "2020,01|02 12:20:10 INFO Test", 1, timestampFormat = "yyyy,MM|dd HH:mm:ss")),
            Pair(
                LogLine("03,01?2024 INFO Test", 1, timestampFormat = "dd,MM?yyyy"),
                LogLine("03,02?2024 INFO Test", 1, timestampFormat = "dd,MM?yyyy")),
        )) {
      assert(line1.timestamp.epoch!! < line2.timestamp.epoch!!)
    }
  }

  @Test
  fun `Check timestamps without format`() {
    for ((line1, line2) in
        listOf(
            Pair(
                LogLine("2020-01-01 12:20:10 INFO Test", 1),
                LogLine("2020-01-01 12:30:10 INFO Test", 1)),
            Pair(LogLine("03/01/2024 INFO Test", 1), LogLine("03/02/2024 INFO Test", 1)),
        )) {
      assert(line1.timestamp.epoch!! < line2.timestamp.epoch!!)
    }
  }
}
