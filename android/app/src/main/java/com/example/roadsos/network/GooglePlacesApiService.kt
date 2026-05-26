package com.example.roadsos.network

import com.example.roadsos.models.GooglePlacesRequest
import com.example.roadsos.models.GooglePlacesResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.POST

interface GooglePlacesApiService {
    @POST("v1/places:searchNearby")
    suspend fun searchNearby(
        @Header("X-Goog-Api-Key") apiKey: String,
        @Header("X-Goog-FieldMask") fieldMask: String = "places.id,places.displayName,places.location,places.types,places.formattedAddress,places.nationalPhoneNumber",
        @Body request: GooglePlacesRequest
    ): Response<GooglePlacesResponse>
}
