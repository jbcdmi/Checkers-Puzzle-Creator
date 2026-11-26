package DraughtsPlay.engine.rules

/**
 * Brazilian Checkers: 8x8 board played with International-style rules — flying kings,
 * backward captures for men, mandatory capture with a maximum-capture requirement.
 */
class BrazilianRules : RuleVariant(
    boardSize = 8,
    flyingKings = true,
    menCaptureBackward = true,
    mandatoryCapture = true,
    mustMaximizeCapture = true
) {
    override val variantType: VariantType = VariantType.BRAZILIAN
}
