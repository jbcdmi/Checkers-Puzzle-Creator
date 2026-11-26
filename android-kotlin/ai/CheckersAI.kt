package DraughtsPlay.engine.ai

import DraughtsPlay.engine.core.Board
import DraughtsPlay.engine.core.Move
import DraughtsPlay.engine.core.PlayerColor
import DraughtsPlay.engine.move.MoveGenerator
import DraughtsPlay.engine.rules.RuleVariant
import kotlin.random.Random

/** Selectable AI strength. See [CheckersAI] for how each maps to search depth/behavior. */
enum class Difficulty {
    EASY, MEDIUM, HARD, VERY_HARD;

    override fun toString(): String = when (this) {
        EASY -> "Easy"
        MEDIUM -> "Medium"
        HARD -> "Hard"
        VERY_HARD -> "Very Hard"
    }
}

/**
 * Public entry point for computer play: owns the search infrastructure (transposition
 * table, Zobrist hasher) for a given [variant] and exposes [findBestMove] as the single
 * call a UI layer needs to make.
 *
 * - EASY: depth 2, then picks randomly among the top-scoring moves for variety.
 * - MEDIUM: fixed depth 4 alpha-beta.
 * - HARD: fixed depth 6 alpha-beta.
 * - VERY_HARD: iterative deepening from 1 to 8+ plies with transposition-table reuse
 *   and killer-move ordering between iterations, returning the deepest completed result.
 */
class CheckersAI(private val variant: RuleVariant, var difficulty: Difficulty = Difficulty.MEDIUM) {

    private val zobrist = ZobristHash(variant.boardSize)
    private val tt = TranspositionTable()
    private val random = Random(System.nanoTime())

    /** Total nodes examined during the most recent [findBestMove] call, for diagnostics/UI display. */
    var lastSearchNodes: Long = 0
        private set

    /** Depth actually completed by the most recent [findBestMove] call. */
    var lastSearchDepth: Int = 0
        private set

    /**
     * Computes the engine's chosen [Move] for [color] to play on [board]. Returns null
     * only if [color] has no legal move (the caller should treat that as game over).
     */
    fun findBestMove(board: Board, color: Int): Move? {
        val legalMoves = MoveGenerator.generateMoves(board, color, variant)
        if (legalMoves.isEmpty()) return null
        if (legalMoves.size == 1) return legalMoves[0]

        return when (difficulty) {
            Difficulty.EASY -> findEasyMove(board, color, legalMoves)
            Difficulty.MEDIUM -> findFixedDepthMove(board, color, legalMoves, depth = 4)
            Difficulty.HARD -> findFixedDepthMove(board, color, legalMoves, depth = 6)
            Difficulty.VERY_HARD -> findIterativeDeepeningMove(
                board,
                color,
                legalMoves,
                maxDepth = 8
            )
        }
    }

    private fun findEasyMove(board: Board, color: Int, moves: List<Move>): Move {
        val search = AlphaBeta(variant, zobrist, tt)
        val scored = moves.map { move ->
            val undo = board.applyMove(move)
            val value = -search.search(board, depth = 1, sideToMove = PlayerColor.opposite(color))
            board.undoMove(undo)
            move to value
        }
        lastSearchNodes = search.nodesSearched
        lastSearchDepth = 2
        var best = Int.MIN_VALUE
        for ((_, value) in scored) if (value > best) best = value
        // Widen the acceptance window slightly so Easy doesn't always find the single best move.
        val topTier = scored.filter { it.second >= best - 25 }
        return topTier[random.nextInt(topTier.size)].first
    }

    private fun findFixedDepthMove(board: Board, color: Int, moves: List<Move>, depth: Int): Move {
        val search = AlphaBeta(variant, zobrist, tt)
        var bestMove = moves[0]
        var bestValue = Int.MIN_VALUE
        val nextSide = PlayerColor.opposite(color)
        val ordered = MoveOrdering.orderMoves(moves)
        for (move in ordered) {
            val undo = board.applyMove(move)
            val value = -search.search(board, depth - 1, nextSide)
            board.undoMove(undo)
            if (value > bestValue) {
                bestValue = value
                bestMove = move
            }
        }
        lastSearchNodes = search.nodesSearched
        lastSearchDepth = depth
        return bestMove
    }

    private fun findIterativeDeepeningMove(
        board: Board,
        color: Int,
        moves: List<Move>,
        maxDepth: Int
    ): Move {
        var bestMove = moves[0]
        var totalNodes = 0L
        val nextSide = PlayerColor.opposite(color)

        for (depth in 2..maxDepth) {
            val search = AlphaBeta(variant, zobrist, tt)
            var bestValue = Int.MIN_VALUE
            val ordered = MoveOrdering.orderMoves(moves, ttMove = bestMove)
            for (move in ordered) {
                val undo = board.applyMove(move)
                val value = -search.search(board, depth - 1, nextSide)
                board.undoMove(undo)
                if (value > bestValue) {
                    bestValue = value
                    bestMove = move
                }
            }
            totalNodes += search.nodesSearched
            lastSearchDepth = depth
        }
        lastSearchNodes = totalNodes
        return bestMove
    }

    /** Clears cached search state, e.g. when starting a new game or switching variants. */
    fun reset() {
        tt.clear()
    }
}
