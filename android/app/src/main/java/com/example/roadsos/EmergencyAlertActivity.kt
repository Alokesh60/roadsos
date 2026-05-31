package com.example.roadsos

import android.app.NotificationManager
import android.os.Build
import android.os.Bundle
import android.view.WindowManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.roadsos.theme.RoadSoSTheme
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import androidx.compose.animation.core.*
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.alpha

class EmergencyAlertActivity :
    ComponentActivity() {

    override fun onCreate(
        savedInstanceState: Bundle?
    ) {

        super.onCreate(savedInstanceState)

        // LOCKSCREEN

        window.addFlags(

            WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON or
                    WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON or
                    WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED or
                    WindowManager.LayoutParams.FLAG_DISMISS_KEYGUARD
        )

        if (
            Build.VERSION.SDK_INT >=
            Build.VERSION_CODES.O_MR1
        ) {

            setShowWhenLocked(true)

            setTurnScreenOn(true)
        }

        setContent {

            RoadSoSTheme {

                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = Color.Transparent
                ) {
                    val isManual = intent.getBooleanExtra("isManual", false)
                    EmergencyAlertScreen(
                        isManual = isManual,
                        onSafe = {
                            CrashDetectionService.cancelCrashCountdown(this@EmergencyAlertActivity)
                            finishAndReturnToApp()
                        },

                        onSOS = {
                            if (isManual) {
                                // For manual SOS, we dispatch it immediately here
                                com.example.roadsos.utils.EmergencyDispatcher.dispatchEmergency(this, "mobile_app") { response ->
                                    CrashDetectionService.sosResponseData.value = response
                                    CrashDetectionService.sosDispatchState.value = "SUCCESS"
                                }
                            } else {
                                // For crash detection, let the background service handle it, or we can force it
                                CrashDetectionService.stopAlarm()
                                clearEmergencyNotification()
                                com.example.roadsos.utils.EmergencyDispatcher.dispatchEmergency(this, "crash_detection") {
                                    CrashDetectionService.sosDispatchState.value = "SUCCESS"
                                }
                            }
                        },

                        onFinish = {
                            finishAndReturnToApp()
                        },

                        clearNotification = {
                            clearEmergencyNotification()
                        }
                    )
                }
            }
        }
    }

    private fun clearEmergencyNotification() {

        val manager =
            getSystemService(
                NotificationManager::class.java
            )

        manager.cancel(99)
    }

    private fun finishAndReturnToApp() {
        CrashDetectionService.resetEmergency()
        val intent = android.content.Intent(this, MainActivity::class.java)
        intent.addFlags(android.content.Intent.FLAG_ACTIVITY_CLEAR_TOP or android.content.Intent.FLAG_ACTIVITY_SINGLE_TOP or android.content.Intent.FLAG_ACTIVITY_NEW_TASK)
        startActivity(intent)
        finish()
    }

    // dispatchEmergency has been moved to EmergencyDispatcher
}

@Composable
fun EmergencyAlertScreen(
    isManual: Boolean,
    onSafe: () -> Unit,
    onSOS: () -> Unit,
    onFinish: () -> Unit,
    clearNotification: () -> Unit
) {

    val backgroundCountdown by CrashDetectionService.crashCountdown.collectAsState()
    val backgroundSosState by CrashDetectionService.sosDispatchState.collectAsState()
    val apiResponse by CrashDetectionService.sosResponseData.collectAsState()

    var countdown by remember { mutableIntStateOf(if (isManual) 0 else 15) }
    var sosSent by remember { mutableStateOf(false) }

    // Sync background countdown to UI countdown
    LaunchedEffect(backgroundCountdown) {
        if (!isManual) {
            backgroundCountdown?.let { 
                countdown = it 
            }
        }
    }

    // Check background dispatch state
    LaunchedEffect(backgroundSosState) {
        if (backgroundSosState == "SUCCESS" || backgroundSosState == "FAILED") {
            sosSent = true
        }
    }

    // Manual countdown (only used for manual trigger, background trigger is handled by CrashDetectionService)
    LaunchedEffect(countdown) {
        if (isManual && countdown > 0 && !sosSent) {
            delay(1000)
            countdown--
        }

        if (countdown == 0 && !sosSent) {
            if (isManual) {
                clearNotification()
                onSOS()
                sosSent = true
            }
        }
    }

    val scale by animateFloatAsState(
        targetValue = if (sosSent) 1.5f else 0.5f,
        animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessLow)
    )
    val alpha by animateFloatAsState(
        targetValue = if (sosSent) 1f else 0f,
        animationSpec = tween(500)
    )

    LaunchedEffect(sosSent) {
        if (sosSent) {
            delay(5000) // Show for 5 seconds then auto disappear
            onFinish()
        }
    }

    if (sosSent) {
        AlertDialog(
            onDismissRequest = { onFinish() },
            confirmButton = {
                Button(onClick = { onFinish() }) {
                    Text("OK")
                }
            },
            title = { Text("SOS Sent Successfully") },
            text = {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Icon(
                        imageVector = Icons.Default.CheckCircle,
                        contentDescription = "Success",
                        tint = Color(0xFF2ECC71),
                        modifier = Modifier
                            .size(72.dp)
                            .scale(scale)
                            .alpha(alpha)
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    val context = androidx.compose.ui.platform.LocalContext.current
                    Text(
                        text = "Emergency SOS process started. Alerts are being sent.",
                        textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                        color = Color.White
                    )
                }
            }
        )
    } else if (!isManual) {
        // CRASH DETECTION UI
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.75f)),
            contentAlignment = Alignment.Center
        ) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp),
                shape = RoundedCornerShape(32.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF171C24))
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(30.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    // ICON
                    Box(
                        modifier = Modifier
                            .size(92.dp)
                            .background(
                                brush = Brush.radialGradient(
                                    colors = listOf(Color(0xFFFF8A80), Color(0xFFE53935))
                                ),
                                shape = CircleShape
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Warning,
                            contentDescription = null,
                            tint = Color.White,
                            modifier = Modifier.size(46.dp)
                        )
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    Text(
                        text = "Possible Accident Detected",
                        color = Color.White,
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold
                    )

                    Spacer(modifier = Modifier.height(14.dp))

                    Text(
                        text = "Emergency SOS will trigger automatically.",
                        color = Color(0xFFBAC4CF),
                        fontSize = 16.sp
                    )

                    Spacer(modifier = Modifier.height(30.dp))

                    // TIMER
                    Box(
                        modifier = Modifier
                            .size(130.dp)
                            .background(Color(0xFF242B36), CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(
                                text = "$countdown",
                                color = Color.White,
                                fontSize = 42.sp,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = "seconds",
                                color = Color(0xFF9CA9B5),
                                fontSize = 14.sp
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(30.dp))

                    Column(
                        verticalArrangement = Arrangement.spacedBy(14.dp)
                    ) {
                        Button(
                            onClick = onSafe,
                            modifier = Modifier.fillMaxWidth().height(58.dp),
                            shape = RoundedCornerShape(18.dp)
                        ) {
                            Text("I'm Safe", fontSize = 18.sp)
                        }

                        OutlinedButton(
                            onClick = {
                                CrashDetectionService.stopAlarm()
                                clearNotification()
                                onSOS()
                                sosSent = true
                            },
                            modifier = Modifier.fillMaxWidth().height(58.dp),
                            shape = RoundedCornerShape(18.dp)
                        ) {
                            Text("Send SOS Now", fontSize = 18.sp)
                        }
                    }
                }
            }
        }
    }
}