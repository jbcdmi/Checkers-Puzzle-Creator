package DraughtsPlay.engine.ai

import DraughtsPlay.engine.core.Board
import DraughtsPlay.engine.core.Piece
import DraughtsPlay.engine.core.PlayerColor
import kotlin.random.Random

/**
 * Zobrist hashing for a board of [boardSize] x [boardSize] squares. Produces a 64-bit
 * incremental hash suitable as a [TranspositionTable] key. One table is built per board
 * size (piece-type table is fixed at 5 entries: empty is never hashed) with a fixed seed
 * so hashes are reproducible across runs/devices for a given engine version.
 */
class ZobristHash(private val boardSize: Int, seed: Long = 0x5EED1234ABCDL) {

    private val random = Random(seed)
    private val squareCount = boardSize * boardSize

    // [pieceType][squareIndex] -> random 64-bit key. Piece types: 1..4 (see Piece constants).
    private val pieceKeys: Array<LongArray> =
        Array(5) { LongArray(squareCount) { random.nextLong() } }
    private val blackToMoveKey: Long = random.nextLong()

    /** Computes the full hash for [board] from scratch, with [sideToMove] folded in. */
    fun hash(board: Board, sideToMove: Int): Long {
        var h = 0L
        for (index in board.squares.indices) {
            val piece = board.squares[index]
            if (piece != Piece.EMPTY) h = h xor pieceKeys[piece][index]
        }
        if (sideToMove == PlayerColor.BLACK) h = h xor blackToMoveKey
        return h
    }

    /** XOR delta to toggle [piece] being present at [index] — apply twice to add then remove, or once each way. */
    fun pieceKey(piece: Int, index: Int): Long = pieceKeys[piece][index]

    /** XOR delta representing whose turn it is; XOR this in whenever the side to move flips. */
    fun sideToMoveKey(): Long = blackToMoveKey

    /**
     * Incrementally updates [previousHash] to reflect [move] having just been applied by
     * [mover] (the piece value that was on the from-square before the move, e.g. [Piece.WHITE_MAN]).
     * Avoids a full re-hash after every ply during search.
     */
    fun updateHash(
        previousHash: Long,
        fromIndex: Int,
        toIndex: Int,
        movingPieceBefore: Int,
        movingPieceAfter: Int,
        capturedPath: List<Int>,
        capturedPieces: List<Int>
    ): Long {
        var h = previousHash
        h = h xor pieceKeys[movingPieceBefore][fromIndex]
        h = h xor pieceKeys[movingPieceAfter][toIndex]
        for (i in capturedPath.indices) {
            h = h xor pieceKeys[capturedPieces[i]][capturedPath[i]]
        }
        h = h xor blackToMoveKey
        return h
    }
}