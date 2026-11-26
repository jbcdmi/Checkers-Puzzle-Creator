package DraughtsPlay.engine.puzzle_ai

import DraughtsPlay.engine.core.Piece
import DraughtsPlay.engine.core.PlayerColor
import DraughtsPlay.engine.core.PositionUtils
import DraughtsPlay.engine.rules.RuleVariant
import DraughtsPlay.engine.rules.VariantType
import org.json.JSONObject

/** Puzzle difficulty levels matching the Level Creator JSON. */
enum class PuzzleDifficulty {
    BEGINNER,
    INTERMEDIATE,
    ADVANCED,
    EXPERT;

    companion object {
        fun fromString(value: String?): PuzzleDifficulty = when (value?.trim()?.uppercase()) {
            "INTERMEDIATE" -> INTERMEDIATE
            "ADVANCED" -> ADVANCED
            "EXPERT" -> EXPERT
            else -> BEGINNER
        }
    }
}

/** Supported puzzle challenge objectives matching the Level Creator JSON. */
enum class PuzzleChallengeType {
    CAPTURE_COUNT,
    WIN_IN_X_MOVES,
    MAKE_KINGS,
    CAPTURE_ALL_OPPONENTS,
    WIN_NO_LOSS,
    CAPTURE_KING,
    SURVIVE_MOVES;

    companion object {
        fun fromString(value: String?): PuzzleChallengeType = when (value?.trim()?.uppercase()) {
            "WIN_IN_X_MOVES" -> WIN_IN_X_MOVES
            "MAKE_KINGS" -> MAKE_KINGS
            "CAPTURE_ALL_OPPONENTS" -> CAPTURE_ALL_OPPONENTS
            "WIN_NO_LOSS" -> WIN_NO_LOSS
            "CAPTURE_KING" -> CAPTURE_KING
            "SURVIVE_MOVES" -> SURVIVE_MOVES
            else -> CAPTURE_COUNT
        }
    }
}

/** Challenge configuration for a puzzle level. */
data class PuzzleChallenge(
    val type: PuzzleChallengeType,
    val target: Int = 1,
    val moveLimit: Int = 3
)

/**
 * Single piece placement matching the compact Level Creator JSON:
 * `{ "pIndex": 0|1, "isKing": Boolean, "pos": [x, y] }`
 * where `pIndex = 0` is Player (WHITE) and `pIndex = 1` is Robot (BLACK).
 */
data class PuzzlePiecePlacement(
    val pIndex: Int,
    val isKing: Boolean,
    val x: Int,
    val y: Int
)

/**
 * Optional scripted Robot move in puzzle JSON:
 * `{ "from": [x, y], "to": [x, y] }`
 * Used when the puzzle requires a specific opening/setup move from the Robot
 * (e.g. `0-7 -> 1-8`) that a minimax defender would otherwise avoid.
 */
data class PuzzleScriptedMove(
    val fromX: Int,
    val fromY: Int,
    val toX: Int,
    val toY: Int
)

/**
 * Full puzzle level definition matching the Level Creator JSON:
 * `levelId`, `difficulty`, `boardSize`, `firstTurn` (`0` = Player, `1` = Robot),
 * `board`, `challenge`, and optional `robotMoves`.
 */
data class PuzzleLevel(
    val levelId: String,
    val difficulty: PuzzleDifficulty = PuzzleDifficulty.BEGINNER,
    val boardSize: Int = 8,
    val firstTurn: Int = PlayerColor.WHITE,
    val board: List<PuzzlePiecePlacement>,
    val challenge: PuzzleChallenge,
    val robotMoves: List<PuzzleScriptedMove> = emptyList()
) {
    companion object {
        /** Parses a Level Creator JSON object into a [PuzzleLevel]. */
        fun fromJson(json: JSONObject): PuzzleLevel {
            val levelId = json.optString("levelId", "1")
            val difficulty = PuzzleDifficulty.fromString(json.optString("difficulty", "BEGINNER"))
            val boardSize = json.optInt("boardSize", 8).coerceIn(6, 14)
            val firstTurn = if (json.optInt("firstTurn", 0) == 1) {
                PlayerColor.BLACK
            } else {
                PlayerColor.WHITE
            }

            val pieces = ArrayList<PuzzlePiecePlacement>()
            val boardArr = json.optJSONArray("board")
            if (boardArr != null) {
                for (i in 0 until boardArr.length()) {
                    val item = boardArr.optJSONObject(i) ?: continue
                    val posArr = item.optJSONArray("pos") ?: continue
                    if (posArr.length() < 2) continue
                    pieces.add(
                        PuzzlePiecePlacement(
                            pIndex = item.optInt("pIndex", PlayerColor.WHITE),
                            isKing = item.optBoolean("isKing", false),
                            x = posArr.optInt(0, 0),
                            y = posArr.optInt(1, 0)
                        )
                    )
                }
            }

            val chObj = json.optJSONObject("challenge")
            val challenge = PuzzleChallenge(
                type = PuzzleChallengeType.fromString(chObj?.optString("type")),
                target = chObj?.optInt("target", 1) ?: 1,
                moveLimit = chObj?.optInt("moveLimit", 3) ?: 3
            )

            val scriptedMoves = ArrayList<PuzzleScriptedMove>()
            val rmArr = json.optJSONArray("robotMoves")
            if (rmArr != null) {
                for (i in 0 until rmArr.length()) {
                    val item = rmArr.optJSONObject(i) ?: continue
                    val fromArr = item.optJSONArray("from") ?: continue
                    val toArr = item.optJSONArray("to") ?: continue
                    if (fromArr.length() < 2 || toArr.length() < 2) continue
                    scriptedMoves.add(
                        PuzzleScriptedMove(
                            fromX = fromArr.optInt(0, 0),
                            fromY = fromArr.optInt(1, 0),
                            toX = toArr.optInt(0, 0),
                            toY = toArr.optInt(1, 0)
                        )
                    )
                }
            }

            return PuzzleLevel(
                levelId = levelId,
                difficulty = difficulty,
                boardSize = boardSize,
                firstTurn = firstTurn,
                board = pieces,
                challenge = challenge,
                robotMoves = scriptedMoves
            )
        }

        /** Convenience parser for a raw JSON string. */
        fun fromJsonString(raw: String): PuzzleLevel = fromJson(JSONObject(raw))
    }
}

/** Live puzzle progress tracked across moves during play and search. */
data class PuzzleProgress(
    val playerMovesUsed: Int = 0,
    val robotMovesUsed: Int = 0,
    val capturesByPlayer: Int = 0,
    val kingsMadeByPlayer: Int = 0,
    val kingsCapturedByPlayer: Int = 0,
    val playerPiecesLost: Int = 0,
    val initialPlayerKings: Int = 0
)

/** Outcome state of a puzzle. */
enum class PuzzleStatus {
    IN_PROGRESS,
    PLAYER_WON,
    PLAYER_LOST
}

/**
 * Configurable [RuleVariant] that accepts any [boardSize] (6, 8, 10, 12, etc.) from
 * puzzle JSON while preserving the chosen ruleset's movement/capture flags.
 */
class PuzzleRuleVariant(
    boardSize: Int,
    flyingKings: Boolean = false,
    menCaptureBackward: Boolean = false,
    mandatoryCapture: Boolean = true,
    mustMaximizeCapture: Boolean = false,
    preferKingCaptures: Boolean = mustMaximizeCapture,
    override val variantType: VariantType = VariantType.AMERICAN
) : RuleVariant(
    boardSize = boardSize,
    flyingKings = flyingKings,
    menCaptureBackward = menCaptureBackward,
    mandatoryCapture = mandatoryCapture,
    mustMaximizeCapture = mustMaximizeCapture,
    preferKingCaptures = preferKingCaptures
) {
    /** Puzzles use custom piece placement rather than a full starting setup. */
    override fun initialSetup(): IntArray {
        return IntArray(boardSize * boardSize) { Piece.EMPTY }
    }

    companion object {
        /** Adapts any existing [RuleVariant] (American, International, etc.) to [boardSize]. */
        fun fromVariant(base: RuleVariant, boardSize: Int): PuzzleRuleVariant = PuzzleRuleVariant(
            boardSize = boardSize,
            flyingKings = base.flyingKings,
            menCaptureBackward = base.menCaptureBackward,
            mandatoryCapture = base.mandatoryCapture,
            mustMaximizeCapture = base.mustMaximizeCapture,
            preferKingCaptures = base.preferKingCaptures,
            variantType = base.variantType
        )

        fun american(boardSize: Int): PuzzleRuleVariant = PuzzleRuleVariant(
            boardSize = boardSize,
            flyingKings = false,
            menCaptureBackward = false,
            mandatoryCapture = true,
            mustMaximizeCapture = false,
            variantType = VariantType.AMERICAN
        )

        fun international(boardSize: Int): PuzzleRuleVariant = PuzzleRuleVariant(
            boardSize = boardSize,
            flyingKings = true,
            menCaptureBackward = true,
            mandatoryCapture = true,
            mustMaximizeCapture = true,
            preferKingCaptures = true,
            variantType = VariantType.INTERNATIONAL
        )
    }
}

/** Converts [PuzzlePiecePlacement] coordinates to a board piece constant. */
internal fun PuzzlePiecePlacement.toPieceValue(): Int {
    val color = if (pIndex == PlayerColor.BLACK) PlayerColor.BLACK else PlayerColor.WHITE
    return if (isKing) Piece.kingOf(color) else Piece.manOf(color)
}

internal fun isValidPlacement(p: PuzzlePiecePlacement, boardSize: Int): Boolean {
    return PositionUtils.isInside(p.x, p.y, boardSize) && PositionUtils.isDarkSquare(p.x, p.y)
}
