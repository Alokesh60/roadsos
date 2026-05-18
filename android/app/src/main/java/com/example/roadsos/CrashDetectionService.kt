package com.example.roadsos

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.media.MediaPlayer
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.VibrationEffect
import android.os.Vibrator
import androidx.core.app.NotificationCompat
import kotlin.math.sqrt

class CrashDetectionService :
    Service(),
    SensorEventListener {

    companion object {

        var emergencyActive = false

        var mediaPlayerInstance:
                MediaPlayer? = null

        fun resetEmergency() {

            emergencyActive = false
        }

        fun stopAlarm() {

            try {

                mediaPlayerInstance?.stop()

                mediaPlayerInstance?.release()

                mediaPlayerInstance = null

            } catch (_: Exception) {

            }
        }
    }

    private lateinit var sensorManager:
            SensorManager

    private var accelerometer: Sensor? = null

    private var lastAcceleration = 0f

    private var currentAcceleration = 0f

    private var shakeAcceleration = 0f

    override fun onCreate() {

        super.onCreate()

        try {

            createNotificationChannel()

            startForeground(
                1,
                createForegroundNotification()
            )

        } catch (e: Exception) {

            e.printStackTrace()
        }

        // DELAY SENSOR START

        Handler(
            Looper.getMainLooper()
        ).postDelayed({

            initializeSensors()

        }, 1000)
    }

    // SENSOR INITIALIZATION

    private fun initializeSensors() {

        sensorManager =
            getSystemService(
                Context.SENSOR_SERVICE
            ) as SensorManager

        accelerometer =
            sensorManager.getDefaultSensor(
                Sensor.TYPE_ACCELEROMETER
            )

        lastAcceleration =
            SensorManager.GRAVITY_EARTH

        currentAcceleration =
            SensorManager.GRAVITY_EARTH

        shakeAcceleration = 0f

        accelerometer?.also {

            sensorManager.registerListener(
                this,
                it,
                SensorManager.SENSOR_DELAY_NORMAL
            )
        }
    }

    override fun onStartCommand(
        intent: Intent?,
        flags: Int,
        startId: Int
    ): Int {

        return START_STICKY
    }

    override fun onDestroy() {

        super.onDestroy()

        try {

            sensorManager.unregisterListener(this)

        } catch (_: Exception) {

        }

        stopAlarm()
    }

    override fun onBind(
        intent: Intent?
    ): IBinder? {

        return null
    }

    override fun onSensorChanged(
        event: SensorEvent?
    ) {

        if (event != null) {

            val x = event.values[0]

            val y = event.values[1]

            val z = event.values[2]

            lastAcceleration =
                currentAcceleration

            currentAcceleration =
                sqrt(
                    (
                            x * x +
                                    y * y +
                                    z * z
                            ).toDouble()
                ).toFloat()

            val delta =
                currentAcceleration -
                        lastAcceleration

            shakeAcceleration =
                shakeAcceleration * 0.8f + delta

            // ACCIDENT DETECTION

            if (
                shakeAcceleration > 12 &&
                !emergencyActive
            ) {

                emergencyActive = true

                // START ALERTS

                triggerEmergencyAlert()

                // SHOW EMERGENCY NOTIFICATION

                // ALWAYS SHOW NOTIFICATION

                showEmergencyNotification()

// IF APP OPEN → SHOW POPUP DIRECTLY

                if (MainActivity.isAppOpen) {

                    val intent =
                        Intent(
                            this,
                            EmergencyAlertActivity::class.java
                        )

                    intent.addFlags(
                        Intent.FLAG_ACTIVITY_NEW_TASK
                    )

                    intent.addFlags(
                        Intent.FLAG_ACTIVITY_SINGLE_TOP
                    )

                    intent.addFlags(
                        Intent.FLAG_ACTIVITY_CLEAR_TOP
                    )

                    startActivity(intent)
                }
            }
        }
    }

    override fun onAccuracyChanged(
        sensor: Sensor?,
        accuracy: Int
    ) {

    }

    // VIBRATION + ALARM

    private fun triggerEmergencyAlert() {

        // VIBRATION

        val vibrator =
            getSystemService(
                Context.VIBRATOR_SERVICE
            ) as Vibrator

        if (
            Build.VERSION.SDK_INT >=
            Build.VERSION_CODES.O
        ) {

            vibrator.vibrate(
                VibrationEffect.createWaveform(
                    longArrayOf(
                        0,
                        700,
                        400,
                        700,
                        400,
                        700
                    ),
                    -1
                )
            )
        }

        // STOP OLD ALARM

        stopAlarm()

        // START NEW ALARM

        try {

            mediaPlayerInstance =
                MediaPlayer.create(
                    this,
                    android.provider.Settings.System.DEFAULT_NOTIFICATION_URI
                )

            mediaPlayerInstance?.isLooping = true

            mediaPlayerInstance?.start()

        } catch (e: Exception) {

            e.printStackTrace()
        }
    }

    // FOREGROUND SERVICE NOTIFICATION

    private fun createForegroundNotification():
            Notification {

        return NotificationCompat.Builder(
            this,
            "crash_detection_channel"
        )

            .setSmallIcon(
                android.R.drawable.stat_notify_sync
            )

            .setContentTitle(
                "RoadSOS Protection Active"
            )

            .setContentText(
                "Crash detection running"
            )

            .setPriority(
                NotificationCompat.PRIORITY_LOW
            )

            .setOngoing(true)

            .build()
    }

    // EMERGENCY NOTIFICATION

    private fun showEmergencyNotification() {

        val intent =
            Intent(
                this,
                EmergencyAlertActivity::class.java
            )

        intent.addFlags(
            Intent.FLAG_ACTIVITY_NEW_TASK
        )

        intent.addFlags(
            Intent.FLAG_ACTIVITY_SINGLE_TOP
        )

        intent.addFlags(
            Intent.FLAG_ACTIVITY_CLEAR_TOP
        )

        val pendingIntent =

            PendingIntent.getActivity(

                this,

                200,

                intent,

                PendingIntent.FLAG_UPDATE_CURRENT or
                        PendingIntent.FLAG_IMMUTABLE
            )

        val notification =

            NotificationCompat.Builder(
                this,
                "crash_detection_channel"
            )

                .setSmallIcon(
                    android.R.drawable.stat_notify_error
                )

                .setContentTitle(
                    "Possible Accident Detected"
                )

                .setContentText(
                    "Tap to open emergency alert"
                )

                .setPriority(
                    NotificationCompat.PRIORITY_MAX
                )

                .setCategory(
                    NotificationCompat.CATEGORY_ALARM
                )

                .setContentIntent(
                    pendingIntent
                )

                .setAutoCancel(true)

                .build()

        val manager =
            getSystemService(
                NotificationManager::class.java
            )

        manager.notify(
            99,
            notification
        )
    }

    // NOTIFICATION CHANNEL

    private fun createNotificationChannel() {

        if (
            Build.VERSION.SDK_INT >=
            Build.VERSION_CODES.O
        ) {

            val channel =
                NotificationChannel(
                    "crash_detection_channel",
                    "Crash Detection",
                    NotificationManager.IMPORTANCE_MAX
                )

            channel.description =
                "RoadSOS background crash detection"

            val manager =
                getSystemService(
                    NotificationManager::class.java
                )

            manager.createNotificationChannel(
                channel
            )
        }
    }
}