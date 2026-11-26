package DraughtsPlay.engine.ai

import DraughtsPlay.engine.core.Board
import DraughtsPlay.engine.core.Move
import DraughtsPlay.engine.core.PlayerColor
import DraughtsPlay.engine.move.MoveGenerator
import DraughtsPlay.engine.rules.RuleVariant

/** Score magnitude used to represent "side to move has no legal moves" (a loss). Kept well below any realistic material swing. */
private const val LOSS_SCORE = 1_000_000
private const val MAX_QUIESCENCE_DEPTH = 6

/**
 * Negamax-formulated alpha-beta search with transposition-table cutoffs/move-ordering and
 * a capture-only quiescence extension at the search horizon (so the engine never evaluates
 * a position mid-capture-exchange, which is the single biggest source of horizon-effect
 * blunders in checkers engines).
 *
 * All scores returned by [search] are from the perspective of [sideToMove] at the root of
 * that call (positive = good for the mover), per standard negamax convention.
 */
class AlphaBeta(
    private val variant: RuleVariant,
    private val zobrist: ZobristHash,
    private val tt: TranspositionTable
) {
    var nodesSearched: Long = 0
        private set

    /**
     * Searches [board] to [depth] plies for [sideToMove], returning the negamax score.
     * [killers] is an optional per-ply killer-move table (index = ply) shared across the
     * whole iterative-deepening call for better move ordering.
     */
    fun search(
        board: Board,
        depth: Int,
        sideToMove: Int,
        alpha: Int = -LOSS_SCORE - 1,
        beta: Int = LOSS_SCORE + 1,
        ply: Int = 0,
        killers: Array<MutableList<Move>>? = null
    ): Int {
        nodesSearched++
        val hash = zobrist.hash(board, sideToMove)
        val ttEntry = tt.get(hash)
        var a = alpha
        var b = beta

        if (ttEntry != null && ttEntry.depth >= depth) {
            when (ttEntry.bound) {
                BoundType.EXACT -> return ttEntry.score
                BoundType.LOWER_BOUND -> if (ttEntry.score > a) a = ttEntry.score
                BoundType.UPPER_BOUND -> if (ttEntry.score < b) b = ttEntry.score
            }
            if (a >= b) return ttEntry.score
        }

        val moves = MoveGenerator.generateMoves(board, sideToMove, variant)
        if (moves.isEmpty()) return -(LOSS_SCORE - ply)

        if (depth == 0) {
            return quiescence(board, sideToMove, a, b, 0)
        }

        val ordered = MoveOrdering.orderMoves(
            moves,
            ttEntry?.bestMove,
            killers?.getOrNull(ply) ?: emptyList()
        )
        val nextSide = PlayerColor.opposite(sideToMove)
        var best = Int.MIN_VALUE
        var bestMove: Move? = null
        val originalAlpha = a

        for (move in ordered) {
            val undo = board.applyMove(move)
            val value = -search(board, depth - 1, nextSide, -b, -a, ply + 1, killers)
            board.undoMove(undo)

            if (value > best) {
                best = value
                bestMove = move
            }
            if (best > a) a = best
            if (a >= b) {
                if (!move.isCapture) {
                    killers?.getOrNull(ply)?.let { list ->
                        if (list.none { it.fromIndex == move.fromIndex && it.toIndex == move.toIndex }) {
                            list.add(0, move)
                            if (list.size > 2) list.removeAt(list.size - 1)
                        }
                    }
                }
                break
            }
        }

        val bound = when {
            best <= originalAlpha -> BoundType.UPPER_BOUND
            best >= b -> BoundType.LOWER_BOUND
            else -> BoundType.EXACT
        }
        tt.store(hash, depth, best, bound, bestMove)
        return best
    }

    /**
     * Extends the search along capture chains only, past the nominal horizon, so the
     * static evaluator is never applied in the middle of a forced capture exchange.
     */
    private fun quiescence(board: Board, sideToMove: Int, alpha: Int, beta: Int, qDepth: Int): Int {
        nodesSearched++
        val standPat = perspectiveScore(board, sideToMove)
        if (qDepth >= MAX_QUIESCENCE_DEPTH) return standPat

        var a = alpha
        if (standPat >= beta) return standPat
        if (standPat > a) a = standPat

        val captures = MoveGenerator.generateCaptureMoves(board, sideToMove, variant)
        if (captures.isEmpty()) return standPat

        val ordered = MoveOrdering.orderMoves(captures)
        val nextSide = PlayerColor.opposite(sideToMove)
        var best = standPat
        for (move in ordered) {
            val undo = board.applyMove(move)
            val value = -quiescence(board, nextSide, -beta, -a, qDepth + 1)
            board.undoMove(undo)
            if (value > best) best = value
            if (best > a) a = best
            if (a >= beta) break
        }
        return best
    }

    private fun perspectiveScore(board: Board, sideToMove: Int): Int {
        val white = Evaluation.evaluateBoard(board, variant, sideToMove)
        return if (sideToMove == PlayerColor.WHITE) white else -white
    }
}
