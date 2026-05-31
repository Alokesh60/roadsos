package com.example.roadsos.models

data class SosRequest(
    val message: String,
    val latitude: Double,
    val longitude: Double,
    val country: String = "India",
    val nearby_services: Map<String, String>,
    val nearby_places: List<NearbyPlaceJson>,
    val source: String,
    val offline_mode: Boolean = false
)

data class NearbyPlaceJson(
    val id: String,
    val category: String,
    val name: String,
    val phone: String,
    val latitude: Double,
    val longitude: Double,
    val rating: Double?,
    val isOpenNow: Boolean?,
    val distanceMeters: Float?,
    val estimatedEtaMinutes: Int?
)

data class SosResponse(
    val success: Boolean,
    val sos_triggered: Boolean,
    val message: String,
    val guidance: String,
    val source: String,
    val detected_type: String,
    val priority: String,
    val suggested_actions: List<SuggestedAction>?,
    val emergency_contact_notifications: List<NotificationResult>?,
    val nearby_responder_notifications: List<NotificationResult>?
)

data class SuggestedAction(
    val label: String,
    val number: String
)

data class NotificationResult(
    val uid: String,
    val type: String,
    val distance_km: Double? = null,
    val result: Map<String, Any>? = null
)
