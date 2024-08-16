package org.analyzer.kotlin.log

import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue
import kotlin.test.fail

fun Random.nextString(maxSize: Int): String {
  assert(maxSize > 0)

  val builder = StringBuilder()
  val size = nextInt(1, maxSize)
  (0..size).forEach { builder.append(Char(nextInt('a'.code, 'z'.code))) }

  return builder.toString()
}

class LogFormatTests {
  @Test
  fun `Test log format`() {
    val format = LogFormat("<Day> <Month> - ")
    val result = format.matchLine("Monday January - Some random line content")

    println(result.fields)
    assertEquals("Monday", result.fields.get("Day"))
    assertEquals("January", result.fields.get("Month"))
    assertEquals("Some random line content", result.content)
  }
}

class ParserTests {
  @Test
  fun `Test basic tokenization`() {
    val tokenizer = Tokenizer().withSeparators(" ")
    assertEquals(listOf("Sample", "log", "message"), tokenizer.tokenize("Sample log message"))
  }

  @Test
  fun `Test tokenizer construction`() {
    val tokenizer = Tokenizer()
    try {
      tokenizer.tokenize("Sample log message")
      fail("Tokenizer construction should have failed")
    } catch (ex: IllegalArgumentException) {
      // pass
    } catch (ex: Exception) {
      ex.printStackTrace()
      fail(
          "Tokenizer construction should have failed with illegal argument exception, but got ${ex}")
    }
  }
}

class LogsTests {
  @Test
  fun `Log file sanity check`() {
    val inputFile = javaClass.getResourceAsStream("/sample-log-file.txt").bufferedReader()
    val logFile = LogFile(inputFile)
    println("Input lines:")
    println(logFile.lines.map { it.content }.joinToString("\n"))
    assert(logFile.lines.size > 0)
    logFile.lines.forEach { assert(it.content.length > 0) }
  }

  @Test
  fun `Test formatting in log files`() {
    val random = Random(10)
    val inputFile = javaClass.getResourceAsStream("/sample-log-file.txt").bufferedReader()
    val logFile = LogFile(inputFile, format = LogFormat("<Timestamp> "))
    logFile.lines.forEachIndexed { i, it ->
      val randomString = random.nextString(10)
      assertTrue(it.metadata.containsKey("Timestamp"))
      assertFalse(it.metadata.containsKey(random.nextString(10)))
      assertEquals("[$i.0]", it.metadata.get("Timestamp"))
    }
  }

  @Test
  fun `Test log files matching`() {
    fun loadLogfile(file: String): LogFile {
      val inputFile = javaClass.getResourceAsStream(file).bufferedReader()
      return LogFile(inputFile)
    }

    val random = Random(10)
    val f1 = loadLogfile("/sample-log-file.txt")
    val f2 = loadLogfile("/sample-log-file2.txt")
  }
}
