package DraughtsPlay.engine.ai

import DraughtsPlay.engine.ai.Evaluation.evaluateBoard
import DraughtsPlay.engine.core.Board
import DraughtsPlay.engine.core.Piece
import DraughtsPlay.engine.core.PlayerColor
import DraughtsPlay.engine.core.PositionUtils
import DraughtsPlay.engine.move.MoveGenerator
import DraughtsPlay.engine.rules.RuleVariant
import kotlin.math.abs

/**
 * Static board evaluator. [evaluateBoard] returns a score from White's perspective —
 * positive favors White, negative favors Black — combining material, positional, and
 * tactical heuristics. All weights are tunable constants at the top of the file.
 */
object Evaluation {

    private const val MAN_VALUE = 100
    private const val KING_VALUE = 175
    private const val MOBILITY_WEIGHT = 4
    private const val CENTER_WEIGHT = 6
    private const val EDGE_PENALTY = 4
    private const val PROMOTION_DISTANCE_WEIGHT = 3
    private const val THREATENED_PENALTY = 35
    private const val PROTECTED_BONUS = 8
    private const val DOUBLE_CORNER_BONUS = 12
    private const val BACK_ROW_BONUS = 10
    private const val TEMPO_WEIGHT = 2
    private const val ADVANCEMENT_WEIGHT = 2

    /** Full weighted evaluation of [board] under [variant], from White's perspective. */
    fun evaluateBoard(board: Board, variant: RuleVariant, sideToMove: Int): Int {
        var score = 0
        score += materialScore(board)
        score += mobilityScore(board, variant)
        score += positionalScore(board, variant)
        score += tacticalScore(board, variant)
        score += tempoScore(sideToMove)
        score += endgameAdjustment(board)
        return score
    }

    // --- Material & kings -------------------------------------------------

    private fun materialScore(board: Board): Int {
        var score = 0
        for (piece in board.squares) {
            score += when (piece) {
                Piece.WHITE_MAN -> MAN_VALUE
                Piece.WHITE_KING -> KING_VALUE
                Piece.BLACK_MAN -> -MAN_VALUE
                Piece.BLACK_KING -> -KING_VALUE
                else -> 0
            }
        }
        return score
    }

    // --- Mobility -----------------------------------------------------------

    private fun mobilityScore(board: Board, variant: RuleVariant): Int {
        val whiteMoves = MoveGenerator.generateMoves(board, PlayerColor.WHITE, variant).size
        val blackMoves = MoveGenerator.generateMoves(board, PlayerColor.BLACK, variant).size
        return (whiteMoves - blackMoves) * MOBILITY_WEIGHT
    }

    // --- Positional: center control, edge penalty, promotion distance, advancement, double corner, back row ---

    private fun positionalScore(board: Board, variant: RuleVariant): Int {
        var score = 0
        val size = board.size
        val centerLo = size / 2 - 1
        val centerHi = size / 2
        for (index in board.squares.indices) {
            val piece = board.squares[index]
            if (piece == Piece.EMPTY) continue
            val color = Piece.colorOf(piece)
            val sign = if (color == PlayerColor.WHITE) 1 else -1
            val x = PositionUtils.indexToX(index, size)
            val y = PositionUtils.indexToY(index, size)

            // Center control.
            if (x in centerLo..centerHi && y in centerLo..centerHi) score += sign * CENTER_WEIGHT

            // Edge penalty (pieces on the outer file are less flexible).
            if (x == 0 || x == size - 1) score -= sign * EDGE_PENALTY

            // Promotion distance / advancement for men.
            if (Piece.isMan(piece)) {
                val promotionRow = variant.promotionRow(color)
                val distance = abs(y - promotionRow)
                score += sign * (size - distance) * PROMOTION_DISTANCE_WEIGHT / size
                val advancement = if (color == PlayerColor.WHITE) (size - 1 - y) else y
                score += sign * advancement * ADVANCEMENT_WEIGHT
            }

            // Back row protection: a man still on its own back row denies the opponent an easy king.
            val ownBackRow = if (color == PlayerColor.WHITE) size - 1 else 0
            if (Piece.isMan(piece) && y == ownBackRow) score += sign * BACK_ROW_BONUS
        }

        score += doubleCornerScore(board, PlayerColor.WHITE) - doubleCornerScore(
            board,
            PlayerColor.BLACK
        )
        return score
    }

    /** Bonus for [color] retaining control of its own defensive double-corner squares. */
    private fun doubleCornerScore(board: Board, color: Int): Int {
        val size = board.size
        val backRow = if (color == PlayerColor.WHITE) size - 1 else 0
        var score = 0
        for (x in intArrayOf(1, size - 2)) {
            if (!PositionUtils.isInside(x, backRow, size)) continue
            val index = PositionUtils.xyToIndex(x, backRow, size)
            if (Piece.colorOf(board.getPiece(index)) == color) score += DOUBLE_CORNER_BONUS
        }
        return score
    }

    // --- Tactical: threatened / protected pieces ----------------------------

    private fun tacticalScore(board: Board, variant: RuleVariant): Int {
        var score = 0
        val whiteCaptures = MoveGenerator.generateCaptureMoves(board, PlayerColor.WHITE, variant)
        val blackCaptures = MoveGenerator.generateCaptureMoves(board, PlayerColor.BLACK, variant)

        val threatenedByWhite = whiteCaptures.flatMap { it.capturedPath }.toSet()
        val threatenedByBlack = blackCaptures.flatMap { it.capturedPath }.toSet()

        for (index in threatenedByWhite) {
            score -= pieceWeight(board.getPiece(index)) * THREATENED_PENALTY / 100
        }
        for (index in threatenedByBlack) {
            score += pieceWeight(board.getPiece(index)) * THREATENED_PENALTY / 100
        }

        // Protected pieces: a man/king with a same-color piece diagonally behind it (supporting it)
        // is harder to profitably capture.
        val size = board.size
        for (index in board.squares.indices) {
            val piece = board.squares[index]
            if (piece == Piece.EMPTY) continue
            val color = Piece.colorOf(piece)
            val sign = if (color == PlayerColor.WHITE) 1 else -1
            val x = PositionUtils.indexToX(index, size)
            val y = PositionUtils.indexToY(index, size)
            val behindY = if (color == PlayerColor.WHITE) y + 1 else y - 1
            var protectedCount = 0
            for (dx in intArrayOf(-1, 1)) {
                val bx = x + dx
                if (!PositionUtils.isInside(bx, behindY, size)) continue
                val behindIndex = PositionUtils.xyToIndex(bx, behindY, size)
                if (Piece.colorOf(board.getPiece(behindIndex)) == color) protectedCount++
            }
            score += sign * protectedCount * PROTECTED_BONUS
        }
        return score
    }

    private fun pieceWeight(piece: Int): Int = if (Piece.isKing(piece)) KING_VALUE else MAN_VALUE

    // --- Tempo & endgame adjustment ------------------------------------------

    private fun tempoScore(sideToMove: Int): Int =
        if (sideToMove == PlayerColor.WHITE) TEMPO_WEIGHT else -TEMPO_WEIGHT

    /**
     * When one side has a decisive material edge and few pieces remain, nudge the score
     * further in that side's favor (encourage trading down toward a won endgame) rather
     * than drifting toward drawish simplification.
     */
    private fun endgameAdjustment(board: Board): Int {
        val white = board.countPieces(PlayerColor.WHITE)
        val black = board.countPieces(PlayerColor.BLACK)
        val totalPieces = white + black
        if (totalPieces > 8) return 0
        val diff = white - black
        return if (abs(diff) >= 2) diff * 15 else 0
    }
}