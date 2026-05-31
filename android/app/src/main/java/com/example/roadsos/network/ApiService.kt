package com.example.roadsos.network

import com.example.roadsos.models.NearbyResponse

import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query
import com.example.roadsos.models.UpdatePlacesRequest
import com.example.roadsos.models.UpdatePlacesResponse
import retrofit2.http.Body
import retrofit2.http.POST

interface ApiService {
    @POST("update_places")
    suspend fun updatePlaces(
        @Body request: UpdatePlacesRequest
    ): Response<UpdatePlacesResponse>

    @GET("nearby")
    suspend fun getNearbyServices(

        @Query("lat")
        lat: Double,

        @Query("lon")
        lon: Double,

        @Query("radius")
        radius: Int,

        @Query("type")
        type: String? = null

    ): Response<NearbyResponse>

    @POST("sos")
    suspend fun triggerSos(@retrofit2.http.Body request: com.example.roadsos.models.SosRequest): Response<com.example.roadsos.models.SosResponse>



    @POST("chat")
    suspend fun sendChatMessage(@retrofit2.http.Body request: com.example.roadsos.models.ChatRequest): Response<com.example.roadsos.models.ChatResponse>
}