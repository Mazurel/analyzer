package org.analyzer.kotlin.log

import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.fail
import kotlin.test.assertTrue
import kotlin.test.assertEquals

class LogFormatTest {
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

class ParserTest {
    @Test
    fun `Test basic tokenization`() {
        val tokenizer = Tokenizer().withSeparator(" ")
        assertEquals(listOf("Sample", "log", "message"), tokenizer.tokenize("Sample log message"))
    }

    @Test
    fun `Test tokenizer construction`() {
        val tokenizer = Tokenizer()
        try {
            tokenizer.tokenize("Sample log message")
            fail("Tokenizer construction should have failed")
        }
        catch (ex: IllegalArgumentException) {
            // pass
        }
        catch (ex: Exception) {
            fail("Tokenizer construction should have failed with illegal argument exception, but got $ex")
        }
    }
}
