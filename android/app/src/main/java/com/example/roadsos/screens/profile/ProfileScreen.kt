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


data class CountryCode(
    val flag: String,
    val name: String,
    val code: String
)

val countryCodes = listOf(

    CountryCode("🇮🇳","India","+91"),
    CountryCode("🇺🇸","USA","+1"),
    CountryCode("🇬🇧","UK","+44"),
    CountryCode("🇨🇦","Canada","+1"),
    CountryCode("🇦🇺","Australia","+61"),
    CountryCode("🇩🇪","Germany","+49"),
    CountryCode("🇫🇷","France","+33"),
    CountryCode("🇯🇵","Japan","+81"),
    CountryCode("🇨🇳","China","+86"),
    CountryCode("🇸🇬","Singapore","+65")
)
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

        mutableStateOf("9876543210")
    }

    var expanded by remember {

        mutableStateOf(false)
    }

    var selectedCountry by remember {

        mutableStateOf(
            countryCodes[0]
        )
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
        ) {

            // FIXED HEADER

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp)
            ) {

                Spacer(
                    modifier =
                        Modifier.height(42.dp)
                )

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

                            contentDescription =
                                null,

                            tint = TextWhite
                        )
                    }

                    Spacer(
                        modifier =
                            Modifier.width(8.dp)
                    )

                    Text(
                        text = "Profile",

                        color = TextWhite,

                        fontSize = 28.sp,

                        fontWeight =
                            FontWeight.Bold
                    )
                }
            }

            // SCROLLABLE CONTENT

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(
                        rememberScrollState()
                    )
                    .padding(
                        horizontal = 20.dp
                    )
            ) {

                Spacer(
                    modifier =
                        Modifier.height(10.dp)
                )

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
                        .align(
                            Alignment.CenterHorizontally
                        ),

                    contentAlignment =
                        Alignment.Center
                ) {

                    Icon(
                        imageVector =
                            Icons.Default.Person,

                        contentDescription =
                            null,

                        tint = Color.White,

                        modifier =
                            Modifier.size(60.dp)
                    )
                }

                Spacer(
                    modifier =
                        Modifier.height(18.dp)
                )

                Text(
                    text = name,

                    color = TextWhite,

                    fontSize = 26.sp,

                    fontWeight =
                        FontWeight.Bold,

                    modifier =
                        Modifier.align(
                            Alignment.CenterHorizontally
                        )
                )

                Spacer(
                    modifier =
                        Modifier.height(42.dp)
                )

                // NAME

                ProfileInputField(
                    label = "Full Name",
                    value = name,
                    icon = Icons.Default.Person,
                    enabled = isEditing
                ) {

                    name = it
                }

                Spacer(
                    modifier =
                        Modifier.height(20.dp)
                )

                // PHONE + COUNTRY

                Column {

                    Text(
                        text = "Phone Number",
                        color = TextGray,
                        fontSize = 14.sp
                    )

                    Spacer(
                        modifier =
                            Modifier.height(10.dp)
                    )

                    Row(
                        modifier =
                            Modifier.fillMaxWidth(),

                        verticalAlignment =
                            Alignment.CenterVertically
                    ) {

                        Box(
                            modifier =
                                Modifier.width(105.dp)
                        ) {

                            OutlinedButton(

                                onClick = {

                                    if (
                                        isEditing
                                    ) {

                                        expanded = true
                                    }
                                },

                                modifier =
                                    Modifier.height(
                                        58.dp
                                    ),

                                shape =
                                    RoundedCornerShape(
                                        22.dp
                                    ),

                                colors =
                                    ButtonDefaults.outlinedButtonColors(

                                        containerColor =
                                            CardBackground,

                                        contentColor =
                                            TextWhite
                                    )
                            ) {

                                Text(
                                    text =
                                        "${selectedCountry.flag} ${selectedCountry.code}"
                                )
                            }

                            DropdownMenu(

                                expanded =
                                    expanded,

                                onDismissRequest = {

                                    expanded = false
                                }
                            ) {

                                countryCodes.forEach {

                                    DropdownMenuItem(

                                        text = {

                                            Text(
                                                "${it.flag} ${it.name} (${it.code})"
                                            )
                                        },

                                        onClick = {

                                            selectedCountry =
                                                it

                                            expanded =
                                                false
                                        }
                                    )
                                }
                            }
                        }

                        Spacer(
                            modifier =
                                Modifier.width(
                                    6.dp
                                )
                        )

                        OutlinedTextField(

                            value = phone,

                            onValueChange = {

                                phone = it
                            },

                            modifier =
                                Modifier.weight(
                                    1f
                                ),

                            enabled =
                                isEditing,

                            singleLine =
                                true,

                            leadingIcon = {

                                Icon(
                                    imageVector =
                                        Icons.Default.Phone,

                                    contentDescription =
                                        null,

                                    tint =
                                        PrimaryRed
                                )
                            },

                            colors =
                                OutlinedTextFieldDefaults.colors(

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

                                    focusedTextColor =
                                        TextWhite,

                                    unfocusedTextColor =
                                        TextWhite,

                                    disabledTextColor =
                                        TextWhite,

                                    cursorColor =
                                        PrimaryRed
                                ),

                            shape =
                                RoundedCornerShape(
                                    22.dp
                                )
                        )
                    }
                }

                Spacer(
                    modifier =
                        Modifier.height(20.dp)
                )

                // EMAIL

                ProfileInputField(
                    label = "Email",
                    value = email,
                    icon = Icons.Default.Email,
                    enabled = isEditing
                ) {

                    email = it
                }

                Spacer(
                    modifier =
                        Modifier.height(26.dp)
                )

                // PERMISSIONS CARD

                Card(
                    onClick = {

                        onOpenPermissions()
                    },

                    colors =
                        CardDefaults.cardColors(
                            containerColor =
                                CardBackground
                        ),

                    shape =
                        RoundedCornerShape(
                            24.dp
                        )
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
                                    PrimaryRed.copy(
                                        alpha = 0.12f
                                    )
                                ),

                            contentAlignment =
                                Alignment.Center
                        ) {

                            Icon(
                                imageVector =
                                    Icons.Default.Lock,

                                contentDescription =
                                    null,

                                tint =
                                    PrimaryRed
                            )
                        }

                        Spacer(
                            modifier =
                                Modifier.width(
                                    16.dp
                                )
                        )

                        Column(
                            modifier =
                                Modifier.weight(1f)
                        ) {

                            Text(
                                "Permission Settings",
                                color =
                                    TextWhite,

                                fontSize =
                                    17.sp,

                                fontWeight =
                                    FontWeight.Bold
                            )

                            Spacer(
                                modifier =
                                    Modifier.height(
                                        4.dp
                                    )
                            )

                            Text(
                                "Manage location & emergency permissions.",
                                color =
                                    TextGray,

                                fontSize =
                                    13.sp
                            )
                        }

                        Icon(
                            imageVector =
                                Icons.Default.Edit,

                            contentDescription =
                                null,

                            tint =
                                TextGray
                        )
                    }
                }

                Spacer(
                    modifier =
                        Modifier.height(34.dp)
                )

                // SAVE

                Button(
                    onClick = {

                        isEditing = false
                    },

                    modifier = Modifier
                        .fillMaxWidth()
                        .height(60.dp),

                    shape =
                        RoundedCornerShape(
                            24.dp
                        ),

                    colors =
                        ButtonDefaults.buttonColors(
                            containerColor =
                                PrimaryRed
                        )
                ) {

                    Text(
                        "Save Changes",
                        fontSize = 17.sp,
                        fontWeight =
                            FontWeight.Bold
                    )
                }

                Spacer(
                    modifier =
                        Modifier.height(18.dp)
                )

                // LOGOUT

                OutlinedButton(
                    onClick = {

                        onLogout()
                    },

                    modifier = Modifier
                        .fillMaxWidth()
                        .height(58.dp),

                    shape =
                        RoundedCornerShape(
                            24.dp
                        ),

                    colors =
                        ButtonDefaults.outlinedButtonColors(
                            contentColor =
                                PrimaryRed
                        )
                ) {

                    Icon(
                        imageVector =
                            Icons.Default.Logout,

                        contentDescription =
                            null
                    )

                    Spacer(
                        modifier =
                            Modifier.width(
                                10.dp
                            )
                    )

                    Text(
                        "Logout",
                        fontWeight =
                            FontWeight.Bold
                    )
                }

                Spacer(
                    modifier =
                        Modifier.height(
                            60.dp
                        )
                )
            }
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