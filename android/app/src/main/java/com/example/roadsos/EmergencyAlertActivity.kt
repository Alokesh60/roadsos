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
                    modifier =
                        Modifier.fillMaxSize(),

                    color =
                        MaterialTheme
                            .colorScheme
                            .background
                ) {

                    EmergencyAlertScreen(

                        onSafe = {

                            CrashDetectionService.stopAlarm()

                            CrashDetectionService.resetEmergency()

                            clearEmergencyNotification()

                            finish()
                        },

                        onSOS = {

                            CrashDetectionService.stopAlarm()

                            CrashDetectionService.resetEmergency()

                            clearEmergencyNotification()

                            finish()
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
}

@Composable
fun EmergencyAlertScreen(

    onSafe: () -> Unit,

    onSOS: () -> Unit,

    clearNotification:
        () -> Unit
) {

    var countdown by remember {

        mutableIntStateOf(15)
    }

    var sosSent by remember {

        mutableStateOf(false)
    }

    // COUNTDOWN

    LaunchedEffect(
        countdown
    ) {

        if (
            countdown > 0 &&
            !sosSent
        ) {

            delay(1000)

            countdown--
        }

        // AUTO SOS

        if (
            countdown == 0
        ) {

            CrashDetectionService.stopAlarm()

            clearNotification()

            sosSent = true
        }
    }

    Box(
        modifier =
            Modifier
                .fillMaxSize()
                .background(
                    Color.Black.copy(
                        alpha = 0.75f
                    )
                ),

        contentAlignment =
            Alignment.Center
    ) {

        Card(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .padding(
                        horizontal = 24.dp
                    ),

            shape =
                RoundedCornerShape(
                    32.dp
                ),

            colors =
                CardDefaults.cardColors(
                    containerColor =
                        Color(
                            0xFF171C24
                        )
                )
        ) {

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(
                            30.dp
                        ),

                horizontalAlignment =
                    Alignment.CenterHorizontally
            ) {

                // ICON

                Box(
                    modifier =
                        Modifier
                            .size(
                                92.dp
                            )
                            .background(
                                brush =
                                    Brush.radialGradient(
                                        colors =
                                            listOf(
                                                Color(
                                                    0xFFFF8A80
                                                ),
                                                Color(
                                                    0xFFE53935
                                                )
                                            )
                                    ),
                                shape =
                                    CircleShape
                            ),

                    contentAlignment =
                        Alignment.Center
                ) {

                    Icon(
                        imageVector =
                            Icons.Default.Warning,

                        contentDescription =
                            null,

                        tint =
                            Color.White,

                        modifier =
                            Modifier.size(
                                46.dp
                            )
                    )
                }

                Spacer(
                    modifier =
                        Modifier.height(
                            24.dp
                        )
                )

                Text(
                    text =
                        "Possible Accident Detected",

                    color =
                        Color.White,

                    fontSize =
                        24.sp,

                    fontWeight =
                        FontWeight.Bold
                )

                Spacer(
                    modifier =
                        Modifier.height(
                            14.dp
                        )
                )

                Text(
                    text =
                        "Emergency SOS will trigger automatically.",

                    color =
                        Color(
                            0xFFBAC4CF
                        ),

                    fontSize =
                        16.sp
                )

                Spacer(
                    modifier =
                        Modifier.height(
                            30.dp
                        )
                )

                // TIMER

                Box(
                    modifier =
                        Modifier
                            .size(
                                130.dp
                            )
                            .background(
                                Color(
                                    0xFF242B36
                                ),
                                CircleShape
                            ),

                    contentAlignment =
                        Alignment.Center
                ) {

                    Column(
                        horizontalAlignment =
                            Alignment.CenterHorizontally
                    ) {

                        Text(
                            text =
                                "$countdown",

                            color =
                                Color.White,

                            fontSize =
                                42.sp,

                            fontWeight =
                                FontWeight.Bold
                        )

                        Text(
                            text =
                                "seconds",

                            color =
                                Color(
                                    0xFF9CA9B5
                                ),

                            fontSize =
                                14.sp
                        )
                    }
                }

                Spacer(
                    modifier =
                        Modifier.height(
                            30.dp
                        )
                )

                Column(
                    verticalArrangement =
                        Arrangement.spacedBy(
                            14.dp
                        )
                ) {

                    Button(

                        onClick =
                            onSafe,

                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .height(
                                    58.dp
                                ),

                        shape =
                            RoundedCornerShape(
                                18.dp
                            )
                    ) {

                        Text(
                            "I'm Safe",

                            fontSize =
                                18.sp
                        )
                    }

                    OutlinedButton(

                        onClick = {

                            CrashDetectionService.stopAlarm()

                            clearNotification()

                            sosSent = true
                        },

                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .height(
                                    58.dp
                                ),

                        shape =
                            RoundedCornerShape(
                                18.dp
                            )
                    ) {

                        Text(
                            "Send SOS Now",

                            fontSize =
                                18.sp
                        )
                    }
                }
            }
        }

        // SUCCESS

        if (
            sosSent
        ) {

            AlertDialog(

                onDismissRequest = {

                    onSOS()
                },

                confirmButton = {

                    Button(

                        onClick = {

                            onSOS()
                        }
                    ) {

                        Text(
                            "OK"
                        )
                    }
                },

                title = {

                    Text(
                        "SOS Sent Successfully"
                    )
                },

                text = {

                    Column {

                        Icon(
                            imageVector =
                                Icons.Default.CheckCircle,

                            contentDescription =
                                null,

                            tint =
                                Color(
                                    0xFF2ECC71
                                ),

                            modifier =
                                Modifier.size(
                                    48.dp
                                )
                        )

                        Spacer(
                            modifier =
                                Modifier.height(
                                    12.dp
                                )
                        )

                        Text(
                            "Emergency SOS shared successfully with your contacts."
                        )
                    }
                }
            )
        }
    }
}