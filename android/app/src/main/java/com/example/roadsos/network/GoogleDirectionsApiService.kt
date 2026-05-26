package com.example.roadsos.network

import com.example.roadsos.models.GoogleDirectionsResponse
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Query

interface GoogleDirectionsApiService {
    @GET("api/directions/json")
    suspend fun getDirections(
        @Query("origin") origin: String,
        @Query("destination") destination: String,
        @Query("key") apiKey: String
    ): Response<GoogleDirectionsResponse>
}
