package com.example.roadsos.models

data class EmergencyService(

    val id: Int,

    val name: String,

    val type: String,

    val phone: String,

    val address: String,

    val city: String,

    val latitude: Double,

    val longitude: Double,

    val rating: Double,

    val distance_km: Double,

    val isOpenNow: Boolean? = null
)