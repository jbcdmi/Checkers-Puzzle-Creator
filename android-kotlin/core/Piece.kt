package DraughtsPlay.engine.core

/**
 * Player color constants. Kept as plain [Int] (rather than an enum) so they can be used
 * directly as array indices and compared with zero-allocation integer branches in hot
 * search/evaluation loops.
 */
object PlayerColor {
    const val WHITE: Int = 0
    const val BLACK: Int = 1
    const val NONE: Int = -1

    /** Returns the opposing color of [color]. */
    fun opposite(color: Int): Int = when (color) {
        WHITE -> BLACK
        BLACK -> WHITE
        else -> NONE
    }
}

/**
 * Piece value constants and pure helper functions operating on the [IntArray] board
 * representation. All functions are branch-cheap and allocation-free so they can be
 * called millions of times per second during search.
 */
object Piece {
    const val EMPTY: Int = 0
    const val WHITE_MAN: Int = 1
    const val BLACK_MAN: Int = 2
    const val WHITE_KING: Int = 3
    const val BLACK_KING: Int = 4

    /** True if [piece] represents an empty square. */
    fun isEmpty(piece: Int): Boolean = piece == EMPTY

    /** True if [piece] belongs to the white player (man or king). */
    fun isWhite(piece: Int): Boolean = piece == WHITE_MAN || piece == WHITE_KING

    /** True if [piece] belongs to the black player (man or king). */
    fun isBlack(piece: Int): Boolean = piece == BLACK_MAN || piece == BLACK_KING

    /** True if [piece] is a king (either color). */
    fun isKing(piece: Int): Boolean = piece == WHITE_KING || piece == BLACK_KING

    /** True if [piece] is a regular man (either color). */
    fun isMan(piece: Int): Boolean = piece == WHITE_MAN || piece == BLACK_MAN

    /** Returns [PlayerColor.WHITE], [PlayerColor.BLACK] or [PlayerColor.NONE] for [piece]. */
    fun colorOf(piece: Int): Int = when {
        isWhite(piece) -> PlayerColor.WHITE
        isBlack(piece) -> PlayerColor.BLACK
        else -> PlayerColor.NONE
    }

    /** Returns the man piece constant for [color]. */
    fun manOf(color: Int): Int = if (color == PlayerColor.WHITE) WHITE_MAN else BLACK_MAN

    /** Returns the king piece constant for [color]. */
    fun kingOf(color: Int): Int = if (color == PlayerColor.WHITE) WHITE_KING else BLACK_KING

    /** Returns the promoted (king) version of [piece], or [piece] itself if already a king or empty. */
    fun promote(piece: Int): Int = when (piece) {
        WHITE_MAN -> WHITE_KING
        BLACK_MAN -> BLACK_KING
        else -> piece
    }

    /** True if [a] and [b] are non-empty and belong to the same player. */
    fun isFriend(a: Int, b: Int): Boolean = a != EMPTY && b != EMPTY && colorOf(a) == colorOf(b)

    /** True if [a] and [b] are non-empty and belong to opposing players. */
    fun isEnemy(a: Int, b: Int): Boolean = a != EMPTY && b != EMPTY && colorOf(a) != colorOf(b)
}
