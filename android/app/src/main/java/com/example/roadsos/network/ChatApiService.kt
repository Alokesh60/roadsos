package com.example.roadsos.network

import com.example.roadsos.models.ChatRequest
import com.example.roadsos.models.ChatResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface ChatApiService {

    @POST("chat")
    suspend fun sendMessage(

        @Body
        request: ChatRequest

    ): Response<ChatResponse>
}