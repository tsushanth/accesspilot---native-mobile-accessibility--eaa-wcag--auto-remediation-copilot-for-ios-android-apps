package com.accesspilot.sample

import android.view.View
import android.widget.Button
import androidx.fragment.app.Fragment

class SettingsFragment : Fragment() {

    private fun bindSignOutButton(signOutButton: Button) {
        signOutButton.importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
        signOutButton.setOnClickListener {
            performSignOut()
        }
    }

    private fun performSignOut() {
        // sign-out logic
    }
}
