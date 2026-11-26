package DraughtsPlay.engine.puzzle_ai

import DraughtsPlay.engine.ai.MoveOrdering
import DraughtsPlay.engine.core.Board
import DraughtsPlay.engine.core.Move
import DraughtsPlay.engine.core.PlayerColor
import DraughtsPlay.engine.move.MoveGenerator
import DraughtsPlay.engine.rules.RuleVariant
import kotlin.math.max
import kotlin.math.min

/**
 * Deterministic puzzle-aware AI engine for Checkers puzzles.
 *
 * Unlike [DraughtsPlay.engine.ai.CheckersAI] (which plays general checkers without
 * knowing the puzzle's [PuzzleChallenge] or `moveLimit`), [PuzzleAI]:
 * 1. Understands every [PuzzleChallengeType] and `moveLimit` via [PuzzleGoalEvaluator].
 * 2. Treats reaching `moveLimit` without the player meeting the goal as a win for the Robot.
 * 3. Runs deterministically (no random move jitter) so puzzles always defend consistently.
 * 4. Reuses [Board], [MoveGenerator], [MoveOrdering], and [DraughtsPlay.engine.ai.Evaluation]
 *    without modifying any existing AI/engine files.
 */
class PuzzleAI(
    private val variant: RuleVariant,
    private val maxSearchDepth: Int = 8
) {
    companion object {
        private const val PUZZLE_WIN_SCORE = 1_000_000
    }

    var lastSearchNodes: Long = 0
        private set

    var lastSearchDepth: Int = 0
        private set

    /**
     * Computes the Robot's ([PlayerColor.BLACK]) move for the given [board], [progress],
     * and [challenge]. If [scriptedMoves] contains an entry for `progress.robotMovesUsed`
     * that is legal on [board], that scripted move is returned; otherwise runs search.
     */
    fun findBestRobotMove(
        board: Board,
        progress: PuzzleProgress,
        challenge: PuzzleChallenge,
        robotColor: Int = PlayerColor.BLACK,
        scriptedMoves: List<PuzzleScriptedMove> = emptyList()
    ): Move? {
        val scripted = scriptedMoves.getOrNull(progress.robotMovesUsed)
        if (scripted != null) {
            val legalMoves = MoveGenerator.generateMoves(board, robotColor, variant)
            val match = legalMoves.firstOrNull {
                it.fromX == scripted.fromX &&
                    it.fromY == scripted.fromY &&
                    it.toX == scripted.toX &&
                    it.toY == scripted.toY
            }
            if (match != null) {
                lastSearchNodes = 1
                lastSearchDepth = 0
                return match
            }
        }
        return findBestMoveInternal(board, progress, challenge, robotColor)
    }

    /**
     * Computes the Player's ([PlayerColor.WHITE]) best solving move (useful for a
     * Hint button or verifying puzzle solvability). Returns null if no legal moves exist.
     */
    fun findBestPlayerMove(
        board: Board,
        progress: PuzzleProgress,
        challenge: PuzzleChallenge,
        playerColor: Int = PlayerColor.WHITE
    ): Move? = findBestMoveInternal(board, progress, challenge, playerColor)

    private fun findBestMoveInternal(
        board: Board,
        progress: PuzzleProgress,
        challenge: PuzzleChallenge,
        sideToMove: Int
    ): Move? {
        val legalMoves = MoveGenerator.generateMoves(board, sideToMove, variant)
        if (legalMoves.isEmpty()) return null
        if (legalMoves.size == 1) {
            lastSearchNodes = 1
            lastSearchDepth = 1
            return legalMoves[0]
        }

        val remainingPlayerMoves = max(1, challenge.moveLimit - progress.playerMovesUsed)
        // Each player move is 2 plies (player + robot), plus 2 extra plies for horizon safety.
        val targetDepth = min(maxSearchDepth, max(4, remainingPlayerMoves * 2 + 2))

        lastSearchNodes = 0
        var bestMove = legalMoves[0]
        var bestValue = Int.MIN_VALUE
        val ordered = MoveOrdering.orderMoves(legalMoves)
        val nextSide = PlayerColor.opposite(sideToMove)

        for (move in ordered) {
            val undo = board.applyMove(move)
            val nextProgress = PuzzleGoalEvaluator.advanceProgress(progress, move, sideToMove)
            val value = -negamax(
                board = board,
                progress = nextProgress,
                challenge = challenge,
                depth = targetDepth - 1,
                sideToMove = nextSide,
                alpha = -PUZZLE_WIN_SCORE - 1,
                beta = PUZZLE_WIN_SCORE + 1,
                ply = 1
            )
            board.undoMove(undo)

            if (value > bestValue) {
                bestValue = value
                bestMove = move
            }
        }

        lastSearchDepth = targetDepth
        return bestMove
    }

    private fun negamax(
        board: Board,
        progress: PuzzleProgress,
        challenge: PuzzleChallenge,
        depth: Int,
        sideToMove: Int,
        alpha: Int,
        beta: Int,
        ply: Int
    ): Int {
        lastSearchNodes++

        val moves = MoveGenerator.generateMoves(board, sideToMove, variant)
        val status = PuzzleGoalEvaluator.evaluateStatus(
            board = board,
            progress = progress,
            challenge = challenge,
            sideToMove = sideToMove,
            variant = variant,
            hasLegalMovesForSideToMove = moves.isNotEmpty()
        )

        if (status == PuzzleStatus.PLAYER_WON) {
            val playerScore = PUZZLE_WIN_SCORE - ply
            return if (sideToMove == PlayerColor.WHITE) playerScore else -playerScore
        }
        if (status == PuzzleStatus.PLAYER_LOST) {
            val playerScore = -(PUZZLE_WIN_SCORE - ply)
            return if (sideToMove == PlayerColor.WHITE) playerScore else -playerScore
        }

        if (depth <= 0) {
            val playerScore = PuzzleGoalEvaluator.evaluateFromPlayerPerspective(
                board = board,
                progress = progress,
                challenge = challenge,
                variant = variant,
                sideToMove = sideToMove
            )
            return if (sideToMove == PlayerColor.WHITE) playerScore else -playerScore
        }

        var a = alpha
        var best = Int.MIN_VALUE
        val nextSide = PlayerColor.opposite(sideToMove)
        val ordered = MoveOrdering.orderMoves(moves)

        for (move in ordered) {
            val undo = board.applyMove(move)
            val nextProgress = PuzzleGoalEvaluator.advanceProgress(progress, move, sideToMove)
            val value = -negamax(
                board = board,
                progress = nextProgress,
                challenge = challenge,
                depth = depth - 1,
                sideToMove = nextSide,
                alpha = -beta,
                beta = -a,
                ply = ply + 1
            )
            board.undoMove(undo)

            if (value > best) best = value
            if (best > a) a = best
            if (a >= beta) break
        }

        return best
    }
}
