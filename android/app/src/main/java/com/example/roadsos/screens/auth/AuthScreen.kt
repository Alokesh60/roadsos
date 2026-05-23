package com.example.roadsos.screens.auth

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.roadsos.R
import com.example.roadsos.theme.PrimaryRed
import com.example.roadsos.theme.TextGray
import com.example.roadsos.theme.TextWhite




import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@Composable
fun AuthScreen(
    onLoginSuccess: () -> Unit,
    onSignupSuccess: () -> Unit
) {

    var isSignup by remember {
        mutableStateOf(true)
    }

    var name by remember {
        mutableStateOf("")
    }

    var phone by remember {
        mutableStateOf("")
    }
    var countryCode by remember {
        mutableStateOf("")
    }

    var otp by remember {
        mutableStateOf("")
    }

    // ERROR + LOADING STATES

    var authError by remember {
        mutableStateOf("")
    }

    var isLoading by remember {
        mutableStateOf(false)
    }

    Box(
        modifier = Modifier.fillMaxSize()
    ) {

        // BACKGROUND IMAGE

        Image(
            painter = painterResource(
                id = R.drawable.splash_bg
            ),

            contentDescription = null,

            modifier = Modifier.fillMaxSize(),

            contentScale = ContentScale.Crop
        )

        // DARK OVERLAY

        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Color.Black.copy(alpha = 0.72f)
                )
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(
                    rememberScrollState()
                )
                .padding(24.dp),

            horizontalAlignment =
                Alignment.CenterHorizontally
        ) {

            Spacer(modifier = Modifier.height(62.dp))

            // LOGO

            Box(
                modifier = Modifier
                    .size(120.dp)
                    .clip(CircleShape)
                    .background(
                        Brush.radialGradient(
                            colors = listOf(
                                Color(0xFFFF6B6B),
                                PrimaryRed
                            )
                        )
                    ),

                contentAlignment = Alignment.Center
            ) {

                Text(
                    text = "SOS",
                    color = Color.White,
                    fontSize = 34.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            Text(
                text = "RoadSoS",
                color = TextWhite,
                fontSize = 34.sp,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(10.dp))

            Text(
                text = "Emergency Assistance Fast",
                color = TextGray,
                fontSize = 16.sp
            )

            Spacer(modifier = Modifier.height(42.dp))

            // TOGGLE BUTTONS

            Row(
                modifier = Modifier.fillMaxWidth()
            ) {

                AuthToggleButton(
                    text = "Sign Up",
                    selected = isSignup,

                    modifier = Modifier.weight(1f)
                ) {

                    isSignup = true

                    authError = ""
                }

                Spacer(modifier = Modifier.width(12.dp))

                AuthToggleButton(
                    text = "Login",
                    selected = !isSignup,

                    modifier = Modifier.weight(1f)
                ) {

                    isSignup = false

                    authError = ""
                }
            }

            Spacer(modifier = Modifier.height(28.dp))

            // NAME FIELD

            if (isSignup) {

                AuthInputField(
                    value = name,
                    placeholder = "Full Name",
                    icon = Icons.Default.Person
                ) {

                    name = it
                }

                Spacer(modifier = Modifier.height(18.dp))
            }

            // PHONE FIELD

            // COUNTRY CODE + PHONE

            Row(
                modifier = Modifier.fillMaxWidth(),

                verticalAlignment =
                    Alignment.CenterVertically
            ) {

                // COUNTRY CODE

                AuthInputField(

                    value = countryCode,

                    placeholder = "+91",

                    icon = Icons.Default.Phone,

                    modifier =
                        Modifier.width(100.dp),

                    keyboardType =
                        KeyboardType.Phone
                ) {

                    countryCode = it
                }

                Spacer(
                    modifier =
                        Modifier.width(6.dp)
                )

                // PHONE

                AuthInputField(

                    value = phone,

                    placeholder = "Phone Number",

                    icon = Icons.Default.Phone,

                    modifier =
                        Modifier.weight(1f),

                    keyboardType =
                        KeyboardType.Phone
                ) {

                    phone = it
                }
            }

            Spacer(modifier = Modifier.height(18.dp))

            // OTP FIELD

            AuthInputField(
                value = otp,
                placeholder = "OTP",
                icon = Icons.Default.Phone,
                keyboardType = KeyboardType.Number
            ) {

                otp = it
            }

            // ERROR MESSAGE BELOW OTP

            if (authError.isNotEmpty()) {

                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    text = authError,
                    color = Color(0xFFFF6B6B),
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Medium
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            // SEND OTP

            TextButton(
                onClick = { }
            ) {

                Text(
                    text = "Send OTP",
                    color = PrimaryRed
                )
            }

            Spacer(modifier = Modifier.height(18.dp))

            // CONTINUE BUTTON

            Button(
//                onClick = {
//
//                    authError = ""
//
//                    isLoading = true
//
//                    kotlinx.coroutines.CoroutineScope(
//                        kotlinx.coroutines.Dispatchers.Main
//                    ).launch {
//
//                        kotlinx.coroutines.delay(2000)
//
//                        isLoading = false
//
//                        authError = "Invalid OTP"
//                    }
//                },
                onClick = {

                    if (isSignup) {

                        onSignupSuccess()

                    } else {

                        onLoginSuccess()
                    }
                },

                modifier = Modifier
                    .fillMaxWidth()
                    .height(60.dp),

                shape = RoundedCornerShape(22.dp),

                colors = ButtonDefaults.buttonColors(
                    containerColor = PrimaryRed
                )
            ) {

                if (isLoading) {

                    CircularProgressIndicator(
                        color = Color.White,
                        strokeWidth = 3.dp,
                        modifier = Modifier.size(24.dp)
                    )

                } else {

                    Text(
                        text = "Continue",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            Spacer(modifier = Modifier.height(18.dp))

            // OR TEXT

            Text(
                text = "OR CONTINUE WITH",
                color = TextGray,
                fontSize = 13.sp
            )

            Spacer(modifier = Modifier.height(14.dp))

            // GOOGLE BUTTON

            OutlinedButton(
                onClick = {

                    authError = ""

                    if (isSignup) {

                        onSignupSuccess()

                    } else {

                        onLoginSuccess()
                    }
                },

                modifier = Modifier
                    .fillMaxWidth()
                    .height(58.dp),

                shape = RoundedCornerShape(22.dp),

                colors = ButtonDefaults.outlinedButtonColors(
                    contentColor = TextWhite
                )
            ) {

                Text(
                    text = "Continue with Google",
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(30.dp))
        }
    }
}

@Composable
fun AuthToggleButton(
    text: String,
    selected: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {

    Button(
        onClick = onClick,

        modifier = modifier.height(54.dp),

        shape = RoundedCornerShape(20.dp),

        colors = ButtonDefaults.buttonColors(

            containerColor =
                if (selected) PrimaryRed
                else Color(0xFF1A1F29)
        )
    ) {

        Text(
            text = text,
            color = Color.White,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
fun AuthInputField(
    value: String,
    placeholder: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    modifier: Modifier = Modifier,
    keyboardType: KeyboardType = KeyboardType.Text,
    onValueChange: (String) -> Unit
) {

    OutlinedTextField(
        value = value,

        onValueChange = onValueChange,

        modifier = modifier.fillMaxWidth(),

        singleLine = true,

        leadingIcon = {

            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = PrimaryRed
            )
        },

        placeholder = {

            Text(
                text = placeholder,
                color = TextGray
            )
        },

        keyboardOptions = KeyboardOptions(
            keyboardType = keyboardType
        ),

        colors = OutlinedTextFieldDefaults.colors(

            focusedContainerColor =
                Color(0xFF161B24),

            unfocusedContainerColor =
                Color(0xFF161B24),

            focusedBorderColor =
                PrimaryRed,

            unfocusedBorderColor =
                Color.Transparent,

            focusedTextColor =
                TextWhite,

            unfocusedTextColor =
                TextWhite,

            cursorColor =
                PrimaryRed
        ),

        shape = RoundedCornerShape(22.dp)
    )
}