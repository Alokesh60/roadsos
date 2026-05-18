package com.example.roadsos.repository

import com.example.roadsos.network.ApiClient
import com.example.roadsos.network.ApiService

class ServiceRepository {

    private val api =
        ApiClient
            .retrofit
            .create(ApiService::class.java)

    suspend fun getNearbyServices(

        lat: Double,

        lon: Double,

        radius: Int,

        type: String?

    ) = api.getNearbyServices(
        lat,
        lon,
        radius,
        type
    )
}