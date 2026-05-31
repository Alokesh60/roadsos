package com.example.roadsos.utils

import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.util.Log
import com.example.roadsos.database.AppDatabase
import com.example.roadsos.database.entity.LocalNearbyService
import com.example.roadsos.models.GooglePlacesRequest
import com.example.roadsos.models.GoogleLocationRestriction
import com.example.roadsos.models.GoogleCircle
import com.example.roadsos.models.GoogleLocation
import com.example.roadsos.network.GooglePlacesApiClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import java.util.UUID

object PlacesSyncManager {
    private const val TAG = "PlacesSyncManager"
    
    suspend fun syncNearbyServices(context: Context, latitude: Double, longitude: Double) {
        if (!NetworkUtils.isNetworkAvailable(context)) return

        val appInfo = context.packageManager.getApplicationInfo(context.packageName, PackageManager.GET_META_DATA)
        val apiKey = appInfo.metaData.getString("com.google.android.geo.API_KEY") ?: return

        val serviceDao = AppDatabase.getDatabase(context).nearbyServiceDao()
        val apiService = GooglePlacesApiClient.api

        val types = mapOf(
            "police" to listOf("police"),
            "hospital" to listOf("hospital"),
            "garage" to listOf("car_repair"),
            "food" to listOf("restaurant")
        )

        coroutineScope {
            types.map { (key, includedTypes) ->
                async {
                    try {
                        val request = GooglePlacesRequest(
                            includedTypes = includedTypes,
                            locationRestriction = GoogleLocationRestriction(
                                circle = GoogleCircle(
                                    center = GoogleLocation(latitude = latitude, longitude = longitude),
                                    radius = 10000.0 // 10km radius
                                )
                            ),
                            maxResultCount = 10
                        )
                        
                        val response = apiService.searchNearby(apiKey = apiKey, request = request)
                        if (response.isSuccessful) {
                            val places = response.body()?.places ?: emptyList()
                            
                            val localPlaces = places.map { place ->
                                val phone = place.nationalPhoneNumber ?: place.internationalPhoneNumber ?: ""
                                val placeLat = place.location?.latitude ?: 0.0
                                val placeLng = place.location?.longitude ?: 0.0
                                
                                val results = FloatArray(1)
                                Location.distanceBetween(latitude, longitude, placeLat, placeLng, results)
                                val distance = results[0]

                                // Rough city driving heuristic: ~30km/h = ~500 meters per minute
                                val etaMinutes = (distance / 500.0).toInt().coerceAtLeast(1)

                                val isOpenNow = place.currentOpeningHours?.openNow
                                    ?: (place.businessStatus == "OPERATIONAL")

                                LocalNearbyService(
                                    id = place.id ?: UUID.randomUUID().toString(),
                                    category = key,
                                    name = place.displayName?.text ?: key.uppercase(),
                                    phone = phone.replace(" ", ""),
                                    latitude = placeLat,
                                    longitude = placeLng,
                                    rating = place.rating,
                                    isOpenNow = isOpenNow,
                                    distanceMeters = distance,
                                    estimatedEtaMinutes = etaMinutes,
                                    lastUpdated = System.currentTimeMillis()
                                )
                            }

                            serviceDao.deleteByCategory(key)
                            if (localPlaces.isNotEmpty()) {
                                serviceDao.insertServices(localPlaces)
                            }
                        } else {
                            Log.e(TAG, "Failed to fetch $key: ${response.errorBody()?.string()}")
                        }
                    } catch (e: Exception) {
                        Log.e(TAG, "Error syncing $key", e)
                    }
                }
            }.forEach { it.await() }
        }
    }
}
