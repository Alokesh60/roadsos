package com.example.roadsos.network

object ChatApiClient {

    val service:
            ChatApiService =

        ApiClient.retrofit
            .create(
                ChatApiService::class.java
            )
}