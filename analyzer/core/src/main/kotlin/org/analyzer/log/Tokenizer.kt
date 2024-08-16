package org.analyzer.kotlin.log

class Tokenizer {
  private var discardableSymbols: String = ""
  private var separators: MutableList<String> = mutableListOf()

  public fun withSeparators(vararg separators: String): Tokenizer {
    this.separators.addAll(separators)
    return this
  }

  public fun withDiscardableSymbols(vararg discardable: String): Tokenizer {
    discardableSymbols = discardable.joinToString(separator = "")
    return this
  }

  public fun tokenize(line: String): List<String> {
    if (this.separators.size <= 0) {
      throw IllegalArgumentException(
          "Tokenizer is not properly configured - No separator was provided")
    }

    return line
        .split(*this.separators.toTypedArray())
        .map { eachLine ->
          eachLine
              .trim { discardableSymbols.contains(it) }
              .trimEnd { discardableSymbols.contains(it) }
              .toString()
        }
        .filter { it.length > 0 }
  }
}
