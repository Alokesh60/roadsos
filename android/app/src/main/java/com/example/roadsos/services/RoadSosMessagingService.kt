package com.example.roadsos.services

import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.util.Log
import androidx.core.app.NotificationCompat
import com.example.roadsos.EmergencyResponderActivity
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import kotlin.random.Random

class RoadSosMessagingService : FirebaseMessagingService() {

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        Log.d("FCM", "Refreshed token: $token")
        
        // Save to Firestore if user is logged in
        val user = FirebaseAuth.getInstance().currentUser
        if (user != null) {
            FirebaseFirestore.getInstance().collection("users").document(user.uid)
                .update("fcm_token", token)
                .addOnFailureListener { e ->
                    Log.e("FCM", "Error updating token", e)
                }
        }
    }

    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)

        val data = message.data
        if (data.isNotEmpty()) {
            val type = data["type"]
            val title = message.notification?.title ?: "Emergency Alert"
            val body = message.notification?.body ?: "Someone requires immediate assistance."
            val latitude = data["latitude"]?.toDoubleOrNull()
            val longitude = data["longitude"]?.toDoubleOrNull()
            val mapsLink = data["maps_link"]
            val senderName = data["sender_name"] ?: "A RoadSOS user"
            val emergencyType = data["emergency_type"] ?: "Emergency"

            showNotification(title, body, type, latitude, longitude, mapsLink, senderName, emergencyType)
        }
    }

    private fun showNotification(
        title: String,
        body: String,
        type: String?,
        latitude: Double?,
        longitude: Double?,
        mapsLink: String?,
        senderName: String,
        emergencyType: String
    ) {
        val intent = Intent(this, EmergencyResponderActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("type", type)
            putExtra("latitude", latitude)
            putExtra("longitude", longitude)
            putExtra("mapsLink", mapsLink)
            putExtra("title", title)
            putExtra("body", body)
            putExtra("senderName", senderName)
            putExtra("emergencyType", emergencyType)
        }

        val pendingIntent = PendingIntent.getActivity(
            this,
            Random.nextInt(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(this, "roadsos_emergency")
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setFullScreenIntent(pendingIntent, true)
            .setAutoCancel(true)
            .build()

        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.notify(Random.nextInt(), notification)
    }
}
