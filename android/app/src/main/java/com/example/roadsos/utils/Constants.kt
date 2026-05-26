package com.example.roadsos.utils

object Constants {
    const val PLACES_BASE_URL = "https://places.googleapis.com/"
    const val BACKEND_BASE_URL = "https://api.roadsos.dummy/" // Dummy backend for now
    
    const val LOCATION_UPDATE_INTERVAL = 10000L
    const val LOCATION_FASTEST_INTERVAL = 5000L
    
    const val LOCATION_CHANGE_THRESHOLD_METERS = 10000f // 10km as requested
}
