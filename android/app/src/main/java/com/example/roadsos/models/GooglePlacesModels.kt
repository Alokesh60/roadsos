package com.example.roadsos.models

import com.google.gson.annotations.SerializedName

data class GooglePlacesResponse(
    val places: List<GooglePlace>?
)

data class GooglePlace(
    val id: String?,
    @SerializedName("displayName") val displayName: GoogleDisplayName?,
    val location: GoogleLocation?,
    val types: List<String>?,
    val formattedAddress: String?,
    @SerializedName("nationalPhoneNumber") val nationalPhoneNumber: String?
)

data class GoogleDisplayName(
    val text: String?
)

data class GoogleLocation(
    val latitude: Double,
    val longitude: Double
)

data class GooglePlacesRequest(
    val includedTypes: List<String>,
    val maxResultCount: Int,
    val locationRestriction: GoogleLocationRestriction
)

data class GoogleLocationRestriction(
    val circle: GoogleCircle
)

data class GoogleCircle(
    val center: GoogleLocation,
    val radius: Double
)
