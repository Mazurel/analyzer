package org.analyzer.kotlin.dictionary

fun alphabethicCompare(input: String, lookup: String): Int {
    // We compare `input` to `lookup`
    // When > 0 -> lookup is before input
    // When < 0 -> lookup is after input
    // When == 0 -> lookup == input
    return input.compareTo(lookup) // Use default comparison
}

public class DictLookuper constructor(val resourcePath: String, var resourceObject: Any? = null) {
    val words: List<String> = loadWords()

    private fun loadWords(): List<String> {
        if (resourceObject == null) {
            resourceObject = this
        }
        val reader =
            resourceObject!!.javaClass.getResourceAsStream(this.resourcePath)?.bufferedReader()
                        ?: throw RuntimeException("Invalid resource - $resourcePath")
        return reader.readLines()
                .map { it.trim().lowercase() }
                .sortedWith { a, b -> alphabethicCompare(a, b) }
                .toList()
    }

    public fun lookupWord(word: String): Boolean {
        val wordLowered = word.lowercase()
        val i = words.binarySearch { alphabethicCompare(it, wordLowered) }
        if (i < 0) return false else return true
    }
}

public enum class AvailableDictionaries(val resourcePath: String) {
    ENGLISH("/dictionaries/english.txt");

    public fun getDictLookuper(): DictLookuper {
      return DictLookuper(this.resourcePath)
    }
}
