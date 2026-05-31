package com.example.roadsos.models

data class BackendPlace(
    val id: String,
    val name: String,
    val category: String,
    val phone: String,
    val address: String,
    val latitude: Double,
    val longitude: Double,
    val distance_km: Double
)

data class UpdatePlacesRequest(
    val user_id: String,
    val latitude: Double,
    val longitude: Double,
    val timestamp: String,
    val places: List<BackendPlace>
)

data class UpdatePlacesResponse(
    val success: Boolean,
    val places_received: Int
)