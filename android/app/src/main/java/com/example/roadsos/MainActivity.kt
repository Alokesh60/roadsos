package com.example.roadsos

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.example.roadsos.screens.auth.AuthScreen
import com.example.roadsos.screens.navigation.MainContainerScreen
import com.example.roadsos.screens.permissions.PermissionScreen
import com.example.roadsos.screens.splash.SplashScreen
import com.example.roadsos.theme.RoadSoSTheme
import kotlinx.coroutines.delay
class MainActivity : ComponentActivity() {
    companion object {

        var isAppOpen = false
    }

    override fun onCreate(savedInstanceState: Bundle?) {

        super.onCreate(savedInstanceState)

        // NOTIFICATION PERMISSION
        // REQUIRED FOR ANDROID 13+

        if (
            Build.VERSION.SDK_INT >=
            Build.VERSION_CODES.TIRAMISU
        ) {

            if (
                ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {

                ActivityCompat.requestPermissions(
                    this,
                    arrayOf(
                        Manifest.permission.POST_NOTIFICATIONS
                    ),
                    101
                )
            }
        }

        // START CRASH DETECTION SERVICE

        val serviceIntent =
            Intent(
                this,
                CrashDetectionService::class.java
            )

        if (
            Build.VERSION.SDK_INT >=
            Build.VERSION_CODES.O
        ) {

            startForegroundService(
                serviceIntent
            )

        } else {

            startService(
                serviceIntent
            )
        }

        try {
            val ai = packageManager.getApplicationInfo(packageName, PackageManager.GET_META_DATA)
            val bundle = ai.metaData
            val mapsApiKey = bundle?.getString("com.google.android.geo.API_KEY")
            if (mapsApiKey != null && !com.google.android.libraries.places.api.Places.isInitialized()) {
                com.google.android.libraries.places.api.Places.initialize(applicationContext, mapsApiKey)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }

        setContent {

            RoadSoSTheme {

                Surface(
                    modifier = Modifier.fillMaxSize(),

                    color =
                        MaterialTheme.colorScheme.background
                ) {

                    RoadSoSApp()
                }
            }
        }
    }
    override fun onStart() {

        super.onStart()

        isAppOpen = true
    }

    override fun onStop() {

        super.onStop()

        isAppOpen = false
    }
}

@Composable
fun RoadSoSApp() {

    var showSplash by remember {

        mutableStateOf(true)
    }

    var isLoggedIn by remember {

        mutableStateOf(com.google.firebase.auth.FirebaseAuth.getInstance().currentUser != null)
    }

    var showPermissions by remember {

        mutableStateOf(false)
    }

    // SPLASH DELAY

    LaunchedEffect(Unit) {

        delay(2500)

        showSplash = false
    }

    when {

        // SPLASH SCREEN

        showSplash -> {

            SplashScreen()
        }

        // PERMISSION SCREEN

        showPermissions -> {

            PermissionScreen(

                onBack = {

                    showPermissions = false
                },

                onContinue = {

                    showPermissions = false

                    isLoggedIn = true
                }
            )
        }

        // MAIN APP

        isLoggedIn -> {

            MainContainerScreen(

                onLogout = {

                    isLoggedIn = false
                }
            )
        }

        // AUTH SCREEN

        else -> {

            AuthScreen(

                onLoginSuccess = {

                    isLoggedIn = true
                },

                onSignupSuccess = {

                    showPermissions = true
                }
            )
        }
    }
}