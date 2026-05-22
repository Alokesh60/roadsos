package com.example.roadsos.screens.contacts

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.roadsos.screens.home.BottomNavBar
import com.example.roadsos.screens.navigation.BottomNavScreen
import com.example.roadsos.theme.CardBackground
import com.example.roadsos.theme.DarkBackground
import com.example.roadsos.theme.PrimaryRed
import com.example.roadsos.theme.TextGray
import com.example.roadsos.theme.TextWhite

import com.example.roadsos.ui.components.EmptyStateCard

data class EmergencyContact(
    val name: String,
    val relation: String,
    val number: String,
    val priority: String
)

@Composable
fun ContactsScreen(
    currentScreen: BottomNavScreen,
    onTabSelected: (BottomNavScreen) -> Unit,
    contacts: List<EmergencyContact>,
    onAddContact: () -> Unit,
    onDeleteContact: (EmergencyContact) -> Unit
) {

    var searchText by remember {
        mutableStateOf("")
    }

    val filteredContacts = contacts.filter { contact ->

        contact.name.contains(
            searchText,
            ignoreCase = true
        ) ||

                contact.relation.contains(
                    searchText,
                    ignoreCase = true
                ) ||

                contact.number.contains(
                    searchText,
                    ignoreCase = true
                )
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(DarkBackground)
    ) {

        Column(
            modifier = Modifier.fillMaxSize()
        ) {

            // HEADER

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        Brush.verticalGradient(
                            colors = listOf(
                                Color(0xFF151F2E),
                                DarkBackground
                            )
                        )
                    )
                    .padding(
                        horizontal = 20.dp,
                        vertical = 58.dp
                    )
            ) {

                Text(
                    text = "Emergency Contacts",
                    color = TextWhite,
                    fontSize = 32.sp,
                    fontWeight = FontWeight.Bold
                )

                Spacer(modifier = Modifier.height(10.dp))

                Text(
                    text = "Quickly reach trusted people during emergencies.",
                    color = TextGray,
                    fontSize = 15.sp,
                    lineHeight = 24.sp
                )

                Spacer(modifier = Modifier.height(24.dp))

                // SEARCH BAR

                OutlinedTextField(

                    value = searchText,

                    onValueChange = {

                        searchText = it
                    },

                    modifier = Modifier.fillMaxWidth(),

                    placeholder = {

                        Text(
                            text = "Search contacts...",
                            color = TextGray
                        )
                    },

                    leadingIcon = {

                        Icon(
                            imageVector = Icons.Default.Search,
                            contentDescription = null,
                            tint = TextGray
                        )
                    },

                    singleLine = true,

                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Text
                    ),

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
                            TextWhite,

                        cursorColor =
                            PrimaryRed
                    ),

                    shape = RoundedCornerShape(22.dp)
                )

                Spacer(modifier = Modifier.height(18.dp))

                // ADD CONTACT

                Card(
                    onClick = onAddContact,

                    colors = CardDefaults.cardColors(
                        containerColor = PrimaryRed
                    ),

                    shape = RoundedCornerShape(24.dp)
                ) {

                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(
                                horizontal = 20.dp,
                                vertical = 18.dp
                            ),

                        verticalAlignment = Alignment.CenterVertically
                    ) {

                        Box(
                            modifier = Modifier
                                .size(48.dp)
                                .clip(CircleShape)
                                .background(
                                    Color.White.copy(alpha = 0.15f)
                                ),

                            contentAlignment = Alignment.Center
                        ) {

                            Icon(
                                imageVector = Icons.Default.Add,
                                contentDescription = null,
                                tint = Color.White
                            )
                        }

                        Spacer(modifier = Modifier.width(16.dp))

                        Column(
                            modifier = Modifier.weight(1f)
                        ) {

                            Text(
                                text = "Add Emergency Contact",
                                color = Color.White,
                                fontWeight = FontWeight.Bold,
                                fontSize = 17.sp
                            )

                            Spacer(modifier = Modifier.height(4.dp))

                            Text(
                                text = "Keep your trusted people ready.",
                                color = Color.White.copy(alpha = 0.85f),
                                fontSize = 13.sp
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))
            }

            // CONTACT LIST

            if (filteredContacts.isEmpty()) {

                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(
                            horizontal = 18.dp,
                            vertical = 22.dp
                        )
                ) {

                    EmptyStateCard(

                        title = "No Contacts Found",

                        subtitle =
                            "Add emergency contacts or try another search."
                    )
                }

            } else {

                LazyColumn(
                    modifier = Modifier.weight(1f),

                    contentPadding = PaddingValues(
                        horizontal = 18.dp,
                        vertical = 10.dp
                    ),

                    verticalArrangement =
                        Arrangement.spacedBy(16.dp)
                ) {

                    items(filteredContacts) { contact ->

                        ContactCard(

                            contact = contact,

                            onDelete = {

                                onDeleteContact(contact)
                            }
                        )
                    }

                    item {

                        Spacer(modifier = Modifier.height(120.dp))
                    }
                }
            }
        }

        // NAVBAR

        Box(
            modifier = Modifier.align(Alignment.BottomCenter)
        ) {

            BottomNavBar(
                currentScreen = currentScreen,

                onTabSelected = onTabSelected,

                onSOSError = { }
            )
        }
    }
}

@Composable
fun ContactCard(
    contact: EmergencyContact,
    onDelete: () -> Unit
) {

    var showDeleteDialog by remember {
        mutableStateOf(false)
    }

    Card(
        colors = CardDefaults.cardColors(
            containerColor = CardBackground
        ),

        shape = RoundedCornerShape(28.dp)
    ) {

        Column(
            modifier = Modifier.padding(20.dp)
        ) {

            // TOP ROW

            Row(
                modifier = Modifier.fillMaxWidth(),

                verticalAlignment = Alignment.CenterVertically
            ) {

                Row(
                    modifier = Modifier.weight(1f),

                    verticalAlignment = Alignment.CenterVertically
                ) {

                    // PROFILE

                    Box(
                        modifier = Modifier
                            .size(58.dp)
                            .clip(CircleShape)
                            .background(
                                Brush.radialGradient(
                                    colors = listOf(
                                        Color(0xFFFF6464),
                                        PrimaryRed
                                    )
                                )
                            ),

                        contentAlignment = Alignment.Center
                    ) {

                        Icon(
                            imageVector = Icons.Default.Person,
                            contentDescription = null,
                            tint = Color.White
                        )
                    }

                    Spacer(modifier = Modifier.width(16.dp))

                    Column {

                        Text(
                            text = contact.name,
                            color = TextWhite,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold
                        )

                        Spacer(modifier = Modifier.height(4.dp))

                        Text(
                            text = contact.relation,
                            color = TextGray,
                            fontSize = 14.sp
                        )
                    }
                }

                // DELETE ICON

                IconButton(
                    onClick = {
                        showDeleteDialog = true
                    }
                ) {

                    Icon(
                        imageVector = Icons.Default.Delete,
                        contentDescription = null,
                        tint = PrimaryRed
                    )
                }
            }

            Spacer(modifier = Modifier.height(18.dp))

            // PRIORITY CHIP

            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(18.dp))
                    .background(
                        PrimaryRed.copy(alpha = 0.15f)
                    )
                    .padding(
                        horizontal = 14.dp,
                        vertical = 8.dp
                    )
            ) {

                Text(
                    text = contact.priority,
                    color = PrimaryRed,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }

            Spacer(modifier = Modifier.height(20.dp))

            // PHONE + CALL

            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {

                Column(
                    modifier = Modifier.weight(1f)
                ) {

                    Text(
                        text = "Phone Number",
                        color = TextGray,
                        fontSize = 12.sp
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = contact.number,
                        color = TextWhite,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium
                    )
                }

                // CALL BUTTON

                Box(
                    modifier = Modifier
                        .size(52.dp)
                        .clip(CircleShape)
                        .background(
                            Brush.radialGradient(
                                colors = listOf(
                                    Color(0xFFFF6464),
                                    PrimaryRed
                                )
                            )
                        ),

                    contentAlignment = Alignment.Center
                ) {

                    IconButton(
                        onClick = { }
                    ) {

                        Icon(
                            imageVector = Icons.Default.Call,
                            contentDescription = null,
                            tint = Color.White
                        )
                    }
                }
            }
        }
    }

    // DELETE CONFIRMATION

    if (showDeleteDialog) {

        AlertDialog(

            onDismissRequest = {
                showDeleteDialog = false
            },

            confirmButton = {

                TextButton(

                    onClick = {

                        showDeleteDialog = false

                        onDelete()
                    }
                ) {

                    Text(
                        text = "Delete",
                        color = PrimaryRed
                    )
                }
            },

            dismissButton = {

                TextButton(

                    onClick = {
                        showDeleteDialog = false
                    }
                ) {

                    Text(
                        text = "Cancel",
                        color = TextGray
                    )
                }
            },

            title = {

                Text(
                    text = "Delete Contact",
                    color = TextWhite
                )
            },

            text = {

                Text(
                    text =
                        "Are you sure you want to delete ${contact.name}?",

                    color = TextGray
                )
            },

            containerColor = CardBackground
        )
    }
}