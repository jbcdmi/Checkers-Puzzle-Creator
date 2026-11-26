package DraughtsPlay.engine.core

/**
 * Represents a single legal move, which may be a simple step or a full multi-jump
 * capture sequence. For multi-jump captures, [completePath] holds every square index
 * visited (from -> intermediate landing squares -> final square) and [capturedPath] /
 * [capturedPieces] hold the indices and piece values of every piece removed along the way.
 */
data class Move(
    val fromX: Int,
    val fromY: Int,
    val toX: Int,
    val toY: Int,
    val fromIndex: Int,
    val toIndex: Int,
    val completePath: List<Int> = listOf(fromIndex, toIndex),
    val capturedPieces: List<Int> = emptyList(),
    val capturedPath: List<Int> = emptyList(),
    val isCapture: Boolean = false,
    val isMultipleCapture: Boolean = false,
    val isPromotion: Boolean = false,
    val isKingMove: Boolean = false,
    var score: Int = 0
) {
    /** Number of enemy pieces removed by this move. */
    val captureCount: Int get() = capturedPieces.size

    override fun toString(): String {
        val path = completePath.joinToString("->")
        return "Move($path, capture=$isCapture x$captureCount, promo=$isPromotion)"
    }
}