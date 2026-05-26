package com.example.roadsos.screens.home

import androidx.compose.animation.core.InfiniteTransition
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
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
import androidx.compose.material.icons.filled.Layers
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
import com.example.roadsos.LocationUtils
import com.example.roadsos.models.PlaceCategory
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
import com.example.roadsos.viewmodel.NearbyPlacesViewModel
import com.example.roadsos.viewmodel.NearbyPlaceItem
import kotlinx.coroutines.delay
import androidx.compose.ui.platform.LocalContext

@Composable
fun HomeScreen(
    currentScreen: BottomNavScreen,
    onTabSelected: (BottomNavScreen) -> Unit,
    onMapClick: (PlaceCategory?) -> Unit
) {
    val context = LocalContext.current
    val nearbyPlacesViewModel: NearbyPlacesViewModel = viewModel()

    var latitude by remember { mutableStateOf(0.0) }
    var longitude by remember { mutableStateOf(0.0) }

    val nearbyPlaces by nearbyPlacesViewModel.nearbyPlaces.collectAsState()
    val isGpsActive by nearbyPlacesViewModel.isGpsActive.collectAsState()

    val profileViewModel: com.example.roadsos.viewmodel.ProfileViewModel = viewModel()
    val profileState = profileViewModel.profileState.collectAsState().value
    val profileUrl = if (profileState is com.example.roadsos.viewmodel.ProfileState.Success) profileState.profile.profileUrl else ""

    LaunchedEffect(Unit) {
        profileViewModel.fetchProfile()
    }

    // Get GPS location and fetch nearby places
    LaunchedEffect(Unit) {
        LocationUtils.getCurrentLocation(context) { lat, lon ->
            if (lat != 0.0 && lon != 0.0) {
                latitude = lat
                longitude = lon
                nearbyPlacesViewModel.fetchIfNeeded(lat, lon, context)
            }
        }
    }

    // Periodically check GPS status (every 3 seconds)
    LaunchedEffect(Unit) {
        while (true) {
            nearbyPlacesViewModel.updateGpsStatus(context)
            delay(3000)
        }
    }

    var showNotifications by remember {
        mutableStateOf(false)
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

            // FIXED HEADER

            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp)
            ) {

                Spacer(
                    modifier =
                        Modifier.height(55.dp)
                )

                TopSection(
                    isGpsActive = isGpsActive,
                    profileUrl = profileUrl,

                    onNotificationClick = {

                        showNotifications = true
                    },

                    onProfileClick = {

                        onTabSelected(
                            BottomNavScreen.PROFILE
                        )
                    }
                )
            }

            // SCROLLABLE CONTENT

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(
                        rememberScrollState()
                    )
                    .padding(horizontal = 20.dp)
                    .padding(bottom = 110.dp)
            ) {

                Spacer(
                    modifier =
                        Modifier.height(22.dp)
                )
                Row(
                    verticalAlignment =
                        Alignment.CenterVertically
                ) {

                    Box(
                        modifier = Modifier
                            .size(10.dp)
                            .clip(CircleShape)
                            .background(Color.Green)
                    )

                    Spacer(
                        modifier =
                            Modifier.width(8.dp)
                    )

                    Text(
                        text = "GPS Active",
                        color = TextGray,
                        fontSize = 13.sp
                    )
                }

                Spacer(
                    modifier =
                        Modifier.height(18.dp)
                )

                MapLegend(onCategoryClick = { category ->
                    onMapClick(category)
                })
                Spacer(modifier = Modifier.height(8.dp))

                LocationMapCard(
                    latitude = latitude,
                    longitude = longitude,
                    nearbyPlaces = nearbyPlaces,
                    onMapClick = onMapClick
                )

                Spacer(
                    modifier =
                        Modifier.height(26.dp)
                )

                QuickActionsSection()

                Spacer(
                    modifier =
                        Modifier.height(28.dp)
                )

                SOSSection()

                Spacer(
                    modifier =
                        Modifier.height(28.dp)
                )

                NearbyServicesSection(latitude = latitude, longitude = longitude)

                Spacer(
                    modifier =
                        Modifier.height(40.dp)
                )
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

        // BOTTOM NAVBAR

        Box(
            modifier =
                Modifier.align(
                    Alignment.BottomCenter
                )
        ) {

            if (
                sosError.isNotEmpty()
            ) {

                Column(
                    modifier = Modifier
                        .align(
                            Alignment.BottomCenter
                        )
                        .padding(
                            bottom = 130.dp
                        )
                        .padding(
                            horizontal = 18.dp
                        )
                ) {

                    ErrorBanner(
                        message = sosError
                    )
                }
            }

            BottomNavBar(
                currentScreen =
                    currentScreen,

                onTabSelected =
                    onTabSelected,

                onSOSError = {

                    sosError = it
                }
            )
        }
    }
}

@Composable
fun TopSection(
    isGpsActive: Boolean = true,
    profileUrl: String = "",
    onNotificationClick: () -> Unit,
    onProfileClick: () -> Unit
) {
    // Blinking animation for GPS dot
    val infiniteTransition = rememberInfiniteTransition(label = "gps_blink")
    val blinkAlpha by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 0.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 800),
            repeatMode = RepeatMode.Reverse
        ),
        label = "gps_blink_alpha"
    )

    val gpsColor = if (isGpsActive) Color(0xFF4CAF50) else Color(0xFFE53935)
    val gpsDotAlpha = if (isGpsActive) blinkAlpha else 1f
    val gpsText = if (isGpsActive) "GPS Active" else "GPS Inactive"

    Row(
        modifier = Modifier.fillMaxWidth(),

        horizontalArrangement =
            Arrangement.SpaceBetween,

        verticalAlignment =
            Alignment.CenterVertically
    ) {

        Column {

            Text(
                text = "RoadSoS",

                color = TextWhite,

                fontSize = 34.sp,

                fontWeight =
                    FontWeight.Bold
            )

            // REDUCED GAP

            Spacer(
                modifier =
                    Modifier.height(1.dp)
            )

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
                        .background(gpsColor.copy(alpha = gpsDotAlpha))
                )

                Spacer(modifier = Modifier.width(8.dp))

                Text(
                    text = gpsText,
                    color = gpsColor,
                    fontSize = 13.sp
                )
            }
        }

        Row(verticalAlignment = Alignment.CenterVertically) {

            // NOTIFICATION

            IconButton(
                onClick = onNotificationClick
            ) {

                BadgedBox(
                    badge = {

                        Badge(
                            containerColor =
                                PrimaryRed
                        )
                    }
                ) {

                    Icon(
                        imageVector =
                            Icons.Default.Notifications,

                        contentDescription =
                            null,

                        tint =
                            TextWhite,

                        modifier =
                            Modifier.size(28.dp)
                    )
                }
            }

            Spacer(
                modifier =
                    Modifier.width(6.dp)
            )

            // PROFILE

            IconButton(onClick = onProfileClick) {
                if (profileUrl.isNotEmpty()) {
                    coil.compose.AsyncImage(
                        model = profileUrl,
                        contentDescription = "Profile",
                        contentScale = androidx.compose.ui.layout.ContentScale.Crop,
                        modifier = Modifier
                            .size(34.dp)
                            .clip(CircleShape)
                    )
                } else {
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
fun MapLegend(onCategoryClick: (PlaceCategory) -> Unit = {}) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(start = 4.dp, end = 4.dp, bottom = 8.dp)
    ) {
        Text(
            text = "Quick Navigate to Nearest:",
            color = TextGray,
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
            modifier = Modifier.padding(bottom = 8.dp, start = 4.dp)
        )
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            LegendItem("Police", Color(0xFF1565C0), onClick = { onCategoryClick(PlaceCategory.POLICE) })
            LegendItem("Hospital", Color(0xFFC62828), onClick = { onCategoryClick(PlaceCategory.HOSPITAL) })
            LegendItem("Garage", Color(0xFFE65100), onClick = { onCategoryClick(PlaceCategory.GARAGE) })
            LegendItem("Food", Color(0xFF2E7D32), onClick = { onCategoryClick(PlaceCategory.FOOD) })
        }
    }
}

@Composable
fun LegendItem(label: String, color: Color, onClick: (() -> Unit)? = null) {
    Surface(
        color = color.copy(alpha = 0.15f), // Light tint of the category color
        shape = RoundedCornerShape(20.dp),
        modifier = if (onClick != null) Modifier.clip(RoundedCornerShape(20.dp)).clickable { onClick() } else Modifier
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(12.dp)
                    .clip(CircleShape)
                    .background(color)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = label,
                color = TextWhite,
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold
            )
        }
    }
}

@Composable
fun LocationMapCard(
    latitude: Double,
    longitude: Double,
    nearbyPlaces: List<NearbyPlaceItem> = emptyList(),
    onMapClick: (PlaceCategory?) -> Unit = {}
) {

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(250.dp),

        colors = CardDefaults.cardColors(
            containerColor = CardBackground
        ),

        shape = RoundedCornerShape(30.dp),
        onClick = { onMapClick(null) }
    ) {

        var isSatellite by remember { mutableStateOf(false) }

        Box(
            modifier = Modifier.fillMaxSize()
        ) {

            // MAP COMPONENT (Google Map)
            com.example.roadsos.ui.components.MapComponent(
                latitude = latitude,
                longitude = longitude,
                nearbyPlaces = nearbyPlaces,
                isSatellite = isSatellite,
                modifier = Modifier.fillMaxSize()
            )
            
            // Transparent overlay to ensure the Card captures clicks instead of the MapView
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Transparent)
                    .clickable { onMapClick(null) }
            )

            // Satellite Toggle Button (Placed ON TOP of the transparent overlay)
            androidx.compose.material3.IconButton(
                onClick = { isSatellite = !isSatellite },
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(16.dp)
                    .size(40.dp)
                    .clip(CircleShape)
                    .background(Color(0xFF182232).copy(alpha = 0.9f))
            ) {
                androidx.compose.material3.Icon(
                    imageVector = Icons.Filled.Layers,
                    contentDescription = if (isSatellite) "Normal Map" else "Satellite Map",
                    tint = if (isSatellite) Color(0xFF4CAF50) else Color.White
                )
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
        Triple("Hospitals", "104", Icons.Default.LocalHospital),
        Triple("Towing", "103", Icons.Default.DirectionsCar)
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
fun NearbyServicesSection(latitude: Double, longitude: Double) {

    val viewModel: ServiceViewModel = viewModel()

    val services by viewModel.services.collectAsState()

    LaunchedEffect(latitude, longitude) {
        if (latitude != 0.0 && longitude != 0.0) {
            viewModel.fetchNearbyServices(
                lat = latitude,
                lon = longitude
            )
        }
    }

    // Latitude & Longitude Coordinate Display
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(
                text = "Lat: ${if (latitude == 0.0) "..." else String.format("%.5f", latitude)}",
                color = TextGray,
                fontSize = 14.sp
            )
            Text(
                text = "Lon: ${if (longitude == 0.0) "..." else String.format("%.5f", longitude)}",
                color = TextGray,
                fontSize = 14.sp
            )
        }
    }

    Spacer(modifier = Modifier.height(18.dp))

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