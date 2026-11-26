package DraughtsPlay.engine.core

/**
 * Snapshot of every square touched by a single [Move] application, sufficient to
 * exactly reverse it via [Board.undoMove] without re-cloning the whole board.
 */
class MoveUndo internal constructor(
    internal val touchedIndices: IntArray,
    internal val touchedValues: IntArray
)

/**
 * Mutable board of size [size] x [size] backed by a flat [IntArray] of piece values.
 * Designed for high-frequency mutation during search: [applyMove] / [undoMove] mutate
 * in place and avoid allocating a new board on every ply.
 */
class Board(val size: Int, val squares: IntArray) {

    companion object {
        /** Creates an empty board of [size] x [size] squares. */
        fun empty(size: Int): Board = Board(size, IntArray(size * size) { Piece.EMPTY })
    }

    /** Returns the piece at flat [index]. */
    fun getPiece(index: Int): Int = squares[index]

    /** Returns the piece at coordinate ([x], [y]). */
    fun getPiece(x: Int, y: Int): Int = squares[PositionUtils.xyToIndex(x, y, size)]

    /** Sets the piece at flat [index] to [piece]. */
    fun setPiece(index: Int, piece: Int) {
        squares[index] = piece
    }

    /** Sets the piece at coordinate ([x], [y]) to [piece]. */
    fun setPiece(x: Int, y: Int, piece: Int) {
        squares[PositionUtils.xyToIndex(x, y, size)] = piece
    }

    /** Clears the square at flat [index]. */
    fun removePiece(index: Int) {
        squares[index] = Piece.EMPTY
    }

    /** True if the square at [index] is empty. */
    fun isEmpty(index: Int): Boolean = squares[index] == Piece.EMPTY

    /** True if [index] is a valid on-board index. */
    fun isInsideBoard(index: Int): Boolean = PositionUtils.isInsideIndex(index, size)

    /** True if (x, y) is a valid on-board coordinate. */
    fun isInsideBoard(x: Int, y: Int): Boolean = PositionUtils.isInside(x, y, size)

    /** Returns a deep, independent copy of this board. */
    fun cloneBoard(): Board = Board(size, squares.copyOf())

    /** Copies this board's squares into the caller-provided [dest] buffer (no allocation). */
    fun copyBoard(dest: IntArray) {
        squares.copyInto(dest)
    }

    /** Counts all pieces (men + kings) belonging to [color]. */
    fun countPieces(color: Int): Int {
        var count = 0
        for (p in squares) if (Piece.colorOf(p) == color) count++
        return count
    }

    /** Counts only king pieces belonging to [color]. */
    fun countKings(color: Int): Int {
        var count = 0
        for (p in squares) if (Piece.isKing(p) && Piece.colorOf(p) == color) count++
        return count
    }

    /** Counts only man pieces belonging to [color]. */
    fun countMen(color: Int): Int {
        var count = 0
        for (p in squares) if (Piece.isMan(p) && Piece.colorOf(p) == color) count++
        return count
    }

    /**
     * Applies [move] in place: relocates the moving piece along its full path, removes
     * every captured piece, and promotes the piece if [Move.isPromotion] is set.
     * Returns a [MoveUndo] snapshot that can be passed to [undoMove] to exactly reverse it.
     */
    fun applyMove(move: Move): MoveUndo {
        val touchedSet = LinkedHashMap<Int, Int>()

        fun touch(index: Int) {
            // Only remember the value the very first time a square is touched,
            // so undo restores the pre-move state even if a square is written twice.
            if (!touchedSet.containsKey(index)) touchedSet[index] = squares[index]
        }

        touch(move.fromIndex)
        touch(move.toIndex)
        for (cap in move.capturedPath) touch(cap)

        val movingPiece = squares[move.fromIndex]
        squares[move.fromIndex] = Piece.EMPTY
        for (cap in move.capturedPath) squares[cap] = Piece.EMPTY
        squares[move.toIndex] = if (move.isPromotion) Piece.promote(movingPiece) else movingPiece

        return MoveUndo(touchedSet.keys.toIntArray(), touchedSet.values.toIntArray())
    }

    /** Reverses a previously applied move using the [undo] snapshot returned by [applyMove]. */
    fun undoMove(undo: MoveUndo) {
        for (i in undo.touchedIndices.indices) {
            squares[undo.touchedIndices[i]] = undo.touchedValues[i]
        }
    }
}
