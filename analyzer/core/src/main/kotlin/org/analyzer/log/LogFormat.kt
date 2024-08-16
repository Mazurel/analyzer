package org.analyzer.kotlin.log

/*
 *  This class accepts `format` which specifies log format.
 *  The format should consist of <Symbols> and normal characters.
 *  All <Symbols> will be extracted as single words, at the end it is assumed, that log content is specified.
 *  Ex.
 *  Format: "<Test1> <Test2> abc"
 *  Log: "SomeWord AnotherWord abc Log line content here"
 *  Result: {
 *    Test1 = SomeWord,
 *    Test2 = AnotherWord,
 *    Content = Log line content here
 *  }
 */

class FormattingException(message: String) : RuntimeException(message)

class FormattedLogContent(val fields: Map<String, String>, val content: String)

class LogFormat(val format: String) {
  // TODO: Timestamp and it's format
  // TODO: Handle normal characters
  private val tokenizer = Tokenizer().withSeparators(" ")
  private val symbolList: List<String?>

  init {
    val tokens = tokenizer.tokenize(format)
    symbolList = tokens.map { getPredefinedSymbol(it) }.toList()
  }

  companion object {
    fun basic() = LogFormat("")
  }

  public fun matchLine(line: String): FormattedLogContent {
    val lineTokens = tokenizer.tokenize(line)
    if (lineTokens.size < symbolList.size) {
      throw FormattingException("Input line does not match this format !")
    }

    val fields = emptyMap<String, String>().toMutableMap()
    for (i in 0..symbolList.size - 1) {
      if (symbolList[i] != null) {
        fields.put(symbolList[i]!!, lineTokens[i])
      }
    }
    val content =
        lineTokens.slice(symbolList.size..lineTokens.size - 1).joinToString(separator = " ")

    return FormattedLogContent(fields, content)
  }

  public fun hasSymbol(symbol: String): Boolean {
    return symbolList.contains(symbol)
  }

  private fun getPredefinedSymbol(word: String): String? {
    if (word.length < 2) {
      return null
    }

    if (word.first() == '<' && word.last() == '>') {
      return word.slice(1..word.length - 2)
    } else {
      return null
    }
  }
}
