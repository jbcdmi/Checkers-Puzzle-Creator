package DraughtsPlay.engine.move

import DraughtsPlay.ActionMove
import DraughtsPlay.Position
import DraughtsPlay.engine.core.Board
import DraughtsPlay.engine.core.Move
import DraughtsPlay.engine.core.MovePossibility
import DraughtsPlay.engine.core.Piece
import DraughtsPlay.engine.core.PositionUtils
import DraughtsPlay.engine.rules.RuleVariant
import DraughtsPlay.engine.rules.VariantType
import com.potential.zone.checkers.offline.board.game.draughts.MyGame

private val DIAGONALS = arrayOf(
    intArrayOf(-1, -1), intArrayOf(1, -1), intArrayOf(-1, 1), intArrayOf(1, 1)
)

/**
 * Generates every legal move for a given board/variant combination: quiet moves, single
 * captures, multi-jump capture chains (including flying-king captures), promotions, and
 * the mandatory / maximum-capture filtering each variant requires. All search is
 * allocation-light: capture chains are explored via in-place backtracking on a scratch
 * copy of the board's squares rather than cloning the board on every ply.
 */
object MoveGenerator {

    private val TAG: String = MyGame.MainTAG + this.javaClass.simpleName

    // ---------------------------------------------------------------------
    // Public facade — named per the required API surface.
    // ---------------------------------------------------------------------

    /** All legal moves for [color] on [board] under [variant], with mandatory/maximum-capture rules applied. */
    fun generateMovesForPlayer(
        board: Board,
        color: Int,
        variant: RuleVariant
    ): List<MovePossibility> {
//        val allMoves: List<Move> = generateMoves(board, color, variant)

//        return allMoves
//            .sortedBy { it.fromIndex }
//            .groupBy { it.fromIndex }
//            .map { (index, moves) ->
//                MovePossibility(
//                    index = index,
//                    x = moves.first().fromX,
//                    y = moves.first().fromY,
//                    moves = moves
//                )
//            }
//            .sortedBy { it.index }

        return generateMoves(board, color, variant)
            .groupBy { it.fromIndex }
            .map { (index, moves) ->
                MovePossibility(
                    index = index,
                    x = moves.first().fromX,
                    y = moves.first().fromY,
                    moves = moves.map { buildActionMoves(it, variant) }
                        .toCollection(ArrayList())
                )
            }
            .sortedBy { it.index }

    }

    private fun buildActionMoves(
        move: Move,
        variant: RuleVariant
    ): ArrayList<ActionMove> {

        val actions = ArrayList<ActionMove>()

        for (i in 1 until move.completePath.size) {

            val fromIndex = move.completePath[i - 1]
            val toIndex = move.completePath[i]

            val fromPosition = Position(
                PositionUtils.indexToX(fromIndex, variant.boardSize),
                PositionUtils.indexToY(fromIndex, variant.boardSize)
            )
            val toPosition = Position(
                PositionUtils.indexToX(toIndex, variant.boardSize),
                PositionUtils.indexToY(toIndex, variant.boardSize)
            )
            val action = if (move.isCapture) {
                val hitIndex = move.capturedPath[i - 1]
                val hitPos = Position(
                    PositionUtils.indexToX(hitIndex, variant.boardSize),
                    PositionUtils.indexToY(hitIndex, variant.boardSize)
                )
                ActionMove(
                    fromPosition = fromPosition,
                    toPosition = toPosition,
                    hitPos = hitPos
                )
            } else {
                ActionMove(
                    fromPosition = fromPosition,
                    toPosition = toPosition,
                )
            }

            actions.add(action)
        }

        return actions
    }

    /** All legal moves for [color] on [board] under [variant], with mandatory/maximum-capture rules applied. */
    fun generateMoves(board: Board, color: Int, variant: RuleVariant): List<Move> {
        val captures = generateCaptureMoves(board, color, variant)
        if (captures.isNotEmpty()) {
            return if (variant.mandatoryCapture) applyMaximumCaptureFilter(
                captures,
                variant
            ) else captures
        }
        return generateNormalMoves(board, color, variant)
    }

    /** All legal moves (quiet + capture, unfiltered) originating from the single piece at [index]. */
    fun generateMovesForPiece(board: Board, index: Int, variant: RuleVariant): List<Move> {
        val piece = board.getPiece(index)
        if (Piece.isEmpty(piece)) return emptyList()
        val color = Piece.colorOf(piece)
        val captures = generateCaptureTree(board, index, variant)
        return captures.ifEmpty { generateNormalMovesForPiece(board, index, color, variant) }
    }

    /** All quiet (non-capturing) moves for [color]. */
    fun generateNormalMoves(board: Board, color: Int, variant: RuleVariant): List<Move> {
        val moves = mutableListOf<Move>()
        for (index in board.squares.indices) {
            val piece = board.squares[index]
            if (piece == Piece.EMPTY || Piece.colorOf(piece) != color) continue
            moves += generateNormalMovesForPiece(board, index, color, variant)
        }
        return moves
    }

    /** All capture moves (fully expanded multi-jump chains) for [color], unfiltered by maximum-capture rules. */
    fun generateCaptureMoves(board: Board, color: Int, variant: RuleVariant): List<Move> {
        val moves = mutableListOf<Move>()
        for (index in board.squares.indices) {
            val piece = board.squares[index]
            if (piece == Piece.EMPTY || Piece.colorOf(piece) != color) continue
            moves += generateCaptureTree(board, index, variant)
        }
        return moves
    }

    /** Quiet moves for kings only (non-flying: one step; flying: any distance along empty diagonal). */
    fun generateKingMoves(board: Board, color: Int, variant: RuleVariant): List<Move> {
        val moves = mutableListOf<Move>()
        for (index in board.squares.indices) {
            val piece = board.squares[index]
            if (!Piece.isKing(piece) || Piece.colorOf(piece) != color) continue
            moves += generateNormalMovesForPiece(board, index, color, variant)
        }
        return moves
    }

    /** Capture chains originating from king pieces only. */
    fun generateKingCaptures(board: Board, color: Int, variant: RuleVariant): List<Move> {
        val moves = mutableListOf<Move>()
        for (index in board.squares.indices) {
            val piece = board.squares[index]
            if (!Piece.isKing(piece) || Piece.colorOf(piece) != color) continue
            moves += generateCaptureTree(board, index, variant)
        }
        return moves
    }

    /** Quiet long-distance slides for flying kings. Empty list under non-flying-king variants. */
    fun generateFlyingKingMoves(board: Board, color: Int, variant: RuleVariant): List<Move> {
        if (!variant.flyingKings) return emptyList()
        return generateKingMoves(board, color, variant)
    }

    /** All capture chains of length &gt; 1 jump (true multi-jumps) for [color]. */
    fun generateMultipleCaptures(board: Board, color: Int, variant: RuleVariant): List<Move> =
        generateCaptureMoves(board, color, variant).filter { it.isMultipleCapture }

    /** Every maximal capture sequence reachable from the piece at [index], as a flat list of [Move]s (the "tree" flattened to root-to-leaf paths). */
    fun generateCaptureTree(board: Board, index: Int, variant: RuleVariant): List<Move> {
        val piece = board.getPiece(index)
        if (Piece.isEmpty(piece)) return emptyList()
        val color = Piece.colorOf(piece)
        val scratch = board.squares.copyOf()
        val results = mutableListOf<Move>()
        val path = mutableListOf(index)
        val capturedPath = mutableListOf<Int>()
        val capturedPieces = mutableListOf<Int>()
        captureDFS(
            scratch,
            board.size,
            variant,
            color,
            index,
            piece,
            Piece.isMan(piece),
            path,
            capturedPath,
            capturedPieces,
            results
        )
        return results
    }

    /** Legal moves for [color] restricted to captures only, if [RuleVariant.mandatoryCapture] and any exist; otherwise all moves. */
    fun generateForcedMoves(board: Board, color: Int, variant: RuleVariant): List<Move> =
        generateMoves(board, color, variant)

    /** Capture moves for [color] filtered down to only the maximum-length (and, if applicable, king-preferring) sequences. */
    fun generateMaximumCaptureMoves(board: Board, color: Int, variant: RuleVariant): List<Move> {
        val captures = generateCaptureMoves(board, color, variant)
        return applyMaximumCaptureFilter(captures, variant)
    }

    // ---------------------------------------------------------------------
    // Move Converter
    // ---------------------------------------------------------------------

    fun convertMoveToActionMoveList(move: Move?, variant: RuleVariant): ArrayList<ActionMove> {
        if (move == null) {
            return ArrayList(0)
        }
        return buildActionMoves(move = move, variant = variant)
    }


    // ---------------------------------------------------------------------
    // Internal implementation
    // ---------------------------------------------------------------------

    private fun applyMaximumCaptureFilter(captures: List<Move>, variant: RuleVariant): List<Move> {
        if (captures.isEmpty()) return captures
        if (!variant.mustMaximizeCapture) return captures
        var maxCount = 0
        for (m in captures) if (m.captureCount > maxCount) maxCount = m.captureCount
        var filtered = captures.filter { it.captureCount == maxCount }
        if (variant.preferKingCaptures && filtered.size > 1) {
            val kingCounts = filtered.map { m -> m.capturedPieces.count { p -> Piece.isKing(p) } }
            var maxKings = 0
            for (k in kingCounts) if (k > maxKings) maxKings = k
            filtered = filtered.filterIndexed { idx, _ -> kingCounts[idx] == maxKings }
        }
        return filtered
    }

    private fun generateNormalMovesForPiece(
        board: Board,
        index: Int,
        color: Int,
        variant: RuleVariant
    ): List<Move> {
        val piece = board.getPiece(index)
        val moves = mutableListOf<Move>()
        val x = PositionUtils.indexToX(index, board.size)
        val y = PositionUtils.indexToY(index, board.size)

        if (Piece.isKing(piece) && variant.flyingKings) {
            for (dir in DIAGONALS) {
                var step = 1
                while (true) {
                    val nx = x + dir[0] * step
                    val ny = y + dir[1] * step
                    if (!PositionUtils.isInside(nx, ny, board.size)) break
                    val toIndex = PositionUtils.xyToIndex(nx, ny, board.size)
                    if (board.getPiece(toIndex) != Piece.EMPTY) break
                    moves += Move(
                        fromX = x, fromY = y, toX = nx, toY = ny,
                        fromIndex = index, toIndex = toIndex,
                        completePath = listOf(index, toIndex),
                        isKingMove = true
                    )
                    step++
                }
            }
            return moves
        }

        // Men (and non-flying kings) move exactly one square. Men move only forward;
        // kings under non-flying rules may move in all four diagonal directions.
        val directions = if (Piece.isKing(piece)) {
            DIAGONALS
        } else {
            val fwd = variant.forwardDirection(color)
            DIAGONALS.filter { it[1] == fwd }.toTypedArray()
        }

        for (dir in directions) {
            val nx = x + dir[0]
            val ny = y + dir[1]
            if (!PositionUtils.isInside(nx, ny, board.size)) continue
            val toIndex = PositionUtils.xyToIndex(nx, ny, board.size)
            if (board.getPiece(toIndex) != Piece.EMPTY) continue
            val promotes = Piece.isMan(piece) && variant.isPromotionSquare(ny, color)
            moves += Move(
                fromX = x, fromY = y, toX = nx, toY = ny,
                fromIndex = index, toIndex = toIndex,
                completePath = listOf(index, toIndex),
                isPromotion = promotes,
                isKingMove = Piece.isKing(piece)
            )
        }
        return moves
    }

    /**
     * Backtracking DFS over capture chains. Mutates [squares] in place (removing jumped
     * pieces and relocating the mover) then restores it on the way back up, so the caller's
     * real board is never touched. A branch that finds no further captures is recorded as a
     * completed [Move]; promotion — for men landing on the back row — always ends the chain.
     */
    private fun captureDFS(
        squares: IntArray,
        boardSize: Int,
        variant: RuleVariant,
        color: Int,
        currentIndex: Int,
        pieceType: Int,
        startedAsMan: Boolean,
        path: MutableList<Int>,
        capturedPath: MutableList<Int>,
        capturedPieces: MutableList<Int>,
        results: MutableList<Move>
    ) {
        val isFlyingKing = variant.flyingKings && Piece.isKing(pieceType)
        val x = PositionUtils.indexToX(currentIndex, boardSize)
        val y = PositionUtils.indexToY(currentIndex, boardSize)
        var foundAny = false

        for (dir in DIAGONALS) {
            if (isFlyingKing) {
                foundAny = flyingCaptureBranch(
                    squares, boardSize, variant, color, x, y, dir,
                    pieceType, startedAsMan, path, capturedPath, capturedPieces, results
                ) || foundAny
            } else {
                foundAny = stepCaptureBranch(
                    squares, boardSize, variant, color, x, y, dir,
                    pieceType, startedAsMan, path, capturedPath, capturedPieces, results
                ) || foundAny
            }
        }

        if (!foundAny && path.size > 1) {
            results += buildCaptureMove(
                path,
                capturedPath,
                capturedPieces,
                boardSize,
                pieceType,
                startedAsMan
            )
        }
    }

    private fun stepCaptureBranch(
        squares: IntArray, boardSize: Int, variant: RuleVariant, color: Int,
        x: Int, y: Int, dir: IntArray, pieceType: Int, startedAsMan: Boolean,
        path: MutableList<Int>, capturedPath: MutableList<Int>, capturedPieces: MutableList<Int>,
        results: MutableList<Move>
    ): Boolean {
        val midX = x + dir[0];
        val midY = y + dir[1]
        val landX = x + dir[0] * 2;
        val landY = y + dir[1] * 2
        if (!PositionUtils.isInside(landX, landY, boardSize)) return false
        val midIndex = PositionUtils.xyToIndex(midX, midY, boardSize)
        val landIndex = PositionUtils.xyToIndex(landX, landY, boardSize)
        val midPiece = squares[midIndex]
        if (midPiece == Piece.EMPTY || Piece.colorOf(midPiece) == color) return false
        if (midIndex in capturedPath) return false
        if (squares[landIndex] != Piece.EMPTY) return false

        val currentIndex = path.last()
        val savedFrom = squares[currentIndex]
        val savedMid = squares[midIndex]
        val savedLand = squares[landIndex]

        val promotes = Piece.isMan(pieceType) && variant.isPromotionSquare(landY, color)
        val newPieceType = if (promotes) Piece.promote(pieceType) else pieceType

        squares[currentIndex] = Piece.EMPTY
        squares[midIndex] = Piece.EMPTY
        squares[landIndex] = newPieceType

        path.add(landIndex)
        capturedPath.add(midIndex)
        capturedPieces.add(savedMid)

        if (promotes) {
            results += buildCaptureMove(
                path,
                capturedPath,
                capturedPieces,
                boardSize,
                newPieceType,
                startedAsMan
            )
        } else {
            captureDFS(
                squares,
                boardSize,
                variant,
                color,
                landIndex,
                newPieceType,
                startedAsMan,
                path,
                capturedPath,
                capturedPieces,
                results
            )
        }

        path.removeAt(path.size - 1)
        capturedPath.removeAt(capturedPath.size - 1)
        capturedPieces.removeAt(capturedPieces.size - 1)
        squares[currentIndex] = savedFrom
        squares[midIndex] = savedMid
        squares[landIndex] = savedLand
        return true
    }

    private fun flyingCaptureBranch(
        squares: IntArray, boardSize: Int, variant: RuleVariant, color: Int,
        x: Int, y: Int, dir: IntArray, pieceType: Int, startedAsMan: Boolean,
        path: MutableList<Int>, capturedPath: MutableList<Int>, capturedPieces: MutableList<Int>,
        results: MutableList<Move>
    ): Boolean {
        var step = 1
        // Slide until we hit a non-empty square (or the edge).
        var mx = x + dir[0] * step
        var my = y + dir[1] * step
        while (PositionUtils.isInside(mx, my, boardSize) && squares[PositionUtils.xyToIndex(
                mx,
                my,
                boardSize
            )] == Piece.EMPTY
        ) {
            step++
            mx = x + dir[0] * step
            my = y + dir[1] * step
        }
        if (!PositionUtils.isInside(mx, my, boardSize)) return false
        val midIndex = PositionUtils.xyToIndex(mx, my, boardSize)
        val midPiece = squares[midIndex]
        if (midPiece == Piece.EMPTY || Piece.colorOf(midPiece) == color) return false
        if (midIndex in capturedPath) return false

        var foundLanding = false
        var landStep = step + 1
        var lx = x + dir[0] * landStep
        var ly = y + dir[1] * landStep
        val currentIndex = path.last()
        while (PositionUtils.isInside(lx, ly, boardSize) && squares[PositionUtils.xyToIndex(
                lx,
                ly,
                boardSize
            )] == Piece.EMPTY
        ) {
            foundLanding = true
            val landIndex = PositionUtils.xyToIndex(lx, ly, boardSize)

            val savedFrom = squares[currentIndex]
            val savedMid = squares[midIndex]
            val savedLand = squares[landIndex]

            squares[currentIndex] = Piece.EMPTY
            squares[midIndex] = Piece.EMPTY
            squares[landIndex] = pieceType

            path.add(landIndex)
            capturedPath.add(midIndex)
            capturedPieces.add(savedMid)

            captureDFS(
                squares,
                boardSize,
                variant,
                color,
                landIndex,
                pieceType,
                startedAsMan,
                path,
                capturedPath,
                capturedPieces,
                results
            )

            path.removeAt(path.size - 1)
            capturedPath.removeAt(capturedPath.size - 1)
            capturedPieces.removeAt(capturedPieces.size - 1)
            squares[currentIndex] = savedFrom
            squares[midIndex] = savedMid
            squares[landIndex] = savedLand

            landStep++
            lx = x + dir[0] * landStep
            ly = y + dir[1] * landStep
        }
        return foundLanding
    }

    private fun buildCaptureMove(
        path: List<Int>, capturedPath: List<Int>, capturedPieces: List<Int>,
        boardSize: Int, finalPieceType: Int, startedAsMan: Boolean
    ): Move {
        val fromIndex = path.first()
        val toIndex = path.last()
        return Move(
            fromX = PositionUtils.indexToX(fromIndex, boardSize),
            fromY = PositionUtils.indexToY(fromIndex, boardSize),
            toX = PositionUtils.indexToX(toIndex, boardSize),
            toY = PositionUtils.indexToY(toIndex, boardSize),
            fromIndex = fromIndex,
            toIndex = toIndex,
            completePath = path.toList(),
            capturedPieces = capturedPieces.toList(),
            capturedPath = capturedPath.toList(),
            isCapture = true,
            isMultipleCapture = capturedPath.size > 1,
            isPromotion = startedAsMan && Piece.isKing(finalPieceType),
            isKingMove = Piece.isKing(finalPieceType)
        )
    }

}
