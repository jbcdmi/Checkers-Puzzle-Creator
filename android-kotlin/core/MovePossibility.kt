package DraughtsPlay.engine.core

import DraughtsPlay.ActionMove

/**
 * Represents a single legal move, which may be a simple step or a full multi-jump
 * capture sequence. For multi-jump captures, [completePath] holds every square index
 * visited (from -> intermediate landing squares -> final square) and [capturedPath] /
 * [capturedPieces] hold the indices and piece values of every piece removed along the way.
 */
data class MovePossibility(
    val index: Int,
    val x: Int,
    val y: Int,
    val moves: ArrayList<ArrayList<ActionMove>>
)
