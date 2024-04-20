package org.analyzer.kotlin.monge

private data class Border(val left: Int, val right: Int, val top: Int, val bottom: Int)

private class PreallocatedArray<T>(val size: Int, def: (Int) -> T) {
    init {
        assert(size > 0)
    }

    private val internalData = MutableList<T>(size, def)
    private var end = 0

    fun push(v: T) {
        if (end >= size) {
            throw RuntimeException("Tried to push over array size")
        }
        internalData[end] = v
        end++
    }

    fun last(): T {
        if (end <= 0) {
            throw RuntimeException("Array is empty")
        }

        return internalData[end - 1]
    }

    fun reset() {
        end = 0
    }
}

// We match blues to reds
// In terms of array:
// reds - Are vertical - we refer to them via `i` index
// blues - Are horizontal - we refer to them via `j` index
class BitonicMongeArray<R, B>(
        public val reds: List<R>,
        public val blues: List<B>,
        public val distanceBetween: (red: R, blue: B) -> Double
) {
    init {
        if (reds.size > blues.size) {
            throw RuntimeException("Reds list cannot be longer than blues")
        }
    }

    public val height = reds.size
    public val diagonalsAmount = blues.size - reds.size + 1

    private val diagonals: List<List<Double>> =
            List(diagonalsAmount) { diagonalIndex ->
                List(height) { elementIndex ->
                    val (i, j) = intoArrayIndicies(diagonalIndex + 1, elementIndex + 1)!!
                    distanceBetween(reds[i - 1], blues[j - 1])
                }
            }

    inline public fun show(
            printText: (String) -> Unit = { print(it) },
            newLine: () -> Unit = { println() },
            printHighlightedText: (String) -> Unit = { print(it) },
    ) {
        val matching = perfmatch()
        val colSize = blues.map { it.toString().length }.max() + 2

        newLine()
        printText(" ${" ".repeat(colSize)} ")
        for (h in blues) {
            printText(" ${h.toString().padEnd(colSize)} ")
        }
        for (i in 0..reds.size - 1) {
            val subresult = matching[i]

            newLine()
            printText(" ${reds[i].toString().padEnd(colSize)} ")
            for (j in 0..blues.size - 1) {
                val s = " " + distanceBetween(reds[i], blues[j]).toString().padEnd(colSize) + " "

                if (subresult != null && blues[j] == subresult.second) {
                    printHighlightedText(s)
                } else {
                    printText(s)
                }
            }
        }
        newLine()
    }

    private fun intoArrayIndicies(diagonalIndex: Int, element: Int): Pair<Int, Int>? {
        // Convert diagonal-based coordinates into array-based
        val i = element
        val j = diagonalIndex + element - 1

        if (i < 0 || i > reds.size || j < 0 || j > blues.size) {
            return null
        }
        return Pair(i, j)
    }

    // TODO: For concurrency, this will need to be modified
    private val separatingRows = PreallocatedArray<Int>(height + 1) { 0 }

    private fun findSeparatingRow(centerK: Int, top: Int, bottom: Int): Int {
        fun V(i1: Int, i2: Int): Double {
            return (i1..i2).map { diagonals[centerK - 1][it - 1] }.sum()
        }

        fun W(i1: Int, i2: Int): Double {
            return (i1..i2).map { diagonals[centerK][it - 1] }.sum()
        }

        separatingRows.reset()
        separatingRows.push(top)
        for (x in top..bottom) {
            if (V(separatingRows.last(), x) <
                            W(separatingRows.last(), x)
            ) {
                separatingRows.push(x)
            } else {
                separatingRows.push(separatingRows.last())
            }
        }

        return separatingRows.last()
    }

    public fun perfmatch(): List<Pair<Double, B>?> {
        // This is an implementation of section 4 - "Efficient minimum cost matching using quadrangle inequality"
        // DOI: https://doi.org/10.1109/SFCS.1992.267793
        //
        // Implementation notes:
        //  - I use 1-indexed values in the algorithm. The conversion is done right before reading
        // diagonals.
        //  - Always true: blues.size > reds.size

        // Simplest possible case - width == height
        if (diagonalsAmount == 1) {
            return (0..height - 1).map { Pair(diagonals[0][it], blues[it]) }.toList()
        }

        val result: MutableList<Pair<Double, B>?> = MutableList(height) { null }
        val borders: MutableList<Border> = mutableListOf()

        fun updateResult(diagonal: Int, element: Int) {
            var (i, j) = intoArrayIndicies(diagonal, element)!!
            val newCost = diagonals[diagonal - 1][element - 1]

            // Update only if there is no result, or current result is worse
            if (result[i - 1] != null && result[i - 1]!!.first < newCost) {
                return
            }

            result[i - 1] = Pair(newCost, blues[j - 1])
        }

        borders.add(Border(left = 1, top = 1, right = diagonalsAmount, bottom = height))
        while (borders.size > 0) {
            val border = borders.removeFirst()

            // Trival border cases
            if (border.left == border.right) {
                for (x in border.top..border.bottom) {
                    updateResult(border.left, x)
                }
                continue
            } else if (border.top == border.bottom) {
                for (x in border.left..border.right) {
                    updateResult(x, border.top)
                }
                continue
            }
            else if (border.top > border.bottom) {
                // Yet another edge case
                continue
            }

            assert(border.left < border.right)
            assert(border.top < border.bottom)

            val centerK = (border.right + border.left) / 2
            val separatingRow = findSeparatingRow(centerK, border.top, border.bottom)

            val topLeft =
                    Border(
                            left = border.left,
                            top = border.top,
                            right = centerK,
                            bottom = separatingRow
                    )
            borders.add(topLeft)

            if (separatingRow <= border.bottom) {
                val bottomRight =
                        Border(
                                left = centerK + 1,
                                top = separatingRow + 1,
                                right = border.right,
                                bottom = border.bottom
                        )

                borders.add(bottomRight)
            }
        }

        return result
    }
}
