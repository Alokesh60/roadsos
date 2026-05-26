package com.example.roadsos.screens.home

import android.content.pm.PackageManager
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Directions
import androidx.compose.material.icons.filled.Layers
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.roadsos.LocationUtils
import com.example.roadsos.models.PlaceCategory
import com.example.roadsos.network.GoogleDirectionsApiClient
import com.example.roadsos.theme.DarkBackground
import com.example.roadsos.theme.PrimaryRed
import com.example.roadsos.theme.TextGray
import com.example.roadsos.theme.TextWhite
import com.example.roadsos.viewmodel.NearbyPlaceItem
import com.example.roadsos.viewmodel.NearbyPlacesViewModel
import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.LatLngBounds
import com.google.maps.android.compose.*
import kotlinx.coroutines.launch

@Composable
fun FullMapScreen(
    initialCategory: PlaceCategory? = null,
    onBack: () -> Unit
) {
    val context = LocalContext.current
    val nearbyPlacesViewModel: NearbyPlacesViewModel = viewModel()
    val coroutineScope = rememberCoroutineScope()

    var latitude by remember { mutableStateOf(0.0) }
    var longitude by remember { mutableStateOf(0.0) }
    var selectedPlace by remember { mutableStateOf<NearbyPlaceItem?>(null) }
    var routeDuration by remember { mutableStateOf<String?>(null) }
    var routeDistance by remember { mutableStateOf<String?>(null) }
    var routePoints by remember { mutableStateOf<List<LatLng>>(emptyList()) }
    var isSatellite by remember { mutableStateOf(false) }
    
    val nearbyPlaces by nearbyPlacesViewModel.nearbyPlaces.collectAsState()

    val cameraPositionState = rememberCameraPositionState()

    // Get API Key from Manifest
    val apiKey = remember {
        try {
            val ai = context.packageManager.getApplicationInfo(context.packageName, PackageManager.GET_META_DATA)
            ai.metaData?.getString("com.google.android.geo.API_KEY") ?: ""
        } catch (e: Exception) {
            ""
        }
    }

    LaunchedEffect(Unit) {
        LocationUtils.getCurrentLocation(context) { lat, lon ->
            if (lat != 0.0 && lon != 0.0) {
                latitude = lat
                longitude = lon
                nearbyPlacesViewModel.fetchIfNeeded(lat, lon, context)
                cameraPositionState.position = CameraPosition.fromLatLngZoom(LatLng(lat, lon), 15f)
            }
        }
    }

    var autoSelected by remember { mutableStateOf(false) }

    // Function to draw route using Google Directions API
    val drawRoute = { place: NearbyPlaceItem ->
        selectedPlace = place
        coroutineScope.launch {
            try {
                val origin = "$latitude,$longitude"
                val destination = "${place.latitude},${place.longitude}"
                val response = GoogleDirectionsApiClient.api.getDirections(origin, destination, apiKey)
                
                if (response.isSuccessful) {
                    val route = response.body()?.routes?.firstOrNull()
                    if (route != null) {
                        val leg = route.legs.firstOrNull()
                        if (leg != null) {
                            routeDistance = leg.distance.text
                            routeDuration = leg.duration.text
                        }

                        // Decode polyline
                        val points = decodePolyline(route.overviewPolyline.points)
                        routePoints = points

                        // Zoom to fit route
                        if (points.isNotEmpty()) {
                            val boundsBuilder = LatLngBounds.Builder()
                            points.forEach { boundsBuilder.include(it) }
                            boundsBuilder.include(LatLng(latitude, longitude))
                            boundsBuilder.include(LatLng(place.latitude, place.longitude))
                            
                            cameraPositionState.animate(
                                CameraUpdateFactory.newLatLngBounds(boundsBuilder.build(), 100)
                            )
                        }
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    // Auto-select nearest place of requested category
    LaunchedEffect(nearbyPlaces, initialCategory, latitude, longitude) {
        if (!autoSelected && initialCategory != null && nearbyPlaces.isNotEmpty() && latitude != 0.0) {
            val place = nearbyPlaces.find { it.category == initialCategory }
            if (place != null) {
                autoSelected = true
                drawRoute(place)
            }
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
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
            ),
            onMapClick = {
                // Clear selection on map click
                selectedPlace = null
                routePoints = emptyList()
            }
        ) {
            // Draw Route Polyline
            if (routePoints.isNotEmpty()) {
                Polyline(
                    points = routePoints,
                    color = Color(0xFF2196F3),
                    width = 15f,
                    geodesic = true
                )
            }

            // Add User Marker
            if (latitude != 0.0 && longitude != 0.0) {
                Marker(
                    state = MarkerState(position = LatLng(latitude, longitude)),
                    title = "Your Location",
                    icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_AZURE)
                )
            }

            // Add Place Markers
            nearbyPlaces.forEach { place ->
                val markerColor = when (place.category) {
                    PlaceCategory.POLICE -> BitmapDescriptorFactory.HUE_BLUE
                    PlaceCategory.HOSPITAL -> BitmapDescriptorFactory.HUE_RED
                    PlaceCategory.GARAGE -> BitmapDescriptorFactory.HUE_ORANGE
                    PlaceCategory.FOOD -> BitmapDescriptorFactory.HUE_GREEN
                }

                Marker(
                    state = MarkerState(position = LatLng(place.latitude, place.longitude)),
                    title = place.name,
                    snippet = "Tap for directions",
                    icon = BitmapDescriptorFactory.defaultMarker(markerColor),
                    onClick = {
                        drawRoute(place)
                        it.showInfoWindow()
                        true
                    }
                )
            }
        }

        // Top Bar: Back Button and Legend
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 48.dp, start = 16.dp, end = 16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.Top
        ) {
            IconButton(
                onClick = onBack,
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(Color(0xFF182232).copy(alpha = 0.9f))
            ) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Back",
                    tint = Color.White
                )
            }

            // Satellite Toggle Button
            IconButton(
                onClick = { isSatellite = !isSatellite },
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(Color(0xFF182232).copy(alpha = 0.9f))
            ) {
                Icon(
                    imageVector = Icons.Filled.Layers,
                    contentDescription = if (isSatellite) "Normal Map" else "Satellite Map",
                    tint = if (isSatellite) Color(0xFF4CAF50) else Color.White
                )
            }

            // Map Legend
            Card(
                colors = CardDefaults.cardColors(containerColor = Color(0xFF182232).copy(alpha = 0.9f)),
                shape = RoundedCornerShape(16.dp)
            ) {
                Column(
                    modifier = Modifier.padding(12.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    LegendItem(color = Color(0xFF2196F3), label = "Police Station")
                    LegendItem(color = Color(0xFFF44336), label = "Hospital")
                    LegendItem(color = Color(0xFFFF9800), label = "Garage")
                    LegendItem(color = Color(0xFF4CAF50), label = "Food & Rest")
                }
            }
        }

        // Bottom Details Card
        if (selectedPlace != null) {
            Card(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .fillMaxWidth()
                    .padding(16.dp),
                colors = CardDefaults.cardColors(containerColor = DarkBackground),
                shape = RoundedCornerShape(24.dp)
            ) {
                Column(
                    modifier = Modifier.padding(20.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = selectedPlace!!.name,
                            color = TextWhite,
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.weight(1f)
                        )
                        
                        if (routeDuration != null) {
                            Card(
                                colors = CardDefaults.cardColors(containerColor = Color(0xFF4CAF50).copy(alpha = 0.2f)),
                                shape = RoundedCornerShape(12.dp)
                            ) {
                                Text(
                                    text = routeDuration!!,
                                    color = Color(0xFF4CAF50),
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Text(
                        text = selectedPlace!!.category.label,
                        color = PrimaryRed,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                    
                    Spacer(modifier = Modifier.height(4.dp))
                    
                    Text(
                        text = if (routeDistance != null) "${routeDistance} away" else "Calculating...",
                        color = TextGray,
                        fontSize = 14.sp
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    Button(
                        onClick = {
                            // Already drawing route, could launch intent to Google Maps app here if desired
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(50.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2196F3)),
                        shape = RoundedCornerShape(16.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Directions,
                            contentDescription = "Directions",
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "Directions Shown",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }
        }
    }
}

// Utility to decode Google Maps encoded polyline
private fun decodePolyline(encoded: String): List<LatLng> {
    val poly = ArrayList<LatLng>()
    var index = 0
    val len = encoded.length
    var lat = 0
    var lng = 0

    while (index < len) {
        var b: Int
        var shift = 0
        var result = 0
        do {
            b = encoded[index++].code - 63
            result = result or (b and 0x1f shl shift)
            shift += 5
        } while (b >= 0x20)
        val dlat = if (result and 1 != 0) (result shr 1).inv() else result shr 1
        lat += dlat

        shift = 0
        result = 0
        do {
            b = encoded[index++].code - 63
            result = result or (b and 0x1f shl shift)
            shift += 5
        } while (b >= 0x20)
        val dlng = if (result and 1 != 0) (result shr 1).inv() else result shr 1
        lng += dlng

        val p = LatLng(lat.toDouble() / 1E5, lng.toDouble() / 1E5)
        poly.add(p)
    }
    return poly
}
