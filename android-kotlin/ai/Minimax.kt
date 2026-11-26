package DraughtsPlay.engine.ai

import DraughtsPlay.engine.core.Board
import DraughtsPlay.engine.core.PlayerColor
import DraughtsPlay.engine.move.MoveGenerator
import DraughtsPlay.engine.rules.RuleVariant

/**
 * Plain minimax search with no pruning. Provided as a correctness reference and for very
 * shallow searches (e.g. Easy difficulty) where alpha-beta's extra bookkeeping isn't
 * needed; [AlphaBeta] should be preferred for anything depth >= 3.
 */
object Minimax {

    /** Returns the minimax value of [board] to [depth] plies, from White's perspective. */
    fun minimax(board: Board, depth: Int, sideToMove: Int, variant: RuleVariant): Int {
        if (depth == 0) return Evaluation.evaluateBoard(board, variant, sideToMove)

        val moves = MoveGenerator.generateMoves(board, sideToMove, variant)
        if (moves.isEmpty()) {
            // No legal moves: the side to move loses.
            return if (sideToMove == PlayerColor.WHITE) Int.MIN_VALUE + 1 else Int.MAX_VALUE - 1
        }

        val nextSide = PlayerColor.opposite(sideToMove)
        return if (sideToMove == PlayerColor.WHITE) {
            var best = Int.MIN_VALUE
            for (move in moves) {
                val undo = board.applyMove(move)
                val value = minimax(board, depth - 1, nextSide, variant)
                board.undoMove(undo)
                if (value > best) best = value
            }
            best
        } else {
            var best = Int.MAX_VALUE
            for (move in moves) {
                val undo = board.applyMove(move)
                val value = minimax(board, depth - 1, nextSide, variant)
                board.undoMove(undo)
                if (value < best) best = value
            }
            best
        }
    }
}
