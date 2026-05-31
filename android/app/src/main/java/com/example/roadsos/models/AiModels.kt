package com.example.roadsos.models

data class ChatRequest(
    val session_id: String,
    val user_message: String,
    val context: ChatContext,
    val history: List<ChatMessage>
)

data class ChatContext(
    val lat: Double,
    val lng: Double,
    val state: String? = null,
    val district: String? = null,
    val nearest_highway: String? = null,
    val nearest_hospital: String? = null,
    val nearest_hospital_phone: String? = null,
    val nearest_police_phone: String? = null,
    val nearest_ambulance_phone: String? = null,
    val nearest_towing_phone: String? = null,
    val is_sos_active: Boolean,
    val nearby_places: List<NearbyPlaceJson>
)

data class ChatMessage(
    val role: String,
    val content: String
)

data class ChatResponse(
    val session_id: String,
    val reply: String,
    val intent_detected: String?,
    val detected_type: String?,
    val priority: String?,
    val suggested_actions: List<SuggestedAction>?,
    val source: String
)
