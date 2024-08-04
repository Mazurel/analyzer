package org.analyzer.kotlin.log

import kotlin.math.min

private val timestampSurroundings: List<Pair<Char, Char>> =
        listOf(
                Pair('[', ']'),
                Pair('(', ')'),
                Pair('{', '}'),
                Pair('<', '>'),
        )

class TimestampSubtokens(private val text: String) : Iterator<String> {
    private val tokens = text.split(" ").map { it.trim() }.filter { it.length > 0 }
    private var subtokenIndex = min(5, tokens.size - 1)
    private var surroundingsIndex = 0
    private val maxJ = timestampSurroundings.size
    private var nextToken: String?

    init {
        nextToken = null
        while (!isLastState() && nextToken == null) {
            nextToken = tokenByState()
            nextState()
        }
    }

    companion object {
        fun textMinusSubtoken(text: String, subtoken: String): String {
            if (subtoken == "") {
                return text
            }

            val spacesCount = subtoken.count { it == ' ' }
            assert(spacesCount >= 0)
            var sliceIndex = 0
            for (i in 0..spacesCount) {
                sliceIndex = text.indexOf(' ', sliceIndex + 1)

                if (sliceIndex == -1) {
                    throw RuntimeException("Invalid arguments provided ! ('$text', '$subtoken')")
                }
            }
            return text.drop(sliceIndex + 1)
        }
    }

    override operator fun hasNext(): Boolean {
        return nextToken != null && !isLastState()
    }

    override operator fun next(): String {
        val result = nextToken!!

        nextToken = null
        while (nextToken == null && !isLastState()) {
            nextToken = tokenByState()
            nextState()
        }

        return result
    }

    private fun tokenByState(): String? {
        if (surroundingsIndex == 0) {
            return tokens.slice(0..subtokenIndex).joinToString(" ")
        }

        val token = tokens.slice(0..subtokenIndex).joinToString(" ")
        if (token.length <= 2) {
            return null
        }

        val (a, b) = timestampSurroundings[surroundingsIndex - 1]
        if (token.first() == a && token.last() == b) {
            return token.slice(1..token.length - 2)
        }

        return null
    }

    private fun nextState() {
        if (surroundingsIndex >= maxJ) {
            surroundingsIndex = 0
            subtokenIndex -= 1
        } else {
            surroundingsIndex += 1
        }
    }

    private fun isLastState(): Boolean {
        return subtokenIndex < 0
    }
}

class Timestamp(private val line: LogLine, private val timestampFormat: String? = null) {
    // ... how did it become so convoluted ???
    //
    // TODO: Using LogFormat
    // TODO: Refactor this class into something nicer
    private var timestampString = ""

    public val nonTimestampString
        get() = TimestampSubtokens.textMinusSubtoken(line.line, timestampString)
    public val string
        get() = timestampString
    public val actualEpoch = extractEpoch()
    public var injectedEpoch: Double? = null
    public val epoch
        get() = if (injectedEpoch != null) injectedEpoch else actualEpoch

    private fun generateSubTokens(): Sequence<String> {
        return TimestampSubtokens(line.line).asSequence()
    }

    private fun extractEpoch(): Double? {
        for (possiblyTimestamp in generateSubTokens()) {
            var timestampVal: Double? = null

            if (this.timestampFormat != null) {
                val formatter = TimestampFormatter(this.timestampFormat)

                formatter.parse(possiblyTimestamp).let {
                    if (it != null) {
                        timestampVal = it
                    }
                }
            }

            for (formatter in dateFormatters) {
                if (timestampVal != null) {
                    break
                }

                formatter.parse(possiblyTimestamp).let {
                    if (it != null) {
                        timestampVal = it
                    }
                }
            }

            try {
                timestampVal = possiblyTimestamp.toDouble()
            } catch (ex: NumberFormatException) {}

            if (timestampVal != null) {
                this.timestampString = possiblyTimestamp
                return timestampVal
            }
        }

        this.timestampString = ""
        return null
    }
}
