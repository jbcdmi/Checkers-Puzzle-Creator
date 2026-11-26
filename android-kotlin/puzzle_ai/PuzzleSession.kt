package DraughtsPlay.engine.puzzle_ai

import DraughtsPlay.engine.core.Board
import DraughtsPlay.engine.core.Move
import DraughtsPlay.engine.core.PlayerColor
import DraughtsPlay.engine.move.MoveGenerator
import DraughtsPlay.engine.rules.RuleVariant

/**
 * Stateful runtime session for playing a [PuzzleLevel] in Android.
 *
 * Handles:
 * - Building the [Board] from [PuzzleLevel.boardSize] and [PuzzleLevel.board] (`pos = [x, y]`).
 * - Starting on [PuzzleLevel.firstTurn] (`0` = Player, `1` = Robot).
 * - Applying Player or Robot moves, updating [PuzzleProgress], and reporting [PuzzleStatus].
 */
class PuzzleSession private constructor(
    val level: PuzzleLevel,
    val variant: PuzzleRuleVariant,
    val board: Board
) {
    var currentTurn: Int = if (level.firstTurn == PlayerColor.BLACK) PlayerColor.BLACK else PlayerColor.WHITE
        private set

    var progress: PuzzleProgress = PuzzleProgress(
        initialPlayerKings = level.board.count { it.pIndex == PlayerColor.WHITE && it.isKing }
    )
        private set

    var status: PuzzleStatus = PuzzleStatus.IN_PROGRESS
        private set

    init {
        refreshStatus()
    }

    /** Returns all legal moves for the side currently to move (empty if puzzle is over). */
    fun getLegalMoves(): List<Move> {
        if (status != PuzzleStatus.IN_PROGRESS) return emptyList()
        return MoveGenerator.generateMoves(board, currentTurn, variant)
    }

    /** Applies a legal [move] for [currentTurn], advances turn and [progress], and updates [status]. */
    fun applyMove(move: Move): PuzzleStatus {
        if (status != PuzzleStatus.IN_PROGRESS) return status

        board.applyMove(move)
        progress = PuzzleGoalEvaluator.advanceProgress(progress, move, currentTurn)
        currentTurn = PlayerColor.opposite(currentTurn)
        refreshStatus()
        return status
    }

    /**
     * Lets [ai] choose and apply the Robot's move when `currentTurn == PlayerColor.BLACK`.
     * Returns the move played (or null if it's not Robot's turn / puzzle ended / no moves).
     */
    fun playRobotTurn(ai: PuzzleAI = PuzzleAI(variant)): Move? {
        if (status != PuzzleStatus.IN_PROGRESS || currentTurn != PlayerColor.BLACK) return null
        val move = ai.findBestRobotMove(
            board = board,
            progress = progress,
            challenge = level.challenge,
            robotColor = PlayerColor.BLACK,
            scriptedMoves = level.robotMoves
        ) ?: return null
        applyMove(move)
        return move
    }

    /** Computes a hint move for the Player when `currentTurn == PlayerColor.WHITE`. */
    fun findHintMove(ai: PuzzleAI = PuzzleAI(variant)): Move? {
        if (status != PuzzleStatus.IN_PROGRESS || currentTurn != PlayerColor.WHITE) return null
        return ai.findBestPlayerMove(board, progress, level.challenge, PlayerColor.WHITE)
    }

    private fun refreshStatus() {
        status = PuzzleGoalEvaluator.evaluateStatus(
            board = board,
            progress = progress,
            challenge = level.challenge,
            sideToMove = currentTurn,
            variant = variant
        )
    }

    companion object {
        /**
         * Creates a [PuzzleSession] from a [PuzzleLevel], adapting [baseVariant] (default
         * American rules) to `level.boardSize`.
         */
        fun create(
            level: PuzzleLevel,
            baseVariant: RuleVariant? = null
        ): PuzzleSession {
            val size = level.boardSize.coerceIn(6, 14)
            val variant = if (baseVariant != null) {
                PuzzleRuleVariant.fromVariant(baseVariant, size)
            } else {
                PuzzleRuleVariant.american(size)
            }

            val board = Board.empty(size)
            for (piece in level.board) {
                if (isValidPlacement(piece, size)) {
                    board.setPiece(piece.x, piece.y, piece.toPieceValue())
                }
            }

            return PuzzleSession(level, variant, board)
        }
    }
}
