package com.example.roadsos

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.Box
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.example.roadsos.screens.auth.AuthScreen
import com.example.roadsos.screens.navigation.MainContainerScreen
import com.example.roadsos.screens.permissions.PermissionScreen
import com.example.roadsos.screens.splash.SplashScreen
import com.example.roadsos.theme.RoadSoSTheme
import com.example.roadsos.theme.PrimaryRed
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

        // HANDLE SYSTEM NOTIFICATION CLICKS (When app was killed/background)
        if (intent?.extras?.getString("type") == "sos_alert") {
            val alertIntent = Intent(this, EmergencyResponderActivity::class.java).apply {
                putExtras(intent.extras!!)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
            }
            startActivity(alertIntent)
            // Continue loading MainActivity underneath so they have something to return to
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

    var showPhoneEntry by remember { mutableStateOf(false) }
    var isCheckingPhone by remember { mutableStateOf(false) }

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
        
        isCheckingPhone -> {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = PrimaryRed)
            }
        }

        // PERMISSION SCREEN

        showPermissions -> {

            PermissionScreen(

                onBack = {

                    showPermissions = false
                },

                onContinue = {
                    isCheckingPhone = true
                    showPermissions = false
                    val user = com.google.firebase.auth.FirebaseAuth.getInstance().currentUser
                    if (user != null) {
                        com.google.firebase.firestore.FirebaseFirestore.getInstance()
                            .collection("users")
                            .document(user.uid)
                            .get()
                            .addOnSuccessListener { doc ->
                                val phone = doc.getString("phone")
                                if (phone.isNullOrBlank()) {
                                    showPhoneEntry = true
                                } else {
                                    isLoggedIn = true
                                }
                                isCheckingPhone = false
                            }
                            .addOnFailureListener {
                                isLoggedIn = true
                                isCheckingPhone = false
                            }
                    } else {
                        isLoggedIn = true
                        isCheckingPhone = false
                    }
                }
            )
        }
        
        showPhoneEntry -> {
            com.example.roadsos.screens.auth.PhoneEntryScreen(
                onContinue = {
                    showPhoneEntry = false
                    isLoggedIn = true
                }
            )
        }

        // MAIN APP

        isLoggedIn -> {
            LaunchedEffect(Unit) {
                try {
                    com.google.firebase.messaging.FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
                        if (task.isSuccessful) {
                            val token = task.result
                            val user = com.google.firebase.auth.FirebaseAuth.getInstance().currentUser
                            if (user != null) {
                                val data = mapOf("fcm_token" to token)
                                com.google.firebase.firestore.FirebaseFirestore.getInstance()
                                    .collection("users").document(user.uid)
                                    .set(data, com.google.firebase.firestore.SetOptions.merge())
                            }
                        }
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }

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