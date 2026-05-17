package com.example.roadsos

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import com.example.roadsos.screens.auth.AuthScreen
import com.example.roadsos.screens.navigation.MainContainerScreen
import com.example.roadsos.screens.splash.SplashScreen
import com.example.roadsos.theme.RoadSoSTheme
import kotlinx.coroutines.delay
import com.example.roadsos.screens.permissions.PermissionScreen

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {

        super.onCreate(savedInstanceState)

        setContent {

            RoadSoSTheme {

                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {

                    RoadSoSApp()
                }
            }
        }
    }
}

@Composable
fun RoadSoSApp() {

    var showSplash by remember {
        mutableStateOf(true)
    }

    var isLoggedIn by remember {
        mutableStateOf(false)
    }

    var showPermissions by remember {
        mutableStateOf(false)
    }

    LaunchedEffect(Unit) {

        delay(2500)

        showSplash = false
    }

    when {

        // SPLASH

        showSplash -> {

            SplashScreen()
        }

        // PERMISSION FLOW AFTER SIGNUP

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