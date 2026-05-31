package com.example.roadsos.repository

import com.example.roadsos.models.UpdatePlacesRequest
import com.example.roadsos.network.ApiClient
import com.example.roadsos.network.ApiService

class AIRepository {

    private val api =
        ApiClient.retrofit.create(ApiService::class.java)

    suspend fun updatePlaces(
        request: UpdatePlacesRequest
    ) = api.updatePlaces(request)
}