package com.example.roadsos.screens.home

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.Call
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.LocalHospital
import androidx.compose.material.icons.filled.LocalPolice
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Map
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.People
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.roadsos.screens.navigation.BottomNavScreen
import com.example.roadsos.theme.CardBackground
import com.example.roadsos.theme.DarkBackground
import com.example.roadsos.theme.PrimaryRed
import com.example.roadsos.theme.TextGray
import com.example.roadsos.theme.TextWhite

import com.example.roadsos.ui.components.NoInternetBanner
import com.example.roadsos.ui.components.ErrorBanner
import androidx.compose.runtime.LaunchedEffect
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.roadsos.viewmodel.ServiceViewModel
import kotlinx.coroutines.delay
import androidx.compose.ui.platform.LocalContext
import com.example.roadsos.LocationUtils

@Composable
fun HomeScreen(
    currentScreen: BottomNavScreen,
    onTabSelected: (BottomNavScreen) -> Unit
) {


    var showNotifications by remember {
        mutableStateOf(false)
    }

    var latitude by remember {
        mutableStateOf(0.0)
    }

    var longitude by remember {
        mutableStateOf(0.0)
    }

    var showSOSDialog by remember {
        mutableStateOf(false)
    }

    var noInternet by remember {
        mutableStateOf(false)
    }

    var sosError by remember {
        mutableStateOf("")
    }

    LaunchedEffect(sosError) {

        if (sosError.isNotEmpty()) {

            kotlinx.coroutines.delay(3000)

            sosError = ""
        }
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

            // NO INTERNET BANNER

            if (noInternet) {

                NoInternetBanner()
            }

            // MAIN CONTENT

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = 20.dp)
                    .padding(bottom = 110.dp)
            ) {

                Spacer(modifier = Modifier.height(55.dp))

                TopSection(

                    onNotificationClick = {

                        showNotifications = true
                    },

                    onProfileClick = {

                        onTabSelected(
                            BottomNavScreen.PROFILE
                        )
                    }
                )

                Spacer(modifier = Modifier.height(22.dp))

                LocationMapCard()

                Spacer(modifier = Modifier.height(26.dp))

                QuickActionsSection()

                Spacer(modifier = Modifier.height(28.dp))

                SOSSection()

                Spacer(modifier = Modifier.height(28.dp))

                NearbyServicesSection()

                Spacer(modifier = Modifier.height(40.dp))
            }
        }

        // NOTIFICATION POPUP

        if (showNotifications) {

            NotificationPopup(

                onDismiss = {

                    showNotifications = false
                }
            )
        }

        // SOS ERROR BANNER

        if (sosError.isNotEmpty()) {

            Box(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(
                        horizontal = 18.dp,
                        vertical = 120.dp
                    )
            ) {

                ErrorBanner(
                    message = sosError
                )
            }
        }

        // BOTTOM NAVBAR

        Box(
            modifier = Modifier.align(Alignment.BottomCenter)
        ) {

            BottomNavBar(
                currentScreen = currentScreen,

                onTabSelected = onTabSelected,

                onSOSError = {

                    sosError = it
                }
            )
        }
    }
}

@Composable
fun TopSection(
    onNotificationClick: () -> Unit,
    onProfileClick: () -> Unit
) {

    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {

        Column {

            Text(
                text = "RoadSoS",
                color = TextWhite,
                fontSize = 34.sp,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(4.dp))

            Text(
                text = "Your Safety, Our Priority",
                color = TextGray,
                fontSize = 15.sp
            )

            Spacer(modifier = Modifier.height(12.dp))

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
                    text = "GPS Active",
                    color = TextGray,
                    fontSize = 13.sp
                )
            }
        }

        Row {

            IconButton(
                onClick = onNotificationClick
            ) {

                BadgedBox(
                    badge = {
                        Badge(
                            containerColor = PrimaryRed
                        )
                    }
                ) {

                    Icon(
                        imageVector = Icons.Default.Notifications,
                        contentDescription = null,
                        tint = TextWhite,
                        modifier = Modifier.size(28.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.width(6.dp))

            IconButton(onClick = onProfileClick) {

                Icon(
                    imageVector = Icons.Default.AccountCircle,
                    contentDescription = null,
                    tint = TextWhite,
                    modifier = Modifier.size(34.dp)
                )
            }
        }
    }
}

@Composable
fun NotificationPopup(
    onDismiss: () -> Unit
) {

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Color.Black.copy(alpha = 0.45f)
            )
    ) {

        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = 18.dp,
                    vertical = 95.dp
                )
                .align(Alignment.TopCenter),

            colors = CardDefaults.cardColors(
                containerColor = Color(0xFF141922)
            ),

            shape = RoundedCornerShape(32.dp)
        ) {

            Column(
                modifier = Modifier
                    .height(520.dp)
                    .padding(22.dp)
            ) {

                Row(
                    modifier = Modifier.fillMaxWidth(),

                    horizontalArrangement =
                        Arrangement.SpaceBetween,

                    verticalAlignment =
                        Alignment.CenterVertically
                ) {

                    Text(
                        text = "Emergency Alerts",
                        color = TextWhite,
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold
                    )

                    TextButton(
                        onClick = onDismiss
                    ) {

                        Text(
                            text = "Close",
                            color = PrimaryRed
                        )
                    }
                }

                Spacer(modifier = Modifier.height(18.dp))

                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f)
                        .verticalScroll(
                            rememberScrollState()
                        )
                ) {

                    NotificationCard(
                        title = "Ambulance Assigned",
                        description =
                            "Unit #A108 is arriving in 4 mins.",

                        time = "2 mins ago",

                        accent = Color(0xFF4CAF50)
                    )

                    Spacer(modifier = Modifier.height(14.dp))

                    NotificationCard(
                        title = "Accident Reported Nearby",

                        description =
                            "Heavy traffic detected on NH37.",

                        time = "5 mins ago",

                        accent = PrimaryRed
                    )

                    Spacer(modifier = Modifier.height(14.dp))

                    NotificationCard(
                        title = "Hospital Available",

                        description =
                            "AIIMS Trauma Centre has emergency beds.",

                        time = "12 mins ago",

                        accent = Color(0xFF4DA3FF)
                    )

                    Spacer(modifier = Modifier.height(14.dp))

                    NotificationCard(
                        title = "Emergency Team Dispatched",

                        description =
                            "Nearest response unit is on the way.",

                        time = "15 mins ago",

                        accent = Color(0xFFFF9800)
                    )

                    Spacer(modifier = Modifier.height(14.dp))

                    NotificationCard(
                        title = "Road Blocked",

                        description =
                            "Traffic congestion detected nearby.",

                        time = "22 mins ago",

                        accent = PrimaryRed
                    )
                }
            }
        }
    }
}

@Composable
fun NotificationCard(
    title: String,
    description: String,
    time: String,
    accent: Color
) {

    Card(
        modifier = Modifier.fillMaxWidth(),

        colors = CardDefaults.cardColors(
            containerColor = CardBackground
        ),

        shape = RoundedCornerShape(26.dp)
    ) {

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(18.dp),

            verticalAlignment = Alignment.Top
        ) {

            Box(
                modifier = Modifier
                    .padding(top = 6.dp)
                    .size(12.dp)
                    .clip(CircleShape)
                    .background(accent)
            )

            Spacer(modifier = Modifier.width(16.dp))

            Column(
                modifier = Modifier.weight(1f)
            ) {

                Text(
                    text = title,
                    color = TextWhite,
                    fontSize = 17.sp,
                    fontWeight = FontWeight.Bold
                )

                Spacer(modifier = Modifier.height(6.dp))

                Text(
                    text = description,
                    color = TextGray,
                    fontSize = 14.sp,
                    lineHeight = 22.sp
                )

                Spacer(modifier = Modifier.height(12.dp))

                Text(
                    text = time,
                    color = accent,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }
        }
    }
}


@Composable
fun LocationMapCard() {

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(250.dp),

        colors = CardDefaults.cardColors(
            containerColor = CardBackground
        ),

        shape = RoundedCornerShape(30.dp)
    ) {

        Box(
            modifier = Modifier.fillMaxSize()
        ) {

            // DARK MAP BG

            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        Color(0xFF101826)
                    )
            )

            // SOFT ROAD LAYOUT

            Canvas(
                modifier = Modifier.fillMaxSize()
            ) {

                val roadColor = Color(0xFF263245)

                // roads

                drawLine(
                    color = roadColor,
                    start = Offset(0f, 180f),
                    end = Offset(size.width, 180f),
                    strokeWidth = 14f
                )

                drawLine(
                    color = roadColor,
                    start = Offset(160f, 0f),
                    end = Offset(160f, size.height),
                    strokeWidth = 14f
                )

                drawLine(
                    color = roadColor.copy(alpha = 0.7f),
                    start = Offset(320f, 0f),
                    end = Offset(320f, size.height),
                    strokeWidth = 8f
                )

                // route

                drawPath(
                    path = androidx.compose.ui.graphics.Path().apply {

                        moveTo(160f, 180f)

                        cubicTo(
                            240f,
                            130f,
                            320f,
                            220f,
                            470f,
                            120f
                        )
                    },

                    color = PrimaryRed,

                    style = Stroke(
                        width = 8f,
                        cap = StrokeCap.Round
                    )
                )
            }

            // BLUE USER DOT

            Box(
                modifier = Modifier
                    .offset(
                        x = 95.dp,
                        y = 120.dp
                    )
                    .size(18.dp)
                    .shadow(
                        elevation = 16.dp,
                        shape = CircleShape,
                        ambientColor = Color(0xFF4DA3FF)
                    )
                    .clip(CircleShape)
                    .background(Color(0xFF4DA3FF))
            )

            // DESTINATION PIN

            Box(
                modifier = Modifier
                    .offset(
                        x = 250.dp,
                        y = 78.dp
                    )
                    .size(16.dp)
                    .clip(CircleShape)
                    .background(PrimaryRed)
            )

            // ETA CARD

            Card(
                modifier = Modifier
                    .offset(
                        x = 170.dp,
                        y = 150.dp
                    ),

                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFF141C28)
                ),

                shape = RoundedCornerShape(14.dp)
            ) {

                Text(
                    text = "3 min away",
                    color = Color(0xFF4CAF50),

                    modifier = Modifier.padding(
                        horizontal = 12.dp,
                        vertical = 8.dp
                    ),

                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }

            // TOP OVERLAY

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(18.dp),

                horizontalArrangement = Arrangement.SpaceBetween
            ) {

                Column {

                    Text(
                        text = "Your Location",
                        color = TextGray,
                        fontSize = 11.sp
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = "Connaught Place",
                        color = TextWhite,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold
                    )

                    Spacer(modifier = Modifier.height(4.dp))

                    Text(
                        text = "New Delhi",
                        color = TextGray,
                        fontSize = 12.sp
                    )
                }

                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = Color(0xFF182232)
                    ),

                    shape = RoundedCornerShape(16.dp)
                ) {

                    Row(
                        modifier = Modifier.padding(
                            horizontal = 12.dp,
                            vertical = 8.dp
                        ),

                        verticalAlignment = Alignment.CenterVertically
                    ) {

                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .clip(CircleShape)
                                .background(Color.Green)
                        )

                        Spacer(modifier = Modifier.width(6.dp))

                        Text(
                            text = "LIVE",
                            color = TextWhite,
                            fontSize = 11.sp
                        )
                    }
                }
            }

            // SEARCH BAR

            Card(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(14.dp),

                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFF151D2A)
                ),

                shape = RoundedCornerShape(18.dp)
            ) {

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(
                            horizontal = 16.dp,
                            vertical = 14.dp
                        ),

                    verticalAlignment = Alignment.CenterVertically
                ) {

                    Icon(
                        imageVector = Icons.Default.Search,
                        contentDescription = null,
                        tint = TextGray
                    )

                    Spacer(modifier = Modifier.width(10.dp))

                    Text(
                        text = "Search hospitals, police...",
                        color = TextGray,
                        fontSize = 14.sp
                    )
                }
            }
        }
    }
}
@Composable
fun QuickActionsSection() {

    Text(
        text = "Quick Actions",
        color = TextWhite,
        fontSize = 24.sp,
        fontWeight = FontWeight.Bold
    )

    Spacer(modifier = Modifier.height(20.dp))

    val actions = listOf(
        Triple("Ambulance", "108", Icons.Default.Call),
        Triple("Police", "100", Icons.Default.LocalPolice),
        Triple("Hospitals", "Nearby", Icons.Default.LocalHospital),
        Triple("Towing", "Services", Icons.Default.DirectionsCar)
    )

    LazyRow {

        items(actions) { item ->

            Card(
                modifier = Modifier
                    .padding(end = 16.dp)
                    .shadow(
                        elevation = 10.dp,
                        shape = RoundedCornerShape(28.dp),
                        ambientColor = PrimaryRed.copy(alpha = 0.08f)
                    )
                    .width(118.dp)
                    .height(150.dp),

                colors = CardDefaults.cardColors(
                    containerColor = CardBackground
                ),

                shape = RoundedCornerShape(28.dp)
            ) {

                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 20.dp),

                    horizontalAlignment = Alignment.CenterHorizontally
                ) {

                    Box(
                        modifier = Modifier
                            .size(58.dp)
                            .clip(CircleShape)
                            .background(
                                PrimaryRed.copy(alpha = 0.12f)
                            ),

                        contentAlignment = Alignment.Center
                    ) {

                        Icon(
                            imageVector = item.third,
                            contentDescription = null,
                            tint = PrimaryRed,
                            modifier = Modifier.size(28.dp)
                        )
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    Text(
                        text = item.first,
                        color = TextWhite,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.SemiBold
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = item.second,
                        color = PrimaryRed,
                        fontSize = 14.sp
                    )
                }
            }
        }
    }
}

@Composable
fun SOSSection() {

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .shadow(
                elevation = 20.dp,
                shape = RoundedCornerShape(34.dp),
                ambientColor = PrimaryRed.copy(alpha = 0.25f)
            )
            .height(155.dp),

        colors = CardDefaults.cardColors(
            containerColor = CardBackground
        ),

        shape = RoundedCornerShape(34.dp)
    ) {

        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    Brush.horizontalGradient(
                        colors = listOf(
                            Color(0xFF300606),
                            Color(0xFF7A0F0F)
                        )
                    )
                )
        ) {

            Column(
                modifier = Modifier
                    .align(Alignment.CenterStart)
                    .padding(start = 24.dp)
            ) {

                Text(
                    text = "Need Help?",
                    color = TextWhite,
                    fontSize = 22.sp,
                    fontWeight = FontWeight.Bold
                )

                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    text = "Press the SOS button\nin any emergency.",
                    color = TextGray,
                    fontSize = 14.sp,
                    lineHeight = 22.sp
                )
            }

            Box(
                modifier = Modifier
                    .padding(end = 26.dp)
                    .size(105.dp)
                    .align(Alignment.CenterEnd)
                    .shadow(
                        elevation = 28.dp,
                        shape = CircleShape,
                        ambientColor = PrimaryRed,
                        spotColor = PrimaryRed
                    )
                    .clip(CircleShape)
                    .background(PrimaryRed),

                contentAlignment = Alignment.Center
            ) {

                Text(
                    text = "SOS",
                    color = Color.White,
                    fontSize = 30.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}


@Composable
fun NearbyServicesSection() {

    val viewModel: ServiceViewModel = viewModel()

    val services by viewModel.services.collectAsState()

    val context = LocalContext.current

    var latitude by remember { mutableStateOf(0.0) }
    var longitude by remember { mutableStateOf(0.0) }

    LaunchedEffect(Unit) {

        LocationUtils.getCurrentLocation(
            context = context
        ) { latitude, longitude ->

            viewModel.fetchNearbyServices(
                lat = latitude,
                lon = longitude
            )
        }
    }

    Text(
        text = "Lat: $latitude\nLon: $longitude",
        color = Color.White
    )

    Text(
        text = "Nearby Services",
        color = TextWhite,
        fontSize = 24.sp,
        fontWeight = FontWeight.Bold
    )

    Spacer(modifier = Modifier.height(20.dp))

    services.take(3).forEach { service ->

        NearbyCard(
            service.name,
            "${service.distance_km} km"
        )

        Spacer(modifier = Modifier.height(14.dp))
    }
}

@Composable
fun NearbyCard(
    title: String,
    distance: String
) {

    Card(
        modifier = Modifier.fillMaxWidth(),

        colors = CardDefaults.cardColors(
            containerColor = CardBackground
        ),

        shape = RoundedCornerShape(24.dp)
    ) {

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(18.dp),

            verticalAlignment = Alignment.CenterVertically
        ) {

            Box(
                modifier = Modifier
                    .size(54.dp)
                    .clip(RoundedCornerShape(18.dp))
                    .background(PrimaryRed.copy(alpha = 0.12f)),

                contentAlignment = Alignment.Center
            ) {

                Icon(
                    imageVector = Icons.Default.LocationOn,
                    contentDescription = null,
                    tint = PrimaryRed
                )
            }

            Spacer(modifier = Modifier.width(16.dp))

            Column(
                modifier = Modifier.weight(1f)
            ) {

                Text(
                    text = title,
                    color = TextWhite,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )

                Spacer(modifier = Modifier.height(6.dp))

                Text(
                    text = distance,
                    color = TextGray,
                    fontSize = 15.sp
                )
            }

            Button(
                onClick = { },

                shape = RoundedCornerShape(16.dp),

                colors = ButtonDefaults.buttonColors(
                    containerColor = PrimaryRed.copy(alpha = 0.18f)
                )
            ) {

                Icon(
                    imageVector = Icons.Default.Call,
                    contentDescription = null,
                    tint = PrimaryRed
                )
            }
        }
    }
}

@Composable
fun BottomNavBar(
    currentScreen: BottomNavScreen,
    onTabSelected: (BottomNavScreen) -> Unit,
    onSOSError: (String) -> Unit
) {

    var showSOSDialog by remember {
        mutableStateOf(false)
    }

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(
                horizontal = 18.dp,
                vertical = 12.dp
            )
            .height(110.dp)
    ) {

        Row(

            modifier = Modifier
                .fillMaxWidth()
                .height(82.dp)
                .align(Alignment.BottomCenter)
                .clip(RoundedCornerShape(34.dp))
                .background(
                    Color(0xFF141922)
                )
                .padding(horizontal = 18.dp),

            horizontalArrangement = Arrangement.SpaceBetween,

            verticalAlignment = Alignment.CenterVertically
        ) {

            BottomNavItem(
                icon = Icons.Default.LocationOn,
                label = "Home",

                selected =
                    currentScreen == BottomNavScreen.HOME,

                onClick = {
                    onTabSelected(BottomNavScreen.HOME)
                }
            )

            BottomNavItem(
                icon = Icons.Default.Map,
                label = "Services",

                selected =
                    currentScreen == BottomNavScreen.SERVICES,

                onClick = {
                    onTabSelected(BottomNavScreen.SERVICES)
                }
            )

            Spacer(modifier = Modifier.width(70.dp))

            BottomNavItem(
                icon = Icons.Default.People,
                label = "Contacts",

                selected =
                    currentScreen == BottomNavScreen.CONTACTS,

                onClick = {
                    onTabSelected(BottomNavScreen.CONTACTS)
                }
            )

            BottomNavItem(
                icon = Icons.Default.Search,
                label = "AI",

                selected =
                    currentScreen == BottomNavScreen.AI,

                onClick = {
                    onTabSelected(BottomNavScreen.AI)
                }
            )
        }

        Box(
            modifier = Modifier
                .align(Alignment.TopCenter)
                .offset(y = 8.dp)
        ) {

            SOSNavButton(

                onClick = {

                    showSOSDialog = true
                }
            )
        }
    }

    // SOS DIALOG

    if (showSOSDialog) {

        AlertDialog(

            onDismissRequest = {

                showSOSDialog = false
            },

            confirmButton = {

                Button(

                    onClick = {

                        showSOSDialog = false

                        onSOSError(
                            "Emergency alert failed. Check internet connection."
                        )
                    },

                    colors = ButtonDefaults.buttonColors(
                        containerColor = PrimaryRed
                    )
                ) {

                    Text("Send SOS")
                }
            },

            dismissButton = {

                OutlinedButton(

                    onClick = {

                        showSOSDialog = false
                    }
                ) {

                    Text("Cancel")
                }
            },

            title = {

                Text(
                    text = "Emergency SOS",
                    color = TextWhite
                )
            },

            text = {

                Text(
                    text =
                        "Send emergency alert to nearby hospitals and emergency contacts?",

                    color = TextGray
                )
            },

            containerColor = CardBackground
        )
    }
}
@Composable
fun BottomNavItem(
    icon: ImageVector,
    label: String,
    selected: Boolean,
    onClick: () -> Unit
) {

    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {

        Box(
            modifier = Modifier
                .clip(RoundedCornerShape(15.dp))
                .background(
                    if (selected)
                        PrimaryRed.copy(alpha = 0.15f)
                    else
                        Color.Transparent
                )
                .padding(
                    horizontal = 2.dp,
                    vertical = 1.dp
                )
        ) {

            IconButton(
                onClick = onClick
            ) {

                Icon(
                    imageVector = icon,
                    contentDescription = null,

                    tint =
                        if (selected)
                            PrimaryRed
                        else
                            TextGray,

                    modifier = Modifier.size(22.dp)
                )
            }
        }

        Spacer(modifier = Modifier.height(2.dp))

        Text(
            text = label,

            color =
                if (selected)
                    PrimaryRed
                else
                    TextGray,

            fontSize = 10.sp
        )
    }
}
@Composable
fun SOSNavButton(
    onClick: () -> Unit
) {

    IconButton(
        onClick = onClick,

        modifier = Modifier.size(82.dp)
    ) {

        Box(
            modifier = Modifier
                .size(78.dp)
                .shadow(
                    elevation = 22.dp,
                    shape = CircleShape,
                    ambientColor = PrimaryRed,
                    spotColor = PrimaryRed
                )
                .clip(CircleShape)
                .background(
                    Brush.radialGradient(
                        colors = listOf(
                            Color(0xFFFF5A5A),
                            PrimaryRed
                        )
                    )
                ),

            contentAlignment = Alignment.Center
        ) {

            Text(
                text = "SOS",
                color = Color.White,
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold
            )
        }
    }
}