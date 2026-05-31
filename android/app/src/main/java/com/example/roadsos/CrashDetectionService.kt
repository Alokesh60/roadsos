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
import com.example.roadsos.utils.EmergencyDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.launch
import kotlin.math.abs
import kotlin.math.sqrt

class CrashDetectionService :
    Service(),
    SensorEventListener {

    companion object {

        var emergencyActive = false
        val crashCountdown = MutableStateFlow<Int?>(null)
        val sosDispatchState = MutableStateFlow<String>("IDLE")
        val sosResponseData = MutableStateFlow<com.example.roadsos.models.SosResponse?>(null)

        var emergencyStartTime =
            0L

        var mediaPlayerInstance:
                MediaPlayer? = null

        var countdownJob: Job? = null

        fun resetEmergency() {
            emergencyActive = false
            crashCountdown.value = null
            sosDispatchState.value = "IDLE"
            sosResponseData.value = null
        }

        fun stopAlarm() {

            try {

                mediaPlayerInstance?.stop()

                mediaPlayerInstance?.release()

                mediaPlayerInstance = null

            } catch (_: Exception) {

            }
        }
        fun startCrashCountdown(context: android.content.Context) {
            countdownJob?.cancel()
            crashCountdown.value = 15
            sosDispatchState.value = "IDLE"
            
            countdownJob = CoroutineScope(Dispatchers.Default).launch {
                while (crashCountdown.value != null && crashCountdown.value!! > 0) {
                    delay(1000)
                    if (crashCountdown.value != null) {
                        crashCountdown.value = crashCountdown.value!! - 1
                    }
                }
                
                if (crashCountdown.value == 0) {
                    // Timer finished! Dispatch SOS from background.
                    stopAlarm()
                    val manager = context.getSystemService(android.app.NotificationManager::class.java)
                    manager.cancel(200) // Clear the local crash notification
                    
                    com.example.roadsos.utils.EmergencyDispatcher.dispatchEmergency(context, "crash_detection") { response ->
                        if (response != null) {
                            sosResponseData.value = response
                            sosDispatchState.value = "SUCCESS"
                        } else {
                            sosDispatchState.value = "SUCCESS" // Still SUCCESS because SMS was dispatched
                        }
                    }
                }
            }
        }

        fun cancelCrashCountdown(context: android.content.Context) {
            countdownJob?.cancel()
            resetEmergency()
            stopAlarm()
            val manager = context.getSystemService(android.app.NotificationManager::class.java)
            manager.cancel(200)
        }
    }

    private lateinit var sensorManager:
            SensorManager

    private var accelerometer:
            Sensor? = null

    private var gyroscope:
            Sensor? = null

    private var lastAcceleration =
        0f

    private var currentAcceleration =
        0f

    private var shakeAcceleration =
        0f

    private var highImpact =
        false

    private var highRotation =
        false

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

        Handler(
            Looper.getMainLooper()
        ).postDelayed({

            initializeSensors()

        }, 800)
    }

    // SENSOR INIT

    private fun initializeSensors() {

        sensorManager =
            getSystemService(
                Context.SENSOR_SERVICE
            ) as SensorManager

        accelerometer =
            sensorManager.getDefaultSensor(
                Sensor.TYPE_ACCELEROMETER
            )

        gyroscope =
            sensorManager.getDefaultSensor(
                Sensor.TYPE_GYROSCOPE
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
                SensorManager.SENSOR_DELAY_GAME
            )
        }

        gyroscope?.also {

            sensorManager.registerListener(
                this,
                it,
                SensorManager.SENSOR_DELAY_GAME            )
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

        if (
            event == null ||
            emergencyActive
        ) return

        when (
            event.sensor.type
        ) {

            // ACCELEROMETER

            Sensor.TYPE_ACCELEROMETER -> {

                val x =
                    event.values[0]

                val y =
                    event.values[1]

                val z =
                    event.values[2]

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
                    shakeAcceleration *
                            0.8f +
                            delta

                if (
                    shakeAcceleration > 28
                ) {

                    highImpact =
                        true

                    Handler(
                        Looper.getMainLooper()
                    ).postDelayed({

                        highImpact =
                            false

                    }, 1000)
                }
            }

            // GYROSCOPE

            Sensor.TYPE_GYROSCOPE -> {

                val rotX =
                    event.values[0]

                val rotY =
                    event.values[1]

                val rotZ =
                    event.values[2]

                val rotation =

                    abs(rotX) +
                            abs(rotY) +
                            abs(rotZ)

                if (
                    rotation > 22f
                ) {

                    highRotation =
                        true

                    Handler(
                        Looper.getMainLooper()
                    ).postDelayed({

                        highRotation =
                            false

                    }, 1000)
                }
            }
        }

        // SENSOR FUSION

        if (
            highImpact &&
            highRotation &&
            !emergencyActive
        ) {

            emergencyActive =
                true

            emergencyStartTime =
                System.currentTimeMillis()

            triggerEmergencyAlert()

            if (!MainActivity.isAppOpen) {
                showEmergencyNotification()
            }

            startCrashCountdown(this)

            if (
                MainActivity.isAppOpen
            ) {

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

    override fun onAccuracyChanged(
        sensor: Sensor?,
        accuracy: Int
    ) {

    }

    // ALERT

    private fun triggerEmergencyAlert() {

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

        stopAlarm()

        try {

            mediaPlayerInstance =
                MediaPlayer.create(
                    this,
                    android.provider.Settings.System.DEFAULT_NOTIFICATION_URI
                )

            mediaPlayerInstance
                ?.isLooping = true

            mediaPlayerInstance
                ?.start()

        } catch (e: Exception) {

            e.printStackTrace()
        }
    }

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

    private fun showEmergencyNotification() {

        val intent =
            Intent(
                this,
                EmergencyAlertActivity::class.java
            )

        intent.addFlags(
            Intent.FLAG_ACTIVITY_NEW_TASK
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

    private fun createNotificationChannel() {

        if (
            Build.VERSION.SDK_INT >=
            Build.VERSION_CODES.O
        ) {

            val channel =
                NotificationChannel(
                    "crash_detection_channel",
                    "Crash Detection",
                    NotificationManager.IMPORTANCE_HIGH                )

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