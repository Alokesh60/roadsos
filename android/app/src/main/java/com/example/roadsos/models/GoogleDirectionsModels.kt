package com.example.roadsos.models

import com.google.gson.annotations.SerializedName

data class GoogleDirectionsResponse(
    val routes: List<GoogleRoute>
)

data class GoogleRoute(
    val legs: List<GoogleLeg>,
    @SerializedName("overview_polyline")
    val overviewPolyline: GooglePolyline
)

data class GoogleLeg(
    val distance: GoogleTextValue,
    val duration: GoogleTextValue
)

data class GoogleTextValue(
    val text: String,
    val value: Int
)

data class GooglePolyline(
    val points: String
)
