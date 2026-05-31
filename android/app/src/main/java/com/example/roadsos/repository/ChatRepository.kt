package com.example.roadsos.repository

import com.example.roadsos.models.ChatRequest
import com.example.roadsos.models.ChatResponse
import com.example.roadsos.network.ChatApiClient

class ChatRepository {

    suspend fun sendMessage(

        request: ChatRequest

    ): Result<ChatResponse> {

        return try {

            val response =

                ChatApiClient
                    .service
                    .sendMessage(request)

            if (

                response.isSuccessful

                &&

                response.body() != null
            ) {

                Result.success(
                    response.body()!!
                )

            } else {

                Result.failure(

                    Exception(
                        "Server error"
                    )
                )
            }

        } catch (e: Exception) {

            Result.failure(e)
        }
    }
}