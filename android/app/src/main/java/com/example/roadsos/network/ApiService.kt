package com.example.roadsos.network

import com.example.roadsos.models.NearbyResponse

import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Query

interface ApiService {

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
}