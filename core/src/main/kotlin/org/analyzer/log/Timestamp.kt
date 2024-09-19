package org.analyzer.kotlin.log

import kotlin.math.min

private val timestampSurroundings: List<Pair<Char, Char>> =
    listOf(
        Pair('[', ']'),
        Pair('(', ')'),
        Pair('{', '}'),
        Pair('<', '>'),
    )

private fun doesStringContainSurrounding(str: String): Boolean {
  timestampSurroundings.forEach { (s1, s2) ->
    if (str.contains(s1) || str.contains(s2)) {
      return true
    }
  }
  return false
}

data class TimestampSubtokens(
    private val text: String,
    private var subtokenIndex: Int = 5,
    private var surroundingsIndex: Int = 0,
    private var nextToken: String? = null,
) : Iterator<String> {
  private val tokens = text.split(" ").map { it.trim() }.filter { it.length > 0 }
  private val maxJ = timestampSurroundings.size

  init {
    this.subtokenIndex = min(this.subtokenIndex, this.tokens.size - 1)

    this.nextToken = this.tokenByState()
    while (this.nextToken == null && !this.isLastState()) {
      this.nextToken = this.nextState()
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
    return this.nextToken != null && !isLastState()
  }

  public fun current(): String {
    return this.nextToken!!
  }

  override operator fun next(): String {
    val result = this.nextToken!!

    this.nextToken = null
    while (this.nextToken == null && !this.isLastState()) {
      this.nextToken = this.nextState()
    }

    return result
  }

  private fun tokenByState(): String? {
    var token = this.tokens.slice(0..subtokenIndex).joinToString(" ")

    if (!doesStringContainSurrounding(token)) {
      return when (surroundingsIndex) {
        0 -> token
        else -> null
      }
    }

    if (surroundingsIndex > 0) {
      if (token.length <= 2) {
        return null
      }

      val (a, b) = timestampSurroundings[surroundingsIndex - 1]
      if (token.first() == a && token.last() == b) {
        token = token.slice(1..token.length - 2)
      } else {
        return null
      }
    } else {
      return null
    }

    return token
  }

  private fun nextState(): String? {
    if (surroundingsIndex >= maxJ) {
      surroundingsIndex = 0
      subtokenIndex -= 1
    } else {
      surroundingsIndex += 1
    }

    return this.tokenByState()
  }

  private fun isLastState(): Boolean {
    return subtokenIndex < 0
  }
}

// NOTE: This is not thread safe
val CYCLIC_CAP = 100
private val cyclicTimestampSubtokenPatterns: MutableList<TimestampSubtokens> = mutableListOf()

private fun pushSubtokenPattern(pattern: TimestampSubtokens) {
  if (cyclicTimestampSubtokenPatterns.size > CYCLIC_CAP) {
    cyclicTimestampSubtokenPatterns.removeAt(0)
  }
  cyclicTimestampSubtokenPatterns.add(pattern)
}

class Timestamp(private val line: String, private val timestampFormat: String? = null) {
  // ... how did it become so convoluted ???
  //
  // TODO: Using LogFormat
  // TODO: Refactor this class into something nicer
  private var timestampString = ""

  public val nonTimestampString
    get() = TimestampSubtokens.textMinusSubtoken(line, timestampString)

  public val string
    get() = timestampString

  public val actualEpoch = extractEpoch()
  public var injectedEpoch: Double? = null
  public val epoch
    get() = if (injectedEpoch != null) injectedEpoch else actualEpoch

  private fun generateSubTokens(): Sequence<String> {
    return TimestampSubtokens(line).asSequence()
  }

  private fun tryExtractEpoch(from: String): Double? {
    var timestampVal: Double? = null

    if (this.timestampFormat != null) {
      val formatter = TimestampFormatter(this.timestampFormat)

      formatter.parse(from).let {
        if (it != null) {
          timestampVal = it
        }
      }
    }

    if (timestampVal == null) {
      for (formatter in dateFormatters) {
        if (timestampVal != null) {
          break
        }

        formatter.parse(from).let {
          if (it != null) {
            timestampVal = it
          }
        }
      }
    }

    if (timestampVal == null) {
      try {
        timestampVal = from.toDouble()
      } catch (ex: NumberFormatException) {}
    }

    if (timestampVal != null) {
      this.timestampString = from
      return timestampVal
    }
    return null
  }

  private fun extractEpoch(): Double? {
    for (potentialPattern in cyclicTimestampSubtokenPatterns.iterator()) {
      this.tryExtractEpoch(potentialPattern.copy(text = line).current()).let {
        if (it != null) {
          return it
        }
      }
    }

    for (possiblyTimestamp in generateSubTokens()) {
      this.tryExtractEpoch(possiblyTimestamp).let {
        if (it != null) {
          return it
        }
      }
    }

    this.timestampString = ""
    return null
  }
}
