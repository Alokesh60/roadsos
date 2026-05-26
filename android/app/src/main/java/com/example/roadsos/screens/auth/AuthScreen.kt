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
import androidx.compose.ui.tooling.preview.Preview
import com.example.roadsos.R
import com.example.roadsos.theme.PrimaryRed
import com.example.roadsos.theme.RoadSoSTheme
import com.example.roadsos.theme.TextGray
import com.example.roadsos.theme.TextWhite
import com.example.roadsos.ui.components.CountryCodePhoneField

import android.app.Activity
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.roadsos.viewmodel.AuthState
import com.example.roadsos.viewmodel.AuthViewModel



import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@Composable
fun AuthScreen(
    onLoginSuccess: () -> Unit,
    onSignupSuccess: () -> Unit,
    viewModel: AuthViewModel = viewModel()
) {
    val context = LocalContext.current
    val authState by viewModel.authState.collectAsState()

    LaunchedEffect(authState) {
        if (authState is AuthState.Success) {
            if (isSignupTemp) { // Will track this in state
                onSignupSuccess()
            } else {
                onLoginSuccess()
            }
            viewModel.resetState()
        }
    }

    AuthScreenContent(
        authState = authState,
        onSendOtp = { phone, isSignup, name -> viewModel.sendVerificationCode(phone, context as Activity, isSignup, name) },
        onVerifyOtp = { code, isSignup, name -> viewModel.verifyOtp(code, isSignup, name) },
        onGoogleSignIn = { isSignup, name -> viewModel.signInWithGoogle(context, isSignup, name) },
        onAuthTypeChange = { isSignup -> isSignupTemp = isSignup }
    )
}

var isSignupTemp = false

@Composable
fun AuthScreenContent(
    authState: AuthState,
    onSendOtp: (String, Boolean, String) -> Unit,
    onVerifyOtp: (String, Boolean, String) -> Unit,
    onGoogleSignIn: (Boolean, String) -> Unit,
    onAuthTypeChange: (Boolean) -> Unit
) {

    var isSignup by remember {
        mutableStateOf(false)
    }

    var name by remember {
        mutableStateOf("")
    }

    var countryCode by remember {
        mutableStateOf("+91")
    }
    var countryCode by remember {
        mutableStateOf("")
    }

    var phone by remember {
        mutableStateOf("")
    }

    var otp by remember {
        mutableStateOf("")
    }

    val isLoading = authState is AuthState.Loading
    val authError = if (authState is AuthState.Error) (authState as AuthState.Error).message else ""
    val isOtpSent = authState is AuthState.OtpSent

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
                .systemBarsPadding()
                .imePadding()
                .verticalScroll(
                    rememberScrollState()
                )
                .padding(24.dp),

            horizontalAlignment =
                Alignment.CenterHorizontally
        ) {

            Spacer(modifier = Modifier.height(32.dp))

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

            Spacer(modifier = Modifier.height(24.dp))

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
                    onAuthTypeChange(true)
                }

                Spacer(modifier = Modifier.width(12.dp))

                AuthToggleButton(
                    text = "Login",
                    selected = !isSignup,

                    modifier = Modifier.weight(1f)
                ) {

                    isSignup = false
                    onAuthTypeChange(false)
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

            CountryCodePhoneField(
                phoneNumber = phone,
                countryCode = countryCode,
                onPhoneNumberChange = { phone = it },
                onCountryCodeChange = { countryCode = it }
            )

            Spacer(modifier = Modifier.height(18.dp))

            // OTP FIELD (Only show if OTP sent)

            if (isOtpSent) {
                AuthInputField(
                    value = otp,
                    placeholder = "OTP",
                    icon = Icons.Default.Phone,
                    keyboardType = KeyboardType.Number
                ) {
                    otp = it
                }
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

            if (!isOtpSent) {
                TextButton(
                    onClick = { onSendOtp(countryCode + phone, isSignup, name) }
                ) {
                    Text(
                        text = "Send OTP",
                        color = PrimaryRed
                    )
                }
            }

            Spacer(modifier = Modifier.height(18.dp))

            // CONTINUE BUTTON

            Button(
                onClick = {
                    if (isOtpSent) {
                        onVerifyOtp(otp, isSignup, name)
                    } else {
                        onSendOtp(countryCode + phone, isSignup, name)
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
                onClick = { onGoogleSignIn(isSignup, name) },

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

@Preview(showBackground = true, showSystemUi = true)
@Composable
fun AuthScreenPreview() {

    RoadSoSTheme {
        AuthScreenContent(
            authState = AuthState.Idle,
            onSendOtp = { _, _, _ -> },
            onVerifyOtp = { _, _, _ -> },
            onGoogleSignIn = { _, _ -> },
            onAuthTypeChange = {}
        )
    }
}