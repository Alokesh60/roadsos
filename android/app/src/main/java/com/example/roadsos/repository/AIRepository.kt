package com.example.roadsos.repository

import com.example.roadsos.models.ChatRequest
import com.example.roadsos.network.ApiClient
import com.example.roadsos.network.ApiService

class AIRepository {

    private val apiService = ApiClient.retrofit.create(ApiService::class.java)

    suspend fun sendChatMessage(request: ChatRequest): Result<String> {
        return try {
            val response = apiService.sendChatMessage(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!.reply)
            } else {
                Result.failure(Exception(response.errorBody()?.string()))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
