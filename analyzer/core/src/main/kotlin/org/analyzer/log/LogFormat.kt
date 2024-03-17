package org.analyzer.kotlin.log

/*
 *  This class accepts `format` which specifies log format.
 *  The format should consist of <Symbols> and normal characters.
 *  All <Symbols> will be extracted as single words, at the end it is assumed, that log content is specifies.
 *  Ex.
 *  Format: "<Test1> <Test2> abc"
 *  Log: "SomeWord AnotherWord abc Log line content here"
 *  Result: {
 *    Test1 = SomeWord,
 *    Test2 = AnotherWord,
 *    Content = Log line content here
 *  }
 */

class LogContents(
    val fields: Map<String, String>,
    val content: String
)

class LogFormat(val format: String) {
    // TODO: Handle normal characters
    private val tokenizer = Tokenizer().withSeparator(" ")
    private val symbolList: List<String?>

    init {
        val tokens = tokenizer.tokenize(format)
        symbolList = tokens.map {
            getPredefinedSymbol(it)
        }.toList()
    }

    public fun matchLine(line: String): LogContents {
        val lineTokens = tokenizer.tokenize(line)
        if (lineTokens.size < symbolList.size) {
            throw RuntimeException("Input line does not match this format !")
        }

        val fields = emptyMap<String, String>().toMutableMap()
        for (i in 0..symbolList.size-1) {
            if (symbolList[i] != null) {
                fields.put(symbolList[i]!!, lineTokens[i])
            }
        }
        val content = lineTokens.slice(symbolList.size..lineTokens.size-1).joinToString(separator=" ")

        return LogContents(fields, content)
    }

    private fun getPredefinedSymbol(word: String): String? {
        if (word.length < 2) {
            return null;
        }

        if (word.first() == '<' && word.last() == '>') {
            return word.slice(1 .. word.length - 2)
        }
        else {
            return null;
        }
    }
}
