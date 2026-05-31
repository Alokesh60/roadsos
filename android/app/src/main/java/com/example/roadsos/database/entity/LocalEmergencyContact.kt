package com.example.roadsos.database.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "emergency_contacts")
data class LocalEmergencyContact(
    @PrimaryKey
    val id: String, // Same as Firestore document ID
    val name: String,
    val phone: String,
    val countryCode: String,
    val relation: String,
    val priority: Int
)
