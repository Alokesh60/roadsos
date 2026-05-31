package com.example.roadsos.models

data class ChatRequest(

    val session_id: String = "roadsos_mobile",

    val user_message: String,

    val context: ChatContext = ChatContext(),

    val history: List<HistoryMessage> =
        emptyList()
)

data class ChatContext(

    val lat: Double? = null,

    val lng: Double? = null,

    val state: String? = null,

    val district: String? = null,

    val nearest_highway: String? = null,

    val nearest_hospital: String? = null,

    val nearest_hospital_phone: String? = null,

    val nearest_police_phone: String? = null,

    val is_sos_active: Boolean = false
)

data class HistoryMessage(

    val role: String,

    val content: String
)