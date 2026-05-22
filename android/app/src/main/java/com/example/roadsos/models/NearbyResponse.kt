package com.example.roadsos.models

data class NearbyResponse(

    val success: Boolean,

    val count: Int,

    val radius_km: Int,

    val data: List<EmergencyService>
)