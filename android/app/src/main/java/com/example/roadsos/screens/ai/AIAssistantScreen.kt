package com.example.roadsos.screens.ai

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
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
import com.example.roadsos.theme.ChatBackgroundBrush
import com.example.roadsos.theme.PrimaryRed
import com.example.roadsos.theme.TextGray
import com.example.roadsos.theme.TextWhite
import androidx.compose.foundation.layout.imePadding

import com.example.roadsos.ui.components.ErrorBanner

data class AIChatMessage(
    val text: String,
    val isUser: Boolean,
    val time: String
)

@Composable
fun AIAssistantScreen(
    onBack: () -> Unit
) {

    BackHandler {
        onBack()
    }

    var messageText by remember {
        mutableStateOf("")
    }

    val messages = remember {

        mutableStateListOf(

            AIChatMessage(
                text = "Hello 👋\nI’m your RoadSOS AI assistant.\nHow can I help you today?",
                isUser = false,
                time = "9:41 AM"
            )
        )
    }
    var aiError by remember {
        mutableStateOf("")
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(ChatBackgroundBrush)
    ) {

        Column(
            modifier = Modifier.fillMaxSize()
        ) {

            // TOP BAR

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(
                        horizontal = 16.dp,
                        vertical = 54.dp
                    ),

                verticalAlignment = Alignment.CenterVertically
            ) {

                IconButton(
                    onClick = onBack
                ) {

                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = null,
                        tint = Color.White
                    )
                }

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

                    Text(
                        text = "AI",
                        color = Color.White,
                        fontWeight = FontWeight.Bold,
                        fontSize = 18.sp
                    )
                }

                Spacer(modifier = Modifier.width(14.dp))

                Column {

                    Text(
                        text = "RoadSOS AI",
                        color = TextWhite,
                        fontSize = 22.sp,
                        fontWeight = FontWeight.Bold
                    )

                    Text(
                        text = "Online",
                        color = Color(0xFF4DFF88),
                        fontSize = 14.sp
                    )
                }
            }

            // SECURITY BANNER

            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 18.dp),

                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFF101B2A)
                ),

                shape = RoundedCornerShape(22.dp)
            ) {

                Row(
                    modifier = Modifier.padding(18.dp),

                    verticalAlignment = Alignment.CenterVertically
                ) {

                    Box(
                        modifier = Modifier
                            .size(42.dp)
                            .clip(CircleShape)
                            .background(
                                PrimaryRed.copy(alpha = 0.15f)
                            ),

                        contentAlignment = Alignment.Center
                    ) {

                        Text(
                            text = "🛡",
                            fontSize = 18.sp
                        )
                    }

                    Spacer(modifier = Modifier.width(14.dp))

                    Column {

                        Text(
                            text = "Emergency AI is active",
                            color = TextWhite,
                            fontWeight = FontWeight.SemiBold
                        )

                        Spacer(modifier = Modifier.height(4.dp))

                        Text(
                            text = "Do not share sensitive personal data.",
                            color = TextGray,
                            fontSize = 13.sp
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(18.dp))

            // CHAT AREA
            if (aiError.isNotEmpty()) {

                ErrorBanner(
                    message = aiError
                )

                Spacer(modifier = Modifier.height(12.dp))
            }

            LazyColumn(
                modifier = Modifier.weight(1f),

                contentPadding = PaddingValues(
                    horizontal = 18.dp,
                    vertical = 12.dp
                ),

                verticalArrangement =
                    Arrangement.spacedBy(18.dp)
            ) {

                items(messages) { message ->

                    Row(
                        modifier = Modifier.fillMaxWidth(),

                        horizontalArrangement =
                            if (message.isUser)
                                Arrangement.End
                            else
                                Arrangement.Start,

                        verticalAlignment = Alignment.Bottom
                    ) {

                        // AI PROFILE

                        if (!message.isUser) {

                            Box(
                                modifier = Modifier
                                    .size(32.dp)
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

                                Text(
                                    text = "AI",
                                    color = Color.White,
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }

                            Spacer(modifier = Modifier.width(10.dp))
                        }

                        Column(
                            horizontalAlignment =
                                if (message.isUser)
                                    Alignment.End
                                else
                                    Alignment.Start
                        ) {

                            Card(
                                modifier = Modifier.widthIn(max = 280.dp),

                                colors = CardDefaults.cardColors(
                                    containerColor =
                                        if (message.isUser)
                                            PrimaryRed
                                        else
                                            Color(0xFF111C2B)
                                ),

                                shape = RoundedCornerShape(
                                    topStart = 22.dp,
                                    topEnd = 22.dp,

                                    bottomStart =
                                        if (message.isUser) 22.dp else 6.dp,

                                    bottomEnd =
                                        if (message.isUser) 6.dp else 22.dp
                                )
                            ) {

                                Column(
                                    modifier = Modifier.padding(
                                        horizontal = 18.dp,
                                        vertical = 14.dp
                                    )
                                ) {

                                    Text(
                                        text = message.text,
                                        color = Color.White,
                                        fontSize = 15.sp,
                                        lineHeight = 24.sp
                                    )

                                    Spacer(modifier = Modifier.height(6.dp))

                                    Text(
                                        text = message.time,
                                        color = Color.White.copy(alpha = 0.65f),
                                        fontSize = 11.sp
                                    )
                                }
                            }
                        }

                        // USER PROFILE

                        if (message.isUser) {

                            Spacer(modifier = Modifier.width(10.dp))

                            Box(
                                modifier = Modifier
                                    .size(32.dp)
                                    .clip(CircleShape)
                                    .background(Color(0xFF2A3955)),

                                contentAlignment = Alignment.Center
                            ) {

                                Icon(
                                    imageVector = Icons.Default.Person,
                                    contentDescription = null,
                                    tint = Color.White,
                                    modifier = Modifier.size(16.dp)
                                )
                            }
                        }
                    }
                }
            }

            // INPUT BAR

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .imePadding()
                    .padding(
                        horizontal = 16.dp,
                        vertical = 14.dp
                    ),

                verticalAlignment = Alignment.CenterVertically
            ) {

                OutlinedTextField(
                    value = messageText,

                    onValueChange = {

                        messageText = it
                    },

                    modifier = Modifier.weight(1f),

                    placeholder = {

                        Text(
                            text = "Type a message...",
                            color = TextGray
                        )
                    },

                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Text
                    ),

                    shape = RoundedCornerShape(30.dp),

                    colors = OutlinedTextFieldDefaults.colors(

                        focusedContainerColor =
                            Color(0xFF101B2A),

                        unfocusedContainerColor =
                            Color(0xFF101B2A),

                        focusedBorderColor =
                            PrimaryRed,

                        unfocusedBorderColor =
                            Color.Transparent,

                        focusedTextColor =
                            Color.White,

                        unfocusedTextColor =
                            Color.White,

                        cursorColor =
                            PrimaryRed
                    )
                )

                Spacer(modifier = Modifier.width(14.dp))

                // SEND BUTTON

                IconButton(

                    onClick = {

                        if (messageText.isNotBlank()) {

                            val userMessage = messageText

                            messages.add(
                                AIChatMessage(
                                    text = userMessage,
                                    isUser = true,
                                    time = "Now"
                                )
                            )

                            messageText = ""

                            // DUMMY AI RESPONSE
                            aiError = "AI service temporarily unavailable"
                            messages.add(

                                AIChatMessage(
                                    text = "RoadSOS AI received your message:\n\"$userMessage\"\n\nEmergency assistance suggestions will appear here.",
                                    isUser = false,
                                    time = "Now"
                                )
                            )
                        }
                    }

                ) {

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
                            imageVector = Icons.Default.Send,
                            contentDescription = null,
                            tint = Color.White
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(14.dp))
        }
    }
}