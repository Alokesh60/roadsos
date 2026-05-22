package com.example.roadsos.screens.profile

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Logout
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.roadsos.theme.CardBackground
import com.example.roadsos.theme.DarkBackground
import com.example.roadsos.theme.PrimaryRed
import com.example.roadsos.theme.TextGray
import com.example.roadsos.theme.TextWhite
import androidx.activity.compose.BackHandler

@Composable
fun ProfileScreen(
    onBack: () -> Unit,
    onOpenPermissions: () -> Unit,
    onLogout: () -> Unit
) {
    BackHandler {

        onBack()
    }

    var name by remember {
        mutableStateOf("Tarpan Saikia")
    }

    var phone by remember {
        mutableStateOf("+91 9876543210")
    }

    var email by remember {
        mutableStateOf("tarpan@email.com")
    }
    var isEditing by remember {
        mutableStateOf(true)
    }
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(DarkBackground)
    ) {

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(
                    rememberScrollState()
                )
                .padding(20.dp)
        ) {

            Spacer(modifier = Modifier.height(42.dp))

            // TOP BAR

            Row(
                verticalAlignment =
                    Alignment.CenterVertically
            ) {

                IconButton(
                    onClick = onBack
                ) {

                    Icon(
                        imageVector =
                            Icons.Default.ArrowBack,

                        contentDescription = null,

                        tint = TextWhite
                    )
                }

                Spacer(modifier = Modifier.width(8.dp))

                Text(
                    text = "Profile",
                    color = TextWhite,
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(36.dp))

            // PROFILE ICON

            Box(
                modifier = Modifier
                    .size(120.dp)
                    .clip(CircleShape)
                    .background(
                        Brush.radialGradient(
                            colors = listOf(
                                Color(0xFFFF6666),
                                PrimaryRed
                            )
                        )
                    )
                    .align(Alignment.CenterHorizontally),

                contentAlignment = Alignment.Center
            ) {

                Icon(
                    imageVector = Icons.Default.Person,
                    contentDescription = null,
                    tint = Color.White,
                    modifier = Modifier.size(60.dp)
                )
            }

            Spacer(modifier = Modifier.height(18.dp))

            Text(
                text = name,
                color = TextWhite,
                fontSize = 26.sp,
                fontWeight = FontWeight.Bold,

                modifier = Modifier.align(
                    Alignment.CenterHorizontally
                )
            )

            Spacer(modifier = Modifier.height(42.dp))

            ProfileInputField(
                label = "Full Name",
                value = name,
                icon = Icons.Default.Person,
                enabled = isEditing,
                onValueChange = {
                    name = it
                }
            )

            Spacer(modifier = Modifier.height(20.dp))

            ProfileInputField(
                label = "Phone Number",
                value = phone,
                icon = Icons.Default.Phone,
                enabled = isEditing,

                onValueChange = {
                    phone = it
                }
            )

            Spacer(modifier = Modifier.height(20.dp))

            ProfileInputField(
                label = "Email",
                value = email,
                icon = Icons.Default.Email,
                enabled = isEditing,
                onValueChange = {
                    email = it
                }
            )

            Spacer(modifier = Modifier.height(26.dp))

            // PERMISSION SETTINGS

            Card(
                onClick = {

                    onOpenPermissions()
                },

                colors = CardDefaults.cardColors(
                    containerColor = CardBackground
                ),

                shape = RoundedCornerShape(24.dp)
            ) {

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(20.dp),

                    verticalAlignment =
                        Alignment.CenterVertically
                ) {

                    Box(
                        modifier = Modifier
                            .size(52.dp)
                            .clip(CircleShape)
                            .background(
                                PrimaryRed.copy(alpha = 0.12f)
                            ),

                        contentAlignment = Alignment.Center
                    ) {

                        Icon(
                            imageVector = Icons.Default.Lock,
                            contentDescription = null,
                            tint = PrimaryRed
                        )
                    }

                    Spacer(modifier = Modifier.width(16.dp))

                    Column(
                        modifier = Modifier.weight(1f)
                    ) {

                        Text(
                            text = "Permission Settings",
                            color = TextWhite,
                            fontSize = 17.sp,
                            fontWeight = FontWeight.Bold
                        )

                        Spacer(modifier = Modifier.height(4.dp))

                        Text(
                            text = "Manage location & emergency permissions.",
                            color = TextGray,
                            fontSize = 13.sp
                        )
                    }

                    Icon(
                        imageVector = Icons.Default.Edit,
                        contentDescription = null,
                        tint = TextGray
                    )
                }
            }

            Spacer(modifier = Modifier.height(34.dp))

            // SAVE BUTTON

            Button(
                onClick = {

                    isEditing = false
                },

                modifier = Modifier
                    .fillMaxWidth()
                    .height(60.dp),

                shape = RoundedCornerShape(24.dp),

                colors = ButtonDefaults.buttonColors(
                    containerColor = PrimaryRed
                )
            ) {

                Text(
                    text = "Save Changes",
                    fontSize = 17.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(18.dp))

            // LOGOUT

            OutlinedButton(
                onClick = {

                    onLogout()
                },

                modifier = Modifier
                    .fillMaxWidth()
                    .height(58.dp),

                shape = RoundedCornerShape(24.dp),

                colors = ButtonDefaults.outlinedButtonColors(
                    contentColor = PrimaryRed
                )
            ) {

                Icon(
                    imageVector = Icons.Default.Logout,
                    contentDescription = null
                )

                Spacer(modifier = Modifier.width(10.dp))

                Text(
                    text = "Logout",
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(60.dp))
        }
    }
}

@Composable
fun ProfileInputField(
    label: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    enabled: Boolean,
    onValueChange: (String) -> Unit
) {

    Column {

        Text(
            text = label,
            color = TextGray,
            fontSize = 14.sp
        )

        Spacer(modifier = Modifier.height(10.dp))

        OutlinedTextField(
            value = value,

            onValueChange = onValueChange,

            modifier = Modifier.fillMaxWidth(),

            enabled = enabled,

            singleLine = true,

            leadingIcon = {

                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = PrimaryRed
                )
            },

            colors = OutlinedTextFieldDefaults.colors(

                focusedContainerColor =
                    CardBackground,

                unfocusedContainerColor =
                    CardBackground,

                disabledContainerColor =
                    CardBackground,

                focusedBorderColor =
                    PrimaryRed,

                unfocusedBorderColor =
                    Color.Transparent,

                disabledBorderColor =
                    Color.Transparent,

                cursorColor = PrimaryRed,

                focusedTextColor =
                    TextWhite,

                unfocusedTextColor =
                    TextWhite,

                disabledTextColor =
                    TextWhite
            ),

            shape = RoundedCornerShape(22.dp)
        )
    }
}