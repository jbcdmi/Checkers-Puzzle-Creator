package DraughtsPlay.engine.rules

/**
 * Russian Checkers: 8x8 board, flying kings, men may capture backward, capture is
 * mandatory but there is no maximum-capture requirement (the player picks any legal
 * capture sequence, short or long).
 */
class RussianRules : RuleVariant(
    boardSize = 8,
    flyingKings = true,
    menCaptureBackward = true,
    mandatoryCapture = true,
    mustMaximizeCapture = false
) {
    override val variantType: VariantType = VariantType.RUSSIAN
}
