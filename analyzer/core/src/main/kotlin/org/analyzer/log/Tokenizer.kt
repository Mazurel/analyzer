package org.analyzer.kotlin.log

class Tokenizer {
    private var mainSeparator: String? = null
    private var discardableSymbols: String = ""

    public fun withSeparator(sep: String): Tokenizer {
        mainSeparator = sep
        return this
    }

    public fun withDiscardableSymbols(vararg discardable: String): Tokenizer {
        discardableSymbols = discardable.joinToString(separator="")
        return this
    }

    public fun tokenize(line: String): List<String> {
        if (mainSeparator == null) {
            throw IllegalArgumentException("Tokenizer is not properly configured - No main separator was provided")
        }

        return line.split(mainSeparator!!)
                .map { eachLine ->
                    eachLine
                            .trim { discardableSymbols.contains(it) }
                            .trimEnd { discardableSymbols.contains(it) }
                            .toString()
                }
                .filter { it.length > 0 }
    }
}

