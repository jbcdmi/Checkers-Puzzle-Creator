package DraughtsPlay.engine.move

import DraughtsPlay.engine.core.Board
import DraughtsPlay.engine.core.Move
import DraughtsPlay.engine.core.Piece
import DraughtsPlay.engine.core.PlayerColor
import DraughtsPlay.engine.rules.RuleVariant

/**
 * Pure validation/query helpers used by both the UI layer (to check a proposed tap/drag
 * before applying it) and by the AI search. All functions are read-only with respect to
 * [Board]; none mutate state.
 */
object MoveValidator {

    /** True if [move] is present in this position's legal move list under [variant]. */
    fun isLegalMove(board: Board, move: Move, color: Int, variant: RuleVariant): Boolean =
        MoveGenerator.generateMoves(board, color, variant).any {
            it.fromIndex == move.fromIndex && it.toIndex == move.toIndex && it.capturedPath == move.capturedPath
        }

    /** True if moving from [fromIndex] to [toIndex] is legal for [color] under [variant]. */
    fun isValidMove(
        board: Board,
        fromIndex: Int,
        toIndex: Int,
        color: Int,
        variant: RuleVariant
    ): Boolean =
        MoveGenerator.generateMoves(board, color, variant)
            .any { it.fromIndex == fromIndex && it.toIndex == toIndex }

    /** True if the piece at [index] has at least one legal move (quiet or capture). */
    fun canMove(board: Board, index: Int, variant: RuleVariant): Boolean =
        MoveGenerator.generateMovesForPiece(board, index, variant).isNotEmpty()

    /** True if the piece at [index] has at least one legal capture available. */
    fun canCapture(board: Board, index: Int, variant: RuleVariant): Boolean =
        MoveGenerator.generateCaptureTree(board, index, variant).isNotEmpty()

    /** True if [color] has at least one mandatory capture available under [variant]. */
    fun mustCapture(board: Board, color: Int, variant: RuleVariant): Boolean =
        variant.mandatoryCapture && MoveGenerator.generateCaptureMoves(board, color, variant)
            .isNotEmpty()

    /** True if the piece at [index] has zero legal moves (fully blocked). */
    fun isBlocked(board: Board, index: Int, variant: RuleVariant): Boolean =
        !canMove(board, index, variant)

    /** True if the square at [index] holds a piece belonging to [color] that can currently move. */
    fun isMovable(board: Board, index: Int, color: Int, variant: RuleVariant): Boolean {
        val piece = board.getPiece(index)
        return Piece.colorOf(piece) == color && canMove(board, index, variant)
    }

    /** True if the piece at [index] has any legal (quiet or capture) moves. */
    fun pieceCanMove(board: Board, index: Int, variant: RuleVariant): Boolean =
        canMove(board, index, variant)

    /** True if the piece at [index] has any legal capture. */
    fun pieceCanCapture(board: Board, index: Int, variant: RuleVariant): Boolean =
        canCapture(board, index, variant)

    /**
     * True if, mid-capture-chain, the piece now at [index] (with current type [pieceType])
     * has a further capture available from its current square — used by UI layers driving
     * an interactive multi-jump.
     */
    fun canContinueCapture(
        board: Board,
        index: Int,
        pieceType: Int,
        variant: RuleVariant
    ): Boolean {
        val scratchBoard = board.cloneBoard()
        scratchBoard.setPiece(index, pieceType)
        return MoveGenerator.generateCaptureTree(scratchBoard, index, variant).isNotEmpty()
    }

    /** True if landing on row [y] would promote a man belonging to [color]. */
    fun isPromotion(y: Int, color: Int, variant: RuleVariant): Boolean =
        variant.isPromotionSquare(y, color)

    /** True if the piece at [index] is a king. */
    fun isKing(board: Board, index: Int): Boolean = Piece.isKing(board.getPiece(index))

    /** True if the piece at [index] belongs to the opponent of [color]. */
    fun isEnemy(board: Board, index: Int, color: Int): Boolean =
        Piece.colorOf(board.getPiece(index)) == PlayerColor.opposite(color)

    /** True if the piece at [index] belongs to [color]. */
    fun isFriend(board: Board, index: Int, color: Int): Boolean =
        Piece.colorOf(board.getPiece(index)) == color

    /** True if the square at [index] is empty. */
    fun isEmpty(board: Board, index: Int): Boolean = board.isEmpty(index)

    /** True if [index] is a valid on-board index for [board]'s size. */
    fun isInsideBoard(board: Board, index: Int): Boolean = board.isInsideBoard(index)
}
