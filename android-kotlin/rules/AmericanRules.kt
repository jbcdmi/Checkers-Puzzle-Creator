package DraughtsPlay.engine.rules

/**
 * American Checkers (English Draughts): 8x8 board, non-flying kings, men may capture
 * backward but never step backward on a quiet move, capture is mandatory but the player
 * is free to choose any legal capture (no maximum-capture requirement).
 */
class AmericanRules : RuleVariant(
    boardSize = 8,
    flyingKings = false,
    menCaptureBackward = true,
    mandatoryCapture = true,
    mustMaximizeCapture = false
) {
    override val variantType: VariantType = VariantType.AMERICAN
}