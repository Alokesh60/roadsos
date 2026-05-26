package com.example.roadsos.ui.components

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.example.roadsos.models.PlaceCategory
import com.example.roadsos.theme.CardBackground
import com.example.roadsos.viewmodel.NearbyPlaceItem
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import com.google.android.gms.maps.model.CameraPosition
import com.google.android.gms.maps.model.LatLng
import com.google.maps.android.compose.GoogleMap
import com.google.maps.android.compose.MapProperties
import com.google.maps.android.compose.MapUiSettings
import com.google.maps.android.compose.Marker
import com.google.maps.android.compose.MarkerState
import com.google.maps.android.compose.rememberCameraPositionState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Layers
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.foundation.background
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.ui.Alignment

@Composable
fun MapComponent(
    latitude: Double,
    longitude: Double,
    nearbyPlaces: List<NearbyPlaceItem> = emptyList(),
    isSatellite: Boolean = false,
    modifier: Modifier = Modifier,
    onMapClick: (LatLng) -> Unit = {}
) {
    val userLat = latitude.takeIf { it != 0.0 } ?: 28.6139
    val userLon = longitude.takeIf { it != 0.0 } ?: 77.2090
    val userLatLng = LatLng(userLat, userLon)

    val cameraPositionState = rememberCameraPositionState {
        position = CameraPosition.fromLatLngZoom(userLatLng, 15f)
    }

    LaunchedEffect(latitude, longitude) {
        if (latitude != 0.0 && longitude != 0.0) {
            cameraPositionState.position = CameraPosition.fromLatLngZoom(LatLng(latitude, longitude), 15f)
        }
    }

    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = CardBackground),
        shape = RoundedCornerShape(30.dp)
    ) {
        GoogleMap(
            modifier = Modifier.fillMaxSize().clip(RoundedCornerShape(30.dp)),
            cameraPositionState = cameraPositionState,
            properties = MapProperties(
                isMyLocationEnabled = false,
                mapType = if (isSatellite) com.google.maps.android.compose.MapType.SATELLITE else com.google.maps.android.compose.MapType.NORMAL
            ),
            uiSettings = MapUiSettings(
                zoomControlsEnabled = false,
                compassEnabled = false,
                mapToolbarEnabled = false
            ),
            onMapClick = onMapClick
        ) {
            if (latitude != 0.0 && longitude != 0.0) {
                Marker(
                    state = MarkerState(position = userLatLng),
                    title = "Your Location",
                    icon = BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_AZURE)
                )
            }

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
                    snippet = "${place.category.label} • ${String.format("%.1f", place.distanceKm)} km",
                    icon = BitmapDescriptorFactory.defaultMarker(markerColor)
                )
            }
        }
    }
}
