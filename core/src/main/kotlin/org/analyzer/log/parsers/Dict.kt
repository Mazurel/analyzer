package org.analyzer.kotlin.log.parsers

import kotlin.text.Regex
import org.analyzer.kotlin.dictionary.AvailableDictionaries
import org.analyzer.kotlin.log.Tokenizer

public interface DictPatternNode {
  fun match(word: String): Boolean

  fun humanReadable(): String
}

internal class DictRegexNode(val pattern: String, val fullName: String? = null) : DictPatternNode {
  val regex = Regex(pattern)

  override fun match(word: String): Boolean = regex.matchEntire(word) != null

  override fun equals(other: Any?): Boolean {
    if (this === other) return true
    if (other !is DictRegexNode) return false

    return this.pattern == other.pattern
  }

  override fun toString(): String = "Regex($pattern, $fullName)"

  override fun humanReadable(): String = if (fullName == null) "<$pattern>" else "<$fullName>"
}

internal class DictParamNode : DictPatternNode {
  override fun match(word: String): Boolean = true

  override fun equals(other: Any?): Boolean {
    return other is DictParamNode
  }

  override fun toString(): String = "Parameter"

  override fun humanReadable(): String = "<Param>"
}

internal class DictSymbolNode(val symbol: String) : DictPatternNode {
  val comparableSymbol: String
    get() = symbol.lowercase()

  override fun match(word: String): Boolean = comparableSymbol == word

  override fun equals(other: Any?): Boolean {
    if (this === other) return true
    if (other !is DictSymbolNode) return false

    return symbol == other.symbol
  }

  override fun toString(): String = "Symbol($symbol)"

  override fun humanReadable(): String = "$symbol"
}

@JvmInline
public value class DictPattern(public val nodes: List<DictPatternNode>) {
  fun match(tokens: List<String>): Boolean {
    if (tokens.size != nodes.size) {
      return false
    }

    return nodes.zip(tokens).all { (node, token) -> node.match(token) }
  }

  fun humanReadable(): String {
    val sb = StringBuilder()
    nodes.forEach {
      sb.append(it.humanReadable())
      sb.append(" ")
    }
    return sb.toString()
  }
}

private class DictPatternBuilder {
  val nodes: MutableList<DictPatternNode> = mutableListOf()

  fun pushNode(node: DictPatternNode) {
    nodes.add(node)
  }

  fun build(): DictPattern = DictPattern(nodes.toList())
}

internal val NUMBER_NODE = DictRegexNode("\\-?[0-9]+", "Number")
internal val HEX_NODE = DictRegexNode("0x[0-9ABCDEFabcdef]+", "HexNumber")
internal val CUSTOM_WORD_NODE = DictRegexNode("[a-zA-Z]+", "Word")
internal val SYMBOL_NODE = DictRegexNode("[+-/=<>%^()]+", "Symbol")

public class DictParser(val dictionary: AvailableDictionaries = AvailableDictionaries.ENGLISH) :
    LogParser {
  private val dictLookup = dictionary.getDictLookuper()
  private val patterns: MutableList<DictPattern> = mutableListOf()
  private val tokenizer =
      Tokenizer()
          .withDiscardableSymbols(",", ".", "[", "]", "<", ">", "?", ":", ";")
          .withSeparators(" ", ",", "=")

  public val patternsAmount: Int
    get() = patterns.size

  public fun extractPatternFromLine(line: String): DictPattern {
    val tokens = tokenizer.tokenize(line)
    val builder = DictPatternBuilder()

    for (token in tokens) {
      when {
        NUMBER_NODE.match(token) -> builder.pushNode(NUMBER_NODE)
        HEX_NODE.match(token) -> builder.pushNode(HEX_NODE)
        dictLookup.lookupWord(token) -> builder.pushNode(DictSymbolNode(token))
        CUSTOM_WORD_NODE.match(token) -> builder.pushNode(CUSTOM_WORD_NODE)
        SYMBOL_NODE.match(token) -> builder.pushNode(SYMBOL_NODE)
        else -> builder.pushNode(DictParamNode())
      }
    }

    return builder.build()
  }

  public fun putPattern(inputPattern: DictPattern): PatternID {
    return patterns.indexOf(inputPattern).let {
      when {
        it < 0 -> {
          patterns.add(inputPattern)
          PatternID(0, (patternsAmount - 1).toLong())
        }
        else -> PatternID(0, it.toLong())
      }
    }
  }

  public fun getPatternId(inputPattern: DictPattern): PatternID? {
    return patterns.indexOf(inputPattern).let {
      when {
        it < 0 -> null
        else -> PatternID(0, it.toLong())
      }
    }
  }

  override public fun extractPattern(line: String): PatternID {
    val pattern = extractPatternFromLine(line)
    val res = getPatternId(pattern)
    if (res == null) {
      throw IllegalArgumentException("Unknown pattern")
    }
    return res
  }

  override public fun learnLine(line: String): PatternID? {
    val pattern = extractPatternFromLine(line)
    return putPattern(pattern)
  }

  override public fun humanReadable(patternId: PatternID): String {
    return this.patterns[patternId.leastSignificantBits.toInt()].humanReadable()
  }
}
