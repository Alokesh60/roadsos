package com.example.roadsos.viewmodel

import android.content.Context
import android.content.pm.PackageManager
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.roadsos.models.*
import com.example.roadsos.network.GooglePlacesApiClient
import com.example.roadsos.utils.EmergencyNumbersProvider
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlin.math.*

class ServiceViewModel : ViewModel() {

    private val _services = MutableStateFlow<List<EmergencyService>>(emptyList())
    val services: StateFlow<List<EmergencyService>> = _services

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _selectedFilter = MutableStateFlow("All")
    val selectedFilter: StateFlow<String> = _selectedFilter

    private val _searchText = MutableStateFlow("")
    val searchText: StateFlow<String> = _searchText

    fun setFilter(filter: String) {
        _selectedFilter.value = filter
    }

    fun setSearchText(text: String) {
        _searchText.value = text
    }

    fun fetchNearbyServices(
        lat: Double,
        lon: Double,
        context: Context
    ) {
        if (lat == 0.0 && lon == 0.0) return

        viewModelScope.launch {
            _isLoading.value = true
            try {
                // Get API Key
                val ai = context.packageManager.getApplicationInfo(context.packageName, PackageManager.GET_META_DATA)
                val apiKey = ai.metaData?.getString("com.google.android.geo.API_KEY") ?: ""
                if (apiKey.isEmpty()) {
                    android.util.Log.e("ServiceViewModel", "API Key is empty!")
                    return@launch
                }

                val emergencyNumbers = EmergencyNumbersProvider.getEmergencyNumbers(context, lat, lon)

                // 1. Always add Ambulance first (centrally dispatched)
                val ambulanceService = EmergencyService(
                    id = 0,
                    name = "Central Ambulance Dispatch",
                    type = "Ambulance",
                    phone = emergencyNumbers.ambulance,
                    address = "Serves ${emergencyNumbers.countryName}",
                    city = emergencyNumbers.countryName,
                    latitude = lat,
                    longitude = lon,
                    rating = 5.0,
                    distance_km = 0.0
                )

                val allServices = mutableListOf<EmergencyService>(ambulanceService)

                // 2. Fetch Police, Hospital, Towing from Google Places (50km radius)
                val categoryMapping = mapOf(
                    "Hospital" to listOf("hospital"),
                    "Police" to listOf("police"),
                    "Towing" to listOf("car_repair")
                )

                var idCounter = 1

                for ((uiCategory, types) in categoryMapping) {
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
                            
                            val mapped = places.mapNotNull { place ->
                                val placeLat = place.location?.latitude ?: return@mapNotNull null
                                val placeLon = place.location?.longitude ?: return@mapNotNull null
                                
                                // Clean up city/locality from address
                                val parts = place.formattedAddress?.split(",")?.map { it.trim() } ?: emptyList()
                                val city = if (parts.size >= 3) parts[parts.size - 3] else if (parts.size >= 2) parts[parts.size - 2] else ""
                                
                                // Use the Google Maps phone number, but if it's a Police station without a direct number,
                                // fallback to the country's central police dispatch number (e.g. 100 in India)
                                val rawPhone = if (!place.nationalPhoneNumber.isNullOrBlank()) {
                                    place.nationalPhoneNumber
                                } else if (uiCategory == "Police") {
                                    emergencyNumbers.police
                                } else {
                                    ""
                                }

                                EmergencyService(
                                    id = idCounter++,
                                    name = place.displayName?.text ?: "Unknown",
                                    type = uiCategory,
                                    phone = rawPhone,
                                    address = place.formattedAddress ?: "",
                                    city = city,
                                    latitude = placeLat,
                                    longitude = placeLon,
                                    rating = place.rating ?: 0.0,
                                    distance_km = haversineKm(lat, lon, placeLat, placeLon).let { round(it * 10) / 10.0 },
                                    isOpenNow = place.currentOpeningHours?.openNow
                                )
                            }
                            
                            // Only add services with valid phone numbers OR police stations
                            // Filter out completely garbage unrated places
                            allServices.addAll(mapped.filter { 
                                (it.type == "Police" || EmergencyNumbersProvider.isValidPhoneNumber(it.phone)) &&
                                (it.rating >= 2.0 || it.type == "Police")
                            })
                        }
                    } catch (e: Exception) {
                        android.util.Log.e("ServiceViewModel", "Category $uiCategory failed: ${e.message}")
                    }
                }

                // Sort by distance (ambulance will be 0.0 so it stays first)
                _services.value = allServices.sortedBy { it.distance_km }

            } catch (e: Exception) {
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