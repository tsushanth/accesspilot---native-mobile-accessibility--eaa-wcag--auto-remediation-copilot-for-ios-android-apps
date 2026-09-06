from accesspilot.rules import contrast, focus_order, missing_labels, touch_targets


def test_missing_label_swift_flags_image_without_label():
    lines = [
        'Image(systemName: "person.crop.circle")',
        '.resizable()',
        '.frame(width: 60, height: 60)',
    ]
    findings = missing_labels.scan("Foo.swift", lines)
    assert len(findings) == 1
    assert findings[0].rule_id == "missing-label"
    assert findings[0].line == 1


def test_missing_label_swift_ignores_labeled_image():
    lines = [
        'Image(systemName: "person.crop.circle")',
        '.accessibilityLabel("Profile photo")',
    ]
    assert missing_labels.scan("Foo.swift", lines) == []


def test_missing_label_kotlin_flags_imageview_without_description():
    lines = ["val avatar = ImageView(this)", "avatar.setImageResource(R.drawable.ic_avatar)"]
    findings = missing_labels.scan("Foo.kt", lines)
    assert len(findings) == 1


def test_missing_label_kotlin_ignores_described_imageview():
    lines = ["val avatar = ImageView(this)", 'avatar.contentDescription = "Avatar"']
    assert missing_labels.scan("Foo.kt", lines) == []


def test_touch_target_swift_flags_undersized_frame():
    lines = [".frame(width: 30, height: 30)"]
    findings = touch_targets.scan("Foo.swift", lines)
    assert len(findings) == 1


def test_touch_target_swift_ignores_compliant_frame():
    lines = [".frame(width: 44, height: 44)"]
    assert touch_targets.scan("Foo.swift", lines) == []


def test_touch_target_kotlin_flags_undersized_layout_params():
    lines = ["view.layoutParams = ViewGroup.LayoutParams(30, 30)"]
    findings = touch_targets.scan("Foo.kt", lines)
    assert len(findings) == 1


def test_touch_target_kotlin_ignores_compliant_layout_params():
    lines = ["view.layoutParams = ViewGroup.LayoutParams(48, 48)"]
    assert touch_targets.scan("Foo.kt", lines) == []


def test_contrast_flags_low_ratio_pair():
    lines = [
        'let titleColor = UIColor(hex: "#999999")',
        'backgroundColor = UIColor(hex: "#AAAAAA")',
    ]
    findings = contrast.scan("Foo.swift", lines)
    assert len(findings) == 1


def test_contrast_ignores_high_ratio_pair():
    lines = [
        'let titleColor = UIColor(hex: "#000000")',
        'backgroundColor = UIColor(hex: "#FFFFFF")',
    ]
    assert contrast.scan("Foo.swift", lines) == []


def test_focus_order_flags_hidden_clickable_view():
    lines = [
        "signOutButton.importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO",
        "signOutButton.setOnClickListener {",
        "    performSignOut()",
        "}",
    ]
    findings = focus_order.scan("Foo.kt", lines)
    assert len(findings) == 1


def test_focus_order_ignores_visible_clickable_view():
    lines = ["signOutButton.setOnClickListener {", "    performSignOut()", "}"]
    assert focus_order.scan("Foo.kt", lines) == []
