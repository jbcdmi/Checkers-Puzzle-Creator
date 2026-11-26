package DraughtsPlay.engine.rules

import DraughtsPlay.engine.core.Board
import DraughtsPlay.engine.core.Piece
import DraughtsPlay.engine.core.PlayerColor
import DraughtsPlay.engine.core.PositionUtils

/** Identifies a concrete rule variant without relying on `is` chains elsewhere in the engine. */
enum class VariantType {
    AMERICAN, RUSSIAN, BRAZILIAN, INTERNATIONAL, CANADIAN
}

/**
 * Strategy-pattern base for a checkers rule variant. Each concrete subclass
 * ([AmericanRules], etc.) supplies the configuration that
 * differs between variants; the shared movement/capture algorithms live in
 * [DraughtsPlay.engine.move.MoveGenerator] and are driven entirely by this configuration
 * so no variant-specific branching is required outside this class hierarchy.
 *
 * @property boardSize the N in the variant's NxN board.
 * @property flyingKings if true, kings may move/capture any distance along a diagonal
 *   (international-style); if false, kings move exactly one square like men (American-style).
 * @property menCaptureBackward if true, a man may capture backwards even though it can only
 *   step forward on a non-capturing move.
 * @property mandatoryCapture if true, a capture must be played whenever one is available.
 * @property mustMaximizeCapture if true, when multiple capture sequences are available the
 *   player is restricted to the sequence(s) that capture the greatest number of pieces
 *   (and, where tied, kings are usually preferred — see [preferKingCaptures]).
 * @property preferKingCaptures if true and [mustMaximizeCapture] is true, ties in captured
 *   piece count are broken in favor of sequences that capture more kings.
 */
abstract class RuleVariant(
    val boardSize: Int,
    val flyingKings: Boolean,
    val menCaptureBackward: Boolean,
    val mandatoryCapture: Boolean,
    val mustMaximizeCapture: Boolean,
    val preferKingCaptures: Boolean = mustMaximizeCapture
) {
    abstract val variantType: VariantType

    /** The board row a piece of [color] must reach to be promoted to a king. */
    open fun promotionRow(color: Int): Int = if (color == PlayerColor.WHITE) 0 else boardSize - 1

    /** True if landing on row [y] promotes a man of [color]. */
    fun isPromotionSquare(y: Int, color: Int): Boolean = y == promotionRow(color)

    /** The forward row-delta for a man of [color]'s non-capturing step (-1 = toward row 0). */
    fun forwardDirection(color: Int): Int = if (color == PlayerColor.WHITE) -1 else 1

    /**
     * Builds the standard starting position for this variant: men fill the dark squares
     * of the first and last `rowsPerSide` rows, leaving the middle rows empty.
     */
    open fun initialSetup(): IntArray {
        val squares = IntArray(boardSize * boardSize) { Piece.EMPTY }
        val rowsPerSide = (boardSize - 2) / 2
        for (y in 0 until boardSize) {
            for (x in 0 until boardSize) {
                if (!PositionUtils.isDarkSquare(x, y)) continue
                val index = PositionUtils.xyToIndex(x, y, boardSize)
                when {
                    y < rowsPerSide -> squares[index] = Piece.BLACK_MAN
                    y >= boardSize - rowsPerSide -> squares[index] = Piece.WHITE_MAN
                }
            }
        }
        return squares
    }

    /** Convenience factory for a fresh [Board] set up per [initialSetup]. */
    fun newBoard(): Board = Board(boardSize, initialSetup())
}
