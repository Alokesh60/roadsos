package com.example.roadsos.screens.contacts

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Person
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
fun AddContactScreen(

    onBack: () -> Unit,

    onSave: (EmergencyContact) -> Unit
) {
    BackHandler {

        onBack()
    }

    var name by remember {
        mutableStateOf("")
    }

    var number by remember {
        mutableStateOf("")
    }
    var expanded by remember {

        mutableStateOf(false)
    }

    var selectedCountry by remember {

        mutableStateOf(
            countryCodes[0]
        )
    }

    var relation by remember {
        mutableStateOf("")
    }

    var priority by remember {
        mutableStateOf("")
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
                        tint = Color.White
                    )
                }

                Spacer(modifier = Modifier.width(2.dp))

                Text(
                    text = "Add Contact",
                    color = TextWhite,
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(34.dp))

            // PROFILE ICON

            Box(
                modifier = Modifier
                    .size(110.dp)
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
                    modifier = Modifier.size(52.dp)
                )
            }

            Spacer(modifier = Modifier.height(40.dp))

            // NAME

            InputField(
                label = "Full Name",
                value = name,
                placeholder = "Enter contact name",

                onValueChange = {
                    name = it
                }
            )

            Spacer(modifier = Modifier.height(20.dp))

            // PHONE

            Column {

                Text(
                    text = "Phone Number",
                    color = TextGray,
                    fontSize = 14.sp
                )

                Spacer(
                    modifier = Modifier.height(10.dp)
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),

                    verticalAlignment =
                        Alignment.CenterVertically
                ) {

                    // COUNTRY DROPDOWN

                    Box(
                        modifier =
                            Modifier.width(105.dp)
                    ) {

                        OutlinedButton(

                            onClick = {

                                expanded = true
                            },

                            modifier =
                                Modifier.height(58.dp),

                            shape =
                                RoundedCornerShape(20.dp),

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

                            expanded = expanded,

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

                                        selectedCountry = it

                                        expanded = false
                                    }
                                )
                            }
                        }
                    }

                    Spacer(
                        modifier = Modifier.width(6.dp)
                    )

                    // PHONE INPUT

                    OutlinedTextField(

                        value = number,

                        onValueChange = {

                            number = it
                        },

                        modifier = Modifier.weight(1f),

                        singleLine = true,

                        placeholder = {

                            Text(
                                "Enter phone number",
                                color =
                                    TextGray.copy(alpha = 0.7f)
                            )
                        },

                        colors =
                            OutlinedTextFieldDefaults.colors(

                                focusedContainerColor =
                                    CardBackground,

                                unfocusedContainerColor =
                                    CardBackground,

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

                        shape =
                            RoundedCornerShape(20.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // RELATION

            InputField(
                label = "Relation / Identity",
                value = relation,
                placeholder = "Brother, Friend, Doctor...",

                onValueChange = {
                    relation = it
                }
            )

            Spacer(modifier = Modifier.height(20.dp))

            // PRIORITY DROPDOWN

            PriorityDropdown(
                selectedPriority = priority,

                onPrioritySelected = {
                    priority = it
                }
            )

            Spacer(modifier = Modifier.height(42.dp))

            // SAVE BUTTON

            Button(
                onClick = {

                    if (
                        name.isNotBlank() &&
                        number.isNotBlank() &&
                        relation.isNotBlank() &&
                        priority.isNotBlank()
                    ) {

                        val contact = EmergencyContact(
                            name = name,
                            relation = relation,
                            number = number,
                            priority = priority
                        )

                        onSave(contact)
                    }
                },

                modifier = Modifier
                    .fillMaxWidth()
                    .height(62.dp),

                colors = ButtonDefaults.buttonColors(
                    containerColor = PrimaryRed
                ),

                shape = RoundedCornerShape(24.dp)
            ) {

                Text(
                    text = "Save Contact",
                    color = Color.White,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(40.dp))
        }
    }
}

@Composable
fun InputField(
    label: String,
    value: String,
    placeholder: String,
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

            singleLine = true,

            placeholder = {

                Text(
                    text = placeholder,
                    color = TextGray.copy(alpha = 0.7f)
                )
            },

            colors = OutlinedTextFieldDefaults.colors(

                focusedContainerColor =
                    CardBackground,

                unfocusedContainerColor =
                    CardBackground,

                focusedBorderColor =
                    PrimaryRed,

                unfocusedBorderColor =
                    Color.Transparent,

                cursorColor = PrimaryRed,

                focusedTextColor =
                    TextWhite,

                unfocusedTextColor =
                    TextWhite
            ),

            shape = RoundedCornerShape(20.dp)
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)

@Composable
fun PriorityDropdown(
    selectedPriority: String,
    onPrioritySelected: (String) -> Unit
) {

    val priorities = listOf(
        "Primary",
        "Secondary",
        "Medical",
        "SOS"
    )

    var expanded by remember {
        mutableStateOf(false)
    }

    Column {

        Text(
            text = "Priority Tag",
            color = TextGray,
            fontSize = 14.sp
        )

        Spacer(modifier = Modifier.height(10.dp))

        ExposedDropdownMenuBox(
            expanded = expanded,

            onExpandedChange = {
                expanded = !expanded
            }
        ) {

            OutlinedTextField(
                value = selectedPriority,

                onValueChange = {},

                readOnly = true,

                modifier = Modifier
                    .menuAnchor()
                    .fillMaxWidth(),

                trailingIcon = {

                    ExposedDropdownMenuDefaults
                        .TrailingIcon(
                            expanded = expanded
                        )
                },

                colors = OutlinedTextFieldDefaults.colors(

                    focusedContainerColor =
                        CardBackground,

                    unfocusedContainerColor =
                        CardBackground,

                    focusedBorderColor =
                        PrimaryRed,

                    unfocusedBorderColor =
                        Color.Transparent,

                    focusedTextColor =
                        TextWhite,

                    unfocusedTextColor =
                        TextWhite
                ),

                shape = RoundedCornerShape(20.dp)
            )

            ExposedDropdownMenu(
                expanded = expanded,

                onDismissRequest = {
                    expanded = false
                }
            ) {

                priorities.forEach { item ->

                    DropdownMenuItem(

                        text = {
                            Text(item)
                        },

                        onClick = {

                            onPrioritySelected(item)

                            expanded = false
                        }
                    )
                }
            }
        }
    }
}