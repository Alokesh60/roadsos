package com.example.roadsos.domain.model

data class PlaceModel(
    val id: String,
    val name: String,
    val type: PlaceType,
    val latitude: Double,
    val longitude: Double,
    val distanceMeters: Int,
    val phoneNumber: String? = null
)

enum class PlaceType {
    POLICE,
    HOSPITAL,
    GARAGE_TOWING,
    RESTAURANT,
    UNKNOWN
}
