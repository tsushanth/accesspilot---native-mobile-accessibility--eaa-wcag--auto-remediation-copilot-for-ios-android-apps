import UIKit

final class LoginButton: UIButton {
    func applyStyle() {
        let titleColor = UIColor(hex: "#999999")
        setTitleColor(titleColor, for: .normal)

        backgroundColor = UIColor(hex: "#AAAAAA")
    }
}
