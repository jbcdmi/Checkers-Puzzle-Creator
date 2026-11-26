package DraughtsPlay.engine.ai

import DraughtsPlay.engine.core.Move

/**
 * Orders a move list to maximize alpha-beta cutoffs: transposition-table best move first,
 * then captures (biggest first), then killer moves for the current ply, then promotions,
 * with everything else last. Mutates the score field on each [Move] for diagnostics but
 * does not otherwise mutate the moves themselves.
 */
object MoveOrdering {

    /**
     * Returns [moves] sorted best-first. [ttMove] (if any) is pinned to the front;
     * [killers] are moves that caused a beta cutoff at this ply in a sibling branch.
     */
    fun orderMoves(
        moves: List<Move>,
        ttMove: Move? = null,
        killers: List<Move> = emptyList()
    ): List<Move> {
        for (move in moves) {
            move.score = scoreMove(move, ttMove, killers)
        }
        return moves.sortedByDescending { it.score }
    }

    private fun scoreMove(move: Move, ttMove: Move?, killers: List<Move>): Int {
        if (ttMove != null && sameMove(move, ttMove)) return Int.MAX_VALUE
        var score = 0
        if (move.isCapture) {
            score += 10_000 + move.captureCount * 1_000
            if (move.isMultipleCapture) score += 500
        }
        if (move.isPromotion) score += 800
        if (killers.any { sameMove(move, it) }) score += 300
        if (move.isKingMove) score += 50
        return score
    }

    private fun sameMove(a: Move, b: Move): Boolean =
        a.fromIndex == b.fromIndex && a.toIndex == b.toIndex && a.capturedPath == b.capturedPath
}
