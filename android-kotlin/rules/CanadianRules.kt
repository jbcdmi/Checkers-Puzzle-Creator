package DraughtsPlay.engine.rules

/**
 * Canadian Checkers: 12x12 board using International-style movement — flying kings,
 * backward captures for men, mandatory capture with a maximum-capture requirement.
 */
class CanadianRules : RuleVariant(
    boardSize = 12,
    flyingKings = true,
    menCaptureBackward = true,
    mandatoryCapture = true,
    mustMaximizeCapture = true
) {
    override val variantType: VariantType = VariantType.CANADIAN
}
