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
import com.example.roadsos.theme.RoadSoSTheme
import com.example.roadsos.theme.TextGray
import com.example.roadsos.theme.TextWhite
import androidx.activity.compose.BackHandler
import com.example.roadsos.models.EmergencyService
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.runtime.*
import androidx.compose.ui.platform.LocalContext
import com.example.roadsos.LocationUtils
import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.maps.android.compose.*
import androidx.compose.material.icons.filled.Layers
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import com.example.roadsos.utils.EmergencyNumbersProvider
import android.content.Intent
import android.net.Uri
import androidx.core.content.ContextCompat
import android.Manifest
import android.content.pm.PackageManager
import com.example.roadsos.network.GoogleDirectionsApiClient
import kotlinx.coroutines.launch
import android.widget.Toast

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

    val facilities = when (service.type) {
        "Hospital" -> listOf("Emergency", "ICU", "24/7", "Trauma Care", "Ambulance")
        "Police" -> listOf("24/7", "Patrol", "F.I.R", "Emergency Response", "Security")
        "Towing" -> listOf("24/7", "Flatbed", "Jump Start", "Winch", "Roadside Assist")
        "Ambulance" -> listOf("24/7", "Life Support", "Paramedics", "Oxygen")
        else -> listOf("24/7", "Emergency Support")
    }

    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    var isSatellite by remember { mutableStateOf(false) }
    var routeDuration by remember { mutableStateOf<String?>(null) }
    var routeDistance by remember { mutableStateOf<String?>(null) }

    val serviceLocation = LatLng(service.latitude, service.longitude)
    val cameraPositionState = rememberCameraPositionState {
        position = CameraPosition.fromLatLngZoom(serviceLocation, 15f)
    }

    LaunchedEffect(service) {
        LocationUtils.getCurrentLocation(context) { lat, lon ->
            if (lat != 0.0 && lon != 0.0) {
                coroutineScope.launch {
                    try {
                        val ai = context.packageManager.getApplicationInfo(context.packageName, PackageManager.GET_META_DATA)
                        val apiKey = ai.metaData?.getString("com.google.android.geo.API_KEY") ?: ""
                        if (apiKey.isNotEmpty()) {
                            val origin = "$lat,$lon"
                            val destination = "${service.latitude},${service.longitude}"
                            val response = GoogleDirectionsApiClient.api.getDirections(origin, destination, apiKey)
                            if (response.isSuccessful) {
                                val route = response.body()?.routes?.firstOrNull()
                                if (route != null) {
                                    val leg = route.legs.firstOrNull()
                                    if (leg != null) {
                                        routeDuration = leg.duration.text
                                        routeDistance = leg.distance.text
                                    }
                                }
                            }
                        }
                    } catch (e: Exception) {
                        e.printStackTrace()
                    }
                }
            }
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
                .verticalScroll(
                    rememberScrollState()
                )
        ) {

            // MAP HEADER
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(300.dp)
            ) {
                GoogleMap(
                    modifier = Modifier.fillMaxSize(),
                    cameraPositionState = cameraPositionState,
                    properties = MapProperties(
                        isMyLocationEnabled = false,
                        mapType = if (isSatellite) MapType.SATELLITE else MapType.NORMAL
                    ),
                    uiSettings = MapUiSettings(
                        zoomControlsEnabled = false,
                        compassEnabled = false,
                        mapToolbarEnabled = false
                    )
                ) {
                    Marker(
                        state = MarkerState(position = serviceLocation),
                        title = service.name,
                        icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_RED)
                    )
                }

                // TOP BAR
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(
                            horizontal = 20.dp,
                            vertical = 52.dp
                        ),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {

                    IconButton(onClick = onBack) {
                        Box(
                            modifier = Modifier
                                .size(46.dp)
                                .clip(CircleShape)
                                .background(Color(0xFF1A2433).copy(alpha = 0.9f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.ArrowBack,
                                contentDescription = "Back",
                                tint = Color.White
                            )
                        }
                    }

                    IconButton(onClick = { isSatellite = !isSatellite }) {
                        Box(
                            modifier = Modifier
                                .size(46.dp)
                                .clip(CircleShape)
                                .background(Color(0xFF1A2433).copy(alpha = 0.9f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Layers,
                                contentDescription = "Toggle Map Type",
                                tint = if (isSatellite) Color(0xFF4CAF50) else Color.White
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
                            text = if (routeDuration != null) "$routeDuration away" else "Calculating ETA...",
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

                val statusColor = when (service.isOpenNow) {
                    true -> Color.Green
                    false -> Color.Red
                    else -> Color.Gray
                }
                val statusText = when (service.isOpenNow) {
                    true -> "Open Now"
                    false -> "Closed"
                    else -> "Hours Not Available"
                }

                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {

                    Box(
                        modifier = Modifier
                            .size(10.dp)
                            .clip(CircleShape)
                            .background(statusColor)
                    )

                    Spacer(modifier = Modifier.width(8.dp))

                    Text(
                        text = statusText,
                        color = statusColor,
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
                        value = routeDistance ?: "${service.distance_km} km",
                        modifier = Modifier.weight(1f)
                    )

                    DetailInfoCard(
                        title = "ETA",
                        value = routeDuration ?: "Live",
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
                        onClick = {
                            val uri = Uri.parse("google.navigation:q=${service.latitude},${service.longitude}&mode=d")
                            val mapIntent = Intent(Intent.ACTION_VIEW, uri)
                            mapIntent.setPackage("com.google.android.apps.maps")
                            try {
                                context.startActivity(mapIntent)
                            } catch (e: Exception) {
                                // Fallback if Google Maps is not installed
                                val browserUri = Uri.parse("https://www.google.com/maps/dir/?api=1&destination=${service.latitude},${service.longitude}")
                                context.startActivity(Intent(Intent.ACTION_VIEW, browserUri))
                            }
                        },
                        modifier = Modifier.weight(1f)
                    )

                    ActionButton(
                        text = "Call Now",
                        background = PrimaryRed,
                        icon = Icons.Default.Call,
                        onClick = {
                            val cleaned = EmergencyNumbersProvider.cleanPhoneNumber(service.phone)
                            if (cleaned.isEmpty()) {
                                Toast.makeText(context, "Phone number not available for this location.", Toast.LENGTH_SHORT).show()
                            } else {
                                try {
                                    if (ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) == PackageManager.PERMISSION_GRANTED) {
                                        context.startActivity(Intent(Intent.ACTION_CALL, Uri.parse("tel:$cleaned")))
                                    } else {
                                        context.startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:$cleaned")))
                                    }
                                } catch (e: Exception) {
                                    context.startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:$cleaned")))
                                }
                            }
                        },
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
                        text = if (service.address.isNotBlank()) service.address else service.city,
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
                                text = if (service.phone.isNotBlank()) service.phone else "Not available",
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

@Preview(showBackground = true, showSystemUi = true)
@Composable
fun ServiceDetailScreenPreview() {

    val previewService = EmergencyService(
        id = 1,
        name = "AIIMS Trauma Centre",
        type = "Hospital",
        phone = "+91 9876543210",
        address = "Central Avenue",
        city = "Guwahati",
        latitude = 26.1458,
        longitude = 91.7381,
        rating = 4.8,
        distance_km = 0.8
    )

    RoadSoSTheme {
        ServiceDetailScreen(
            service = previewService,
            currentScreen = BottomNavScreen.SERVICE_DETAIL,
            onTabSelected = {},
            onBack = {}
        )
    }
}

@Composable
fun ActionButton(
    text: String,
    background: Color,
    icon: ImageVector,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {

    Card(
        onClick = onClick,
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