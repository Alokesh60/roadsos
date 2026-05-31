package com.example.roadsos

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build

class RoadSosApp : Application() {
    override fun onCreate() {
        super.onCreate()
        createNotificationChannels()
    }

    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val emergencyChannel = NotificationChannel(
                "roadsos_emergency",
                "Emergency Alerts",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "All backend-generated emergency notifications"
            }

            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(emergencyChannel)
        }
    }
}
