package com.example.roadsos.network

import com.google.android.gms.tasks.Tasks
import com.google.firebase.auth.FirebaseAuth
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object ApiClient {

    private const val BASE_URL =
        "https://roadsos-backend-ufme.onrender.com/"

    private val logging =
        HttpLoggingInterceptor().apply {

            level =
                HttpLoggingInterceptor.Level.BODY
        }

    private val authInterceptor = Interceptor { chain ->
        val original = chain.request()
        val user = FirebaseAuth.getInstance().currentUser
        
        if (user != null) {
            try {
                // Fetch the ID token synchronously
                val task = user.getIdToken(true)
                val result = Tasks.await(task, 10, TimeUnit.SECONDS)
                val token = result.token
                
                if (token != null) {
                    android.util.Log.d("FIREBASE_TOKEN", "Bearer $token")
                    val request = original.newBuilder()
                        .header("Authorization", "Bearer $token")
                        .build()
                    return@Interceptor chain.proceed(request)
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
        
        // Proceed without token if not authenticated or if fetching failed
        chain.proceed(original)
    }

    private val client =
        OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(logging)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()

    val retrofit: Retrofit =
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(
                GsonConverterFactory.create()
            )
            .build()
}