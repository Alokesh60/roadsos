package com.example.roadsos.database.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "nearby_services")
data class LocalNearbyService(
    @PrimaryKey
    val id: String,
    val category: String, // "hospital", "police", "garage", "food"
    val name: String,
    val phone: String,
    val latitude: Double,
    val longitude: Double,
    val rating: Double?,
    val isOpenNow: Boolean?,
    val distanceMeters: Float?,
    val estimatedEtaMinutes: Int?,
    val lastUpdated: Long
)
