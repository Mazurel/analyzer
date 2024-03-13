package org.analyzer.parsers

import kotlin.text.Regex
import org.analyzer.dictionary.AvailableDictionaries
import org.analyzer.parsers.HEX_NODE

const val MAIN_SEPARATOR = " "
const val DISCARDABLE_SYMBOLS = ",.[]<>?:;"

public fun tokenize(line: String): List<String> {
    val separators = arrayOf(MAIN_SEPARATOR)
    return line.split(*separators).map {
      eachLine ->
        eachLine.trim {
            DISCARDABLE_SYMBOLS.contains(it)
        }.trimEnd {
            DISCARDABLE_SYMBOLS.contains(it)
        }.toString()
    }.filter {
        it.length > 0
    }
}

public interface PatternNode {
    fun match(word: String): Boolean
    fun humanReadable(): String
}

public class RegexNode(val pattern: String, val fullName: String? = null) : PatternNode {
    val regex = Regex(pattern)

    override fun match(word: String): Boolean = regex.matchEntire(word) != null
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is RegexNode) return false

        return pattern == other.pattern
    }

    override fun toString(): String = "Regex($pattern, $fullName)"
    override fun humanReadable(): String = if (fullName == null) "<$pattern>"
                                           else "<$fullName>"
}

public class ParamNode : PatternNode {
    override fun match(word: String): Boolean = true
    override fun equals(other: Any?): Boolean {
        return other is ParamNode
    }

    override fun toString(): String = "Parameter"
    override fun humanReadable(): String = "<Param>"
}

public class SymbolNode(val symbol: String) : PatternNode {
    val comparableSymbol: String
        get() = symbol.lowercase() // TODO: Strip surrounding symbols

    override fun match(word: String): Boolean = comparableSymbol == word
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is SymbolNode) return false

        return symbol == other.symbol
    }

    override fun toString(): String = "Symbol($symbol)"
    override fun humanReadable(): String = "$symbol"
}

@JvmInline
public value class Pattern(private val nodes: List<PatternNode>) {
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
            sb.append(MAIN_SEPARATOR)
        }
        return sb.toString()
    }
}

private class PatternBuilder {
    val nodes: MutableList<PatternNode> = mutableListOf()

    fun pushNode(node: PatternNode) {
        nodes.add(node)
    }

    fun build(): Pattern = Pattern(nodes.toList())
}

public typealias PatternId = Int

public val NUMBER_NODE = RegexNode("\\-?[0-9]+", "Number")
public val HEX_NODE = RegexNode("0x[0-9ABCDEFabcdef]+", "HexNumber")
public val CUSTOM_WORD_NODE = RegexNode("[a-zA-Z]+", "Word")
public val SYMBOL_NODE = RegexNode("[+-/=<>%^()]+", "Symbol")

public class DictParser(val dictionary: AvailableDictionaries = AvailableDictionaries.ENGLISH) {
    private val dictLookup = dictionary.getDictLookuper()
    private val patterns: MutableList<Pattern> = mutableListOf()

    val patternsAmount: Int
        get() = patterns.size

    fun extractPatternFromLine(line: String): Pattern {
        val tokens = tokenize(line)
        val builder = PatternBuilder()

        for (token in tokens) {
          when {
              NUMBER_NODE.match(token) -> builder.pushNode(NUMBER_NODE)
              HEX_NODE.match(token) -> builder.pushNode(HEX_NODE)
              dictLookup.lookupWord(token) -> builder.pushNode(SymbolNode(token))
              CUSTOM_WORD_NODE.match(token) -> builder.pushNode(CUSTOM_WORD_NODE)
              SYMBOL_NODE.match(token) -> builder.pushNode(SYMBOL_NODE)
              else -> builder.pushNode(ParamNode())
          }
        }

        return builder.build()
    }

    fun putPattern(inputPattern: Pattern): PatternId {
        return patterns.indexOf(inputPattern).let {
            when {
                it < 0 -> {
                    patterns.add(inputPattern)
                    patternsAmount - 1
                }
                else -> it
            }
        }
    }

    fun getPatternId(inputPattern: Pattern): PatternId {
        return patterns.indexOf(inputPattern).let {
            when {
                it < 0 -> throw RuntimeException("Pattern does not exist")
                else -> it
            }
        }
    }
}

