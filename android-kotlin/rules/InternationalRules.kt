package DraughtsPlay.engine.rules

/**
 * International Draughts: 10x10 board, flying kings, backward captures for men,
 * mandatory capture with a strict maximum-capture requirement (ties broken in favor
 * of sequences that capture more kings).
 */
class InternationalRules : RuleVariant(
    boardSize = 10,
    flyingKings = true,
    menCaptureBackward = true,
    mandatoryCapture = true,
    mustMaximizeCapture = true
) {
    override val variantType: VariantType = VariantType.INTERNATIONAL
}
