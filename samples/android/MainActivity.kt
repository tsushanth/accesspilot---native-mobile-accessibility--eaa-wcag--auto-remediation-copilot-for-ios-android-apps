package com.accesspilot.sample

import android.app.Activity
import android.os.Bundle
import android.widget.ImageView

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val avatar = ImageView(this)
        avatar.setImageResource(R.drawable.ic_avatar)
        addContentView(avatar, null)
    }
}
