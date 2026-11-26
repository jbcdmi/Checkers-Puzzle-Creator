package DraughtsPlay.engine.core

/** Immutable 2D board coordinate. (0,0) is the top-left square. */
data class Position(val x: Int, val y: Int)

/**
 * Pure coordinate <-> index conversion helpers shared by every board size.
 * All functions are `@JvmStatic`-style top-level pure math, safe to inline in hot paths.
 */
object PositionUtils {

    /** Converts a flat [index] into its X (column) coordinate for a board of [boardSize]. */
    fun indexToX(index: Int, boardSize: Int): Int = index % boardSize

    /** Converts a flat [index] into its Y (row) coordinate for a board of [boardSize]. */
    fun indexToY(index: Int, boardSize: Int): Int = index / boardSize

    /** Converts (x, y) coordinates into a flat array index for a board of [boardSize]. */
    fun xyToIndex(x: Int, y: Int, boardSize: Int): Int = y * boardSize + x

    /** True if (x, y) lies within a board of [boardSize]. */
    fun isInside(x: Int, y: Int, boardSize: Int): Boolean =
        x in 0 until boardSize && y in 0 until boardSize

    /** True if [index] lies within a board of [boardSize]. */
    fun isInsideIndex(index: Int, boardSize: Int): Boolean =
        index in 0 until (boardSize * boardSize)

    /** True if (x, y) sits on a playable (dark) square, i.e. (x + y) is odd. */
    fun isDarkSquare(x: Int, y: Int): Boolean = (x + y) % 2 == 1
}
