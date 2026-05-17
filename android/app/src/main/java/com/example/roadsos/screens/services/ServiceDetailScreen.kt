package com.example.roadsos.screens.services

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.Directions
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.roadsos.screens.home.BottomNavBar
import com.example.roadsos.screens.navigation.BottomNavScreen
import com.example.roadsos.theme.CardBackground
import com.example.roadsos.theme.DarkBackground
import com.example.roadsos.theme.PrimaryRed
import com.example.roadsos.theme.TextGray
import com.example.roadsos.theme.TextWhite
import androidx.activity.compose.BackHandler

@Composable
fun ServiceDetailScreen(
    service: EmergencyService,
    currentScreen: BottomNavScreen,
    onTabSelected: (BottomNavScreen) -> Unit,
    onBack: () -> Unit
) {
    BackHandler {

        onBack()
    }

    val facilities = listOf(
        "Emergency",
        "ICU",
        "24/7",
        "Trauma Care",
        "Ambulance"
    )

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
        ) {

            // MAP HEADER

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(300.dp)
                    .background(
                        Brush.verticalGradient(
                            colors = listOf(
                                Color(0xFF132238),
                                Color(0xFF08111F)
                            )
                        )
                    )
            ) {

                // GRID

                Column(
                    modifier = Modifier.fillMaxSize()
                ) {

                    repeat(7) {

                        Row(
                            modifier = Modifier.weight(1f)
                        ) {

                            repeat(5) {

                                Box(
                                    modifier = Modifier
                                        .weight(1f)
                                        .fillMaxHeight()
                                ) {

                                    Box(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .height(1.dp)
                                            .background(
                                                Color.White.copy(alpha = 0.05f)
                                            )
                                    )

                                    Box(
                                        modifier = Modifier
                                            .width(1.dp)
                                            .fillMaxHeight()
                                            .background(
                                                Color.White.copy(alpha = 0.05f)
                                            )
                                    )
                                }
                            }
                        }
                    }
                }

                // ROUTE PATH

                Box(
                    modifier = Modifier
                        .offset(
                            x = 95.dp,
                            y = 150.dp
                        )
                        .width(150.dp)
                        .height(5.dp)
                        .clip(RoundedCornerShape(50.dp))
                        .background(PrimaryRed)
                )

                // USER DOT

                Box(
                    modifier = Modifier
                        .offset(
                            x = 72.dp,
                            y = 138.dp
                        )
                        .size(24.dp)
                        .clip(CircleShape)
                        .background(Color(0xFF4DA3FF))
                )

                // DESTINATION

                Box(
                    modifier = Modifier
                        .offset(
                            x = 230.dp,
                            y = 128.dp
                        )
                        .size(24.dp)
                        .clip(CircleShape)
                        .background(PrimaryRed)
                )

                // TOP BAR

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(
                            horizontal = 20.dp,
                            vertical = 52.dp
                        ),

                    verticalAlignment = Alignment.CenterVertically
                ) {

                    IconButton(
                        onClick = onBack
                    ) {

                        Box(
                            modifier = Modifier
                                .size(46.dp)
                                .clip(CircleShape)
                                .background(Color(0xFF1A2433)),

                            contentAlignment = Alignment.Center
                        ) {

                            Icon(
                                imageVector = Icons.Default.ArrowBack,
                                contentDescription = null,
                                tint = Color.White
                            )
                        }
                    }
                }

                // ETA CHIP

                Card(
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .padding(bottom = 24.dp),

                    colors = CardDefaults.cardColors(
                        containerColor = Color(0xFF14253C)
                    ),

                    shape = RoundedCornerShape(22.dp)
                ) {

                    Row(
                        modifier = Modifier.padding(
                            horizontal = 18.dp,
                            vertical = 12.dp
                        ),

                        verticalAlignment =
                            Alignment.CenterVertically
                    ) {

                        Box(
                            modifier = Modifier
                                .size(10.dp)
                                .clip(CircleShape)
                                .background(Color.Green)
                        )

                        Spacer(modifier = Modifier.width(10.dp))

                        Text(
                            text = "${service.eta} away",
                            color = Color.White,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
            }

            // CONTENT

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp)
            ) {

                Spacer(modifier = Modifier.height(24.dp))

                // TITLE

                Text(
                    text = service.name,
                    color = TextWhite,
                    fontSize = 32.sp,
                    fontWeight = FontWeight.Bold
                )

                Spacer(modifier = Modifier.height(10.dp))

                // STATUS

                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {

                    Box(
                        modifier = Modifier
                            .size(10.dp)
                            .clip(CircleShape)
                            .background(Color.Green)
                    )

                    Spacer(modifier = Modifier.width(8.dp))

                    Text(
                        text = "Open 24/7",
                        color = Color.Green,
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Medium
                    )
                }

                Spacer(modifier = Modifier.height(24.dp))

                // INFO CARDS

                Row(
                    modifier = Modifier.fillMaxWidth(),

                    horizontalArrangement =
                        Arrangement.spacedBy(12.dp)
                ) {

                    DetailInfoCard(
                        title = "Distance",
                        value = service.distance,
                        modifier = Modifier.weight(1f)
                    )

                    DetailInfoCard(
                        title = "ETA",
                        value = service.eta,
                        modifier = Modifier.weight(1f)
                    )

                    DetailInfoCard(
                        title = "Rating",
                        value = "${service.rating} ★",
                        modifier = Modifier.weight(1f)
                    )
                }

                Spacer(modifier = Modifier.height(24.dp))

                // ACTIONS

                Row(
                    modifier = Modifier.fillMaxWidth(),

                    horizontalArrangement =
                        Arrangement.spacedBy(14.dp)
                ) {

                    ActionButton(
                        text = "Directions",
                        background = Color(0xFF1A2433),
                        icon = Icons.Default.Directions,

                        modifier = Modifier.weight(1f)
                    )

                    ActionButton(
                        text = "Call Now",
                        background = PrimaryRed,
                        icon = Icons.Default.Call,

                        modifier = Modifier.weight(1f)
                    )
                }

                Spacer(modifier = Modifier.height(32.dp))

                // LOCATION

                Text(
                    text = "Location",
                    color = TextWhite,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.SemiBold
                )

                Spacer(modifier = Modifier.height(16.dp))

                Row {

                    Icon(
                        imageVector = Icons.Default.LocationOn,
                        contentDescription = null,
                        tint = PrimaryRed
                    )

                    Spacer(modifier = Modifier.width(12.dp))

                    Text(
                        text = "New Delhi, India",
                        color = TextGray,
                        fontSize = 15.sp,
                        lineHeight = 24.sp
                    )
                }

                Spacer(modifier = Modifier.height(32.dp))

                // FACILITIES

                Text(
                    text = "Facilities",
                    color = TextWhite,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.SemiBold
                )

                Spacer(modifier = Modifier.height(16.dp))

                LazyRow(
                    horizontalArrangement =
                        Arrangement.spacedBy(12.dp)
                ) {

                    items(facilities) { facility ->

                        Card(
                            colors = CardDefaults.cardColors(
                                containerColor = CardBackground
                            ),

                            shape = RoundedCornerShape(18.dp)
                        ) {

                            Text(
                                text = facility,
                                color = TextWhite,

                                modifier = Modifier.padding(
                                    horizontal = 18.dp,
                                    vertical = 12.dp
                                ),

                                fontSize = 13.sp
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(36.dp))

                // CONTACT CARD

                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = CardBackground
                    ),

                    shape = RoundedCornerShape(28.dp)
                ) {

                    Column(
                        modifier = Modifier.padding(22.dp)
                    ) {

                        Text(
                            text = "Emergency Contact",
                            color = TextWhite,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold
                        )

                        Spacer(modifier = Modifier.height(18.dp))

                        Row(
                            verticalAlignment =
                                Alignment.CenterVertically
                        ) {

                            Icon(
                                imageVector = Icons.Default.Call,
                                contentDescription = null,
                                tint = PrimaryRed
                            )

                            Spacer(modifier = Modifier.width(12.dp))

                            Text(
                                text = "+91 98765 43210",
                                color = TextGray,
                                fontSize = 15.sp
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(140.dp))
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
fun DetailInfoCard(
    title: String,
    value: String,
    modifier: Modifier = Modifier
) {

    Card(
        modifier = modifier,

        colors = CardDefaults.cardColors(
            containerColor = CardBackground
        ),

        shape = RoundedCornerShape(22.dp)
    ) {

        Column(
            modifier = Modifier.padding(18.dp)
        ) {

            Text(
                text = title,
                color = TextGray,
                fontSize = 12.sp
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = value,
                color = TextWhite,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@Composable
fun ActionButton(
    text: String,
    background: Color,
    icon: ImageVector,
    modifier: Modifier = Modifier
) {

    Card(
        modifier = modifier.height(58.dp),

        colors = CardDefaults.cardColors(
            containerColor = background
        ),

        shape = RoundedCornerShape(20.dp)
    ) {

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = 18.dp,
                    vertical = 16.dp
                ),

            horizontalArrangement = Arrangement.Center,

            verticalAlignment = Alignment.CenterVertically
        ) {

            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = Color.White
            )

            Spacer(modifier = Modifier.width(10.dp))

            Text(
                text = text,
                color = Color.White,
                fontSize = 15.sp,
                fontWeight = FontWeight.SemiBold
            )
        }
    }
}