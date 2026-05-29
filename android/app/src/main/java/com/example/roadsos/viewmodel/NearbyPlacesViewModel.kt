package com.example.roadsos.viewmodel

import android.content.Context
import android.content.pm.PackageManager
import android.location.LocationManager
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.roadsos.models.*
import com.example.roadsos.network.GooglePlacesApiClient
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlin.math.*
import com.example.roadsos.models.BackendPlace
import com.example.roadsos.models.UpdatePlacesRequest
import com.example.roadsos.repository.AIRepository
import java.time.Instant

data class NearbyPlaceItem(
    val name: String,
    val latitude: Double,
    val longitude: Double,
    val category: PlaceCategory,
    val phone: String,
    val address: String,
    val distanceKm: Double
)

class NearbyPlacesViewModel : ViewModel() {
    private val aiRepository = AIRepository()

    private val _nearbyPlaces = MutableStateFlow<List<NearbyPlaceItem>>(emptyList())
    val nearbyPlaces: StateFlow<List<NearbyPlaceItem>> = _nearbyPlaces

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _isGpsActive = MutableStateFlow(true)
    val isGpsActive: StateFlow<Boolean> = _isGpsActive

    private var lastFetchLat: Double = 0.0
    private var lastFetchLon: Double = 0.0

    /**
     * Check if GPS provider is enabled
     */
    fun updateGpsStatus(context: Context) {
        try {
            val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
            _isGpsActive.value = locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)
        } catch (e: Exception) {
            _isGpsActive.value = false
        }
    }

    /**
     * Fetch nearby places only if the user has moved more than 10km from last fetch location
     */
    fun fetchIfNeeded(lat: Double, lon: Double, context: Context) {
        if (lat == 0.0 && lon == 0.0) return

        // First fetch or moved more than 10km
        if (lastFetchLat == 0.0 && lastFetchLon == 0.0) {
            fetchNearbyPlaces(lat, lon, context)
            return
        }

        val distanceFromLastFetch = haversineKm(lastFetchLat, lastFetchLon, lat, lon)
        if (distanceFromLastFetch >= 15.0) {
            fetchNearbyPlaces(lat, lon, context)
        }
    }

    private fun fetchNearbyPlaces(lat: Double, lon: Double, context: Context) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                // Get API Key
                val ai = context.packageManager.getApplicationInfo(context.packageName, PackageManager.GET_META_DATA)
                val apiKey = ai.metaData?.getString("com.google.android.geo.API_KEY") ?: ""
                if (apiKey.isEmpty()) {
                    android.util.Log.e("NearbyPlaces", "API Key is empty!")
                    return@launch
                }

                android.util.Log.d("NearbyPlaces", "Fetching nearby places at $lat, $lon with key=${apiKey.take(10)}...")

                // Make separate requests per category to avoid Google API type conflicts
                val categoryTypes = mapOf(
                    PlaceCategory.POLICE to listOf("police"),
                    PlaceCategory.HOSPITAL to listOf("hospital"),
                    PlaceCategory.GARAGE to listOf("car_repair"),
                    PlaceCategory.FOOD to listOf("restaurant")
                )

                val allPlaces = mutableListOf<NearbyPlaceItem>()

                for ((category, types) in categoryTypes) {
                    try {
                        val request = GooglePlacesRequest(
                            includedTypes = types,
                            maxResultCount = 5,
                            locationRestriction = GoogleLocationRestriction(
                                circle = GoogleCircle(
                                    center = GoogleLocation(lat, lon),
                                    radius = 15000.0 // 15km
                                )
                            )
                        )

                        val response = GooglePlacesApiClient.api.searchNearby(apiKey = apiKey, request = request)

                        if (response.isSuccessful) {
                            val places = response.body()?.places ?: emptyList()
                            android.util.Log.d("NearbyPlaces", "Category ${category.label}: found ${places.size} places")

                            val mappedPlaces = places.mapNotNull { place ->
                                val placeLat = place.location?.latitude ?: return@mapNotNull null
                                val placeLon = place.location?.longitude ?: return@mapNotNull null

                                NearbyPlaceItem(
                                    name = place.displayName?.text ?: "Unknown",
                                    latitude = placeLat,
                                    longitude = placeLon,
                                    category = category,
                                    phone = place.nationalPhoneNumber ?: "",
                                    address = place.formattedAddress ?: "",
                                    distanceKm = haversineKm(lat, lon, placeLat, placeLon)
                                )
                            }.sortedBy { it.distanceKm }.take(3)

                            allPlaces.addAll(mappedPlaces)
                        } else {
                            val errorBody = response.errorBody()?.string() ?: "unknown"
                            android.util.Log.e("NearbyPlaces", "Category ${category.label} failed: ${response.code()} - $errorBody")
                        }
                    } catch (e: Exception) {
                        android.util.Log.e("NearbyPlaces", "Category ${category.label} exception: ${e.message}")
                    }
                }

                android.util.Log.d("NearbyPlaces", "Total places found: ${allPlaces.size}")
                android.util.Log.d(
    "NearbyPlaces",
    "Total places found: ${allPlaces.size}"
)

_nearbyPlaces.value = allPlaces

try {

    val backendPlaces = allPlaces.map { place ->

        BackendPlace(
            id = "${place.name}_${place.latitude}_${place.longitude}",
            name = place.name,
            category = place.category.label,
            phone = place.phone,
            address = place.address,
            latitude = place.latitude,
            longitude = place.longitude,
            distance_km = place.distanceKm
        )
    }

    val updateRequest = UpdatePlacesRequest(
        user_id = "demo_user",
        latitude = lat,
        longitude = lon,
        timestamp = Instant.now().toString(),
        places = backendPlaces
    )

    val backendResponse =
        aiRepository.updatePlaces(updateRequest)

    android.util.Log.d(
        "RoadSOS_AI",
        "Backend sync success = ${backendResponse.isSuccessful}"
    )

} catch (e: Exception) {

    android.util.Log.e(
        "RoadSOS_AI",
        "Backend sync failed: ${e.message}"
    )
}

lastFetchLat = lat
lastFetchLon = lon
            } catch (e: Exception) {
                android.util.Log.e("NearbyPlaces", "Fatal error: ${e.message}")
                e.printStackTrace()
            } finally {
                _isLoading.value = false
            }
        }
    }

    private fun haversineKm(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
        val r = 6371.0
        val dLat = Math.toRadians(lat2 - lat1)
        val dLon = Math.toRadians(lon2 - lon1)
        val a = sin(dLat / 2).pow(2) +
                cos(Math.toRadians(lat1)) * cos(Math.toRadians(lat2)) *
                sin(dLon / 2).pow(2)
        return r * 2 * atan2(sqrt(a), sqrt(1 - a))
    }
}
