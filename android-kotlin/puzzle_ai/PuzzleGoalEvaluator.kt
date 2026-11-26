package DraughtsPlay.engine.puzzle_ai

import DraughtsPlay.engine.ai.Evaluation
import DraughtsPlay.engine.core.Board
import DraughtsPlay.engine.core.Move
import DraughtsPlay.engine.core.Piece
import DraughtsPlay.engine.core.PlayerColor
import DraughtsPlay.engine.core.PositionUtils
import DraughtsPlay.engine.move.MoveGenerator
import DraughtsPlay.engine.rules.RuleVariant
import kotlin.math.abs

/**
 * Evaluates puzzle win/loss conditions and computes goal-aware heuristic scores
 * for non-terminal positions during puzzle search.
 *
 * Convention:
 * - Player = [PlayerColor.WHITE] (`pIndex = 0`)
 * - Robot  = [PlayerColor.BLACK] (`pIndex = 1`)
 */
object PuzzleGoalEvaluator {

    /** Returns an updated [PuzzleProgress] after [moverColor] executes [move]. */
    fun advanceProgress(
        progress: PuzzleProgress,
        move: Move,
        moverColor: Int
    ): PuzzleProgress = advanceProgress(
        progress = progress,
        moverColor = moverColor,
        capturedCount = move.captureCount,
        capturedKingCount = move.capturedPieces.count { Piece.isKing(it) },
        promoted = move.isPromotion
    )

    /**
     * Overload for UI/Activity move code that tracks hits and promotion across
     * `ArrayList<ActionMove>` steps in `moveToNext`.
     */
    fun advanceProgress(
        progress: PuzzleProgress,
        moverColor: Int,
        capturedCount: Int,
        capturedKingCount: Int,
        promoted: Boolean
    ): PuzzleProgress {
        return if (moverColor == PlayerColor.WHITE) {
            progress.copy(
                playerMovesUsed = progress.playerMovesUsed + 1,
                capturesByPlayer = progress.capturesByPlayer + capturedCount,
                kingsMadeByPlayer = progress.kingsMadeByPlayer + if (promoted) 1 else 0,
                kingsCapturedByPlayer = progress.kingsCapturedByPlayer + capturedKingCount
            )
        } else {
            progress.copy(
                robotMovesUsed = progress.robotMovesUsed + 1,
                playerPiecesLost = progress.playerPiecesLost + capturedCount
            )
        }
    }

    /**
     * Checks whether the puzzle is already won, lost, or still in progress.
     * [hasLegalMovesForSideToMove] avoids redundant move generation when the caller
     * has already generated legal moves for [sideToMove].
     */
    fun evaluateStatus(
        board: Board,
        progress: PuzzleProgress,
        challenge: PuzzleChallenge,
        sideToMove: Int,
        variant: RuleVariant,
        hasLegalMovesForSideToMove: Boolean? = null
    ): PuzzleStatus {
        val playerPieces = board.countPieces(PlayerColor.WHITE)
        val robotPieces = board.countPieces(PlayerColor.BLACK)

        if (playerPieces == 0) return PuzzleStatus.PLAYER_LOST

        val hasMoves = hasLegalMovesForSideToMove
            ?: MoveGenerator.generateMoves(board, sideToMove, variant).isNotEmpty()

        // Immediate goal checks (before checking moveLimit expiry)
        when (challenge.type) {
            PuzzleChallengeType.CAPTURE_COUNT -> {
                if (progress.capturesByPlayer >= challenge.target) return PuzzleStatus.PLAYER_WON
            }

            PuzzleChallengeType.MAKE_KINGS -> {
                val kingsOnBoard = (board.countKings(PlayerColor.WHITE) - progress.initialPlayerKings)
                    .coerceAtLeast(0)
                val totalMade = maxOf(progress.kingsMadeByPlayer, kingsOnBoard)
                if (totalMade >= challenge.target) return PuzzleStatus.PLAYER_WON
            }

            PuzzleChallengeType.CAPTURE_KING -> {
                if (progress.kingsCapturedByPlayer >= challenge.target) return PuzzleStatus.PLAYER_WON
            }

            PuzzleChallengeType.CAPTURE_ALL_OPPONENTS -> {
                if (robotPieces == 0) return PuzzleStatus.PLAYER_WON
            }

            PuzzleChallengeType.WIN_IN_X_MOVES -> {
                if (robotPieces == 0) return PuzzleStatus.PLAYER_WON
                if (sideToMove == PlayerColor.BLACK && !hasMoves) return PuzzleStatus.PLAYER_WON
            }

            PuzzleChallengeType.WIN_NO_LOSS -> {
                if (progress.playerPiecesLost > 0) return PuzzleStatus.PLAYER_LOST
                if (robotPieces == 0) return PuzzleStatus.PLAYER_WON
                if (sideToMove == PlayerColor.BLACK && !hasMoves) return PuzzleStatus.PLAYER_WON
            }

            PuzzleChallengeType.SURVIVE_MOVES -> {
                val surviveGoal = if (challenge.target > 0) challenge.target else challenge.moveLimit
                if (progress.playerMovesUsed >= surviveGoal && playerPieces > 0) {
                    return PuzzleStatus.PLAYER_WON
                }
            }
        }

        // If either side has no legal moves and the win condition above was not met, Player loses.
        if (!hasMoves) {
            return PuzzleStatus.PLAYER_LOST
        }

        // Out of moves without completing the challenge.
        if (progress.playerMovesUsed >= challenge.moveLimit) {
            return PuzzleStatus.PLAYER_LOST
        }

        return PuzzleStatus.IN_PROGRESS
    }

    /**
     * Goal-aware static heuristic from **White's (Player's) perspective**
     * (positive = favorable for Player, negative = favorable for Robot).
     * Reuses [Evaluation.evaluateBoard] and adds challenge-specific shaping.
     */
    fun evaluateFromPlayerPerspective(
        board: Board,
        progress: PuzzleProgress,
        challenge: PuzzleChallenge,
        variant: RuleVariant,
        sideToMove: Int
    ): Int {
        var score = Evaluation.evaluateBoard(board, variant, sideToMove)

        when (challenge.type) {
            PuzzleChallengeType.CAPTURE_COUNT -> {
                score += progress.capturesByPlayer * 220
            }

            PuzzleChallengeType.MAKE_KINGS -> {
                score += progress.kingsMadeByPlayer * 350
                val promoRow = variant.promotionRow(PlayerColor.WHITE)
                var closestManBonus = 0
                for (i in board.squares.indices) {
                    if (board.squares[i] == Piece.WHITE_MAN) {
                        val y = PositionUtils.indexToY(i, board.size)
                        val dist = abs(y - promoRow)
                        val bonus = (board.size - dist) * 25
                        if (bonus > closestManBonus) closestManBonus = bonus
                    }
                }
                score += closestManBonus
            }

            PuzzleChallengeType.CAPTURE_KING -> {
                score += progress.kingsCapturedByPlayer * 400
            }

            PuzzleChallengeType.CAPTURE_ALL_OPPONENTS,
            PuzzleChallengeType.WIN_IN_X_MOVES -> {
                score -= board.countPieces(PlayerColor.BLACK) * 80
            }

            PuzzleChallengeType.WIN_NO_LOSS -> {
                score -= progress.playerPiecesLost * 500
                score -= board.countPieces(PlayerColor.BLACK) * 80
            }

            PuzzleChallengeType.SURVIVE_MOVES -> {
                score += board.countPieces(PlayerColor.WHITE) * 90
                score += progress.playerMovesUsed * 40
            }
        }

        return score
    }
}
