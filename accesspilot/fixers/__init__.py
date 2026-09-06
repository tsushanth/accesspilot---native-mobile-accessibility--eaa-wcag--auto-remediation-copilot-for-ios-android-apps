from . import missing_labels_fixer, touch_targets_fixer

FIXERS = {
    missing_labels_fixer.RULE_ID: missing_labels_fixer.fix,
    touch_targets_fixer.RULE_ID: touch_targets_fixer.fix,
}
